# SkyBlock gathering progression - research (Farming, Mining, Foraging)

Cloud research, 2026-10-06. For Skyy's BIG DIRECTION (docs/answered/bags.md, 2026-10-05): a SkyBlock-style ladder where collection levels unlock the recipes for better gathering gear, plus compressed ("Enchanted") materials.
**Sourcing note:** the SkyBlock wiki pages (wiki.hypixel.net, the minecraft.wiki mirror, the fandom wiki) cannot be fetched from this cloud session, so everything below comes from **web-search snippets** (cited) and the older verified research in `research/Collections-Spec.md`.
Each row says which. Anything from my memory is marked **memory (UNVERIFIED)**; a local session with a browser should re-check those against the wiki before they become numbers.

## 0. The one-paragraph answer

SkyBlock's gathering ladder has **three interlocking gates**: (1) **skill level** opens *places* (islands / mines), (2) **collection tier** opens *recipes* (tools, armor, sacks, minions, compactors), (3) **material tier** (the Enchanted forms) is what the better recipes cost. A player climbs by: buy a cheap starter tool from an NPC -> gather the first material -> its collection tiers unlock the next tool/armor -> the next tool breaks the next material -> repeat. Collections also hand out the *compression* tools (Compactors) and the *storage* (sacks). That is exactly the structure Skyy described.

## 1. How a collection ladder is built (SkyBlock)

