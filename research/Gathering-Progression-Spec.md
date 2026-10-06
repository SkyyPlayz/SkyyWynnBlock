# Gathering Progression - build spec (Mining, Foraging, Farming)

Written 2026-10-06 (spec author, Fable; SPEC round - nothing built, nothing deployed); revised the same day after three critic passes
(economy + loops, progression, engine + phasing - see "Review notes" at the end). Merges the cloud drafts
(`research/cloud/SkyBlock-Gathering-Progression.md`, `research/cloud/Gathering-Tiers-Draft.md`, `research/cloud/Collection-Unlocks-Draft.md`,
`research/cloud/Enchanted-Materials-Draft.md`, `research/cloud/Gathering-Numbers-Reconciled.md`, `research/cloud/Foraging-Armor-Design.md`, `research/cloud/Gathering-Armor-Mining-Farming.md`)
with the four verifier fact sheets of this round (mining, foraging, farming, engine-collections; Assets.zip + live build scripts, read only).
Where a draft and a fact sheet disagree, the fact sheet wins; the wrong draft lines are listed in section 9.

Live versions (corrected from the task text): SkyyCollections **0.2.7**, SkyySacks 0.7.12 (**0.7.13 built, unpinned**), SkyyBazaar 0.1.4
(**0.1.5 built, unpinned**), SkyySkills 0.4.16, SkyyAccessories 0.5.6, SkyyGear 0.2.3. Version numbers in section 6 shift if other rounds
of the same mod land first; each is derived from the pinned SET version (PROJECT-RULES section 4).

Legend: **VERIFIED** = seen in Assets.zip, bytecode or a live build script. **UNVERIFIED** = needs the game (probe round P0, section 6).
**PLACEHOLDER** = a number Skyy has not picked; every runtime placeholder is a Server Setup row.

---

## 0. Plain words (for Skyy)

- Each gathering skill gets a short ladder of **material tiers**, in the order the zones hand them out. Mining: Copper, Iron, Thorium,
  Cobalt, Adamantite (Mithril waits for real Zone 4 veins, Onyxium for Zone 5 / 0.7 - vanilla 0.6 places neither). Foraging: **5 tree
  tiers**, not 33 (Zone 1 has two: the common grove and the autumn / blue forest). Farming: the 7 Farmer's Workbench crop pairs, as locked.
- Collecting a tier's material fills its **collection**. Set levels hand out **recipes**: the compressed "Enchanted" form of the
  material, the **next tier's tool**, that tier's **gathering armor**, accessories, bags, plus coins and skill XP. Everything you have
  today stays where it is (Copper / Iron tools, the bag ladder, the Lanterns on Tree Sap).
- **Enchanted X = 160 X** if a quick in-game probe shows a 160-item recipe works, otherwise 100 (one Hytale stack). Fixed at build time.
  Enchanted items are what the next tool and the armor sets cost, count toward the collection as their base amount, sell on the Bazaar
  for exactly base x ratio (no bonus, so no free coins), and never un-compress.
- **Coins never skip any of it (R3).** The Bazaar sells materials, never recipes - and it will not sell you a seed whose recipe you have
  not unlocked (a seed needs no recipe to plant, so selling it would be a skip).
- Vanilla only hard-gates two ores (Adamantite needs a Thorium-or-better pickaxe, Mithril an Adamantite-or-better one). Every other
  "next tool" step is a **speed + Fortune** step, not an access gate. The real gates are the **recipe locks** (collection levels), the
  **tool levels** (your skill level) and the **zone** you can survive in.
- Build order: a small probe round first (P0), then Enchanted materials, then tool levels, then the real recipe locks, then Foraging
  armor, then Mining + Farming armor, then seeds / new farm tools, then extras (collection Fortune, accessories). Mithril, hard ore gates
  and Enchanted Blocks come later.

---

## 1. Decisions followed (not re-decided)

| Where | Decision (short) | What it fixes here |
|---|---|---|
| bags.md LOCKED 2026-10-05 (BIG DIRECTION) | SkyBlock ladder: tiers from vanilla's own tiers tied to zones; group trees; collection levels unlock recipes; Enchanted = compressed, counts as base amount | the whole shape of sections 2-4 |
| bags.md R3 LOCKED | coins never skip collections, recipes or bags | no coin route anywhere; Bazaar buy-lock on gated seeds (F21) |
| bags.md R3 LOCKED | bag unlock collections / tiers / scraps stay (Mining = Iron, Foraging = Oak, Farming = Wheat, Combat = Bone, Smithing = Light Hide; I / III / V / VII) | bag rows untouched; no Enchanted in bag recipes |
| bags.md LOCKED 2026-10-03 | every accessory tier / bag size is crafted FROM the previous one | applies to accessories; gathering armor tiers do NOT eat the previous piece |
| economy.md LOCKED 2026-10-04 | metal ore prices: old price x2 per tier step, the multiplier doubling (Copper x1, Iron x2, Thorium x4 ...) -> 5 / 16 / 48 / 144 / 480 / 1,440 / 3,712 | section 2 price columns; Enchanted prices in 4.4 |
| economy.md LOCKED 2026-10-04 + 05 | logs by today's price tier 3 / 8 / 20 / 48 / 128 (x2 per step from the old tiers); crops in vanilla Farming Bench order 2 / 6 / 16 / 40; seeds + saplings climb with their tier; Silver 14 / Gold 20 / Prisma 75 stay; Tree Sap 12 | prices kept as locked; log re-pricing is only offered (question 2) |
| economy.md LOCKED 2026-10-06 | Lantern recipes on Tree Sap at 50 (I), 250 (III), 1,000 (V), 10,000 (VIII) | TreeSap rows untouched |
| gear.md LOCKED 2026-10-02 / 03 / 05 | tool levels gate by skill (pickaxe + shovel Mining, hatchet Foraging, hoe + sickle Farming); level raises speed + Fortune; hoe / sickle lock ON; every new tool gets a level | the tool-level gate is the second gate of every tier |
| gear.md LOCKED 2026-10-05 | FORAGING ARMOR: tier 1 vanilla Wood armor, then Softwood -> Goldenwood (7), each echoing a metal; Fortune + chopping speed (+ XP), low Defense, Tree Feller higher up | section 3.4 armor table; wood ingredients corrected to the real categories |
| gear.md LOCKED 2026-10-06 | FARMING ARMOR = crop / food armor, 7 steps in bench order; MINING ARMOR starts at Copper (no T0), Iron+ echo vanilla; helmet lamps really emit light (Lantern code) | section 3 armor rows |
| skills.md LOCKED 2026-09-25 | Tree Feller 1 / 2 / 4 / 5 / 6 / 10, 3 s | reused, never a second system |
| research/cloud/Gathering-Numbers-Reconciled.md | Fortune in points (1 = +1% double drop), per-source caps (tool 25, armor 15, accessories 10, pets 10, collections 10), capstone ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 over SIX key collections per skill | section 3 capstones (exactly six per skill), F8 |
| Pocket-Shards-Spec + bags.md R7 | 12 Pocket Shard types at launch; collection tier I = the shard recipe | tier I rows say "Pocket Shard (when SkyyMinions ships)" |
| docs/log 2026-10-06 | Advanced Farming dropped from the pack: "build its tools into ours" | Cobalt+ hoes / sickles are OUR SkyyGear items (phase E) |

---

## 2. Tier tables

Zone level bands (SkyyMobs refit): Zone 1 = 1-20, Zone 2 = 20-30, Zone 3 = 30-45, Zone 4 = 45-60. Tool bands (SkyyGear
`level.material`, VERIFIED): Crude / Wood 1-13, Copper 10-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril /
Onyxium 40-49.

**What a "next tool" really does (say it plainly in game too):** only two steps open new ore - a Thorium-class pickaxe (Thorium, Cobalt,
Adamantite, Mithril all carry Quality 4 on `OreAdamantite`) opens Adamantite, and an Adamantite-or-better pickaxe opens Mithril. Every
other pickaxe step, every hatchet step (no log has a breaking Quality; Thorium-and-up hatchets all have 0.5 Woods power) and every hoe
step (tilling has no tier check) is a speed + Fortune + tool-level step. VERIFIED.

