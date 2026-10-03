# NPC shops spec (SkyyEconomy 0.2)

Cloud draft, 2026-10-03. Paper design; nothing built. Locks used: OPEN-QUESTIONS 2026-09-25 (shops have **buy and sell-back per item, infinite stock by default, optional limited stock with a restock
timer; they live in SkyyEconomy 0.2**) and R3 2026-10-02 (**coins never skip collections, tiers, recipes or bags** - coins may buy items you have not unlocked on the AH / Bazaar, but never the unlock itself).
Reads: `SkyyEconomy-Plan.md`, `research/Server-Setup-Research.md` (Bazaar and Bank rules), `SkyyBazaar/build_skyybazaar_0.1.py` (the real 36-item catalogue and prices). Item ids for non-Bazaar items are UNVERIFIED.

## 0. Research (SkyBlock NPC shops, from web search snippets)

| Fact | Source |
|---|---|
| NPC shops sell items at a fixed price; **most have a daily buy limit of 640 items that resets at midnight GMT** | [SkyBlock wiki Shop](https://hypixelskyblock.minecraft.wiki/w/Shop) (snippet) |
| Farm Merchant sells crops, sand, bone meal, hoes; Builder sells blocks and liquids; Lumber Merchant sells axes and wood | same |
| Cobblestone sells to an NPC for 1 coin each | same |
| Full per-item price lists could not be fetched (wiki hosts blocked in this cloud session) | - |

Lesson taken: NPC prices are **flat and cheap for basics, with a daily limit**; the real economy runs on the market (Bazaar / AH).

## 1. What the Bazaar already gives us (the numbers an NPC must fit)

Bazaar (live): `instant buy = base x factor x 1.10`, `instant sell = base x factor x 0.90`, factor clamped **0.25 .. 4.0**, 36 commodities with tiny base prices
(Cobblestone 1, Stone Rubble 0.5, Copper Ore 5, Iron Ore 8, Gold Ore 20, Oak Log 3, Redwood Log 5, Plant Fiber 1, Tree Sap 4, crops 2-5, Bone Fragments 3, Light Hide 6, Venom Sac 15, Fire Essence 25).
The Bazaar build already has an **arbitrage check** against every recipe; NPC shops must pass the same check.

## 2. Price rules (anti-inflation, anti-arbitrage)

Two directions, both defined from the Bazaar `base` of the item, so one number change moves everything:

| Direction | Formula (default) | Why |
|---|---|---|
| **Player sells to NPC** (sell-back) | `floor(base x 0.25)`, minimum 1 coin, **never more than** `bazaar floor buy` = `base x 0.25 x 1.10` | The Bazaar's cheapest instant buy is `0.275 x base` (factor 0.25), so at 0.25 x base nobody can buy at the Bazaar floor and sell to an NPC for a profit |
| **Player buys from NPC** | `ceil(base x 3.7)` for Bazaar commodities (convenience price, deliberately above the Bazaar's top instant sell of `3.6 x base`) | Cannot be used to buy and flip to the Bazaar at the factor ceiling (4.0 x 0.9 = 3.6) |
| Non-commodity basics (torches, arrows, bread, starter tools) | a flat table price; they are **not** in the Bazaar so there is nothing to flip | the cheap "tutorial" items |
| Items with no Bazaar entry and a recipe | NPC sell-back = `0.25 x (sum of input base values)`; never above crafting cost | closed with the build-time arbitrage check |

Example rows (from the live catalogue):

| Item | Bazaar base | NPC buys it from you (sell-back) | NPC sells it to you |
|---|---|---|---|
| Cobblestone | 1 | 1 (min) | 4 |
| Stone Rubble | 0.5 | 1 (min) | 2 |
| Copper Ore | 5 | 1 | 19 |
| Iron Ore | 8 | 2 | 30 |
| Oak Log | 3 | 1 | 12 |
| Redwood Log | 5 | 1 | 19 |
| Wheat | 2 | 1 | 8 |
| Pumpkin | 5 | 1 | 19 |
| Light Hide | 6 | 1 | 23 |
| Venom Sac | 15 | 3 | 56 |
| Essence of Fire | 25 | 6 | 93 |

The sell-back is a pure **safety net for junk** (the Bazaar pays 3-4x more); selling to an NPC is what you do when you cannot be bothered. The 1-coin minimum
means a stack of 64 cobblestone gives 64 coins (SkyBlock gives 1 each too).

## 3. Limits (the daily caps)

| Limit | Default | Notes |
|---|---|---|
| **Daily buy limit per item per profile** (SkyBlock model) | **640** items, resets at a fixed hour (row, shown in seconds) | stops stockpiling cheap resources from NPCs |
| **Daily sell-back cap per profile** (coins from NPC sell-backs) | 20,000 coins per day in Zone 1, scaling x1.5 per zone | a faucet cap: NPC sell-back creates coins from nothing, the Bazaar/AH only move them |
| Stock | **infinite** by default (locked); optional per-item limited stock + restock timer (locked) | |
| Auto-sell hoppers (Pocket Shards) | pay **half** of the NPC sell-back, count toward the same daily cap | see `Pocket-Shards-Spec.md` |

## 4. What each shop sells (by zone town)

Rule from R3: **shops never sell a collection unlock, a tier, a recipe, a bag or an accessory.** They sell plain items you could farm yourself. Gear sold is the lowest tier of that zone and is a convenience, not a shortcut past crafting levels.

| Town | Shop (NPC) | Sells (player buys) | Buys back (sell-back) |
|---|---|---|---|
| **Zone 1 - Department of Arrivals** | **General Goods** | Torches, bread / basic food, Crude arrows (a stack), bandages, a Crude pickaxe/hatchet/hoe (the lowest tools only), seeds and saplings | any Bazaar commodity at 25% |
| | **Forager** | logs (5 kinds), sticks, fibre, tree sap, Wood Wand / Crude Staff (basic only) | logs, fibre, sap |
| | **Miner** | cobblestone, rubble, coal, Copper Ore, Crude/Copper ingot at a premium | ores, ingots |
| | **Farmer** | seeds, a Crude hoe, water bucket, crops at 3.7x | crops |
| **Zone 2 - Annex of Revisions** | **Desert Trader** | carrots / camel food (for taming), sand, cactus products, water | desert items |
| | **Stablehand Hemi** | **mount food**, a brush (cosmetic); the quest gives the first mount, the shop never sells mounts (they are earned) | - |
| | **Smith Supplier** | iron/thorium **ingots** at 3.7x (so a Smithing player can start), charcoal | ores, ingots |
| **Zone 3 - Cold Storage** | **Outfitter** | warm food, coal / fuel, cold-weather consumables (if Zone 3 has a cold effect) | furs, hides |
| | **Archivist's Stall** | paper/ink for quests (quest items are never sold; only generic stationery) | - |
| **Zone 4 - Observatory of Almost** | **Heat Supplies** | heat-resist consumables, lava-safe food, ember coal | fire essence, ash |
| | **Dr. Voidwright's Parts** | crystal shards at 3.7x for his lens quest (the quest still requires them to be found/crafted once; the shop is for repeats) | crystals |
| **Zone 5 - Egg Desk** | **Pet Supplies** | Pet Treats (cooked food items), taming foods, a basic Pet bed (cosmetic) | feathers, teeth, hides |
| **Hub waiting room** | **Ticket machine** | cosmetic tickets, joke items | - |
| **Outposts (30-35)** | small shop: 3-5 basics for that biome (food, torches, local resource) | local commodities | |

Pet eggs are **not sold** (R9: found at higher rarities; eggs and Upgrade Stones are earned). Pocket Shards are not sold either (crafted).
Quest items and unique drops are never buyable or sellable (bound).

## 5. How it is built (engine view)

| Piece | Design |
|---|---|
| NPC | Admin places a shop NPC **in game** (a command / Server Setup tool); the NPC opens a shop page when you press F / right-click (the Bazaar page is already registered as a custom page id usable from an NPC interaction) |
| Catalog | each shop has an id and a table: item id, buy price, sell-back price (or "auto" = the formulas above), limited stock, restock seconds. Edited **in Server Setup** (PROJECT-RULES: everything editable in game) |
| UI | vanilla-look inline page (Bazaar-style grid, Buy 1 / Buy 64 / Sell 64 / Sell all), prices shown, remaining daily limit shown |
| Purchase | the same anti-dupe pattern as the Bazaar: `coins:fn:take` first, add items, measure, refund difference; sells remove first, then pay |
| Daily limits | per profile (PROFILES-CONTRACT), stored with a reset timestamp |
| Item value tool (later, from the Economy plan) | one price for any item = bazaar price, else cheapest BIN, else NPC formula; feeds networth hints |
| Admin | `/shopadmin` (admin perm group rule: `requirePermission` + empty group list) create/list/remove NPC, reload catalog |

## 6. Exploit and balance check

| Risk | Handling |
|---|---|
| Buy from NPC, sell on Bazaar/AH | NPC buy price >= `3.7 x base` > the Bazaar's maximum instant sell `3.6 x base`; non-commodities are checked by the build-time recipe check; daily 640 limit |
| Buy cheap on the Bazaar, sell back to NPC | sell-back is `0.25 x base`, below the Bazaar floor buy `0.275 x base` |
| Craft items and sell them to an NPC for more than their parts | sell-back capped at `0.25 x` ingredient value; arbitrage check fails the build if not |
| Pocket Shards / minions farming NPC money | auto-sell pays half and shares the daily cap |
| Alt profiles to multiply the daily caps | caps are per profile; a profile's coins need real play; the coin faucet is small (default 20,000 a day) |
| Selling bound/quest items | bound items are refused |
| Stock hoarding of limited items | daily limit + stock timers; limited stock stays optional |
| Shop sells something a recipe/collection unlock is meant to gate (R3) | catalogs never include recipe-gated, bag or tier items; an admin check lists any violation when saving a catalog |
| Rounding | buys round up, sells round down (same as the Bazaar) |
| Coin overflow | per-trade quantity limit 100,000 and totals refused above 1e15 (Bazaar rules) |
| Inflation overall | NPC purchases are sinks; sell-backs are small, capped faucets; pair with the Tab (`Tab-Economy.md`) as the endgame sink |

## 7. Server Setup rows (sketch)

`shops.enabled`, `shops.buyMult` (3.7), `shops.sellBackPercent` (25), `shops.minSell` (1), `shops.dailyLimit` (640 items), `shops.resetSeconds` (anchor hour), `shops.dailySellCap` by zone,
`shops.limitedStock.default` (off), a per-shop catalog table (id, item, buy, sell, stock, restockSeconds), `shops.autoSellShare` (50% of sell-back).

## 8. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Item ids for non-Bazaar goods (torches, arrows, bread, bandages, Crude tools). Use the live item registry and the SkyyCollections/Bazaar id checks. |
| 2 | How a placed NPC can open a custom page (the Bazaar already has the page id `SkyyBazaar`; copy that route). Whether a vanilla "merchant"-style NPC role exists to reuse. |
| 3 | Whether Zone 3 has a cold / Zone 4 a heat player effect (for the Outfitter and Heat Supplies items). If not, drop those lines. |
| 4 | Daily reset anchor: the server's real clock (UTC midnight like SkyBlock), shown in seconds in Server Setup. |
| 5 | The real market will move prices (factor 0.25-4). Re-run the arbitrage check after any Bazaar price change. |

## 9. Questions for Skyy

1. Sell-back at 25% of Bazaar base and buy at 3.7x - OK as the "convenience" prices (the market stays the real way to trade)? Recommended: yes.
2. A daily buy limit of 640 per item like SkyBlock - keep, or higher for the zone 1 starter items so new players are not blocked? (Recommended: 640 everywhere except Torches/Bread = unlimited.)
3. Should NPC shops ever sell Crude weapons/armor? (Recommended: weapons/tools yes, armor no - it is meant to be crafted in the starter chain.)
