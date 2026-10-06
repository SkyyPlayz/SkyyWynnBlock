# Foraging armor - design (the gathering set, 8 tiers: Wood + the 7 bench woods)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `docs/answered/gear.md` (the 2026-10-05 LOCK "oh lets remove wood armor from the
cloth section ...", the REFERENCE line about bark armor, the NOTE about Tree Feller, the ARMOR TYPES lock), `docs/answered/skills.md` (Tree Feller lock 2026-09-25),
`research/cloud/Gathering-Tiers-Draft.md`, `Collection-Unlocks-Draft.md`, `Enchanted-Materials-Draft.md`, `Crude-Armor-Design.md` (set stat style), `research/Tool-Levels-Spec.md` (axe / Fortune).
Every number below is a placeholder and a Server Setup row (times in seconds).
Reconciled 2026-10-06, see research/cloud/Gathering-Numbers-Reconciled.md (sections 4, 5, 6, 8, 9 and questions 3 / 8 changed).

## 1. What Skyy locked (short)

- Foraging armor is a **gathering set**, not Cloth. Tier 1 = vanilla Wood armor (`Armor_Wood`). Then the Farmer's Workbench wood ladder: Softwood, Lightwood, Hardwood, Drywood, Darkwood, Redwood, Goldenwood.
- Each design echoes one metal set (Copper ... Onyxium) but is still obviously wood and looks vanilla.
- Stats: **Foraging Fortune** (bonus logs) + **chopping speed** (+ Foraging XP on higher tiers), **low Defense**. **Tree Feller** on the higher tiers. Axes get Tree Feller too (tool-levels round).
- Tree Feller already exists as a SkyyTrees perk (extra logs 1/2/4/5/6/10 at levels 1-6, 3 s cooldown): **reuse it, no second felling system**.

So the ladder is **8 rows**: Wood is tier 0 (the vanilla start), Softwood..Goldenwood are tiers 1-7 and line up with Copper..Onyxium (Gathering-Tiers-Draft 2.3).
Open check: if the bench already calls the vanilla Wood armor "Softwood", it collapses to 7 rows (question 1).

## 2. Tier table

Gate = **Foraging level** (gathering gear checks Foraging, Tool-Levels-Spec: hatchet -> Foraging; same rule as hatchets). Bands copy the metal bands of the echoed set.
No class gate and no armor-type bonus: Foraging armor is not Plate / Leather / Cloth, so any class wears it with its own stats only (it never competes with class armor for the class bonus).

| # | Tier | Echoes | Band / Foraging gate | Collection unlock (recipe appears) | Wood used (tree group) |
|---|---|---|---|---|---|
| 0 | **Wood** (vanilla) | Crude / Wood | 1-13 / 1 | none (vanilla recipe, start) | any plank / log |
| 1 | **Softwood** | Copper | 10-18 / 10 | Oak Log VI (Gathering draft: Oak III-IV tool, VI armor) | F1 common (Oak) |
| 2 | **Lightwood** | Iron | 15-23 / 15 | Birch Log VI | F1 / F2 (Birch, Maple) |
| 3 | **Hardwood** | Thorium | 20-28 / 20 | Maple Log VI | F2 uncommon (Maple) |
| 4 | **Drywood** | Cobalt | 25-38 / 25 | Redwood Log VI | F3 northern (Redwood, Cedar, Fir) |
| 5 | **Darkwood** | Adamantite | 35-43 / 35 | Azure Log VI | F4 strange (Azure, Petrified) |
| 6 | **Redwood** (armor name) | Mithril | 40-49 / 40 | F5 key log VI (Frostwood or Crystalwood) | F5 elemental |
| 7 | **Goldenwood** | Onyxium | 50-59 / 50 (later, own band) | F5 key log IX + the hidden Goldenwood tree (Zone 4/5, later) | F5 + Goldenwood |

R3 holds: the recipe shows only after the collection tier; no NPC sells it and coins never skip it. The armor name "Redwood" is **not** the Redwood Log (F3): the draft's wood-to-tier map is a guess (UNVERIFIED, section 9).

## 3. Recipes