### 2.1 Mining

Every zone row is VERIFIED from `Server/World/Default/Zones/*/Zone.json` + `Ores/Zone*/*Placement.json`.

| Tier | Ore (collection) | Where it spawns | Vanilla pickaxe gate | Our gates (recipe / tool level) | Bazaar (locked) | Curve |
|---|---|---|---|---|---|---|
| M1 | **Copper** (`Ore_Copper`) | Zones 0-3 (not 4) | none (Crude mines it, slowly) | Copper pickaxe: Cobblestone I (live) | 5 | S |
| M2 | **Iron** (`Ore_Iron`) | Zones 0-4 (Zone 1 caves from the start) | none (speed only) | Iron pickaxe: Cobblestone VI (live) **or Copper IV (new second route)**; tool Lv 15+ | 16 | S |
| M3 | **Thorium** (`Ore_Thorium`) | Zone 2 only (sandstone, dry mud) | none | Thorium pickaxe: **Iron IV**; Lv 20+; Workbench tier 2 (vanilla) | 48 | R |
| M4 | **Cobalt** (`Ore_Cobalt`) | Zone 3 veins (+ Zone 4 volcanic boulder prefabs) | none | Cobalt pickaxe: **Thorium IV**; Lv 25+; Workbench tier 2 | 144 | R |
| M5 | **Adamantite** (`Ore_Adamantite`) | Zone 4 only (magma); Zone 4 encounter drops | **Quality 4** = Thorium / Cobalt pickaxe or better (hard) | Adamantite pickaxe: **Cobalt IV**; Lv 35+; Workbench tier 3 | 480 | E |
| M6 (staged) | **Mithril** (`Ore_Mithril`) | **no world placement in 0.6** - only salvaging Mithril gear | **Quality 5** = Adamantite pickaxe or better (hard) | Mithril pickaxe: **Adamantite III**; Lv 40+; Workbench tier 3. Enchanted Mithril, Mithril armor: **staged until Zone 4 veins ship** (Q6, phase G) | 1,440 | E |
| M7 (hidden) | **Onyxium** (`Ore_Onyxium`) | nowhere; its pickaxe, hatchet, armor and weapons have NO recipes | - | stays hidden; nothing to unlock | 3,712 | E |
| side | Silver (R), Gold (R) | Gold Zones 1-3, Silver Zones 1-4 | none | no tool; economy / accessory materials | 14 / 20 | R |
| side | Gemstones (E), Crystals (R) | gems from Zone 1 (Diamond, Emerald, Sapphire) and Zone 3 geodes, Zephyr in Zone 2; Ruby / Voidstone geodes exist but no node places them | - | accessory materials | 40, Diamond / Voidstone 120 | - |

- **Why the Copper IV second route:** Cobblestone counts only `Rock_Stone_Cobble` (+ Mossy), which spawns in Zones 1 and 4. A miner who
  left Zone 1 early (Zone 2 gives Sandstone cobble, Zone 3 Shale) is not sent back for 2,500 cobble. The live Cobblestone VI line stays.
- **Mithril ore on the Bazaar:** the live market-maker row (1,440) stays - it is a material, and every Mithril recipe is still behind
  a collection. No Enchanted Mithril PRODUCTS row exists until the veins ship.

Stone bulk groups (counts for the bag and Enchanted Cobblestone only; the stone collections stay as they are, no ladder role):

| Group | Collections (live ids) | Zone (VERIFIED counts) |
|---|---|---|
| S1 Stone | Cobblestone (B), Rubble (B) | Zone 1 (507) and Zone 4 (475) |
| S2 Desert | Sandstone (B), Sand (B), Clay (S) | Zone 2 |
| S3 Northern | Shale (B), Slate (B), Ice (S) | Zone 3 (Slate also Zone 4) |
| S4 Wastes | Basalt (B), Volcanic (B) | Zone 4 (Volcanic also Zone 1) |
| no worldgen | Limestone, Salt, Marble (layers), Quartzite | keep the collections |

**Mithril and Onyxium (question 6):** the ladder is 5 real tiers in 0.6. Salvaging Mithril gear returns ore, but salvage is not a counting
hook, so the Mithril COLLECTION cannot fill - every Mithril collection row waits for real veins. Default: SkyyWorldGen adds deep Mithril
veins (`Ore_Mithril_Stone`) to Zone 4 (the orphan `Portals_Mithril` generator shows vanilla intended it); Onyxium waits for Zone 5 / 0.7.

### 2.2 Foraging (5 tree tiers, zone-ordered)

The tree tier is a ZONE + collection + tool-level ladder, never a hatchet gate (VERIFIED, see the box above). Where each log grows is
VERIFIED from the zone tile files.

| Tier | Name | Zone | Logs (key log in bold) | Vanilla bench category of each | Bazaar (locked) | Hatchet step |
|---|---|---|---|---|---|---|
| F1 | Grove | Zone 1 Tiers 1-2 | **Oak** (B), Birch, Beech, Ash, Aspen | Hardwood (Oak, Ash), Lightwood (Birch), Softwood (Beech, Aspen) | 3 | Copper (Oak I, live), Iron (Oak VI, live) |
| F2 | Autumn and Azure | Zone 1 Tier 3 | **Maple**, Azure (R) | Redwood (Maple), none (Azure) | 8 / 48 | Thorium: Maple IV |
| F3 | Savanna | Zone 2 | **Gumboab**, Dry, Bottletree, Palo | Lightwood (Gumboab), Drywood (Dry, Bottletree), Greenwood (Palo) | 8 / 3 / 8 / 8 | Cobalt: Gumboab IV |
| F4 | Northern | Zone 3 | **Redwood**, Fir, Cedar, Poisoned (R), Spiral (R, caves) | Redwood, Hardwood (Fir), Darkwood (Cedar), none | 20 / 3 / 3 / 8 / 8 | Adamantite: Redwood IV |
| F5 | Wastes | Zone 4 Tiers 4-5 | **Sallow**, Burnt, Petrified (R), Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire (R), Crystalwood (R) | Goldenwood (Sallow), Blackwood (Burnt, Fire), Deadwood (Petrified), Tropicalwood (Bamboo), Lightwood (Camphor), Softwood (Banyan), Greenwood (Jungle), Redwood (Blue Fig), none (Crystal) | 2-128 | Mithril: Sallow IV |
| side | Orchard (farmed only) | saplings at the Farmer's Workbench | Apple, Amber, Frostwood, Stormbark, Windwillow, Wild Wisteria (no natural trees); Palm (no log drops at all) | Hardwood (Apple), Goldenwood (Amber, Wisteria, Palm), none | 8-128 | no step |
| support | Plant Fiber (B), Stick (B), Tree Sap (S) | everywhere | - | - | 1 / 1 / 12 | Sap = Lanterns (live I / III / V / VIII) |

- Zone 1 has **two** tree tiers (F1 + F2) - the lock ("not ~6 tiers in Zone 1").
- The key log carries the tier's unlocks (hatchet, Enchanted, armor). The other logs keep the default coins / XP curve.
- **Key-log scarcity check (UNVERIFIED):** Sallow grows only in Zone 4 Tier 4, Redwood only in Zone 3 Tiers 1-2 + shore cliffs. Phase P0
  counts trees per species in the real island (together with the zone-to-ring remap check). If a key log is scarce there, the key moves
  to the most common log of the same tier (Fir for F4, Burnt or Bamboo for F5) before phase A builds - the rows of 3.4 move with it.
- Bazaar prices stay as LOCKED 2026-10-04 (they do not follow the zones: Dry 3 in Zone 2, Bamboo 2 in Zone 4). Re-pricing is only an
  option for Skyy (question 2, default: keep).

### 2.3 Farming (the 7 Farmer's Workbench pairs - LOCKED)

Bench tiers run 1-8 (base bench = tier 1, 7 upgrades). Each upgrade eats one crop pair + one wood category + Essence. VERIFIED.
Crops are planted, so the zone never gates them; the gate is the seed recipe (bench tier, Memories for eternal seeds) + our collection
locks + the Bazaar seed buy-lock. Hoes till any soil with no tier check; there is one tilled soil. VERIFIED.

