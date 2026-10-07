# Zone 4-5 materials - Ember, Amberite and Drakonite (ores, drops, bars, collections, prices)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/SkyyArmory-Roadmap.md` (section 2 tiers), `research/cloud/Gathering-Tiers-Draft.md`, `research/cloud/Tool-Levels-Revision.md`, `research/cloud/Collection-Unlocks-Draft.md`, `research/cloud/Enchanted-Materials-Draft.md`, `research/cloud/Economy-Audit.md` (C4, C13), `research/cloud/Zone-Bosses-Ideas.md`, `research/cloud/Zone-Islands-Layout.md`, `research/cloud/Mob-Levels-Refit.md`, `research/Collections-Spec.md`, `research/Smithing-Smelting-Spec.md`, `docs/answered/economy.md`, `docs/answered/skills.md`, `docs/answered/world.md`. Every number is a placeholder and a Server Setup row (times in seconds). Facts that need the game files are marked UNVERIFIED.

## 0. The decisions this follows (not re-decided)

| Source | What it fixes here |
|---|---|
| `docs/answered/mobs.md` / `docs/answered/world.md` LOCKED 2026-10-01 | Zone 4 = Lv 45-60, guardian 60; R8 LOCKED: Zone 5 = the dinosaur caves under Zone 4, Lv 60-75, the dragon boss at 75 ("needs our own gear tiers above 49 first") |
| `docs/answered/gear.md` LOCKED bands | Wood/Crude 1-13 ... Mithril/Onyxium 40-49; Cindersteel 50-59, Amberite 58-67, Drakonite 66-75 are the Roadmap's **proposal** (`research/cloud/SkyyArmory-Roadmap.md` section 2), used as given |
| `docs/answered/economy.md` LOCKED 2026-10-04 | ore prices x2 per tier (Copper 5 ... Onyxium 3,712); processed goods (bars) +20% over raw inputs (never above 22.2%) |
| `docs/answered/economy.md` LOCKED 2026-10-03 + R3 | coins never skip a collection, tier or recipe; NPC shops never sell unlocks |
| `docs/answered/skills.md` LOCKED 2026-10-04 | Mining XP per block never shrinks as you level, only the level cost rises; live pay: stone 1, copper 5, iron 8, thorium 18, mithril 25 |
| `docs/answered/skills.md` LOCKED 2026-10-02 | need Mining N to use a level-N pickaxe; new tools always get a level |
| `research/cloud/Economy-Audit.md` C4 (proposal, applied as asked) | cumulative premium along any chain from a Bazaar-buyable input <= 15% (`bazaar.maxChainPremium`): Enchanted +10%, Block +4.5% (1.1495x; `research/cloud/Chain-Premium-Fix.md`); Enchanted only from **raw** items, never from bars |
| `research/cloud/Collection-Unlocks-Draft.md` grammar | I shard, II XP, IV next-tier tools (E curve: III), V Enchanted (E: IV), VI armor, IX capstone |

## 1. The three materials at a glance

| | **Cindersteel (T8)** | **Amberite (T9)** | **Drakonite (T10)** |
|---|---|---|---|
| Band | 50-59 | 58-67 | 66-75 |
| Ore | **Ember Ore** (`Ore_Ember`) | **Amberite Ore** (`Ore_Amberite`) | **Drakonite Ore** (`Ore_Drakonite`) |
| Gate item | **Ember Core** (guardian) | **Fossil Shard** (ore bonus + dinosaurs) | **Drake Scale** (deep mobs) + **Dragon Scale** (dragon, mini-boss) |
| Bar | Cindersteel Bar = 1 Ember Ore | Amberite Bar = 1 Amberite Ore | Drakonite Bar = 1 Drakonite Ore + 1 Drake Scale |
| Lore line | "Rejected stamps, still warm" - the Devastated Lands are where the Department of Arrivals burns returned paperwork; the ash hardens into ore | "Resin from a waiting room tree that was never told to leave" - a fossil archive nobody filed | "The dragon's loose change" - scales shed while it paced the queue for its egg |
| Look | dark steel, orange seams (Roadmap) | warm gold-brown, fossil inlays | green-black, wing motif |

Bars follow the vanilla furnace shape: 1 ore -> 1 bar (`research/Smithing-Smelting-Spec.md` 2.5 table). Furnace times (placeholders): Cindersteel 40 s, Amberite 50 s, Drakonite 60 s (Mithril 30 s, Adamantite 20 s).

## 2. Ores: where they spawn

Veins per chunk = 16 x 16 columns over the whole height. Host = the S3 "Volcanic / frozen" group already in Collections (Basalt, Volcanic Rock) for Ember, new "Fossil Seam" rock for the other two. All spawn values are Server Setup rows `ore.<id>.*`.