Per set (4 pieces: Head, Chest, Legs, Hands; no Feet slot) the piece split of Enchanted items is Head 5 / Chest 8 / Legs 7 / Hands 4 = 24 (same split as the metal sets, Enchanted-Materials-Draft 4).

| Tier | Raw logs per set | Enchanted wood per set | Extra vanilla part (UNVERIFIED id) | Feel |
|---|---|---|---|---|
| Wood | vanilla | 0 | vanilla recipe | minutes |
| Softwood | 200 | 0 | Plant Fibre 31 (Crude-set style) | about 1 hour |
| Lightwood | 100 | 8 Enchanted Common Wood | Softwood-tier leather strip or fibre | about 2 hours |
| Hardwood | 0 | 16 Enchanted (F2) | that wood's planks | about 3 hours |
| Drywood | 0 | 24 Enchanted (F3) | planks | 4-8 hours |
| Darkwood | 0 | 24 Enchanted (F4) | planks + Tree Sap | 4-8 hours |
| Redwood | 0 | 24 Enchanted (F5) | planks + Tree Sap | 4-8 hours |
| Goldenwood | 0 | 24 Enchanted (F5) + 4 Enchanted Block | Goldenwood planks | 8+ hours |

Cost check: 24 Enchanted = 24 x 160 = 3,840 base logs (python-checked). Same as the Enchanted draft's "gathering armor = 24 Enchanted". Each tier's armor needs **that tier's wood**, so you cannot skip ahead by buying low-tier wood.
Upgrade path (like the bench): optional rule that tier N+1 also eats the same piece of tier N (default off, question 4). Salvage must **not** return Enchanted items (dupe class from the Bronze loop).
Craft level: crafted at **your Foraging level**, clamped to the tier band (Gear spec rule "crafted at your level").

## 4. Stats

Fortune scale (placeholder, question 3): 1 point = +1% double drop (the same unit as tools, skill perk and trees); armor cap 15 (`armor.fortune.cap`); a full Goldenwood set = **12** (x1.15 set bonus, x rarity, before the cap).

| Tier | Foraging Fortune (set) | Chopping speed (set) | Foraging XP (set) | Health (set) | Resist (set) |
|---|---|---|---|---|---|
| Wood | 1 | +1% | - | 10 | 7% |
| Softwood | 1.5 | +2% | - | 12 | 9% |
| Lightwood | 2.5 | +3% | - | 23 | 12% |
| Hardwood | 4 | +4% | - | 30 | 16% |
| Drywood | 5.5 | +6% | +2% | 30 | 16% |
| Darkwood | 7.5 | +8% | +4% | 34 | 20% |
| Redwood | 10 | +10% | +6% | 34 | 20% |
| Goldenwood | 12 | +12% | +8% | 35 | 22% |

- Health / resist = **about 50% of the echoed metal set** (Copper 25 HP, Iron 46, Thorium / Cobalt 61, Adamantite / Mithril 68; python-checked 12 / 23 / 30 / 34). Low Defense is the price of gathering stats. Wood armor stays vanilla's own numbers.
- Piece split of Fortune and speed: Head 20% / Chest 35% / Legs 30% / Hands 15%, rounded, the remainder to Chest. Health and resist follow the usual armor piece split (Head 5 / Chest 9 / Legs 7 / Hands 4 shares).
- Fortune and speed work **while worn** (like tool Fortune while held). They add to the tool's own, so a Mithril hatchet plus a Redwood set stack.
- Reforge allowed, same pools as hatchets: Foraging Fortune, Foraging Wisdom, Chopping Speed.
- Rarities: gathering armor is crafted, so it is **Normal** (Unique+ only through reforge or a later Foraging drop); reforge / drops may raise it; Fortune x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3 (no multiplier on chopping speed); Set rarity is not used.

## 5. Set bonus (2 / 4 piece)

| Pieces worn | Bonus | Why |
|---|---|---|
| 4 | **Fortune x1.15** (before the cap), **Tree Feller level** from the table in section 6, plus **Sap Sense**: a leaf / sap glow shows trees of the matching tier within 8 blocks (a small, harmless indicator) | the lock says Feller on higher tiers |