| Tier | Crop pair (key crop in bold) | Seed bench tier | Eternal seed (bench / Memories) | Wood the bench upgrade eats | Bazaar (locked) | Farm tool step | Armor (crop armor) |
|---|---|---|---|---|---|---|---|
| P1 | **Wheat**, Lettuce | 1 | 2 / 2 | Softwood x5 | 2 | Crude sickle (Wheat I), Copper hoe (III), Copper sickle (IV), Iron sickle (VI), Iron hoe (VII) - all live | Wheat set |
| P2 | **Carrot**, Corn | 2 | 3 / 3 | Lightwood x10 | 2 | Thorium hoe: Carrot IV (vanilla item; our override lowers its bench tier 6 -> 3, PLACEHOLDER) | Carrot set |
| P3 | **Cauliflower**, Turnip | 3 | 4 / 3 | Hardwood x20 | 6 | Thorium sickle (NEW): Cauliflower IV | Cauliflower set |
| P4 | **Pumpkin**, Aubergine | 4 | 5 / 4 | Drywood x30 | 6 | Cobalt hoe + sickle (NEW): Pumpkin IV | Pumpkin set |
| P5 | **Tomato**, Chilli | 5 | 6 / 4 | Darkwood x40 | 16 | Adamantite hoe + sickle (NEW): Tomato IV | Tomato set |
| P6 | **Cotton**, Rice | 6 | 7 / 5 | Redwood x50 | 16 | Mithril hoe + sickle (NEW): Cotton IV | Cotton set |
| P7 | **Potato**, Onion | 7 | 8 / 6 | Goldenwood x60 | 40 | - | Potato set |

- Vanilla stops at the Thorium hoe and the Iron sickle (VERIFIED). Everything above is a NEW SkyyGear tool (phase E). NEW farm tools set
  their own Farmingbench tier to the pair's seed tier (Thorium sickle 3, Cobalt 4, Adamantite 5, Mithril 6; PLACEHOLDER).
- **Why the Thorium hoe bench tier changes:** vanilla puts it at Farmingbench tier 6, which needs the Tomato / Chilli pair already
  consumed (P5); unlocked at Carrot IV (P2) it would sit unusable for most of the ladder, or be bypassed through `/craft`. The override
  that adds the lock (F20) sets tier 3 instead.
- Eternal seeds are world-gated by Memories (10 / 25 / 50 / 100 / 200 recorded memories for levels 2-6). World-wide, so never a
  per-player collection gate; `/craft` gets the same check in SkyySacks 0.7.13.
- Normal crops are single-harvest (block removed); only eternal crops regrow. VERIFIED. "Green Thumb" auto-replant is a real feature.

---

## 3. Collections: levels, thresholds, unlocks

### 3.1 Curves (live, VERIFIED `CURVES`)

| Curve | Tiers | Thresholds (total items) |
|---|---|---|
| B Bulk | 10 | 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 / 10,000 / 25,000 / 50,000 |
| S Standard | 9 | 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 / 10,000 / 20,000 |
| R Rare | 8 | 25 / 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 |
| E Elite | 7 | 10 / 25 / 50 / 100 / 250 / 500 / 1,000 |

Default rewards on every tier stay: coins 50 ... 25,000; skill XP 500 (III), 2,500 (V), 10,000 (VII), 25,000 on the last tier.

### 3.2 The unlock grammar (same shape for every KEY collection)

| Tier | S (9) | R (8) | E (7) | B Cobblestone (10) |
|---|---|---|---|---|
| I | Pocket Shard recipe (later) + bag Normal on bag keys (live) | Pocket Shard | Pocket Shard | Copper pickaxe (live) |
| II | XP (default) | XP | **Enchanted recipe** | XP |
| III | **Enchanted recipe** (+ bag Unique on bag keys, live) | **Enchanted recipe** | **next tier's tool** | Enchanted Cobblestone |
| IV | **next tier's tool** | **next tier's tool** | **gathering armor** of this tier | Stone Brick (live) |
| V | **gathering armor** of this tier (+ bag Rare, live) | gathering armor | accessory recipe | Compactor (Pocket Shard upgrade, later) |
| VI | accessory recipe (Prospector / Woodsman / Harvester, Rare) | accessory | XP | Iron pickaxe (live) |
| VII | bag Legendary (live) / accessory Legendary | XP | **capstone** | Prospector Rare |
| VIII | XP | **capstone** | - | Prospector Legendary |
| IX | **capstone** | - | - | XP |
| X | - | - | - | **capstone** |

- **Anti-skip rule:** tier N+1's tool recipe appears at tier-N key collection IV (S / R) or III (E), and that recipe COSTS Enchanted N
  (section 4). You cannot buy the recipe (R3); you reach the material through zone access + the tool level.
- **Armor cost rule:** a gathering armor set costs about its unlock threshold in base material, never more than 1.5x (Enchanted per set =
  threshold / 160, rounded; at least 1). That keeps the collection level the real gate in every skill (critic finding: 24 Enchanted =
  3,840 items against a 1,000-item unlock was far out of line, worst for 1-per-harvest crops and Elite ores).
- **Capstone** = collection Fortune (1 / 1 / 1.5 / 2 / 2 / 2.5 points, in ladder order, over EXACTLY six key collections per skill = 10,
  `coll.fortune.cap` 10). Needs a new reward token (F8). Until it exists the capstone tier pays the 25,000 XP only.
  - Mining six: Cobblestone, Copper, Iron, Thorium, Cobalt, Adamantite (Mithril gets none).
  - Foraging six: Oak, Maple, Gumboab, Redwood, Sallow, Azure (Petrified gets none).
  - Farming six: Wheat, Carrot, Cauliflower, Pumpkin, Tomato, Cotton (Potato gets none).
- Nothing live moves. Rows marked (live) are today's `rewards.properties` lines and stay byte-for-byte; new tokens are appended on the
  same key (`RW_ENTRIES` joins several tokens on one line, VERIFIED).
- **Each phase ships only the rows whose item exists in that phase** (column "phase" in 3.3-3.5); the build asserts every recipe id
  resolves at start.

### 3.3 Mining rows (new tokens in bold; `REC(x)` = `recipe:x_Recipe_Generated_0`)

| Collection (curve) | I | II | III | IV | V | VI | VII | VIII | IX / X |
|---|---|---|---|---|---|---|---|---|---|
| Cobblestone (B) | Copper pickaxe (live) | - | **Enchanted Cobblestone** (A) | Stone Brick (live) | (Compactor, later) | Iron pickaxe (live) | **Prospector Rare** (F) | **Prospector Legendary** (F) | X capstone (F) |
| Copper (S) | (shard) | - | **Enchanted Copper** (A) | **Iron pickaxe, second route** (A) | **Copper Miner armor** T1 (D) | - | - | - | IX capstone |
| Iron (S) | bag Normal (live) | - | **Enchanted Iron** (A) + bag Unique (live) | **Thorium pickaxe** (B2) | **Iron Miner armor** T2 (D) + bag Rare (live) | - | bag Legendary (live) | - | IX capstone |
| Thorium (R) | (shard) | - | **Enchanted Thorium** (A) | **Cobalt pickaxe** (B2) | **Thorium Miner armor** T3 (D) | - | - | VIII capstone | |
| Cobalt (R) | (shard) | - | **Enchanted Cobalt** (A) | **Adamantite pickaxe** (B2) | **Cobalt Miner armor** T4 (D) | - | - | VIII capstone | |
| Adamantite (E) | (shard) | **Enchanted Adamantite** (A) | **Mithril pickaxe** (B2) | **Adamantite Miner armor** T5 (D) | - | - | VII capstone | | |
| Mithril (E) - staged | (shard) | **Enchanted Mithril** (G) | - (Onyxium pickaxe has no recipe) | **Mithril Miner armor** T6 (G) | - | - | - (no capstone) | | |

Shovels: only `Tool_Shovel_Iron` has a vanilla recipe (VERIFIED), so no shovel token anywhere; shovels follow the pickaxe's tool level.
Thresholds behind each gate: Thorium pickaxe at 500 Iron ore; Cobalt pickaxe at 250 Thorium; Adamantite pickaxe at 250 Cobalt; Mithril
pickaxe at 50 Adamantite. Armor unlock -> set cost (armor cost rule): Copper / Iron at 1,000 -> 6 Enchanted; Thorium / Cobalt at 500 ->
3 Enchanted; Adamantite at 100 -> 1 Enchanted (+ the bars below).