| Ore | Zone / biome | Host rock | Depth (y) | Vein size | Veins per chunk | Ore per chunk | Notes |
|---|---|---|---|---|---|---|---|
| **Ember Ore** | Zone 4: Charred Woodlands, caldera slopes, **volcanic caves** (names UNVERIFIED) | Basalt, Volcanic Rock, Magma | surface veins y 150-260 (1 per chunk, small); cave veins y 40-140 | 5-9 | 3.0 (1 surface + 2 cave) | 21 | glows (light 8); next to lava, so lava burns apply |
| **Amberite Ore** | Zone 5 caves: Fossil Seams, bone ribs, the amber groves | Fossil Seam (new, `Rock_Fossil`) | y 30-120 | 4-7 | 2.0 | 11 | veins sit inside big skeleton / rib set pieces; Fossil Shard bonus drop |
| **Drakonite Ore** | Zone 5 deep: the lava lake approach and the dragon's cavern rim | Dark basalt + Fossil Seam | y 20-60 only | 3-5 | 0.8 | 3.2 | the rarest; clusters of 2-3 near the dragon lair (**no veins inside the arena**) |

Rules: veins never spawn within 40 blocks of a town or outpost; a mined vein does not regrow in a profile world (Q2); ore counts for collections only when you break it yourself (`research/Collections-Spec.md` counting rules), never from placed blocks.

## 3. Mining tier, hardness and XP

Spine extension (rows 1-7 are from `research/cloud/Gathering-Tiers-Draft.md` 0):

