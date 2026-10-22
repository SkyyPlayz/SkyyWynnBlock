# Balance pass P7 - Economy: coins per hour, Bazaar / AH / shop prices, sinks, death coin loss, buy-across rules (BUILD-READY spec, 2026-10-21)

Phase P7 of research/Balance-Pass-Spec.md section 8 ("Economy: coins per hour, Bazaar / AH / shop prices, sinks, death coin loss, buy-across
rules"; mods SkyyBazaar, SkyyAuctions, SkyyMerchants, SkyyCoins, SkyyIslands (death); "prices follow the P6 gathering speeds"). Skyy 2026-10-20/21:
"keep going down the list. dont stop until the entire list is done" + "just go with the recommended on all of them. i need to go to bed." + "run
whatever you can in parallel to speed up the build". Spec only - nothing built, nothing committed. Where answers go: docs/answered/economy.md
(prices, sinks, death, buy-across, coin curve), docs/answered/skills.md (level-up coins, collection coins, totems); this file holds the plan (the
main session adds it to INDEX.md under research/). Builds ON research/Balance-P6-Gathering-Spec.md (rates, D(T) drops per block, collection
sizes, armor / tool costs - all used as inputs, not redone), research/Balance-P5-Power-Spec.md 1.1 (the Fortune budget behind D(T)) and
research/Balance-P3-XP-Spec.md (levels, the level-up count). **P5 and P6 must be pinned first** (Gear 0.3.35 / 0.3.36, Collections 0.2.31, Shards
0.4.4, Trees 0.4.5): every price here is "coins per hour at the P5 Fortune and the P6 rates".

**Goals used (Skyy's words):** coins "10k / 500k / 10M" if never spending at the end of Zone 1 / 3 / 5 (docs/answered/economy.md:162 Q18); coin
sinks "Even mix" (upgrades, Bazaar, cosmetics about equal, Q19); buy across "Yes, ~1.5x time (Rec.)" (Q20; Balance-Pass-Spec.md:40 "combat gear
buyable (~1.5x the time of earning it), gathering gear not (only its upgrade materials)"); "all the gathering skills make money pretty equally, so
no one skill is really better than the other. the further you level it the more money it can make you. so for money, focusing one is best, then
level the others when they slow you down." (docs/answered/skills.md:187 Q4); death "Small coin loss" (lose ~5% of carried coins, bank safe)
(skills.md:189 Q9, 2026-10-18 - newer than economy.md:127 2026-10-15 "coins yes, loot no" = keep 10-25 %, so 5 % wins); "raise the sell price of
everything to at least 2 coins, and scale everything else accordingly" (economy.md:134) + `market.minSell` 2 (economy.md:130); "make prices all
scale by tier. so T2 buy and sell is a good bit higher than T1" (economy.md:131); Eternal seeds "T1 crops start at like 800 coins. cause it lasts
forever" (economy.md:129); merchants "No scaling" per rebirth (economy.md:144); AH Hypixel fees LOCKED (economy.md:49-56); vault pages LOCKED
(economy.md:31); bank interest option E LOCKED (economy.md:88); Eternal Flame free-fuel loop "Leave it" (economy.md:160); a real coin sink
"Yes, after rebirth R3" (economy.md:142).

**Legend.** VERIFIED = read in code / live config (cited; BZ = SkyyBazaar/build_skyybazaar_0.2.0.py, CN = SkyyCoins/build_skyycoins_0.1.9.py,
ME = SkyyMerchants/build_skyymerchants_0.1.6.py, AU = SkyyAuctions/build_skyyauctions_0.1.14.py, IS = SkyyIslands/build_skyyislands_0.5.24.py,
B = SkyyGear/build_skyygear_0.3.34.py, S = SkyySkills/build_skyyskills_0.4.58.py, COL = SkyyCollections/build_skyycollections_0.2.30.py, TR =
SkyyTrees/build_skyytrees_0.4.4.py, EX = SkyyExploration/build_skyyexploration_0.3.2.py, H = SkyyShards/build_skyyshards_0.4.3.py, SAC =
SkyySacks/build_skyysacks_0.8.24.py, FI = SkyyFishing/build_skyyfishing_0.1.12.py, TT = tools/tier_tags.py; LIVE =
UserData/Saves/NewBetaTest/mods/Skyy_<Mod>/, read only). DERIVED = the scratch model (copy of tools/balance_model.py + p7_econ.py in
tools/dev/scratch/p7spec/, deleted after; its `p7_*` functions go into tools/balance_model.py `--econ`, section 9.6). PROPOSED = a default this spec
picks. UNVERIFIED = needs the game. W = checked on the web, K = my knowledge, not checked.

---

## 0. For Skyy (plain words)

1. **Your coin targets can't hold at today's floor, so the coin "unit" grows x10** (Q1): end of Zone 1 / 3 / 5 = **100k / 5M / 100M** if you
   never spend (was 10k / 500k / 10M). Why: with P5's Fortune a Zone 1 miner breaks ~2,000 items an hour, and your 2-coin minimum sell alone pays
   ~3,000 coins an hour from stone - more than the old Zone 1 target for the whole hour. Only the ratios matter (prices vs costs), and every cost
   below is sized to the new numbers.
2. **Every gathering skill now earns the same coins per hour in each zone** (within 3 % in the model), rising ~5x a zone: a focused gathering
   hour pays ~8k in Zone 1, 42k in Zone 2, 300k in Zone 3, 1.06M in Zone 4, 3.8M in Zone 5. Today Mining paid 1.5-6x the others.
3. **Prices per tier, re-set** (Bazaar): each tier's item sells for at least 1.2x the tier below. Zone 1 items roughly halve (Copper ore 22.5 ->
   12, Oak 13.5 -> 8.5, Wheat 9 -> 4.5); late ores drop to ~1/5 (Mithril 6,480 -> 1,208) because P5 Fortune gives ~10 ores per block. Crops are
   priced per HARVEST, so Corn / Potato / Onion (3 a harvest) sell cheaper per item. Bars, Enchanted items and alloys follow their inputs as today.
4. **Focus pays:** a higher skill level means a higher tool tier and more Fortune, so the same hour earns more - "focusing one is best".
5. **Level-up and collection coins follow one coin curve** (Q5, Q6): level-ups pay 60 coins at Lv 10, 2,800 at Lv 50, 50k at Lv 90 (today 100 x
   level = 1,000 / 5,000 / 9,000 - far too much early, far too little late); a collection's tier coins grow with the item's tier (Copper V 190,
   Chromium V 12k, Titanium V 164k).
6. **Costs follow the same curve** (Q10): reforge, level-up, identify, tree respec, shard upgrades - each is "a slice of an hour" at your level
   (a Rare reforge = 3 minutes of income at any level). Upgrading a zone's whole kit costs about a third of the zone's coins.
7. **Buying across (Q8, Q13):** a gatherer can buy a merchant weapon for ~1.9 hours of gathering (1.5x the ~1.25 h it takes to earn one); a fighter
   can buy gathering materials at ~1.5x the time - so an hour of fighting must sell for ~0.8 of a gathering hour (Combat drops re-priced).
   Gathering gear itself is never for sale (the AH refuses gathering armor too, Q9). Bought items never give collection or skill progress.
8. **Death:** you lose **5 % of the coins you carry** (was 10-25 %), the bank is safe, and nothing is lost on your own island or in your shard
   worlds (Hypixel's private-island rule) (Q7).
9. **Shards (idle) need a cap** (Q11, changes P6): P6's Totem I-V = 20-100 % of an active farming hour, banked up to 3 days, would pay up to 2x
   the coin targets (more for players who log in daily). Proposed: Totem I-V = 3 / 6 / 9 / 12 / 15 % of an active hour and at most 12 h banked
   between visits - "late game farming fully idle" then means your farming share runs itself.
10. **No money loops:** every buy -> craft / smelt / compress -> sell route the Bazaar build already checks still loses 2-18 % (list in Part 4);
    the cosmetic third of the sink mix (The Tab, Wardrobe prices) is a later round (Q14).

---

## Research (short; W / K marked)

| Game | What it does | What we take |
|---|---|---|
| Hypixel SkyBlock death (K) | dying outside the Private Island loses half the purse; the bank is safe | **5 % of the purse** (Skyy "small"), bank safe, **own island + shard worlds safe** |
| Hypixel SkyBlock Bazaar (K + research/Bazaar-Order-Book-Spec.md) | instant buy / sell around an order book, 1.25 % tax on order fills, NPC sell prices tiny (Cobblestone 1) | today's 10 % spread + 1.25 % order tax stay; plain stone at the floor |
| Hypixel SkyBlock coin sinks (K) | reforges / enchants / upgrades priced per item tier, cosmetics, the bank interest cap | **one coin curve**: every coin cost is hours-of-income at your level |
| Hypixel SkyBlock minions (K) | idle production runs offline; for casual players often more than active play | idle **capped** (share + offline hours) so active play stays the main income |
| Wynncraft emeralds (K) | gathered items sell for little; money comes from rarer drops, trade market fees | combat drops share of income, AH fees kept |
| Diablo / WoW gold (K) | rewards and costs scale exponentially with level so a reward never becomes trivial | level-up / collection coins on the curve, not linear in level |

Survey (PROJECT-RULES 2): nothing new is added - P7 tunes our own systems. Reference already recorded: research/cloud/Economy-Audit.md (faucets /
sinks / loops audit; C4 Enchanted Blocks at 0.99 of the loop line), research/cloud/Tab-Economy.md (The Tab endgame sink design), research/Bazaar-
Order-Book-Spec.md (0.2.0 live).

---

## Part 1 - Coin targets and THE coin curve (DERIVED; Q1)

### 1.1 Why the unit must grow (DERIVED)
- The Bazaar floors every instant sell at 2 coins (`market.minSell` 2, BZ:2807; Skyy economy.md:130 / 134). Pickaxe Fortune counts on stone
  (`only.mining` = "Rock_,Rubble_,Ore_", B:1730). Zone 1 mid tier (T2): 900 blocks / h x 75 % stone x D(2) 2.25 = 1,519 stone / h x 2 = **3,040
  coins / h from stone alone**; logs at the floor 900 / h x 2 = 1,800 / h. Skyy's Zone 1 target is 10k / 12 h = **833 / h for everything**.
- So the floor + Fortune fix the bottom. The model's smallest workable unit puts T1 ore at 3x the stone floor (12 base / 10.8 sell) so ore is the
  point of mining: that is **K = 10** (Q1). The SHAPE stays Skyy's (end of Zone 1 : 3 : 5 = 1 : 50 : 1,000).

### 1.2 Targets (PROPOSED, K = 10; Zones 2 / 4 = the geometric middle as in balance_model.py; zone hours from balance_model ZONES)

| Zone | Levels | Hours (first run) | Coins at zone end (never spending) | Target coins / h (all activities) | Focused gathering hour G (Part 2) |
|---|---|---|---|---|---|
| 1 | 1-20 | 12 | 100k | 8,333 | 8,160 |
| 2 | 20-40 | 14 | 707k | 43.4k | 42.5k |
| 3 | 40-60 | 14 | 5M | 307k | 300k |
| 4 | 60-80 | 16 | 22.4M | 1.085M | 1.063M |
| 5 | 80-100 | 20 | 100M | 3.88M | 3.80M |

### 1.3 THE coin curve (PROPOSED; SkyyCoins `coins.curve`, one table for every mod)
Factor at a level, 1.0 = the middle of Zone 1 (Lv 10) = the target hourly income at that level / 8,333 (log-linear between the zone middles
Lv 10 / 30 / 50 / 70 / 90, extended past both ends):

`coins.curve=1:0.476,8:0.848,10:1,15:1.51,20:2.28,28:4.41,30:5.2,35:8.49,40:13.8,48:30.3,50:36.8,55:50.5,60:69.2,68:115,70:130,75:179,80:246,88:410,90:466,95:641,100:881`

SkyyCoins publishes it as `coins:fn:curve` (Object[] { Integer level } -> Double; plain java types, skyy.bridge) - log-linear interpolation,
clamped to 1..100. Every coin price and coin reward that "grows with level" below = (its Lv-10 base) x curve(level). A mod whose SkyyCoins is
older / missing uses a built-in copy of the default (the build asserts its copy equals SkyyCoins' default text).

---

## Part 2 - Where the coins come from (income budget, PROPOSED; DERIVED proof in 9.5)

Balanced player (balance_model SHARE): Class / combat 45 %, Mining 18 %, Foraging 15 %, Farming 10 %, Cooking 4 %, Alchemy 4 %, Fishing 2 %.

| Source | Share of the zone's coins | Rule |
|---|---|---|
| Sales (Bazaar instant sell of gathered + combat items, fish) | **80 %** | gathering hour G = combat hour / 0.815 (Part 5) = fishing hour; 0.43 G + 0.45 x 0.815 G + 0.02 G = 0.817 G per played hour -> G = 0.98 x target / h |
| Level-up coins (SkyySkills, every skill + the class) | 7 % | Part 2.1 |
| Collection tier coins (SkyyCollections) | 7 % | Part 2.2 |
| Other: quests, exploration luggage / airdrops, bank interest, Pocket Change, fishing treasure | 6 % | Part 2.3 (rows follow the curve) |
| Idle shard production | 0 % in the target; capped (Part 8) | +3 .. +15 % on top at Totem I .. V |

Cooking / alchemy consume crops (no sales counted). Starter coins 10,000 (CN:837 / 1181) stay = 1.2 h of Zone 1 (Q18).

### 2.1 Level-up coins (SkyySkills `levelCoins`, NEW row; Q5)
Today (VERIFIED S:2417 / 9375 / 21597): `coinsPerLevel=100`, reaching level L pays 100 x L in every skill and the class (rebirth x
`rebirth.coinFactor` 0.8 per rebirth, S:2418). DERIVED: the P3 simulation (balance_model.simulate_today) counts **108 level-ups across all skills in
Zone 1** (125 in Zone 2); 100 x L is 136k by the end of Zone 1 (targets.md 3) - 13x the old target on its own, and only 9,000 a level at Lv 90.
PROPOSED: coins for reaching level L = 7 % of the zone's coins / the zone's level-ups, along the curve:

`levelCoins=1:30,10:60,20:150,21:190,30:390,40:1000,41:1200,50:2800,60:5200,61:6400,70:11500,80:21500,81:28500,90:50500,100:95000`

(text "level:coins", log-linear between points, rounded to 10 / 100 / 500; empty = the old `coinsPerLevel` x L). `rebirth.coinFactor` 0.8 stays.

### 2.2 Collection tier coins (SkyyCollections `tier.coinsByTier`, NEW row; Q6)
Today (VERIFIED COL:1210): `tier.coins=25,50,100,200,400,750,1500,3000,6000,12500` for every collection (combat x2 on III / V / VII / last). With
P6's shorter ladders a balanced player takes ~13 collections to V per zone (3 skills x the zone's 3 tier items + 1 stone + 3 combat, GUESS).
PROPOSED: tier k of a collection whose item has tier T pays `tier.coins[k] x curve(band start of T)` (band starts TT LEVEL_BANDS: T1 Lv 1, T2 8,
T3 15 ... T15 95); untiered collections (combat mobs, stone) use curve 1.0. `tier.coins` text stays. Result: Copper V 190, Iron V 340, Chromium
V 12k, Titanium V 164k; share of zone coins 9.5 / 8.4 / 7.4 / 7.0 / 5.6 % (Zones 1-5, model) - inside the 7 % +-2.5.

### 2.3 Other sources (PROPOSED rows; small)
- **Exploration** (EX:1367-1373, VERIFIED): luggage `coinsMin=10,25,60,150` / `coinsMax=30,60,150,400` x `coinZoneMult=1,1.5,2,3`, cap 8 / h;
  airdrop 150-400 every 1,800 s. PROPOSED `coinZoneMult=1,5.2,36.8,130,466` (the curve at the zone middles; a 5th entry for Zone 5 - if the key
  reads only 4 the builder extends it) and the airdrop coins x the same zone factor. Zone 1 stays (max ~880 / h while exploring = 10 % of an hour).
- **Pocket Change** (TR:2126 / 2145, VERIFIED keys MCoins per 0.002 / FCoins per 0.006, pays coins = skill level per proc): PROPOSED a proc pays
  `pocket.coinsLv10` 14 x curve(skill level) (Lv 10 14, Lv 50 500, Lv 90 6,300) = ~3 % of that skill's hour at rank 10 (18 / 24 procs / h).
- **Bank interest** (SkyyBank 0.1.16, LOCKED option E: 2 % / 1 % / 0.5 % brackets to 1M / 5M / 10M, once a real day): unchanged (Q15). With K =
  10 it is ~2 % of an hour's income a day early and negligible late - by Skyy's lock.
- **Quests** board 40 / 80 / 140 a day + quest rewards (SkyyQuests 0.4.2): unchanged (< 1 %); `board.coinScalePercent` stays the knob.
- **Fishing** (FI:942 `fish.price.perKg` 26 x rarity x demand, own SELL tab): unchanged (rework pending, skills.md:187); target "a fishing hour ~
  G" is measured in game (9.7 step 8), not tuned.

---

## Part 3 - Bazaar prices (SkyyBazaar 0.2.1; Q2-Q4, Q17)

### 3.1 Today (VERIFIED BZ + LIVE products.properties)
- Line `<ItemId>=<Category>,<base>,<Name>` (549 products, LIVE:1). Instant buy = max(base x f, floor) x 1.10, instant sell = max(min(base, SELL_CAP)
  x f, floor) x 0.90 (`Market.quote` BZ:6045-6062, `SPREAD` 0.10 BZ:918); demand f decays to 1 (half-life 120 min), step per unit
  exp(ln 1.1 x base / `impactCoins` 45,000) (BZ:6034-6042, LIVE market.properties).
- Fixed prices = `TIER_LADDER` per family (BZ:2439, ore 5 / 16 / 48 / 144 / 480 / 1440 / 3712 on the old steps, renumbered to the 15-step ladder
  BZ:2446-2454; `ladder3` BZ:2620 geometric between steps) x `SCALE_X` 4.5 (BZ:2584, Skyy's "cheapest sells for 2"); logs never below their
  0.1.13 rarity price (`OLD_0113`), saplings 3.3 x log (`SAPLING_X` BZ:2536), Eternal seeds 800 x2 a step (not scaled, BZ:355-366).
- AUTO (processed) = raw inputs by recipe ratio + fuel x (1 + `processed.premium` 20 %, range 0-22, BZ:958 / 2029); Enchanted = 100 x base x
  1.2 (tools/skyyench.py:44, `PREMIUM_ITEMS` BZ:957); Bronze fixed (BZ:2661); alloys 1 + 1 = 2 bars (`ALLOY_OUT` BZ:2223).
- LIVE samples: Ore_Copper 22.5, Ore_Iron 72, Ore_Thorium 216, Ore_Cobalt 648, Ore_Adamantite 2,160, Ore_Mithril 6,480; Wood_Oak 13.5, Maple
  56.25, Redwood 416.25, Sallow 1,107, Crystal / Stormbark 2,954.25; Wheat 9, Carrot 24.75, Corn 36, Potato 288, Onion 362.25, Mushroom Cap Brown
  456.75; Rock_Stone_Cobble 4.5; Skyy_Ench_Copper 2,700, Ench Oak 1,620, Ench Wheat 1,080.
- DERIVED (P6 6.2): coins per focused hour at these prices are 25-35x over the old targets and Mining 1.5-6x the others.

### 3.2 THE RULE (PROPOSED)
1. **One gathering hour per tier:** G(T) = log-linear through the zone middles (T2 / T5 / T8 / T11 / T14 = G of Part 1.2), corrected so each
   zone's AVERAGE (its 3 tiers weighted by levels: 7 / 7 / 6) hits G (`p7_fit`).
2. **Ores:** the ore of tier To is the best ore for tiers To .. next ore - 1 (Iron for T2-T3, Lead for T5-T6 ...); its sell price makes the average
   Mining hour over those tiers = G, after the stone part (675 x D(T) stone / h at 2.0). Ore tiers (TT ORES + ZONE_METALS): Copper 1, Iron 2,
   Thorium 4, Lead 5, Cobalt 7, Chromium 8, Adamantite 10, Slag 11, Mithril 13, Titanium 14, Onyxium 16.
3. **Logs:** sell = G(T) / (400 x D(T)), every species of a tier the same (TT LOGS; the OLD_0113 "rare woods stay premium" floor is DROPPED -
   with 15 tiers each wood already has its tier; Q2).
4. **Crops:** sell = G(T) / (500 x q x D(T)) with q = the crop's mean harvest quantity (P6 Part 1, read by the build from Assets
   `Drops_Plant_Crop_<X>_StageFinal_Harvest`: Wheat 1.5, Corn / Potato / Onion 3, Cotton / Rice 2, others 1). Per-HARVEST value rises by tier;
   per item a q-3 crop is cheaper (Q3). Mushroom (T15, q 1).
5. **Monotone:** each tier's sell >= 1.2 x the tier below (ores: 1.2^gap; crops: per harvest), fixed by lowering the lower tier (Skyy "a good bit
   higher"; Q2). Every sell >= the 2-coin floor. Base = sell / 0.9, rounded to 0.5.
6. **Stone:** every plain mined stone / cobble / rubble / zone host rock (`Rock_*` without a recipe, `Rubble_*`) base **2.25** (sells 2.0, Q4).
   Smelted / crafted stones stay AUTO. Gems (Rock_Gem_*) unchanged (rare drops; UNVERIFIED tier).
7. **Processed / Enchanted / alloys:** unchanged rules (AUTO from the new raw prices; `processed.premium` 20; Enchanted 100 x 1.2; alloys 1 + 1 = 2;
   Bronze fixed = its crafting value as 0.1.22). Enchanted alloys AUTO.
8. **Seeds / saplings / planks / sticks / other fixed crafted goods:** keep their 0.2.0 RATIO to their input (seed : crop, sapling = 3.3 x log,
   plank : log ...) on the new input price, then the build's loop holds (`_hold` / `_fixes` BZ:2825 / 2882) cap them. **Eternal seeds unchanged**
   (Skyy's 800 x2, Q19).
9. **Combat family** (bones, hides, essences, feathers, crystals, fibre, mob drops; Combat / Smithing tabs): re-anchored so one kill of a zone's
   mobs sells for **0.815 x G / 150** (Part 5): Zone 1 44, Zone 2 230, Zone 3 1,630, Zone 4 5,770, Zone 5 20,700 coins a kill. The builder computes
   each mob role's expected drop value from the Assets drop lists the build already loads (`asset_model` BZ:1781, DROPS) and SkyyMobs' zone
   rosters; a product's price keeps its 0.2.0 ratio to the family and one factor per zone is solved (printed). If the rosters cannot be read at
   build time: every Combat product x the median ratio 0.5 and the in-game measure decides (UNVERIFIED, 9.7 step 6).
10. `impactCoins` 45,000 -> **22,500** (prices halve on the median, so the same coins move the market the same %; Q17).

### 3.3 Result (DERIVED, p7_econ.py; base prices = products.properties, sell = x 0.9)

| T | Ore (base) | Bar AUTO (x1.2) | Ench ore / bar | Log (base, every species) | Ench log | Crop (base, q) |
|---|---|---|---|---|---|---|
| 1 | Copper **12** (22.5) | 14.4 | 1,440 | **8.5** (Oak 13.5) | 1,020 | Wheat **4.5** (9), q 1.5 |
| 2 | Iron **14.5** (72) | 17.4 | 1,740 | 10.5 | 1,260 | Lettuce 8 (18) |
| 3 | - (Bronze AUTO ~19) | | | 13 (Maple 56.25) | | Carrot 10.5 (24.75) |
| 4 | Thorium **25** (216) | 30 | 3,000 | 18 | | Corn 4.5 (36), q 3 |
| 5 | Lead **55** | 66 | 6,600 | 24.5 | 2,940 | Cauliflower 19.5 (45) |
| 6 | - (Dusk AUTO) | | | 43.5 | | Turnip 34.5 |
| 7 | Cobalt **130.5** (648) | 156.6 | 15,660 | 77 (Cedar 216) | | Pumpkin 62 (72) |
| 8 | Chromium **285.5** | 342.6 | 34,260 | 140 | 16,800 | Aubergine 112 |
| 9 | - (Azurvane AUTO) | | | 186.5 (Redwood 416.25) | | Tomato 149 (114.75) |
| 10 | Adamantite **439.5** (2,160) | 527.4 | 52,740 | 251 | | Chilli 200.5 (144) |
| 11 | Slag **728** | 873.6 | 87,360 | 340 | 40,800 | Cotton 136 (182.25), q 2 |
| 12 | - (Cinder AUTO) | | | 480.5 (Sallow 1,107) | | Rice 192 (229.5), q 2 |
| 13 | Mithril **1,208** (6,480) | 1,449.6 | 144,960 | 683 | | Potato 182 (288), q 3 |
| 14 | Titanium **2,117.5** | 2,541 | 254,100 | 975.5 (Banyan 2,130.75) | 117,060 | Onion 260 (362.25), q 3 |
| 15 | - (Lumen AUTO) | | | 1,400 (Crystal 2,954.25) | 168,000 | Mushroom 1,120 (Cap Brown 456.75) |
| 16 | Onyxium **3,583** | 4,299.6 | 429,960 | - | - | - |

(today's LIVE base in brackets; stone 4.5 -> 2.25.) The Bazaar build computes this table itself from `p7_*` (no hand copy) and prints it.

### 3.4 Coins per hour per skill (DERIVED; zone average of its 3 tiers, x 0.9 sell)

| Zone | Mining | Foraging | Farming | ratio M / F / Fa to their mean | vs G | today (P6 6.2) / new: M / F / Fa |
|---|---|---|---|---|---|---|
| 1 | 8,400 | 8,050 | 7,940 | 1.03 / 0.99 / 0.98 | 1.00 | x3.3 / x2.0 / x2.3 |
| 2 | 43.2k | 42.6k | 41.8k | 1.02 / 1.00 / 0.98 | 1.00 | x4.3 / x3.1 / x2.3 |
| 3 | 302k | 299k | 300k | 1.01 / 1.00 / 1.00 | 1.00 | x2.7 / x1.6 / x1.0 |
| 4 | 1.07M | 1.06M | 1.06M | 1.01 / 1.00 / 1.00 | 1.00 | x3.4 / x1.6 / x0.8 |
| 5 | 3.83M | 3.79M | 3.79M | 1.01 / 1.00 / 1.00 | 1.00 | x3.6 / x0.6 / x0.7 |

Per TIER (not per zone) Mining swings: +20-42 % on a new-ore tier (T5 Lead, T8 Chromium, T11 Slag, T14 Titanium), -8 to -20 % on an alloy tier
(the miner mines the two parents there); logs and crops are equal per tier. Stone is 36 % of a T1 Mining hour, 21 % at T4, under 5 % from T7.
"Focus pays": the hour at a zone's top tier is 2.5-4x its bottom tier (more Fortune + the next item).

---

## Part 4 - No money loops (DERIVED; the routes checked)

The Bazaar build ALREADY proves loops on every price table it ships (VERIFIED BZ:595-683 build notes): `check_assets` (BZ:1621) over every
vanilla recipe at premium 0 / 15 / default / 22, `loop_check` (BZ:2073) at every whole premium 0..22 with fuel, charcoal from 2 fuel items, co-products and
liquidation, `_step_loops` / `_fixes` (BZ:2844 / 2882) holding a crafted good at its loop limit, the SET recipe scan (BZ:2689-2792: SkyyWorldGen
alloys, Collections Enchanted recipes, Enchanted alloys), and `loop_check_selftest` (BZ:2175). P7 changes only the input prices - the 0.2.1
build re-runs all of them on the new table and must end with 0 loops. Routes (margin = sell revenue / buy cost - 1, model at the new prices):

| # | Route | Margin | Why closed |
|---|---|---|---|
| L1 | buy ore -> smelt (Eternal Flame, no fuel) -> sell bar, each of the 11 ores | **-1.8 %** | bar = 1.2 x ore; 0.9 x 1.2 = 1.08 < 1.10 (Skyy "Leave it" for the fuel part, economy.md:160) |
| L2 | buy ore -> smelt with Smelting Fortune up to +100 % -> sell 2 bars | -1.8 % | `smelt.fortune.minedOnly` ON (SAC:675): Fortune only on mined ore |
| L3 | buy 100 bars -> Enchanted ore -> sell (11 metals) | -18 % | premium counted once (BZ:2032-2034) |
| L4 | buy 100 raw (ore / log / crop, all tiers) -> Enchanted -> sell | -1.8 % | 0.9 x 1.2 < 1.1 |
| L5 | buy Copper + Iron bars -> Bronze (1 + 1 = 2) -> sell; the four zone alloys + Electrum | <= -2 % | Bronze fixed at its crafting value + sell cap 0.98 (BZ:105, 2815); zone alloys AUTO |
| L6 | buy 100 Enchanted parents -> Enchanted alloy -> sell | <= -2 % | AUTO, premium once (0.1.22) |
| L7 | buy log -> planks / sticks / charcoal -> sell | held at the loop limit | fixed crafted goods held by `_fixes`; charcoal AUTO (2 fuel -> 1 charcoal is its own recipe) |
| L8 | buy seeds / saplings -> plant -> sell the harvest | production, not a loop (real growing time + land); seeds / saplings sell-capped (`SELL_CAP` BZ:2810) | Skyy: "buy -> grow -> sell still pays, just less" (economy.md:80) |
| L9 | buy Eternal seeds -> sell back | sell cap (`ETERNAL_CAP` BZ:1550) | |
| L10 | buy crops -> cook a dish -> sell | none if dishes are no Bazaar product (LIVE shows only raw `Food_*`); `check_assets` covers any that are | UNVERIFIED for every dish id |
| L11 | buy vanilla fish on the Bazaar -> SkyyFishing SELL tab | harness check (9.4): FI's sell takes only its own fish with a kg value | UNVERIFIED |
| L12 | buy a merchant weapon -> salvage -> sell materials | salvage gives part of the materials, never coins (B:8124); a Lv-10 weapon 15.5k vs a few bars | closed |
| L13 | buy a merchant weapon -> sell on the AH | player-to-player: no coins are created (fees burned) | not a loop |
| L14 | coins -> Bazaar goods before a rebirth -> sell after | -18 % round trip; Skyy allowed it (Q15 2026-10-13) | not a loop |
| L15 | /pay or AH between own profiles | blocked (`coins:fn:sameacct`, CN:1041, AU:193) | closed; SkyyEssentials /trade has no sameacct call (UNVERIFIED gap - Part 5.3) |
| L16 | Collections coin unlock (bypass) | `bypass.enabled` false (COL:2030) | closed |
| L17 | Gear re-roll -> sell | no pool item has a sell / salvage price (assert B:5310 / 5350) | closed |

Bazaar order book: orders sit strictly between market sell and buy (BZ:3877-3908), fills tax 1.25 % - no new route.

---

## Part 5 - Buy-across rules (PROPOSED; Q8, Q9, Q13)

### 5.1 The rule ("combat gear buyable (~1.5x the time of earning it), gathering gear not (only its upgrade materials)")
- **Gatherer buys combat gear:** a merchant weapon at level L costs **1.5 x 1.25 h x G(L)** = 1.875 gathering hours (1.25 h = P5: 4 bags / h, 1 in 5
  a weapon, ~1 in 4 of those worth keeping). AH prices are the players' own.
- **Fighter buys gathering materials:** one gathering hour's materials cost G x 1.1 / 0.9 = 1.22 G on the Bazaar; at 1.5x the time the fighter must
  earn 1.22 G in 1.5 h -> **a combat hour sells for 0.815 G** (Part 3.2 rule 9). P6's armor set (0.75 h of gathering) = 1.1 h of fighting.
- **Gathering gear is never for sale:** lifelong tools are never dropped / sold (VERIFIED B:1056); Merchants sell weapons only (ME tables); the
  Bazaar has no gear; NEW: the AH refuses gathering armor (Mining / Foraging / Farming / Fishing armor ids = TT GA_IDS + MINING_ARMOR + lifelong
  ids, built in like the bag block; row `blockGatheringGear` true; Q9). Direct /trade stays allowed (co-op friends) [Q9 default].
- **Bought items never give progress:** collections count only breaks / F-harvest / F-pickup (COL:753-770), skill XP only gathering; so buying
  across speeds up GEAR, never levels or unlocks (Economy-Audit R3 check). Smithing XP from smelting bought ore stays (a coin -> XP route, like
  SkyBlock).

### 5.2 Between zones (DERIVED)
Buying AHEAD costs ~5-7x the time (a Zone 1 player pays 5.2 h of income for one Zone 2 gathering hour of materials) and tier-ups stay level-gated
(SkyyGear tier gate). Buying BEHIND is cheap on purpose (a Zone 3 player buys a Zone 1 hour in minutes) - Skyy's "level the others when they slow
you down": the materials come cheap, the levels and collections still need the gathering.

### 5.3 Merchants (SkyyMerchants 0.1.7)
Today (VERIFIED LIVE config + ME:196): zone bands `zone1 1-20, zone2 20-30, zone3 30-45, zone4 45-60` = the OLD mob bands (Level-Bands-20 moved
zones to 20 levels: TT ZONE_TOPS 20 / 40 / 60 / 80 / 100); 44 `weapon.<id>=Zones/Price/Stock` rows at 2,000-3,000 (Zone 1) ... 45,000 (Zone 4);
Mithril weapons on zones 3-4 and Onyxium on 4 although Mithril is T13 (Lv 80, Zone 5) and Adamantite T10 (Lv 60, Zone 4) on the 15-step ladder;
fallback = median table price, else 150 x level (ME:2189).
PROPOSED: bands `1-20 / 20-40 / 40-60 / 60-80` (+ `zone5 default/Env_Zone5/80-100` when that environment exists - UNVERIFIED); each weapon's
zones = the zone of its metal's band (TT `tier_for_level` / METAL_BANDS); price = `p7_merchant_price(item level)` rounded:

| Item level | 8 | 10 | 15 | 20 | 25 | 30 | 40 | 48 | 55 | 60 | 68 | 80 | 88 | 95 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Price | 13k | 15.5k | 23k | 35k | 52.5k | 79.5k | 210k | 465k | 770k | 1.06M | 1.76M | 3.77M | 6.28M | 9.8M | 13.5M |

Row `price.hours` (dec, default 1.875) x curve x G at Lv 10 replaces the per-row price when a row still holds its 0.1.6 default; fallback
weapons use the same formula (not 150 x level). Merchant prices do not grow per rebirth (Skyy "No scaling").

---

## Part 6 - Coin sinks (PROPOSED; Q10, Q12, Q14; "Even mix")

### 6.1 Today (VERIFIED)
Gear (B:2946 / 3387 / 2948): `cost.reforge.<r>` base,perLevel normal 250,0 ... mythic 10000,0 (P5 adds perLevel 10 ... 400); `cost.levelUp.<r>`
normal 100,20 ... mythic 4000,800 (cap 6, mythic 2); `cost.identify.<r>` normal 50,5 ... mythic 2500,150; `lifelong.resetCoins` 5000 x points x
(resets + 1) (B:7928). Trees (TR:3704 / 4743 / 4773): `respec.perLevel` 100 x level x n (n <= 5, first per run free), class respec 100 x level.
Vault 50k + 25k a page (LOCKED). Shards (H:694 / 872 / 876 / 881 / 949-952): storage 5k / 25k / 100k / 400k, compactor 50k / 250k, compressor 25k /
100k / 400k, grow 5k / 20k, bench 25k / 100k / 400k. AH (AU:963-976, LIVE = defaults, LOCKED): listing 1 / 2 / 2.5 %, durations 20 / 45 / 100 / 350 /
x2, 1 % claim tax above 1M, fee kept on cancel. Bazaar: 10 % spread a side, 1.25 % order tax (destroyed). Death 10-25 % (Part 7). Classes switch
5,000 (dormant, ALLOW_SWITCH False). No coin cost: Accessories, Pets, Sacks, Wardrobe, Cooking, Islands, Exploration, Essentials (VERIFIED by the audit
grep). Linear-in-level costs are 8 % of an hour at Lv 10 and 0.3 % at Lv 90 - sinks vanish late.

### 6.2 THE RULE: every coin cost = hours of income at your level (base at Lv 10 x curve)

| Sink (mod, row) | Hours of income | Lv-10 base (normal / unique / rare / legendary / fabled / mythic / set / untiered) | Rare at Lv 10 / 50 / 90 |
|---|---|---|---|
| Reforge (Gear `cost.reforge.<r>`) | 0.025 h x rarity factor 1 / 1.5 / 2 / 3 / 4 / 6 / 3 / 4 | 210 / 310 / 420 / 630 / 830 / 1300 / 630 / 830 | 420 / 15.5k / 195k |
| Level-up, each +1 (Gear `cost.levelUp.<r>`) | 0.01 h x factor | 80 / 120 / 170 / 250 / 330 / 500 / 250 / 330 | 170 / 6.1k / 77.5k |
| Identify (Gear `cost.identify.<r>`) | 0.005 h x factor | 40 / 60 / 80 / 120 / 170 / 250 / 120 / 170 | 80 / 3.1k / 39k |
| Tree respec, n-th paid (Trees `respec.base`, class respec too) | 0.25 h x n | 2,100 x n | 2.1k / 76.5k / 970k (n 1) |
| Lifelong points reset (Gear `lifelong.resetCoins`) | unchanged 5,000 x points x (resets + 1) | (per point; points scale with level already) | - |
| Shard upgrades (Shards rows) | 1 h of the zone the upgrade belongs to | storage II-V 43.5k / 305k / 1.085M / 3.88M; compactor I / II 43.5k / 1.085M; compressor I-III 43.5k / 305k / 1.085M; grow M / L 8.3k / 43.5k; bench II-IV 43.5k / 305k / 1.085M | - |
| Merchant weapon (Part 5.3) | 1.875 h of G | 15.5k at Lv 10 | 15.5k / 565k / 7.1M |
| Vault pages | LOCKED 50k + 25k (Skyy) | = 6 h of Zone 1 ... 0.2 h of Zone 3 | - |
| AH / Bazaar fees | LOCKED / unchanged (they are % of trade) | - | - |

Rows store the Lv-10 base; the cost = base x `coins:fn:curve(item level / tree level)`, rounded like p7_round (10 / 100 / 500 / 5,000). Gear row
format stays "base,perLevel" with perLevel 0 and a NEW bool `cost.curve` (true; false = the old linear formula). Which zone a shard upgrade
belongs to = the tier of the Enchanted item it also costs (the Shards builder reads it; the table above is the default mapping).

### 6.3 Size against income (DERIVED)
"Upgrade everything" player per zone (3 tiers x 5 items x [identify + 6 level-ups + 3 reforges] at Rare): **4.2 h of income = 35 / 30 / 30 / 26 / 21
%** of Zones 1-5 (+ ~1-3 h of shard upgrades and a respec) = about **one third** = Skyy's "upgrades" share. Bazaar buy-across (5.1) is the second
third for a player who buys one skill's materials. The **cosmetic third does not exist yet** (Wardrobe has no coin prices; The Tab is a design,
research/cloud/Tab-Economy.md) - Q14 queues it after P8 (Skyy economy.md:142 "Yes, after rebirth R3").

---

## Part 7 - Death coin loss (SkyyCoins 0.1.10; Q7)

### 7.1 Today (VERIFIED CN:1138-1204)
On any death (DeathComponent appears; PvP / void / fall included): pct = penaltyMin + random(0..max-min), LIVE 10 / 25; loss = floor(purse x pct /
100), purse only (bank untouched), coins deleted (no killer / pool), no cap, once per death; `/deathpenalty` command (CN:1531-1589); **no Server
Setup row** (COINS_ROWS CN:1040 has only blockSameAccount + sounds). SkyyIslands has no coin logic on death (respawn only, IS 0.5.23).

### 7.2 PROPOSED
- `penaltyMin` / `penaltyMax` **5 / 5** (Skyy "~5 %"); one-time migration of the two LIVE lines only while they still read 10 / 25.
- NEW `penalty.safeWorlds` (text, world-name prefixes, default `skyy-island-,skyy-shard-`): no loss there (your own island and shard worlds -
  the tutorial camp / Shardkeeper deaths cost nothing). The hub / zone worlds are NOT safe (Zone 1 = the hub world, IS:157).
- NEW Server Setup rows (Coins -> Death): Coin loss on death min % / max % (int 0-100), Safe worlds (text), so it is editable in game
  (PROJECT-RULES 4); `/deathpenalty` keeps working and writes the same rows.
- The death chat line names the amount and "coins in the bank are safe" (UNVERIFIED wording today).
- Size (DERIVED): a 2-hour purse loses 10 % of an hour per death (Zone 1 ~420 coins ... Zone 5 ~195k); at ~0.25 deaths per played hour (GUESS)
  ~2.5 % of income - a nudge to bank, not a sink.

---

## Part 8 - Idle shard production vs the targets (DERIVED; Q11 - changes P6 Part 7.2)

Shards produce lazily: made = elapsed x rate, elapsed at most `shard.maxOfflineSec` 259,200 s = 3 days between menu visits (VERIFIED H:285-287,
899-900, 1240); every skill has shards (storage costs Enchanted Wheat / Cobblestone / Oak, H:946), plus the Time Compressor multiplier.
P6 Q13 proposed Totem I-V = 20 / 40 / 60 / 80 / 100 % of an active farming hour of its zone. DERIVED totals (coins per played hour vs target):

| Totems | Zone 1 | Zone 2 | Zone 3 | Zone 4 | Zone 5 |
|---|---|---|---|---|---|
| none | x1.04 | x1.03 | x1.01 | x1.01 | x0.99 |
| P6: 20-100 %, online only | x1.23 | x1.42 | x1.60 | x1.79 | x1.97 |
| P6 + offline: a 2 h a day player banks 22 h more a day | +11x a day at Totem V | | | | |
| **P7: 3 / 6 / 9 / 12 / 15 %**, `shard.maxOfflineSec` 43,200 (12 h) | x1.07 | x1.09 | x1.10 | x1.13 | x1.14 |

PROPOSED (Q11): the totem shares 3 / 6 / 9 / 12 / 15 % of an active hour (the Shards builder scales P6's measured `totem.rate1..5` by 0.15; same for
the mining / foraging shard producers if the builder finds they exceed the same share), `shard.maxOfflineSec` 259200 -> **43200**, the Time
Compressor counted inside the share (the share is measured WITH compressor III). Reading of Skyy's "late game can be 100% idle": at Totem V your
whole farming share (10 % of play) runs by itself (15 % of an active hour), so you never have to farm by hand; a 2 h a day player still gets about
as much from shards as from that day's gathering (12 h x 15 % = 1.8 G vs 1.6 G).

---

## Part 9 - Files, keys, Server Setup rows, migrations, checks

One FULL round (coins / economy, saved-data migrations, several mods). Build -> adversarial review (lenses: money loops; migrations on hand-edited
files; coins created or lost twice; buy-across numbers; Server Setup rows) -> fix -> crosscheck -> pin -> deploy. Two groups (the P7b mods are also
built by P8 - use the next free version and never build the same mod in parallel):
- **P7a** (core, together): SkyyCoins (curve + death), SkyyBazaar (prices), SkyyMerchants, SkyyAuctions, SkyyGear (sinks), SkyyCollections (tier coins).
- **P7b** (after P8a-d or folded into them): SkyySkills (level coins), SkyyTrees (respec + Pocket Change), SkyyExploration (luggage), SkyyShards (costs +
  idle cap).
Go-together: Coins 0.1.10 first (the curve); every curve reader falls back to its built-in copy, so no FLOOR - but Bazaar 0.2.1 + Collections 0.2.32 +
Skills (level coins) should pin TOGETHER (half of the new income without the other half overshoots / undershoots the targets; comment in
tools/deploy_set.py). Bazaar rollback to 0.2.0 = the migrated prices stay in products.properties (0.2.0 reads them; loop-safe because 0.2.1's build
proved them) - Undo in Server Setup -> Changes restores the old ones.

### 9.1 Versions + patches (derive from the SET pin; new patch script each; never edit generated scripts)

| Mod | SET pin -> P7 | Pin about to change? | Patch | Changes | Anchors to grep |
|---|---|---|---|---|---|
| SkyyCoins | 0.1.9 -> **0.1.10** | no | `tools/coins_0_1_10_patch.py` (or the mod's own pattern - read the header) | 1.3 `coins.curve` + `coins:fn:curve`; 7.2 death rows, safe worlds, migration | `CoinConfig.load` / `CoinTask.run` CN:1138-1204, `COINS_ROWS` CN:1040, `/deathpenalty` CN:1531, `starterK` CN:837 |
| SkyyBazaar | 0.2.0 -> **0.2.1** | no | `tools/bazaar_0_2_1_patch.py` | 3.2 P7 price table (`P7_LADDER` replaces `TIER_LADDER` / `ladder3` results; build computes from the 9.6 functions), stone 2.25, OLD_0113 floor dropped for logs, Combat re-anchor, `impactCoins` 22,500, migration `migrate021`, all loop checks re-run | `TIER_LADDER` BZ:2439, `ladder3` BZ:2620, `LADDER3` BZ:2635, `OLD_0113` BZ:2518, `SAPLING_X` BZ:2536, `SCALE_X` BZ:2584, `IMPACT_DEF` BZ:2597, `PRICE_0122` BZ:2617-2665, `SELL_CAP` BZ:2810, `_fixes` BZ:2882, `Catalog.migrate122p` BZ:5544 (clone), call BZ:11346, `CFG_ROWS` BZ:3909 |
| SkyyMerchants | 0.1.6 -> **0.1.7** | no | `tools/merchants_0_1_7_patch.py` | 5.3 zone bands, weapon zones by metal band, `price.hours`, fallback formula, migration | `ZONES` ME:196, zone tables ME:221+, fallback ME:2189, `CFG.emit` ME:1419 |
| SkyyAuctions | 0.1.14 -> **0.1.15** | no | `tools/auctions_0_1_15_patch.py` | 5.1 `blockGatheringGear` (built-in id list from TT at build time) | `AhCfg.BAG_REASON` / built-in blocked AU:48-53, rows AU:963-976 |
| SkyyGear | 0.3.36 (P6, building) -> **0.3.37** | YES: 0.3.35 (P5) and 0.3.36 (P6) first | `tools/gear_0_3_37_patch.py` reading build_skyygear_0.3.36.py | 6.2 `cost.curve` + the 24 cost rows' Lv-10 bases; curve reader | `cost.reforge` B:2946, `cost.levelUp` B:3387, `cost.identify` B:2948, P5's reforge perLevel lines, `migrateP4` B:15512 (clone `migrateP7`) |
| SkyyCollections | 0.2.31 (P6, building) -> **0.2.32** | YES: 0.2.31 (P6) first | `tools/collections_0_2_32_patch.py` | 2.2 `tier.coinsByTier` + curve reader | `TIER_COINS21` / `tier.coins` COL:1210-1231, `CollCoinMig` COL:2276, tier pay loop near COL:5099 |
| SkyySkills | 0.4.58 -> next free (**0.4.61** if P8a / P8c take 0.4.59-0.4.60) | YES (P8) | `tools/skills_0_4_6x_patch.py` | 2.1 `levelCoins` | `coinsPerLevel` S:2417 / 9375 / 21597, `rebirth.coinFactor` S:2418 |
| SkyyTrees | 0.4.5 (P5) -> next free (**0.4.9** if P8b-d take 0.4.6-0.4.8) | YES (P5, P8) | `tools/trees_0_4_x_patch.py` | 6.2 `respec.base` (+ class), 2.3 `pocket.coinsLv10` | `respec.perLevel` TR:3704 / 4743, `class.respec.perLevel` TR:4773, MCoins / FCoins TR:2126 / 2145 |
| SkyyExploration | 0.3.2 -> **0.3.3** (or next after P8d) | maybe (P8d) | `tools/exploration_0_3_3_patch.py` | 2.3 `coinZoneMult` 5 entries + airdrop factor | `luggage.coin*` EX:1367-1373, airdrop rows |
| SkyyShards | 0.4.4 (P6, building) -> **0.4.5** | YES: 0.4.4 (P6) first | `tools/shards_0_4_5_patch.py` | 6.2 coin costs, 8 idle cap (`totem.rate1..5` x 0.15 of P6's, `shard.maxOfflineSec` 43200) | `RATE_DEF` H:650, `CMP_COINS_DEF` H:872, `TC_COINS_DEF` H:876, storage H:881, grow H:949-952, bench H:694, `shard.maxOfflineSec` H:899 / 1240 / 1506 |
| SkyyIslands | 0.5.24 (no build) | - | - | death lives in SkyyCoins; Islands' world prefixes are the safe list | IS:967 `skyy-island-<key>` |
| SkyyBank / SkyyVault / SkyyQuests / SkyyFishing / SkyyCooking | no build | Cooking 0.1.16 / 0.1.17 being built by P5 / P6 (not touched here) | - | Q15 bank stays; vault LOCKED; quests / fishing unchanged | - |

### 9.2 Server Setup rows (tools/skyycfg.py, KEEP=10; Menu-Pattern pages; times in seconds)

| Mod -> page | Row (key) | Type / range | Default |
|---|---|---|---|
| Coins -> Coin curve | Coin curve by level (`coins.curve`) | text "level:factor" | 1.3 |
| Coins -> Death | Coin loss on death, min % / max % (`penaltyMin` / `penaltyMax`) | int 0-100 | 5 / 5 |
| Coins -> Death | No coin loss in worlds starting with (`penalty.safeWorlds`) | text | skyy-island-,skyy-shard- |
| Bazaar -> Prices | Market move size (existing `impactCoins`) | dec | 22500 |
| Bazaar -> Prices | Combat drop value per kill, Zone 1 (`price.combatKill`) - the anchor of rule 9 | dec | 44 |
| Merchants -> Prices | Weapon price in gathering hours (`price.hours`) | dec 0.1-20 | 1.875 |
| Merchants -> Zones | zone bands (existing `zone.<id>`) | text | 1-20 / 20-40 / 40-60 / 60-80 (+80-100) |
| Auctions -> Rules | No gathering armor / tools on the AH (`blockGatheringGear`) | bool | true |
| Gear -> Costs | Costs follow the coin curve (`cost.curve`) + the 24 cost rows (existing) | bool / text | true / 6.2 |
| Collections -> Rewards | Tier coins grow with the item tier (`tier.coinsByTier`) | bool | true |
| Skills -> General | Level-up coins by level (`levelCoins`) | text "level:coins" | 2.1 |
| Trees -> Respec | Respec cost at Lv 10, per paid respec (`respec.base`, `class.respec.base`) | int coins | 2100 / 2100 |
| Trees -> Nodes | Pocket Change coins per proc at Lv 10 (`pocket.coinsLv10`) | int | 14 |
| Exploration -> Luggage | Coin factor per zone (existing `luggage.coinZoneMult`), airdrop follows zone (`airdrop.zoneMult`) | text / bool | 1,5.2,36.8,130,466 / true |
| Shards -> Upgrades | the 14 coin rows (existing) | int | 6.2 |
| Shards -> Production | Totem speed per tier (existing `totem.rate1..5`), Longest production between visits (existing `shard.maxOfflineSec`) | dec / int s | 0.15 x P6 / 43200 |

### 9.3 One-time migrations (PROJECT-RULES 4; clone the reviewed kits: Bazaar `Catalog.migrate122p`, Gear `migrateP4`, Collections `CollCoinMig`, Shards' newest, Skills' newest P-mig)
- Only lines still holding the EXACT previous default change (a list / table text only when its whole old default matches); a hand-edited value
  is kept + one INFO line; History copy verified first (Bazaar: `config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak`, others their kit's
  History); one config-changes.log / trades.log PRICE line each (Undo in Server Setup -> Changes); bytes + line endings kept (Coins' and Bazaar
  market.properties are java.util.Properties files with a date header - edit the lines in place, never re-store the file); a java.util.Properties check that
  only the planned keys differ; run-once marker written LAST (`Balance P7 economy (SkyyCoins 0.1.10)` / `(SkyyBazaar 0.2.1)` = `migrated.0.2.1` in
  pricing.properties / ...); a fresh file carries it; new keys appended (absent = default).
- Bazaar: every FIXED products.properties line whose base equals its 0.2.0 default -> the P7 base (AUTO lines recompute; `mode.<id>=fixed` lines an
  admin set are kept); market.properties `impactCoins` 45000 -> 22500 only if 45000. LIVE check: products.properties has 549 lines (copy to scratch,
  count moved / kept).
- Coins: `penaltyMin=10` + `penaltyMax=25` -> 5 / 5 only if BOTH still read 10 / 25 (a /deathpenalty-set pair stays).
- Merchants: the 4 `zone.*` lines and every `weapon.*` line still at its 0.1.6 default (zones + price); LIVE file is the 0.1.5 header but the same
  values (check each line).
- Gear: the 24 `cost.*.<r>` lines at their 0.3.36 defaults -> "<P7 base>,0"; `cost.curve=true` appended. Collections / Skills / Exploration / Trees /
  Shards: their listed rows at the previous default; NEW keys appended. **Skills:** if `coinsPerLevel` is not 100 (hand-edited), write `levelCoins=`
  (empty = keep the admin's linear rule) + INFO. **Collections:** if `tier.coins` is not the 0.2.21 default, `tier.coinsByTier=false` + INFO.
- **Saved data:** nothing rewritten. Purses, bank, AH listings, Bazaar orders and escrow stay as they are (an open order keeps its own price; it may
  now sit outside the new market band - the 0.2.0 rule "orders strictly between S and B" is checked on placing only: harness 9.4).
- Copy the live files to `tools/dev/scratch/p7b/` and run each migration in the harness there (LIVE check).

### 9.4 Harness checks (each mod's bare-JVM test, -Xverify:all, then all jars in one JVM)
1. Coins: `coins:fn:curve` returns 1.0 at 10, 466 at 90, interpolates log-linear (Lv 44 = sqrt(13.8 x 30.3) +-1 %), clamps 0 / 200; bad text -> WARN
   + default; death at 5 %: purse 1,000 -> 950, bank unchanged; a death in `skyy-island-x` / `skyy-shard-y` -> no loss; migration 10 / 25 -> 5 / 5,
   7 / 12 kept.
2. Bazaar: the build prints table 3.3 and the per-zone hour table 3.4 and FAILS when a zone's skill ratio leaves 0.85-1.15 or a family breaks the
   1.2x step / the floor; `check_assets` + `loop_check` (premium 0..22) + SET scan + selftest end with 0 loops on the new table; every product
   bought and sold once at f = 1 (no sell above buy); an order resting outside the new band still fills / cancels / claims correctly; migration on
   fresh / LIVE copy / hand-edited / half-migrated (marker last).
3. Merchants: zone of Weapon_Sword_Iron (T2) = 1, Mithril = 5 (or 4 if no Zone 5 environment), price at Lv 10 15.5k, fallback weapon uses the formula.
4. Auctions: listing a Mining / Foraging / Farming / Fishing armor piece or a lifelong tool -> refused with the reason text; a combat weapon lists.
5. Gear: reforge Rare at Lv 10 = 420, Lv 50 15.5k (+-1 rounding step), `cost.curve` false = the 0.3.36 linear numbers; level-up cap rules unchanged.
6. Collections: Copper V = round(400 x 0.476) = 190, Titanium V 164k, untiered = 400; tiers already paid stay paid (no second payment).
7. Skills / Trees / Exploration / Shards: their row values; Pocket Change Lv 90 proc 6,300; shard production over 24 h offline counts 12 h.
8. Fishing (no build, crosscheck only): FI's sell refuses an item without SkyyFishing kg metadata (L11).
9. Crosscheck: no lang key written twice (`tools/ci/langdup.py`), tier tags for any new id (none expected), every curve reader's built-in copy =
   SkyyCoins' default text.

### 9.5 Model check (DERIVED - the numbers hit the targets)

| Target (source) | Today (model) | P7 | OK |
|---|---|---|---|
| Coins at zone end 10k / 500k / 10M x K (economy.md:162 Q18, Q1) | 136k / 1.2M / - (targets.md 3) | x1.04 / x1.03 / x1.01 / x1.01 / x0.99 of target (Zones 1-5, no totems) | yes |
| Gathering skills equal per zone (skills.md:187 Q4), 0.85-1.15 | Mining 1.5-6x the others | 0.98-1.03 every zone | yes (per tier Mining +-20-42 % on ore / alloy tiers) |
| Coins rise with zone / level ("further you level it") | yes, uneven | G x5.2 / x7.1 / x3.5 / x3.6 per zone; zone top tier 2.5-4x its bottom | yes |
| Prices by tier, a clear step (economy.md:131) | x2 a step on the old ladder | >= 1.2x per tier, every family (crops per harvest) | yes |
| Nothing sells under 2 (economy.md:130 / 134) | yes | yes (stone exactly 2.0) | yes |
| No money loop | 0 loops (0.2.0 build) | L1-L17 all negative / closed; the 0.2.1 build re-proves | yes (build) |
| Sinks even mix (Q19) | sinks 0.3-8 % of an hour, vanish late | upgrades 21-35 % of zone coins, Bazaar buy-across ~1/3, cosmetics = Q14 | 2 of 3 (cosmetics later) |
| Buy-across ~1.5x (Q20) | merchant weapon = 0.3 h (Zone 1) | 1.875 h gather -> weapon; 1.5 h fight -> an hour of materials | yes (combat per-kill value UNVERIFIED) |
| Death small, bank safe (skills.md:189 Q9) | 10-25 % | 5 %, bank + island / shards safe | yes |
| Idle stays secondary (P6 7.2 vs Q18) | P6 x1.23-1.97 | x1.07-1.14 | yes (Q11) |

### 9.6 balance_model.py (the P7 builder adds `--econ`, AFTER the P5 / P6 commits - never in parallel with another builder on that file)
Port from the scratch file (deleted with tools/dev/scratch/p7spec/; rebuild from this spec): tables `P7_K`, `P7_END`, `P7_ZONE_H`, `P7_MID_LV`,
`P7_MID_T`, `P7_D` (= P6's `p6_drops`, use it once ported), `P7_RATE`, `P7_SELL`, `P7_FLOOR`, `P7_STONE_BASE`, `P7_STEP_MIN`, `P7_ORE_T`, `P7_ORE_NAME`,
`P7_CROP_Q`, `P7_CROP_T`, `P7_SHARE`, `P7_COMBAT_X`, `P7_BUDGET`, `TIER_COINS`, `P7_COLL_PER_ZONE`, `P7_GEAR_H`, `P7_RARITY_X`, `P7_RESPEC_H`,
`P7_WEAPON_EARN_H`, `P7_BUY_ACROSS`; functions `p7_target_h(z)`, `p7_log_interp(points, x)`, `p7_curve_points()`, `p7_curve(level)`,
`p7_curve_text()`, `p7_G_mid(z)`, `p7_G(t, corr)`, `p7_prices(corr)` (ore / log / crop bases with the 1.2x step and the floor), `p7_hour(skill, t,
prices)`, `p7_zone_avg(skill, z, prices)`, `p7_fit(iters)`, `p7_levelups_per_zone()` (from `simulate_today`), `p7_level_coins(L, ups)`,
`p7_coll_scale()`, `p7_H_at(L)`, `p7_G_lv(L)`, `p7_gear_cost(kind, rarity, L)`, `p7_gear_base(kind, rarity)`, `p7_merchant_price(L)`, `p7_round(x)`,
`p7_loops(prices)`, `p7_totals(coll_scale, idle)`. Hook into `build()` section 3: "Coins" uses `P7_END` / `p7_totals` instead of `COIN_END` /
`coins_per_hour` (keep `--before` = today's); `--econ` writes "### 9. Economy" (tables 1.2, 3.3, 3.4, 6.2, 8) into research/balance/targets.md;
`--check` exits 1 when a zone's skill ratio leaves 0.85-1.15, a total leaves 0.85-1.15, or a loop margin is >= 0. The Bazaar build imports
nothing from the model (it re-computes the same table and asserts it against 3.3 +-1 rounding step).

### 9.7 In-game test steps (TEST-CHECKLIST after deploy)
1. `/bazaar` Mining: Copper Ore buys ~13 / sells ~10.8, Iron ~16 / ~13, Cobblestone sells 2; Foraging: Oak sells ~7.6; Farming: Wheat sells ~4,
   Corn ~4 (cheaper per item - 3 a harvest); Enchanted Copper ~1,440.
2. Mine for 10 min in Zone 1 with your normal kit, SELL MINING: about 1,400 coins (an hour ~8k). Do the same 10 min of chopping and of farming:
   all three within ~15 % of each other.
3. Server Setup -> Coins shows the coin curve, Death min / max 5 / 5 and Safe worlds; Server Setup -> Changes lists every migrated line with Undo.
4. Carry 10,000 coins, die to a mob in Zone 1: lose 500, chat says the bank is safe. Die on your island: lose nothing.
5. Find a Traveling Merchant in Zone 1: weapons ~13-23k; Zone 2 ~35-80k; no Mithril weapon before Zone 5.
6. Fight Zone 1 mobs for 10 min, SELL COMBAT: about 1,100 coins (0.8 of the gathering 10 min) - note the number (it calibrates `price.combatKill`).
7. Reforge a Rare Lv 10 weapon: 420 coins; a level-up 170; respec a tree the second time: 2,100 x 2.
8. Fish for 10 min and sell: note the coins (fishing target ~ a gathering 10 min, not tuned yet).
9. Level a skill from 9 to 10: +60 coins (was 1,000); finish a Copper collection tier V: +190.
10. `/ah` Create with a Mining armor piece: refused ("gathering gear is not for sale"); a sword lists.
11. Farming shard after a night away: shows at most 12 h of production.

### 9.8 UNVERIFIED
Every rate (P6's 225 ore / 400 logs / 500 harvests an hour, 900 blocks, swing / walk) and the Fortune on stone in practice; combat drops per kill
and which mobs a zone spawns (rule 9 needs the in-game number, step 6); fish per hour and value; Tomato / Chilli / Mushroom harvest q (assumed 1);
gem tiers; whether any cooked dish is a Bazaar product (L10); whether FI's sell accepts Bazaar-bought vanilla fish (L11); SkyyEssentials /trade
between own profiles (L15 gap); whether `luggage.coinZoneMult` reads a 5th entry; whether `Env_Zone5` exists for a 5th merchant; deaths per hour;
the death chat line; the level-up count beyond Zone 2 (the sim stops at cap 50 - Zones 3-5 assume Zone 1's 108 a zone); the 13 collections a
zone; shard producers other than totems (mining / foraging) vs the 15 % share; how The Tab / cosmetics will be priced (Q14).

---

## Questions for Skyy (each with today's default in [brackets])

1. **Coin unit x10: end of Zone 1 / 3 / 5 = 100k / 5M / 100M** (your 10k / 500k / 10M can't hold with the 2-coin minimum sell and P5's Fortune -
   Zone 1 stone alone pays ~3k an hour)? [x10] (alternative: drop the minimum sell for stone and lower ones to 1 coin - still ~2x over)
2. **Re-price every gathered item by tier so all skills earn the same per hour** (Zone 1 prices about halve, late ores ~1/5; each tier sells for at
   least 1.2x the one below; rare woods lose their old premium and price by their tier)? [yes]
3. **Crops priced per harvest** (Corn / Potato / Onion give 3 a harvest, so each sells for less than a 1-a-harvest crop of the tier below)? [per harvest]
4. **All plain stone sells at the 2-coin minimum** (Cobblestone 4.5 -> 2.25 base)? [yes]
5. **Level-up coins follow the coin curve** (Lv 10 = 60, Lv 50 = 2,800, Lv 90 = 50k; today 100 x level)? [yes]
6. **Collection tier coins grow with the item's tier** (Copper V 190, Chromium V 12k, Titanium V 164k)? [yes]
7. **Death: lose 5 % of carried coins, bank safe, nothing lost on your own island or in shard worlds** (Zone 1 / hub not safe)? [5 %, island + shards safe]
8. **Merchant weapons cost 1.5x the time it takes to earn one** (Zone 1 ~13-23k ... Lv 100 ~13.5M), merchant zones fixed to the 20-level bands, each
   weapon sold in its own metal's zone? [yes]
9. **Gathering armor can't be listed on the AH** (tools already can't be sold); direct /trade stays allowed? [AH blocked, /trade allowed]
10. **Reforge / level-up / identify / tree respec costs follow the coin curve** (a Rare reforge = 3 min of income at any level: 420 at Lv 10, 15.5k at
    Lv 50, 195k at Lv 90)? [yes]
11. **Idle shards capped:** Totem I-V = 3 / 6 / 9 / 12 / 15 % of an active hour (P6 said 20-100 %) and at most 12 h of production between visits (was
    3 days)? [yes] (P6's numbers would pay 1.2-2x your coin targets, much more for daily log-ins)
12. **Shard upgrades cost about 1 hour of the matching zone's income** (storage II 43.5k ... V 3.9M; today 5k ... 400k)? [yes]
13. **An hour of fighting sells for ~0.8 of a gathering hour** (Combat drops re-priced, so a fighter buys gathering materials at ~1.5x the time)? [yes]
14. **The cosmetic third of the sinks** (The Tab from research/cloud/Tab-Economy.md and Wardrobe coin prices) in a later round after P8? [later, after P8]
15. **Bank interest stays as you locked it** (2 % / 1 % / 0.5 % up to 1M / 5M / 10M - matters less now that coins are x10)? [keep] (alternative: x10 the brackets)
16. **Exploration luggage + airdrop coins follow the zone curve** (Zone 1 unchanged, Zone 4 x130)? [yes]
17. **Bazaar market move size 45,000 -> 22,500** (prices halve on the median, so the market moves the same % per sale)? [yes]
18. **Starter coins stay 10,000** (~1.2 h of Zone 1)? [keep]
19. **Eternal seeds keep your 800, doubling each crop pair**? [keep]