### 3.4 Foraging rows

| Collection (curve) | I | II | III | IV | V | VI | VII | VIII | IX / X |
|---|---|---|---|---|---|---|---|---|---|
| OakLog (B) | Copper hatchet + bag Normal (live) | - | **Enchanted Oak** (A) + bag Unique (live) | **Softwood armor** T1 (C) | bag Rare (live) | Iron hatchet (live) + **Lightwood armor** T2 (C) | bag Legendary (live) | **Woodsman Rare** (F) | X capstone |
| MapleLog (S) | (shard) | - | **Enchanted Maple** (A) | **Thorium hatchet** (B2) | **Hardwood armor** T3 (C) | **Woodsman Legendary** (F) | - | - | IX capstone |
| GumboabLog (S) | (shard) | - | **Enchanted Gumboab** (A) | **Cobalt hatchet** (B2) | **Drywood armor** T4 (C) | - | - | - | IX capstone |
| RedwoodLog (S) | (shard) | - | **Enchanted Redwood** (A) | **Adamantite hatchet** (B2) | **Darkwood armor** T5 (C) | - | - | - | IX capstone |
| SallowLog (S) | (shard) | - | **Enchanted Sallow** (A) | **Mithril hatchet** (B2) | **Redwood armor** T6 (C) | **Goldenwood armor** T7 (C) | - | - | IX capstone |
| AzureLog (R) | (shard) | - | Enchanted (later) | - | - | - | - | VIII capstone | |
| PetrifiedLog (R) | (shard) | - | Enchanted (later) | - | - | - | - | - | |
| TreeSap (S) | Lantern Normal (live) | - | Lantern Unique (live) | - | Lantern Rare (live) | - | - | Lantern Legendary (live) | - |
| Fiber (B), Stick (B) | - | - | Shears / Crude Arrow (live) | - | - | - | - | - | - |

Foraging armor: the NAME follows the bench ladder (LOCKED), the INGREDIENT follows the zone ladder. Category resource types are used only
where no LOWER-zone log carries them (an upward leak - e.g. Zone 4 Banyan counting as Softwood - is harmless); where a lower-zone log
would leak in, the per-species type `Wood_<Species>` is used. Exact species ids are read from each trunk's `ResourceTypes` by the build
(assert), not typed by hand.

| Armor tier | Name (echoes) | Band / skill gate | Collection unlock | Ingredients per set (split Head / Chest / Legs / Hands) |
|---|---|---|---|---|
| 0 | Wood (vanilla) | 1-13 | none | vanilla: `Wood_Trunk` 23 + Fibre 13 (VERIFIED), vanilla stats 46 HP / 25% set |
| 1 | Softwood (Copper) | 10-18 / Foraging 10 | OakLog IV (500) | 200 `Wood_Softwood_Trunk` (Aspen / Beech, Zone 1) + 31 Fibre - no Enchanted (first tier) |
| 2 | Lightwood (Iron) | 15-23 / 15 | OakLog VI (2,500) | 6 Enchanted Oak + 100 `Wood_Lightwood_Trunk` (Birch, Zone 1) |
| 3 | Hardwood (Thorium) | 20-28 / 20 | MapleLog V (1,000) | 6 Enchanted Maple + 100 `Wood_Hardwood_Trunk` (Oak / Ash) |
| 4 | Drywood (Cobalt) | 25-38 / 25 | GumboabLog V (1,000) | 6 Enchanted Gumboab + 100 `Wood_Drywood_Trunk` (Dry / Bottletree, Zone 2) |
| 5 | Darkwood (Adamantite) | 35-43 / 35 | RedwoodLog V (1,000) | 6 Enchanted Redwood + 100 `Wood_Darkwood_Trunk` (Cedar, Zone 3) + 20 Tree Sap |
| 6 | Redwood (Mithril) | 40-49 / 40 | SallowLog V (1,000) | 6 Enchanted Sallow + 100 **Blue Fig** (`Wood_<Blue Fig species>`, Zone 4 Tier 5) + 20 Tree Sap |
| 7 | Goldenwood (Onyxium) | **45-49 / 45 (PLACEHOLDER** - no Onyxium band exists; the armor-types lock says families cover 1-49) | SallowLog VI (2,500) | 15 Enchanted Sallow + 100 `Wood_Sallow` (species; Amber / Wisteria are orchard-only) + 20 Tree Sap |

- T6 moved to Zone 4 (Blue Fig is a real Redwood-category log): the earlier `Wood_Redwood_Trunk` ingredient is the CATEGORY type, which
  Zone 1 Maple also carries - it would have let Maple pay for the Mithril-tier set.
- The first two armor tiers sit in Zone 1 in every skill (Copper / Iron in Mining, Wheat / Carrot need no zone); that matches the two
  Zone 1 tree tiers and is intended.
- Stats, Feller levels, set bonus, look: as `research/cloud/Foraging-Armor-Design.md` after the reconciliation (Fortune 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 /
  10 / 12, speed +1 ... +12%, Feller 1-6 from Lightwood, 4-piece x1.15), Health / resist from the Gear level curve at 50% of Heavy
  (Armor-Types draft Q12). Tier 0 keeps vanilla's own numbers (46 HP / 25%); the drafts' other two figures (10 HP / 7%, 12 HP / 9%) go.

### 3.5 Farming rows

| Collection (S) | I | II | III | IV | V | VI | VII | VIII | IX |
|---|---|---|---|---|---|---|---|---|---|
| Wheat | Crude sickle + bag Normal (live) | - | Copper hoe + bag Unique (live) + **Enchanted Wheat** (A) + **Carrot / Corn seed recipes** (E) | Copper sickle (live) | **Wheat armor** T1 (D) + bag Rare (live) | Iron sickle (live) | Iron hoe + bag Legendary (live) | **Harvester Rare** (F) | capstone |
| Carrot | (shard) | - | **Enchanted Carrot** (A) + **Cauliflower / Turnip seeds** (E) | **Thorium hoe** (B2) | **Carrot armor** T2 (D) | **Harvester Legendary** (F) | - | - | capstone |
| Cauliflower | (shard) | - | **Enchanted Cauliflower** (A) + **Pumpkin / Aubergine seeds** (E) | **Thorium sickle** (E) | **Cauliflower armor** T3 (D) | - | - | - | capstone |
| Pumpkin | (shard) | - | **Enchanted Pumpkin** (A) + **Tomato / Chilli seeds** (E) | **Cobalt hoe + sickle** (E) | **Pumpkin armor** T4 (D) | - | - | - | capstone |
| Tomato | (shard) | - | **Enchanted Tomato** (A) + **Cotton / Rice seeds** (E) | **Adamantite hoe + sickle** (E) | **Tomato armor** T5 (D) | - | - | - | capstone |
| Cotton | (shard) | - | **Enchanted Cotton** (A) + **Potato / Onion seeds** (E) | **Mithril hoe + sickle** (E) | **Cotton armor** T6 (D) | - | - | - | capstone |
| Potato | (shard) | - | **Enchanted Potato** (A) | - | **Potato armor** T7 (D) | - | - | - | (no capstone) |
| Seeds (B), LifeEssence (B) | - | - | - | - | - | - | - | - | default curve only |

- **Seed locks (question 8):** the vanilla `Plant_Seeds_<Crop>` and `_Eternal` recipes get `KnowledgeRequired` and unlock from the
  PREVIOUS pair's key collection at III (250 crops). Wheat / Lettuce seeds stay open. Because a seed needs no recipe to plant, the Bazaar
  **refuses to sell** (instant buy and buy orders) a seed whose recipe the player has not unlocked; selling stays open (F21). Seeds that
  drop from unripe crops, Kweebec camps and encounters still drop - that is gathering, not coins.