| Fact | Detail | Source |
|---|---|---|
| Collections unlock recipes, NPC trades, stat buffs and coins for collecting an item; categories Farming, Mining, Combat, Foraging, Fishing | each collection is a row of about 9 steps (some 11-12) | search snippet: [SkyBlock wiki mirror](https://hypixelskyblock.minecraft.wiki/w/User:Thundercraft5/Drafts/Collections) + Collections-Spec |
| Items from player-made blocks, shops and auctions do not count | anti-bypass | same |
| A compressed "Enchanted" item counts as the number of base items needed to craft it | e.g. Enchanted Rotten Flesh = 160 | Collections-Spec (verified there) |
| Typical reward order | I minion · II first armor / trade · III compressed or portal · IV tool or storage · V utility · VI Enchanted + small sack · VII medium sack / axe · VIII talisman / XP · IX large sack / set | see the three examples below |

### 1.1 Foraging examples (search snippets + Collections-Spec)
| Collection | Reward by tier |
|---|---|
| **Oak Wood** | I minion · II oak leaves trade · III Leaflet armor · IV Small Storage · V Forest Biome Stick · VI **Enchanted Oak Wood** recipe · VII Medium Storage · VIII Wood Affinity talisman · IX Large Storage ([Oak Wood](https://hypixel-skyblock.fandom.com/wiki/Oak_Wood)) |
| **Birch Wood** | I minion · II leaves trade · III **Portal to Birch Park** · IV **Sculptor's Axe** · V Biome Stick · VI Small Foraging Sack + **Enchanted Birch Wood** · VII Medium Foraging Sack + Woodcutting Crystal · VIII Travel Scroll to The Park · IX Large Foraging Sack ([Birch Wood](https://hypixelskyblock.minecraft.wiki/w/Birch_Wood)) |
| **Spruce Log** | Spruce Axe at tier II (+50 Foraging Fortune in The Park), Wolf Pet, Portal to Spruce Woods, Woodcutting Crystal, Enchanted Spruce |
| **Jungle Log** | **Jungle Axe at VII** (2 sticks + 3 Enchanted Jungle Wood), **Treecapitator at VII** (4 Enchanted Jungle + a Spruce Axe; Epic; +100 Foraging Fortune in The Park; breaks whole trees), Portal to Jungle Island, Ocelot Pet |
| **Dark Oak Log** | Armor of Growth, Roofed Forest Island portal, Enchanted Dark Oak |
So: **each wood type unlocks a "next" tool, a portal to the next tree island, and its own Enchanted form**, and the tool for wood N is made from Enchanted wood N-1 or N.

### 1.2 Mining examples (Collections-Spec + snippets)
| Collection | Reward by tier |
|---|---|
| **Cobblestone** (10 tiers: 50 · 100 · 250 · 1k · 2.5k · 5k · 10k · 25k · 40k · 70k) | I minion · **III Auto Smelter** · IV compressed · **V Compactor** · VI +1,000 Mining XP · VII/IX haste accessories · **X Super Compactor 3000** (needs 32 Enchanted Cobblestone + a Compactor + 32 Enchanted Redstone) |
| **Iron Ingot** (12 tiers up to 400k) | I minion · II golem / prospecting armor · III discount · IV compressed · later hoppers / auto-deleters up to XII |
| Mining skill levels | each grants Mining Fortune (+4 per level, max +240 at 60), Defense, coins, access to places ([Mining](https://wiki.hypixel.net/Mining)) |
| Pickaxes | **Promising Pickaxe** (bought for 35 coins at the Mine Merchant, gains Mining Speed per 100 blocks mined), Stone Pickaxe = 3 cobblestone + 2 sticks, Gold = 3 gold ingots + 2 sticks, Refined Mithril Pickaxe (+10 Mining Fortune) |
| Places | Deep Caverns needs Mining V; Dwarven Mines Mining 12; Crystal Hollows Heart-of-the-Mountain tier 4 |

### 1.3 Farming examples (snippets)
| Item | Detail |
|---|---|
| **Wheat** (11 tiers 50 -> 100k) | II Farmhand armor recipe · IV compressed · V Enchanted Bread + Small sack · VI **Haymaker armor** (+ Farming Island) · VII talisman · VIII Medium sack · **IX Farm Armor** (needs Farming X; recipe 24 Enchanted Hay Bales; set bonus +25% Speed near farms) · IX +25,000 Farming XP · X Large sack · XI Large Enchanted sack + Enchanted Hay Bale |
| **Rookie Hoe** | Farm Merchant NPC, 10 coins, 50% chance of a seed from broken crops ([Rookie Hoe](https://hypixel-skyblock.fandom.com/wiki/Rookie_Hoe)) |
| First "later" armor | melon collection's late tiers give the first Farming armor of a series (Farming Fortune + rare-drop chance) |
| Jacob's Farming Contests, Garden (crop milestones) | the later farming endgame; SkyWynn parked the Garden (Decisions 3.8) |

## 2. The Enchanted (compressed) materials

| Fact | Detail | Source |
|---|---|---|
| Base -> Enchanted ratio | **160 base items = 1 Enchanted item** (160 Iron Ingots -> Enchanted Iron Ingot; 160 Enchanted Glowstone Dust -> Enchanted Glowstone) | search snippet ([Super Compactor 3000 guide](https://www.minecraftiplist.com/blog/ultimate-guide-crafting-the-super-compactor-3000-in-hypixel-skyblock/)) |
| Second level | many materials also have an **Enchanted Block** (a further compaction, about 160 of the Enchanted item) | memory (UNVERIFIED) |
| Plain Compactor | compacts to *block form* (9 iron ingots = Block of Iron); needs **Cobblestone V** | snippet |
| Super Compactor 3000 | compacts into Enchanted form (160:1) and second-tier Enchanted; needs **Cobblestone X**; Personal Compactor 4000 / 6000 are later upgrades (auto-crafting in the inventory) | snippet |
| Where it matters | Enchanted items are the **ingredient** for nearly every mid/late tool, armor, sack and minion upgrade; so the whole ladder is a funnel into Enchanted forms | pattern across the examples above |
| Collections | the Enchanted item counts as its base amount toward the collection | Collections-Spec |

## 3. Stats that sit on the ladder (fortune and speed)

| Stat | What it does | Source |
|---|---|---|
| **Mining / Farming / Foraging Fortune** | +1% chance of a double drop per 1; **every 100 gives one guaranteed extra drop** (100 = double, 200 = triple chance...) | snippet ([Stat](https://hypixelskyblock.minecraft.wiki/w/Stat), [Mining Fortune](https://hypixel-skyblock.fandom.com/wiki/Mining_Fortune)) |
| Sources of Fortune | skill levels (Mining +4 per level), tools (Refined Mithril Pickaxe +10), armor sets, pets, accessories, in-zone bonuses (Spruce Axe +50 in The Park, Treecapitator +100) | snippets |
| Mining Speed | how fast blocks break; Promising tools grow it while you use them (+10 per 100 blocks, cap +250) | snippet |
| Breaking power | which blocks a tool can break at all (a tier gate for ores); **memory (UNVERIFIED)** that SkyBlock uses this for Mithril/Titanium etc. | memory |

## 4. Places gated by skill level (the "access" gate)

| Gate | Detail | Source |
|---|---|---|
| Foraging islands (old Floating Islands) | Birch Park (Foraging I), Spruce Woods (II), Jungle Island (III), Savanna Woodland (IV), Dark Thicket (V); today replaced by **The Park** (Foraging 1) | snippet ([Floating Islands](https://hypixel-skyblock.fandom.com/wiki/Floating_Islands), [The Park](https://wiki.hypixel.net/Park)) |
| Mining places | Gold Mine -> Deep Caverns (Mining V) -> Dwarven Mines (Mining 12) -> Crystal Hollows (HotM 4) | snippet |
| Portals | the **recipe** for the portal to each foraging island comes from that wood's collection; the **right to enter** comes from the skill level | snippets |
So SkyBlock uses BOTH: skill level = the right to go, collection = the item that lets you build the way there.

## 5. Tier counts SkyBlock really uses (to answer "how many tiers")
| Skill | Material tiers on the main ladder | Notes |
|---|---|---|
| Foraging | **6 trees** (Oak, Birch, Spruce, Dark Oak, Acacia, Jungle), each on its own island and tool; Skyy wants this grouped | SkyBlock has one island per tree; Skyy: not 6 tiers in Zone 1 |
| Mining | about 6-8 steps before the late game: Cobblestone, Coal, Iron, Gold, Lapis, Redstone, Diamond, Emerald (+ Mithril, Titanium, gemstones later) | memory for the exact list |
| Farming | wheat -> pumpkin/melon -> cane/cactus -> etc., each with an Enchanted form and armor | memory |

## 6. What this means for SkyWynn (research-level takeaways, feeds the next tasks)

| # | Lesson | Why it matters for us |
|---|---|---|
| 1 | **A tier is a material + a tool + an armor + an access rule**, not just a block | `Gathering-Tiers-Draft.md` should define each tier as these four things |
| 2 | **Start tools are bought, the next tool is unlocked.** Promising / Rookie tools cost 10-35 coins from an NPC; every later tool comes from a collection recipe | SkyWynn's NPC shop (`NPC-Shops-Spec.md`) sells only the lowest tools; R3 forbids buying the unlocks |
| 3 | **Compression is the funnel:** Compactor at Cobblestone V and Super Compactor at Cobblestone X turn gathering into progress; keep one "compressed" step per material and tie the compactors to collection tiers | `Enchanted-Materials-Draft.md` |
| 4 | **The tool for tier N is made from tier N-1's compressed material**, so the player cannot skip ahead | clean anti-skip rule (pairs with R3) |
| 5 | **Two gates, not one:** skill level opens the zone / biome; collection opens the recipe; do both | SkyWynn already has zone-level gating (class skill unlocks) and collection recipes |
| 6 | SkyBlock Foraging has one tool per tree and a portal per tree; Skyy wants **grouped tree tiers** (3 to 4 groups, not 6) | the group count is a design choice, not SkyBlock's |
| 7 | Fortune is **uniform across the three skills** (1 = 1% double, 100 = guaranteed +1) | fits SkyWynn's existing double-drop perk (0.5% per level) and the Stats page (`Stats-Page-Spec.md`) |
| 8 | Reward cadence per collection is about one item every tier, mostly *sacks, storage, minions (Pocket Shards), compressed forms* in the early tiers and *armor/tools* in the mid tiers | for `Collection-Unlocks-Draft.md` |

## 7. Gaps (UNVERIFIED, for the local session)
| # | Check |
|---|---|
| 1 | Exact tier thresholds and rewards for every Mining/Foraging/Farming collection (only Wheat, Cobblestone, Oak, Iron, Birch were found; the rest I could not fetch). Pull the wiki tables (CSV) for the 15 largest collections. |
| 2 | Exact Enchanted block ratios and which materials have a block form. |
| 3 | The real mapping from tools to materials (pickaxe tier -> ore tier) and any "breaking power" numbers. |
| 4 | Farming hoes by crop (Wheat Hoe, Cane Hoe ...), farming armor chain (Farmhand -> Haymaker -> Farm -> Melon ...). |
| 5 | Which of the wiki facts Skyy wants to copy exactly versus adapt (collection thresholds are Skyy's design). |