| Tier | Ore | Pickaxe needed (min) | Quality (UNVERIFIED) | Mining level for that pick | Mining XP per ore | Smithing XP per bar |
|---|---|---|---|---|---|---|
| T6 | Mithril | Adamantite | 5 (known) | 40 | 25 | 25 |
| T7 | Onyxium (no source; hole) | Mithril | - | 40 | 40 (spec) | 40 |
| **T8** | **Ember Ore** | **Mithril** pickaxe (skips the T7 hole) | 6 | 50 | **55** | 55 |
| **T9** | **Amberite Ore** | **Cindersteel** pickaxe | 7 | 58 | **70** | 70 |
| **T10** | **Drakonite Ore** | **Amberite** pickaxe | 8 | 66 | **100** | 100 |
| T11 / T12 | Voidglass, Aetherium | drops only (Roadmap) | - | - | - | - |
Rule kept: tier N ore needs the tier N-1 pickaxe (Mithril ore needs Adamantite). The Mining level to use a pick is its tool level (band start of the pick's own tier). Ember is the only skip because Onyxium has no source; if Onyxium ever becomes obtainable, T8 ore moves to "Onyxium pickaxe" (Q1).

Hardness (placeholder): hits to break = Mithril ore x1.25 / x1.5 / x2 for Ember / Amberite / Drakonite at the same pick level (UNVERIFIED how hardness is stored; `tool.power` ladder in `research/cloud/Tool-Levels-Revision.md` 2 still applies). XP stays flat per block (LOCKED: gain never shrinks).

Pace check (python): ore per hour (placeholder 280 / 200 / 120, with walking) x XP / Mining level cost `10 + 5L + 1.5L^2` at the band start: Mithril today 2.9 levels per hour; **Ember 3.8, Amberite 2.6, Drakonite 1.75**. Drakonite is slower on purpose (rare, deepest); raise its XP to 120 if Skyy wants the same pace (Q6).

## 4. Drops (mobs, guardian, dragon)

Mob ids are UNVERIFIED (seen in `research/cloud/Zone-Bosses-Ideas.md`: `Emberwulf`, `Rex_Cave`, `Raptor_Cave`, `Pterodactyl`, `Trillodon`, `Dragon_Fire`).

| Drop | Source | Rate | Qty | Notes |
|---|---|---|---|---|
| **Ember Core** | Zone 4 guardian "Ember Warden" (Lv 60) | 100% | 2-3 per kill (first kill +3); one daily re-fight (Zone-Bosses Q3) | tradable on Auction House, **not** a Bazaar item (no base price); Hard gate: 1 per Cindersteel tool, weapon or armor piece |
| Ember Core (rare) | Zone 4 elites (Emberwulf, Fire Golem) | 0.4% | 1 | keeps the grind alive between boss days |
| **Fossil Shard** | breaking Amberite Ore | 10% per ore | 1-2 | counts for its own collection |
| Fossil Shard | Zone 5 dinosaurs (Raptor_Cave, Trillodon, Rex_Cave) | 6% / 6% / 40% | 1-3 | Rex is the Zone 5 mini-boss |
| **Drake Scale** | Zone 5 deep mobs (level 66+), elites | 8% normal / 25% elite | 1 | needed 1 per Drakonite Bar (24 for a set: about 300 normal kills) |
| **Dragon Scale** | the Zone 5 dragon (Lv 75); first kill 6, daily 2 | 100% first, 70% daily | 1-3 | non-hostile after the story fight; 1 per Drakonite piece (6 per kit) |
| Dragon Scale (side) | Zone 5 deep mini-boss "Brood Rex" (Lv 66-70) | 2% | 1 | so a Lv 66 player is not locked out of Drakonite by a Lv 75 boss (Q4) |
| Ember Shard (junk) | Zone 4 mobs | 12% | 1-2 | sells to NPC for a small coin amount; no recipe (filler for the Cinder Day special) |

Item rate check (python): Fossil Shard base 600 x 10% = 60 coins per ore (+0.2% on a 30,000 ore); Drake Scale base 9,000 x 8% = 720 per kill, in line with mob coin drops of that level (UNVERIFIED mob coin table).

## 5. Bazaar base prices

Fit of the live metal ladder (python, `research/cloud/Enchanted-Materials-Draft.md` 6): 5 / 16 / 48 / 144 / 480 / 1,440 / 3,712 gives step ratios 3.2, 3.0, 3.0, 3.33, 3.0, 2.58; a log-linear fit gives **x3.0 per tier**, so T8 / T9 / T10 would be 12.2k / 36.9k / 111k. I set them lower (x2.96 / x2.73 / x2.5 per tier) because the Enchanted Block must stay under the Bazaar's 1e9 per-product ceiling.

| Material | Base | Bazaar buy / sell | Bar (+20%) | Enchanted (160 raw x 1.10) | Enchanted Block (160 Enchanted x 1.045) | Block under 1e9? |
|---|---|---|---|---|---|---|
| Mithril (ref) | 1,440 | 1,584 / 1,296 | 1,728 | 253,440 | 42,375,168 | yes |
| Onyxium (ref) | 3,712 | 4,083 / 3,341 | 4,454 | 653,312 | 109,233,766 | yes |
| **Ember Ore** | **11,000** | 12,100 / 9,900 | **13,200** | 1,936,000 | 323,699,200 | yes |
| **Amberite Ore** | **30,000** | 33,000 / 27,000 | **36,000** | 5,280,000 | 882,816,000 | yes (88%) |
| **Drakonite Ore** | **75,000** | 82,500 / 67,500 | **90,000** (+ scale: priced as inputs x 1.2) | 13,200,000 | 2,207,040,000 | **no** |
| Fossil Shard | 600 | - | - | no Enchanted form | - | - |
| Drake Scale | 9,000 | - | - | no Enchanted form | - | - |

- **No Drakonite Block** at launch (default). An Enchanted Drakonite is capped by the price ceiling; the only fixes are a lower price (33k would break the ladder) or a higher ceiling (a local check, Q5).
- Loop check (python): buy ore x1.10 -> bar sells at 0.9 x 1.2 / 1.10 = **0.982** of cost (matches the live tightest, `research/cloud/Economy-Audit.md` C13); Enchanted from raw: 0.9 x 1.10 / 1.10 = **0.900**; Block 0.9 x 1.1495 / 1.10 = **0.9405**; cumulative chain premium 1.10 x 1.045 = **1.1495 <= 15%**. An Enchanted made from **bars** would pay 1.08 (a loop) - so the recipe takes **ore only**, never bars (C4).
- Drakonite Bar with a scale: the +20% applies on ore + scale together; the scale is not an Enchanted input.
- Pocket Shard output of these ores is allowed only at the shard tiers Skyy sets in `research/cloud/Pocket-Shards-Spec.md` (ores stay plain items; no compaction before collection V).

## 6. Collections (tier unlock grammar)

Curves from `research/cloud/Collection-Unlocks-Draft.md` 0.1: Ember = **R** (8 tiers, 25 ... 5,000: Zone 4 is a big zone and the ore is common); Amberite and Drakonite = **E** (7 tiers, 10 ... 1,000: rare). R moves the gate to IV and Enchanted to V; E to III and IV. Pocket Shard recipes need SkyyMinions (not built). Time to tier at the placeholder ore rate (python): Ember IV (250) 0.9 h, VI (1,000) 3.6 h, VIII (5,000) 18 h; Amberite III (50) 0.2 h, IV 0.5 h, VII (1,000) 5 h; Drakonite III 0.4 h, IV 0.8 h, VII 8.3 h.

| Collection | I | II | III | IV | V | VI | VII | VIII | Cap |
|---|---|---|---|---|---|---|---|---|---|
| **Ember Ore (R)** | Ember Pocket Shard | +2,500 Mining XP | - | **Amberite pickaxe + shovel** (T9) | Enchanted Ember | Mining gear T8 (Ember-trimmed set, later) | merged into VIII | +6,000 XP; Compactor chain tier | VIII: **Enchanted Ember Block** + Fortune +3 |
| **Amberite Ore (E)** | Amberite Pocket Shard | +3,000 XP | **Drakonite pickaxe + shovel** (T10) | Enchanted Amberite | Mining gear T9 | - | **Enchanted Amberite Block** + Fortune +3 | - | VII = cap |
| **Drakonite Ore (E)** | Drakonite Pocket Shard | +4,000 XP | **Voidglass pickaxe** placeholder (T11, drops-only tier: recipe slot reserved, no recipe yet) | Enchanted Drakonite | Mining gear T10 | - | **+8,000 XP** + Fortune +3 (no Block) | - | VII = cap |
| Mithril Ore (existing E) | - | - | gate III now opens **Cindersteel pickaxe + shovel** (T8) instead of the Onyxium placeholder | - | - | - | - | - | - |
| **Fossil Shard (R)** | Shard | +1,000 XP | Fossil display cabinet (decor) | Amberite armor trim recipe | - | - | - | +3,000 XP | - |
| **Drake Scale (R)** | Shard | +1,200 XP | - | Drakonite armor trim recipe | - | - | - | +4,000 XP | - |
Ember Core and Dragon Scale have **no collection** (boss items; the daily limit is the pacing; R3 still holds since they are not buyable at NPCs).

Fortune perks use the 10-per-skill cap of `research/cloud/Gathering-Numbers-Reconciled.md` (`coll.fortune.cap`): the three caps above (+3 each) would add 9 on top of the earlier six tiers' values; the earlier table must be re-split when Skyy picks the cap (Q8).

## 7. Enchanted forms (160:1) and the ladder

| Item | Recipe | Credit when obtained (never when crafted) |
|---|---|---|
| Enchanted Ember / Amberite / Drakonite | 160 raw ore | +160 to the ore's collection |
| Enchanted Ember Block / Enchanted Amberite Block | 160 Enchanted | +25,600 |
| Stack sizes | 64 / 16 (`ench.stack`, `ench.blockStack`) | - |
Tier-up tool recipes extend the table of `research/cloud/Enchanted-Materials-Draft.md` 4 (tool part = 1 Enchanted per step: 1, 1, 2, 2, 3, 4):

| Recipe | Extra ingredient |
|---|---|
| Cindersteel (T8) pickaxe / shovel | 4 Enchanted **Mithril** (stands in for the missing T7) |
| Amberite (T9) pickaxe / shovel | 5 Enchanted Ember |
| Drakonite (T10) pickaxe / shovel | 6 Enchanted Amberite |
| Mining armor T8 / T9 / T10 (later, 4 pieces) | 24 Enchanted of its own tier (3,840 ore) + bars |
Cost feel (python): a tool part is 640 / 800 / 960 ore; Bazaar coin cost of the part is 1.0M (4 Enchanted Mithril) / 9.7M / 31.7M, so the **gathering** path (a few hours) is the intended one, as with every earlier tier.

## 8. How the materials feed gear (placeholder bar counts; vanilla counts UNVERIFIED)

| Item | Bars | Gate items per item |
|---|---|---|
| Pickaxe / hatchet | 6 | Cindersteel 1 Core / Amberite 6 Fossil Shard / Drakonite 1 Dragon Scale; plus the Enchanted part (section 7) |
| Shovel | 4 | same gate item x1 (Fossil Shard 4) |
| Main weapon (wand, staff, sword, bow, axe, bo staff, dagger) | 8 (staff 10) | Core 1 / Fossil Shard 6 / Dragon Scale 1 |
| Helmet / chest / legs / boots | 5 / 8 / 7 / 4 (24 a set) | Core 1 each / Fossil Shard 10 each / Dragon Scale 1 each |
Kit sizes (python): weapon + 4 armor + pickaxe = **38 bars**, so the whole Zone-4 start-up is 38 Ember Ore plus 6 Cores (about 2-3 guardian days). Amberite kit: 38 bars + 52 Fossil Shards (about 520 ore at 10%, or fewer with dinosaurs). Drakonite kit: 38 bars + 38 Drake Scales (about 480 normal kills; fewer with elites) + 6 Dragon Scales (one dragon day). Coin value of the 24 armor bars at Bazaar buy (with the 20% bar premium): Cindersteel 348k, Amberite 950k, Drakonite 2.38M (Mithril 46k): the jump is deliberate (steep ladder, `docs/answered/economy.md`). Rolled gear still comes from SkyyGear rarity and level: crafting level = your class level clamped to the band (Roadmap section 2).

## 9. Server Setup rows (sketch; times in seconds)

`mat.cinder.enabled`, `mat.<ore>.hostRock`, `mat.<ore>.veinsPerChunk` (3.0 / 2.0 / 0.8), `mat.<ore>.veinMin/Max` (5-9 / 4-7 / 3-5), `mat.<ore>.yMin/yMax`, `mat.<ore>.hardnessMult` (1.25 / 1.5 / 2.0), `mat.<ore>.miningXp` (55 / 70 / 100), `mat.<ore>.smeltSec` (40 / 50 / 60), `mat.<ore>.regen` (off), `drop.emberCore.guardian` (2-3, daily 1), `drop.emberCore.elite` (0.4%), `drop.fossilShard.ore` (10%), `drop.fossilShard.mob` (6 / 40%), `drop.drakeScale.normal` (8%) and `.elite` (25%), `drop.dragonScale.first` (6) and `.daily` (2) and `.minibossChance` (2%), `bazaar.price.<id>` (11,000 / 30,000 / 75,000 / 600 / 9,000), `bazaar.maxChainPremium` (15), `ench.bazaarPremium` (10) and `ench.blockPremium` (5), `coll.<ore>.curve` (R / E / E), `armory.craft.collectionGate` (on).

## For the local session (UNVERIFIED)

1. **Vanilla ores already in the game files**: `Ore_Prisma` exists with no source (`research/Collections-Spec.md` line 194; Prisma gear is listed at Lv 45-49 in `research/Gear-Levels-Wynn-Spec.md`) and `Ore_Onyxium` has none: check whether Ember Ore can reuse the Prisma block or the Onyxium ore as the model / id, and which vanilla Zone 4 volcanic blocks (`Rock_Volcanic*`, `Rock_Magma_Cooled`, `Ore_Adamantite_Magma*`) can host our veins.
2. The vanilla Zone 4 biome and mob ids (Charred Woodlands, caldera, volcanic caves; Emberwulf, Rex_Cave, Raptor_Cave, Trillodon, Fire Golem, `Dragon_Fire`) and whether a vanilla cave layer for Zone 5 exists; my y bands are guesses.
3. Real ore Quality numbers and hardness for Mithril and the pickaxes, so the "Quality 6 / 7 / 8" column and the x1.25-x2 hardness are concrete; whether the engine can set per-ore hardness on a **new** block.
4. Whether new ore blocks are allowed (id, texture, vein prefab) or whether veins must reuse vanilla ore block ids, and the V2 world-gen hook for veins per chunk (`research/SkyyWorldGen-Plan.md`).
5. Whether a bench recipe may take 160 ore, and whether a 4-ingredient bar recipe (ore + Drake Scale) fits the furnace (`research/cloud/Enchanted-Materials-Draft.md` section 8).
6. The Bazaar per-product price ceiling (1e9 assumed) and whether it can be raised; re-run the LP loop check (2,252 recipes + new ones) with the Core / Shard / Scale inputs.
7. Mob coin drops at Lv 60-75 (for the Drake Scale value check) and the Mining XP table beyond Lv 50 in SkyySkills 0.4.16.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Onyxium has no source. Skip its slot (Cindersteel ore mined with a Mithril pickaxe) or add an Onyxium source first? | skip it (Cindersteel pick from Mithril collection III) |
| 2 | Do mined veins ever regrow (timed reset, or an admin command)? | no regrow in profile worlds; ore is finite per island |
| 3 | Ember Core: a hard crafting gate on every Cindersteel piece (6 per kit), tradable on the Auction House? | yes, yes |
| 4 | Dragon Scale also from the Zone 5 deep mini-boss (2%) so a Lv 66 player can start Drakonite before the Lv 75 dragon? | yes |
| 5 | No Enchanted Drakonite Block (price ceiling 1e9), or raise the ceiling? | no Block |
| 6 | Drakonite Mining XP 100 (1.75 levels per hour) or 120 for the same pace as Ember? | 100 |
| 7 | Ember Ore as the Prisma-style vanilla block (if the files confirm it) or all-new ore ids? | new ids; reuse only if the id clash check is clean |
| 8 | Collection Fortune perks for the three new ores (+3 each) or fold into the 10-per-skill cap? | fold into the cap |