- **Farming armor sets** (made from + looking like the crop, LOCKED): 6 Enchanted of the key crop (1 / 2 / 2 / 1; = 960 crops against
  the 1,000-crop unlock) + 40 of the pair's other crop + cloth (Linen T1-T3, Cotton bolt T4-T6, Silk T7) - PLACEHOLDER. Stats per
  `research/cloud/Gathering-Armor-Mining-Farming.md` section 2.2 (reconciled); Green Thumb at T5+ is a real auto-replant.
- **Mining armor sets** (start at Copper, LOCKED): Enchanted per the armor cost rule (Copper / Iron 6 = 1 / 2 / 2 / 1; Thorium / Cobalt 3
  = 1 / 1 / 1 / 0; Adamantite 1 = chest) + the vanilla set's bar count halved + 8 leather (PLACEHOLDER); helmet lamp = real light through
  the Lantern helper-light code (LOCKED).

### 3.6 XP alignment (SkyySkills, phase A)

- Mining XP per ore is inverted against the ladder (Cobalt 15 < Thorium 18, Mithril 25 < Adamantite 30). Set Copper 5, Iron 8, Thorium
  15, Cobalt 20, Adamantite 30, Mithril 40, Onyxium 50 (Silver 10, Gold 12, Prisma 50 stay). PLACEHOLDER.
- Foraging XP per log is a third tiering (price-based). Set by tree tier: F1 6, F2 10, F3 12, F4 15, F5 20; rare specials +5; Bamboo 3.
- Farming XP per crop does not follow bench order (Potato 4). Set by pair: 4 / 5 / 6 / 7 / 8 / 9 / 10.

---

## 4. Enchanted materials

### 4.1 Ids, set, ratios

| Rule | Value | Note |
|---|---|---|
| Ratio | **160 base = 1 Enchanted**, a **build-time constant** in the shared table (not a Server Setup row) | chosen by probe P1 before phase A builds; **100** if P1 fails. A runtime ratio could not change the baked recipe and would mis-credit / mis-price items players already hold |
| Enchanted Block | **not at launch** | 25,600 base per block; nothing needs it yet (question 4) |
| Stack size | 100 (engine default; Skyy: "use Hytale stack numbers") | one slot = 16,000 base |
| Id pattern | `Skyy_Ench_<Key>` | launch: `Skyy_Ench_Cobblestone`, `_Copper`, `_Iron`, `_Thorium`, `_Cobalt`, `_Adamantite`, `_Oak`, `_Maple`, `_Gumboab`, `_Redwood`, `_Sallow`, `_Wheat`, `_Carrot`, `_Cauliflower`, `_Pumpkin`, `_Tomato`, `_Cotton`, `_Potato` |
| Launch set | **18 items**: 6 mining (Cobblestone + 5 ores), 5 key logs, 7 key crops | `Skyy_Ench_Mithril` ships with the veins (phase G); other logs / crops / stones later, same generator |
| One source of truth | `tools/skyyench.py`: key -> base id, bag (Mining / Foraging / Farming), Bazaar base price, display name, ratio | SkyyCollections, SkyySacks and SkyyBazaar builds all import it; `crosscheck` asserts the three jars agree |
| Base item per Enchanted | Cobblestone = `Rock_Stone_Cobble` (Mossy counts toward the collection, the recipe takes plain cobble); ores = `Ore_<Metal>`; logs = `Wood_<X>_Trunk`; crops = `Plant_Crop_<X>_Item` | ingots never (the collection counts ore) |
| Recipe | `<ratio> <base> -> 1 Skyy_Ench_<Key>`, Workbench, new tab "Compressing", `KnowledgeRequired: true`, learned through the KnowSync (F5) from phase A | tab appended through the shared `tools/skyywbtab.py` helper (idempotent, F22) |
| Reverse recipe | **none, ever** | no un-compress, no salvage output of Enchanted items |
| Name / look | "Enchanted Iron Ore" etc.; launch icon = the **base item's own icon** + a custom Quality "Enchanted" (slot frame, tooltip colour, `Drop_Epic` particles) | the SkyySacks / Accessories Quality pattern, VERIFIED. A `recolor_icon` purple shift is a later polish step once P5 shows a recoloured icon draws |

### 4.2 Collection credit (exact)

| Case | Credit | How |
|---|---|---|
| Craft Enchanted from base | nothing new | crafting is not a hook (VERIFIED) - the base already counted when gathered |
| A giver CREATES an Enchanted item (Pocket Shard, reward) | + base x ratio to the base collection, **once, at creation** | the giver calls the new alias entry with the Enchanted id; SkyyCollections loops `coll:fn:add(uuid, <base id>, <=256, source)` in chunks of at most 256 (`cap.perCredit`), one Enchanted item per call, and logs any clip by `cap.perMinute` (20,000 = 125 Enchanted a minute per player) |
| The same item changes hands later (Bazaar, AH, trade, bag, chest, drop) | nothing | the credit belongs to the creation, never to the item; holding or selling an Enchanted item never credits anyone |
| New code | `ench` alias table in SkyyCollections (from `tools/skyyench.py`) | the default registry keeps vanilla ids only (`must(i)`, VERIFIED) |
| Build assert | every source in `bridge.add.sources` is listed with what it may credit; no whitelisted source mints Enchanted items without going through the alias entry | at launch no giver exists (Pocket Shards come with SkyyMinions) |

### 4.3 Where Enchanted items are spent (the funnel)

| Recipe | Enchanted cost (PLACEHOLDER rows) | Phase |
|---|---|---|
| Thorium pickaxe / hatchet / hoe | vanilla recipe + 1 Enchanted Iron / Maple / Carrot | B2 |
| Cobalt pickaxe / hatchet | vanilla + 2 Enchanted Thorium / Gumboab | B2 |
| Adamantite pickaxe / hatchet | vanilla + 2 Enchanted Cobalt / Redwood | B2 |
| Mithril pickaxe / hatchet | vanilla + 3 Enchanted Adamantite / Sallow | B2 |
| NEW farm tools (Thorium sickle, Cobalt+ hoes / sickles) | bars + leather + the Enchanted crop of the collection that unlocks it | E |
| Gathering armor set | armor cost rule (3.2): 6 / 3 / 1 Enchanted by curve, Foraging per the 3.4 table | C / D |
| Prospector / Woodsman / Harvester accessories | Rare: 4 Enchanted of the key material; Legendary: the Rare one + 8 (the "previous tier" rule, LOCKED) | F |
| Magic Bags | **none** (bag recipes stay as locked) | - |
| Pocket Shard tiers VI+ | Enchanted (Pocket-Shards-Spec, later) | G |

Note on hatchets: each hatchet costs the Enchanted log of the collection that unlocks it (Thorium hatchet <- Enchanted Maple, Cobalt
<- Gumboab, Adamantite <- Redwood, Mithril <- Sallow); pickaxes and hoes likewise (Thorium pickaxe <- Enchanted Iron, Thorium hoe <-
Enchanted Carrot ...). The tool overrides are written by ONE mod (SkyyGear, F20).

### 4.4 Bazaar price and the money loop

Price = **base x ratio**, no premium (`ench.premium` default **0**, row 0-22 kept for Skyy). Instant buy = x1.10, instant sell = x0.90
(live quote rule), the same band as the base item, so:

- buy base -> compress -> sell Enchanted returns 0.90 / 1.10 = 0.82: a loss;
- compressing then selling pays exactly what selling the base pays - no free coins on gathering income (the 10% premium of the first
  draft was a free +10% on all gathering income once Bazaar sell-from-bags exists);
- order-book flips (Bazaar 0.2 planned): bids must stay below the market-maker buy and asks above its sell, so with no premium a maker
  earns no more on Enchanted than on the base item. The LP harness adds an order-path case.

| Enchanted | base | price (ratio 160) | price (ratio 100) |
|---|---|---|---|
| Cobblestone | 1 | 160 | 100 |
| Copper | 5 | 800 | 500 |
| Iron | 16 | 2,560 | 1,600 |
| Thorium | 48 | 7,680 | 4,800 |
| Cobalt | 144 | 23,040 | 14,400 |
| Adamantite | 480 | 76,800 | 48,000 |
| Mithril (phase G only) | 1,440 | 230,400 | 144,000 |
| Oak / Maple / Gumboab / Redwood / Sallow | 3 / 8 / 8 / 20 / 8 (live, locked) | 480 / 1,280 / 1,280 / 3,200 / 1,280 | 300 / 800 / 800 / 2,000 / 800 |
| Wheat / Carrot / Cauliflower / Pumpkin / Tomato / Cotton / Potato | 2 / 2 / 6 / 6 / 16 / 16 / 40 | 320 / 320 / 960 / 960 / 2,560 / 2,560 / 6,400 | 200 / 200 / 600 / 600 / 1,600 / 1,600 / 4,000 |