Wood and Softwood have no set bonus (no 2-piece Fortune any more). Mixed tiers: the bonus uses the **lowest tier** of the worn pieces, the stats add per piece. That blocks "one Goldenwood piece plus junk".

## 6. Tree Feller per tier

Levels use the **same table as the perk**: extra logs 1 / 2 / 4 / 5 / 6 / 10, cooldown 3 s, same height as the cut (SkyyTrees lock 2026-09-25). Armor grants it with the **full set (4 pieces)**:

| Tier | Wood | Softwood | Lightwood | Hardwood | Drywood | Darkwood | Redwood | Goldenwood |
|---|---|---|---|---|---|---|---|---|
| Feller level (4 pieces) | - | - | **1** (+1 log) | **2** (+2) | **3** (+4) | **4** (+5) | **5** (+6) | **6** (+10) |

Extra logs break **only through the normal break path** (same tool, so the Foraging gate applies), as SkyyTrees already does.

### How the sources stack (no doubling)

Three sources can give Tree Feller: the SkyyTrees skill-tree perk, the axe (tool-levels round), the armor. Rule: **effective level = the MAX of the three**, never a sum, one shared 3 s cooldown (`feller.cooldownSec`).
Optional small reward for having all three: **+1 level, capped at 6** (`foraging.feller.stackBonus`, default 0 = off). Capped total extra logs per swing: `foraging.feller.maxLogs` = 10 (the perk's own level-6 number).
Hard-coded safety: one Feller activation never starts another (extra logs from Feller do not trigger Feller), and a very big tree is cut in **layers of at most 10** (the reason the lock jumps to 10, not "whole layer").

## 7. The look (generated at build time)

Never commit vanilla textures: the build script recolours the vanilla Wood armor texture / model into each tier (same rule as other assets) and writes them into the jar.
Style comes from Skyy's bark reference (picture stays local in `research/refs/foraging-armor-bark.jpg`): layered **bark plates**, jagged bark tassels at the hem, **vine / root trims** over shoulders and collar, a **glowing green sap-vein** pattern up the chest, small leaves.

| Tier | Echoes (shape) | Base wood colour | Trim / detail | Sap-vein glow |
|---|---|---|---|---|
| Wood | vanilla | vanilla | none | none |
| Softwood | Copper: open plates, thin bands | pale tan | rope lashings, one vine | very faint |
| Lightwood | Iron: layered plates, rivet-like pegs | light birch grey | wooden pegs, leaf tassels | faint green |
| Hardwood | Thorium: thick shoulders, heavy collar | warm brown | root collar | green |
| Drywood | Cobalt: angular cuirass | bleached grey-brown, cracked | dry vine, split bark | pale yellow-green |
| Darkwood | Adamantite: tall spiked pauldrons | near-black brown | thorn spikes | teal |
| Redwood | Mithril: smooth, elegant, tall collar | deep red | curling root trims, gold knots | bright green |
| Goldenwood | Onyxium: ornate, hooded, full | gold-streaked heartwood | gold leaf inlays | white-gold glow |

The glow only brightens up the ladder (Skyy's note). Hands = wrapped bark gauntlets; Head = bark crown (no full helm, low Defense feel).

## 8. Server Setup rows (SkyWynn Menu -> Server Setup -> Gear -> Foraging armor)

| Row | Default |
|---|---|
| `foraging.armor.on` (whole set on / off) | on |
| Level band + gate per tier (8 rows) | section 2 |
| Fortune per tier (8 rows) | section 4 |
| Chopping speed % per tier (8 rows) | section 4 |
| Foraging XP % per tier (8 rows) | section 4 |
| Health / resist share of the echoed metal | 50% |
| Enchanted + log cost per tier (8 rows) | section 3 |
| 4-piece Fortune multiplier | 1.15 |
| `armor.fortune.cap` / `armor.swing.cap` | 15 / 12 |
| 4-piece Feller level per tier (8 rows) | section 6 |
| `foraging.feller.stackBonus` (+1 if perk + axe + armor) | 0 (off) |
| `foraging.feller.maxLogs` (cap per swing) | 10 |
| `feller.cooldownSec` (shared with the perk) | 3 |
| Fortune cap per swing, extra logs included | 3 bonus logs per log broken |
| Sap Sense on / radius | on / 8 blocks |
| Mixed-tier rule (lowest tier counts) | on |
| Upgrade-from-previous-tier recipe | off |

## 9. Exploits and guards

| Risk | Guard |
|---|---|
| **Fortune on every Feller log** multiplies logs (10 extra x Fortune 40 x Foraging Bag) | Fortune rolls on the **block you hit**; Feller logs get Fortune at `bonusBlock.fortuneRate` **50%** (setting, same number as before), and the whole swing is capped at `maxLogs` + the Fortune cap |
| Feller log counts for Collections and XP repeatedly | each log counts once; no bonus-log chains (a bonus log never triggers more bonus logs) |
| Collection dupes: Fortune logs counted again for the Enchanted item | collections count **real drops once**; Enchanted crafting never returns the base counted twice |
| Salvage returns Enchanted wood (loop) | salvage returns no Enchanted items; Bazaar spread is 22.2%, so a crafted set must not sell above the sum of its parts x 0.9 / 1.1 loop break |
| Swapping armor between swings (wear Feller set, swap back) | Fortune and Feller read the worn set **at the moment of the break**; the cooldown is per player, not per item |
| Low-level player in Goldenwood gear | the Foraging gate: under-level gear gives **no stats** (the same under-level rule as tools, with the red "Requires Foraging N" popup) |
| Server crash from a huge tree | layers capped at 10 logs; a per-swing cap; Feller never breaks non-log blocks (leaves untouched) |
| Axe + armor + perk summing to a 20-log swing | MAX rule, cap 10 (section 6) |
| Pets / accessories pushing Fortune past the budget | per-source caps (tool 25, armor 15, accessories 10, pets 10, collections 10) + the global `perk.doubleDropMax` 1.0 |

## For the local session (UNVERIFIED)

1. Which log types the Farmer's Workbench counts as Softwood / Lightwood / Hardwood / Drywood / Darkwood / Redwood / Goldenwood (`Bench_Farming` recipes, `Wood_*` resource types in Assets.zip). Section 2's tree-group column is my guess.
2. Whether vanilla `Armor_Wood` is already the "Softwood" step (then 7 rows, not 8) and what ingredient the vanilla Wood armor recipe uses.
3. Whether the bench has an armor tab for these recipes and how its upgrade recipes chain (previous piece as an ingredient?).
4. Vanilla Wood armor stats and model / texture layout for the recolour (the build script generates it; nothing is committed).
5. Item ids for planks / Plant Fibre / Tree Sap and whether "any species of the group" resource types exist (Enchanted draft question 6).
6. How Foraging Fortune is defined in code today (points per 100 or percent) and whether armor stats can carry a new `chopSpeed` and `foragingXp` stat on `GearData`.
7. SkyyTrees: whether the Tree Feller perk level can be read from the bridge map by SkyyGear (or the armor writes a `feller.armorLevel` bridge key and SkyyTrees takes the max), and whether a "no re-trigger" guard exists.
8. Whether armor stats can be re-balanced to 50% of the metal set without breaking the vanilla armor-box hide (armor types round).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is the vanilla Wood armor its own tier (8 rows) or the Softwood step (7 rows)? | 8 rows, Wood is tier 0 |
| 2 | Tree Feller on the armor: full set only, or per piece (1 level per 1-2 pieces)? | full set (4 pieces) |
| 3 | Foraging Fortune scale: points where 100 = +1 log per log, or percent chance? | points, 1 point = +1% double drop, full Goldenwood = 12 (was 40; reconciled 2026-10-06) |
| 4 | Should each tier eat the previous tier's piece (bench upgrade style)? | no, raw wood + Enchanted only |
| 5 | Stack rule for Feller sources: MAX of three, or MAX +1 when all three? | MAX only |
| 6 | Goldenwood gate: 50-59 (later band) or 40-49 with Onyxium? | 50-59, comes later |
| 7 | Should the glowing sap veins be a real light source or just a bright texture? | texture only |
| 8 | Should Wood armor give any Fortune at all (it is the vanilla item)? | yes, 1 (a small gift; was 4, reconciled 2026-10-06) |