Price rule, testable in the Bazaar build: an Enchanted product's base price must equal `base price x ratio` exactly (assert). The tiered
families keep the LOCKED rule as worded: "x2 per tier step, the multiplier doubles" from the OLD prices (so ores step about x3 between
neighbours today); crops and logs as in the 2026-10-04 / 05 locks.

Other loop checks: salvage of an overridden vanilla tool still returns the vanilla outputs (2 ore), so the Enchanted input is lost on
salvage (VERIFIED E.5) - no loop. No `Tool_*` or `Armor_*` id is a Bazaar product today (VERIFIED, 0.1.4 PRODUCTS); the Bazaar build adds
an assert that it stays so. The LP loop check re-runs over the 18 new recipes.

---

## 5. Engine approach per feature (evidence)

| # | Feature | Approach | Status |
|---|---|---|---|
| F1 | Counting | unchanged: H1 break, H2 / H3 harvest, H4 place (never counts), H5 kill; crafting / salvage never count | VERIFIED |
| F2 | Reward tokens | `recipe:`, `coins:`, `xp:<Skill>:<n>` only today; several tokens per key OK | VERIFIED |
| F3 | Recipe id for a vanilla or Skyy item | `<ItemId>_Recipe_Generated_0`; vanilla tool ids resolve (28 unlocks, no unknown-id line 2026-09-25) | VERIFIED |
| F4 | Per-player recipe LOCK | item json override with `KnowledgeRequired: true` (SkyyArmory staff precedent, in game 2026-10-03) + the KnowSync. Server refuses the craft (`CraftingManager.isValidBenchForRecipe`). Only `Type: Crafting` benches (Workbench, Farmingbench, Armor_Bench); Furnace / Tannery / Salvage cannot be gated | VERIFIED (lock) / **UNVERIFIED**: client hide vs grey + refresh of an open bench -> probe P2 |
| F5 | One generalised KnowSync | SkyyCollections publishes `coll:locked` (the recipe ids it manages) and one sync learns / forgets them per player from `coll:recipes`. Phase A: Enchanted recipe ids only; B2 adds tools; E adds seeds; C / D add armor. Re-runs on login, tier change and **profile switch** (known recipes are per player, collections per profile, so the sync re-derives from the active profile). SkyySacks (bags) and SkyyAccessories (Lanterns) keep their own lists - no id in two lists (build assert) | design; the two live syncs are VERIFIED |
| F6 | Enchanted items as assets | SkyyCollections becomes an asset-pack jar (`IncludesAssetPack: true`, the SkyySacks / Accessories / Cooking precedent); item json + custom Quality + lang; icon = base icon at launch | VERIFIED pattern |
| F7 | 160-input recipe | codec allows any `Quantity > 0`; vanilla max is 100; multi-slot removal exists | **UNVERIFIED** -> probe P1 decides the ratio before phase A |
| F8 | Collection Fortune capstone | new token `perk:dd:<skill>:<points>`; published as `skill:bonus` source `coll` into the live `dd.<skill>` sum (clamped 0-1); UI line on the collection page | design; `skill:bonus` accepts `dd.<skill>` fractions (VERIFIED) |
| F9 | Hard pickaxe gates on Iron / Thorium / Cobalt (Q5, optional, phase G) | override the ore block jsons (every host variant + cracked shells) with a Quality | **UNVERIFIED**: needs a bytecode read of `getSpecPowerDamageBlock` (desk task, P0) and in-game probe P6, plus what a refused break drops and whether H1 still counts it. Not in phase B |
| F10 | Tool level gate | SkyyGear tool-levels round (`GearDefs.enforcedKind`) | VERIFIED design (Tool-Levels-Spec) |
| F11 | "Any log of the tier" recipes | only along real resource types (`Wood_<Cat>_Trunk`, `Wood_<Species>`, `Wood_Trunk`); none exist for zone tiers -> Enchanted recipes take ONE named log, armor uses a category type only where no lower-zone log leaks in (3.4) | VERIFIED |
| F12 | Bag crafting of an Enchanted recipe | SkyySacks bench mirror = 36 slots, max 4 stacks per item: logs / crops 400 OK; **ore 4 x 25 = 100** -> at ratio 160 Enchanted ORE crafts from the inventory only at launch (no mirror change). Raising the mirror cap is phase G with a conservation harness | VERIFIED limit; ResourceType inputs from the mirror -> probe P4 |
| F13 | Enchanted in bags | `SackDefs.homeOf` gets an explicit `Skyy_Ench_<Key>` -> bag TABLE from `tools/skyyench.py` (a prefix cannot tell Iron from Oak from Wheat) | VERIFIED entry point |
| F14 | Bazaar rows | PRODUCTS rows for the 18 items from the shared table (build fails without), `ench.premium` 0, price = base x ratio assert, LP loop check incl. order path, no-`Tool_*` / `Armor_*` assert | VERIFIED build rules |
| F15 | Seed recipe locks (Q8) | same as F4 on `Plant_Seeds_<Crop>` + `_Eternal` (Farmingbench is Crafting) | VERIFIED bench type |
| F16 | New farm tools (Thorium sickle, Cobalt+ hoe / sickle) | new SkyyGear items parented on the vanilla tool templates, `Hoe_Till` and sickle interactions reused, levels from the band table | design; interactions VERIFIED to carry no tier check |
| F17 | Collections tab bypass of bench tier | `/craft` crafts an unlocked recipe with no bench; SkyySacks 0.7.13 adds the bench-tier + Memories re-check | VERIFIED today / fix built - **pinned and deployed in P0, before anything else** |
| F18 | Mithril worldgen (Q6) | SkyyWorldGen placement of `Ore_Mithril_Stone` in Zone 4 deep rock | design; block + migration mapping exist (VERIFIED) |
| F19 | Pocket Shards at tier I | later (SkyyMinions); `bridge.add.sources` + "minion", credit through the alias entry (4.2) | VERIFIED hook |
| F20 | Single owner of vanilla tool overrides | SkyyGear writes every overridden vanilla tool json (tool level + `KnowledgeRequired` + Enchanted inputs + bench-tier change); SkyyCollections only publishes `coll:locked`. The build stores a hash of each vanilla json it copied; `crosscheck` warns when Assets.zip changes under it | design; two-mod override = one winner (UNVERIFIED -> probe P3) |
| F21 | Bazaar seed buy-lock | SkyyBazaar reads `coll:recipes:<uuid>`; BUY (instant + buy orders) of a seed product whose recipe id is locked for that player is refused with a short "unlock in Collections" line; SELL open | design |
| F22 | Workbench tab appends | "Compressing" and "Accessories & Bags" both go through `tools/skyywbtab.py`, which skips a category already present; build assert on the final category list | VERIFIED technique |

---

## 6. Mods, build order, phases (each phase = one round with its own harness)

| Phase | Mods (version) | Scope | Harness (pass before pin) |
|---|---|---|---|
| **P0. Pins + probes** (lean round) | pin + deploy SkyySacks 0.7.13 and SkyyBazaar 0.1.5 (already built); a throwaway probe pack in scratch, pinned for one test session and removed after; desk read of `getSpecPowerDamageBlock` | answers the unknowns BEFORE anything depends on them | in game: **P1** a 160-input Workbench recipe crafts (inventory, and 160 logs split bag + inventory); **P2** a `KnowledgeRequired` recipe at a Crafting bench: hidden or greyed, open bench refreshes on `UpdateKnownRecipes`; **P3** two jars override the same vanilla item: who wins; **P4** a `ResourceTypeId` input satisfied from the bag mirror; **P5** a recoloured icon draws; **P6** (optional) Quality on an ore block; plus the island tree count per species (2.2) |
| **A. Enchanted** (full round, economy) | SkyyCollections 0.2.8 (asset pack: 18 Enchanted items, Compressing tab, `ench` alias table, KnowSync for Enchanted ids, rows marked (A) in 3.3-3.5), SkyySkills 0.4.17 (XP 3.6), SkyyBazaar 0.1.6 (from 0.1.5: 18 rows, premium 0, asserts), SkyySacks 0.7.14 (from 0.7.13: homeOf table, no mirror change); shared `tools/skyyench.py` | Enchanted craftable after the tier, counts right, sells right; Iron pickaxe second route | build asserts: 18 ids x (item json, icon, lang, PRODUCTS row, homeOf entry) from one table; rewards keys unique; every recipe id resolves at start (log "unknown recipe id" = 0); price = base x ratio; LP margin kept; lint 0 fails; crosscheck baseline. In game **T1** craft Enchanted Iron at the Workbench after Iron III, refused before; **T2** sell / buy it; **T3** collection count unchanged after the craft |
| **B1. Tool levels** (full round) | SkyyGear 0.2.5 (as specced in Tool-Levels-Spec; becomes owner of the vanilla tool overrides, F20) | tool levels gate use | as Tool-Levels-Spec |
| **B2. Tool locks** (full round) | SkyyGear next (overrides: `KnowledgeRequired` + Enchanted inputs on Thorium+ pickaxes / hatchets and the Thorium hoe, hoe bench tier 3, vanilla-json hash), SkyyCollections 0.2.9 (rows marked (B2), `coll:locked` += tool ids) | Thorium+ tools refused until the tier | **T4** below Iron IV a Thorium pickaxe is refused at a tier-2 Workbench, allowed after; **T5** the same in `/craft`; **T6** salvage of an overridden tool returns vanilla outputs; server log learn / forget lines per player |
| **C. Foraging armor** (ultracode: art + gear) | SkyyGear next (8-tier set, stats, Feller via SkyyTrees bridge), SkyyTrees 0.3.3 (feller.armorLevel max rule), SkyyCollections next (rows (C), `coll:locked` += armor ids) | 3.4 armor ladder | art sheet approved (Goldenwood helmet = Mithril style, LOCKED); Fortune / Feller caps asserted in a unit model; **T7** set bonus, Feller MAX rule, under-level = no stats |
| **D. Mining + Farming armor** | SkyyGear next (+ Lantern helper light for lamp helmets via SkyyAccessories bridge), SkyyCollections next (rows (D)) | 6 Mining (Copper-Adamantite) + 7 Farming sets | same as C; **T8** helmet lamp lights caves without glare |
| **E. Farming gates + tools** | SkyyCollections next (seed locks, rows (E)), SkyyBazaar next (seed buy-lock F21), SkyyGear next (Thorium sickle, Cobalt / Adamantite / Mithril hoes + sickles) | 2.3 tool column + seed gates | **T9** Carrot seed recipe locked until Wheat III, AND Bazaar refuses to sell Carrot seeds until then; new sickle harvests with the vanilla swing + range |
| **F. Extras** | SkyyCollections next (F8 capstone token), SkyyAccessories 0.5.7 (Prospector / Woodsman / Harvester, rows (F)) | capstones, gathering accessories | Stats page shows the `coll` Fortune source; accessory "previous tier" rule asserted |
| **G. Later** | SkyyWorldGen (Mithril veins, Q6) + SkyyCollections / Bazaar / SkyyGear rows (G) for Enchanted Mithril and Mithril armor; F9 hard ore gates if P6 + the bytecode read say yes; SkyySacks mirror cap for Enchanted ore (harness: craft while selling from the bag, items before = items after + output); SkyyMinions (Pocket Shards); remaining Enchanted logs / crops / stones; Enchanted Blocks | - | own specs |

Deploy rules:
- A, B1, B2 each deploy and roll back as one set. B2 needs A (Enchanted inputs exist) and B1 (same SkyyGear owner). C-F are independent of
  each other once B2 is live.
- **Rollback floor:** once phase A is deployed, `tools/deploy_set.py` gets a SkyyCollections floor of 0.2.8 - rolling back below it would
  turn every Enchanted stack (inventories, chests, bags, Bazaar orders) into unknown ids. To switch the feature off, use `ench.on` false
  instead (the items stay as plain items, the Compressing recipes hide). Run `backup_deploy.py` before A as always.

---

## 7. Migration (never take anything away)

| Item | Rule |
|---|---|
| Live reward rows | unchanged bytes; new tokens are appended on the same keys. A player whose count already passed a tier gets the new recipe at once (recipes are a function of the tier reached); coins / XP `_paid` already advanced, so nothing is paid twice (VERIFIED design) |
| Hand-edited `rewards.properties` | the one-time setting migration rule: only rewrite lines still holding the old default; log + Undo line; run-once marker; keep bytes / line endings |
| Tools, armor and seeds players already own | items are not recipes: every existing tool keeps working; pre-tool-level tools stay lenient (LOCKED); owned seeds still plant, eternal crops keep regrowing |
| Recipes players could craft yesterday (B2 tools, E seeds) | **default: no skill-level grandfather (question 9).** Collection counts carry over, so anyone whose collection reached the tier knows the recipe on first login. A skill-level grant would let Mining 25 skip Thorium IV (against the anti-skip rule), and the KnowSync would forget it on the next run anyway. If Skyy wants a grandfather: a persisted per-player extra list (per `tools/PROFILES-CONTRACT.md`) that the sync unions with `coll:recipes`, granted once for a tool recipe only when the player holds that tool item at first login after B2 |
| Collection counts | untouched (per item id, VERIFIED) |
| Bazaar prices | locked prices unchanged; new Enchanted rows only |
| `ench.on` turned off | Enchanted items stay as plain stackable items (never deleted); Compressing recipes hide |
| SkyySacks KnowSync / AccKnow | keep their own id lists; the generalised sync manages only `coll:locked` ids - no double-manage (asserted at build) |
| Rollback | each phase's set rolls back together, never below the phase-A SkyyCollections floor (section 6); `coll:locked` absent = the syncs do nothing |

---

## 8. Questions for Skyy (each with the recommended default)

| # | Question | Default |
|---|---|---|
| 1 | Tree tiers = **5 zone tiers** (F1 Grove Zone 1, F2 Autumn / Azure Zone 1 Tier 3, F3 Savanna Zone 2, F4 Northern Zone 3, F5 Wastes Zone 4), the 6 sapling-only logs as an "Orchard" side group, Palm dropped (no log ever drops)? Key logs Oak / Maple / Gumboab / Redwood / Sallow, swapped for the tier's commonest log if the island count shows one is scarce? | **yes** |
| 2 | Log prices: keep the LOCKED 2026-10-04 price tiers (they do not follow the zones), or re-price to the zone tiers on a capped x2 scale (F1 3, F2 6, F3 12, F4 24, F5 48; rare specials keep their live price)? A straight 3 -> 128 zone scale would make common Zone 4 logs (Bamboo, Burnt) worth 64x today and the best coins per hit in the game. | **keep the locked prices** |
| 3 | Enchanted ratio **160** (SkyBlock) if probe P1 passes, else 100 = one Hytale stack? (At 160, Enchanted ORE crafts from the inventory only until a later bag change; at 100 it also crafts from bags.) | **160 if P1 passes** |
| 4 | Launch with **18 Enchanted items** (Cobblestone + 5 ores, 5 key logs, 7 key crops), Enchanted Mithril with the veins, **no Enchanted Blocks** yet? | **yes** |
| 5 | SkyBlock-style hard pickaxe gates on Iron / Thorium / Cobalt ore - or keep vanilla's speed-only mining and gate through recipes + tool levels + zones? | **speed-only for now**; revisit in phase G only if the bytecode read + probe P6 show it works |
| 6 | Mithril has no world source in 0.6: add deep Mithril veins to Zone 4 (SkyyWorldGen round), which also switches on the Mithril collection rows - or leave Mithril rows hidden until 0.7? | **add Zone 4 veins** |
| 7 | Next-tool gate at collection **IV** (S / R: 500 / 250 items) and **III** (E: 50); armor sets cost about their unlock threshold (6 / 3 / 1 Enchanted)? | **yes** |
| 8 | Gate the seed RECIPES (each pair unlocks from the previous pair's key collection III; Wheat / Lettuce open), with the Bazaar refusing to sell a seed until you unlocked its recipe? Alternative: drop gated seeds from the Bazaar entirely, or leave seeds ungated. | **yes, with the Bazaar buy-lock** |
| 9 | Grandfather on the first login after the locks: none (collection counts already carry over), or a one-time grant of tool recipes for tools the player already holds? | **none** |
| 10 | Collection capstone Fortune 1 / 1 / 1.5 / 2 / 2 / 2.5 over six key collections per skill (10 total, phase F); Enchanted items sell at exactly base x ratio (no premium)? | **yes / no premium** |
| 11 | Thorium hoe: lower its Farmingbench tier 6 -> 3 so it is usable when Carrot IV unlocks it (or move its unlock to Tomato IV and keep tier 6)? Goldenwood armor band 45-49 until an Onyxium band exists? | **tier 3 / 45-49** |

---

## 9. Draft claims that were WRONG (truth from the fact sheets)

- **Counts:** "159 collections" (all drafts) - it is 105 collections / 273 item ids (Foraging 36).
- **Mining zones:** Adamantite is Zone 4 only (not Zone 3); Cobalt is Zone 3 veins + Zone 4 boulders (not Zone 2-3); Iron spawns from Zone 1
  Tier 1 (not "upper rings"); Mithril has no zone spawn (not Zone 3-4); stone groups: Sandstone / Sand / Clay are Zone 2, Shale Zone 3,
  Limestone / Salt have no worldgen, Ice is Zone 3 only, Volcanic is big in Zone 1 too.
- **Pickaxe gates:** only Adamantite (Quality 4) and Mithril (Quality 5) ore are hard-gated; Copper / Iron / Thorium / Cobalt break with a
  Crude pickaxe. "7 mining tiers" - only 5 metals are gatherable.
- **Prices:** "Bazaar x2 per tier" read as neighbour ratio - neighbours step about x3 (the lock is the multiplier doubling from old prices).
- **Tools that do not exist / have no recipe:** Adamantite / Mithril / Onyxium shovels; Copper / Thorium / Cobalt shovel recipes (only Iron
  has one); Onyxium pickaxe / hatchet recipe; Cobalt / Adamantite / Mithril / Onyxium hoes and sickles (vanilla stops at Thorium hoe, Iron
  sickle).
- **Collections:** Iron collection counts `Ore_Iron`, not ingots; Redwood is curve S (9 tiers), not R; Oak row bag Rare / Legendary are at
  V / VII (not VII / X), Copper hatchet at Oak I and Iron hatchet at Oak VI (not IV / Birch IV); Fiber III is Shears and Stick III the
  Crude Arrow (not "crude armor / rope"); curve S tier IV = 500 (not 1,000); collections cannot pay perks / Fortune today (only recipe,
  coins, xp tokens); `skill:bonus` takes only `xp.` / `dd.` fractions clamped to 1.
- **Foraging:** price-based F1-F5 groups put Zone 4 logs (Burnt, Bamboo, Jungle, Blue Fig, Camphor, Banyan, Sallow) in Zone 1-2 and Amber /
  Frostwood / Stormbark (no natural source) in zone tiers; Azure is Zone 1 Tier 3, Petrified Zone 4; hatchet columns implying Adamantite /
  Mithril hatchets are needed (no log has a Quality); "tool made from wood N" (Iron+ hatchets use no wood); the Foraging-Armor wood map
  (Softwood is Aspen / Beech / Banyan, not Oak; Hardwood is Oak / Ash / Fir / Apple, not Maple; Drywood is Dry / Bottletree; Darkwood is
  Cedar only; Redwood category is Redwood / Maple / Blue Fig; Goldenwood is Sallow / Amber / Palm / Wild Wisteria; no "hidden Goldenwood
  tree"); "Wood armor: any plank" (it is `Wood_Trunk` + Fibre, no planks); Wood armor stats 10 HP / 7% and 12 HP / 9% (vanilla is 46 HP /
  25% set); the ladder is 8 armor tiers (Wood + 7), not 7; Palm logs never drop.
- **Farming:** draft crop groups A-D did not follow the real bench pairs; "wild seeds" plant Wild Grass, not a crop; the bench has 8 tier
  levels (7 upgrades), not "T1-T7"; eternal seeds are 14 items at bench tiers 2-8 / Memories 2-6, not "Eternal I-III, x4 prices";
  "vanilla crops already regrow after F-harvest" (only eternal crops regrow); the metal-echo Farmer armor ladder (superseded by the
  crop armor lock).
- **Enchanted:** "1 slot = 64 items" (ores stack 25, most items 100); "Enchanted Hay Bale block" (only `Ingredient_Hay` exists, id clash);
  a Pumpkin block (none); "any species of the group" recipes for invented groups (only real resource types work); "Enchanted Hardwood /
  Redwood" names clash with real categories; "/craft is being removed" (only in the standalone Pocket Dimension release); Enchanted counts
  as base amount via a multiplier (there is none; a credit is capped at 256 per call); Enchanted Mithril / Onyxium as normal chains (no
  world source); Mithril / Onyxium Miner armor rows (no supply).
- **Engine:** "bag recipes already hide or lock a tool" (only `KnowledgeRequired` recipes lock; tool recipes lack it).
- **This spec's own first version:** `Wood_Redwood_Trunk` called "Redwood-only" (it is the category type Maple and Blue Fig carry);
  Mithril rows shipped as climbable; a 10% Enchanted premium; ratio as a runtime setting; rows for not-yet-existing items in phase A;
  a skill-level grandfather the sync would undo.

---

## Still unknowable without the game (probe P0 answers most)

160-input recipe (P1); client hide / grey of a `KnowledgeRequired` recipe and refresh of an open bench (P2); two mods overriding the same
item (P3); resource-type inputs from the bag mirror (P4); recoloured icon drawing (P5); Quality on `OreIron`-type blocks (P6 + bytecode);
stacks above 100 in the client; Ruby / Voidstone geode placement; Spiral frequency; whether `Lake_Forest_Hedera` (Poisoned) spawns in
the SkyWynn islands; SkyyWorldGen's remap of zone tiers to island rings and per-species tree counts (P0 island check).

---

## Review notes (critic findings, 2026-10-06)

Accepted and fixed above: seed Bazaar skip (F21, Q8); Mithril rows staged to phase G, no Enchanted Mithril product; Q2 default flipped
to keep the locked prices; premium 0; credit once at creation + chunked + source assert (4.2); bag mirror change moved to G with a
conservation harness; price rule stated + asserted; no-Tool/Armor Bazaar assert; armor cost rule (farming / E-curve costs); Iron
pickaxe second route at Copper IV; Redwood-armor leak (now Blue Fig, Zone 4) and T6 moved to Zone 4; key-log scarcity check; tool steps
called speed / Fortune steps; Thorium hoe bench tier; exactly six capstones per skill; Goldenwood band placeholder; grandfather redone;
phase rows only for existing items; P0 probe round before A; ratio build-time; rollback floor; single override owner (SkyyGear) + json
hash; KnowSync in A for Enchanted; 0.7.13 / 0.1.5 pinned first; ResourceType-from-bag probe; seed migration; chunked credit; homeOf
table + shared `tools/skyyench.py`; F9 out of phase B; B split into B1 / B2; base-icon fallback; shared idempotent tab helper.

Rejected or narrowed (one line each):
- "x2 per tier was silently redefined" - the lock's own words define it as the multiplier doubling (Copper x1, Iron x2, Thorium x4); kept,
  now stated as a testable rule.
- "Stop the Bazaar selling Mithril ore" - it is a live LOCKED material row; every Mithril recipe stays collection-gated, so coins buy
  material, not progress.
- "Tier-level progress counter (any log of the tier counts)" - needs registry changes that move live per-item counts; replaced by the
  island count + key swap.
- "T2 and T3 Foraging armor are both Zone 1" - intended: Zone 1 has two tree tiers and every skill's first two armor tiers are Zone 1.
- "Raise the Enchanted credit cap for loot" - not needed at launch (no giver exists); chunked credit covers rewards later.
