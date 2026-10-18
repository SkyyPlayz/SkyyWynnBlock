"""SkyyBazaar 0.1.20 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.20.py           -> SkyyBazaar/SkyyBazaar-0.1.20.jar  (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
Check: python SkyyBazaar/test_skyybazaar_0.1.20.py
       (0.1.20 is GENERATED from build_skyybazaar_0.1.19.py by tools/bazaar_0_1_20_patch.py - edit the patch, not this file;
       0.1.19 came from build_skyybazaar_0.1.18.py by tools/bazaar_0_1_19_patch.py;
       0.1.18 came from build_skyybazaar_0.1.17.py by tools/bazaar_0_1_18_patch.py;
       0.1.17 came from build_skyybazaar_0.1.16.py by tools/bazaar_0_1_17_patch.py;
       0.1.16 came from build_skyybazaar_0.1.15.py by tools/bazaar_0_1_16_patch.py;
       0.1.15 came from build_skyybazaar_0.1.14.py by tools/bazaar_0_1_15_patch.py;
       0.1.14 came from build_skyybazaar_0.1.13.py by tools/bazaar_0_1_14_patch.py;
       0.1.13 came from build_skyybazaar_0.1.12.py by tools/bazaar_0_1_13_patch.py;
       0.1.12 came from build_skyybazaar_0.1.11.py by tools/bazaar_0_1_12_patch.py;
       0.1.11 came from build_skyybazaar_0.1.10.py by tools/bazaar_0_1_11_patch.py; 0.1.10 came
       from 0.1.9 by tools/bazaar_0_1_10_patch.py; 0.1.9 came
       from 0.1.8 by tools/bazaar_0_1_9_patch.py; 0.1.8 came
       from 0.1.7 by tools/bazaar_0_1_8_patch.py, 0.1.7 from 0.1.6, 0.1.6 from 0.1.5, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from
       0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

0.1.20 (2026-10-17) = round ores01 (research/Zone-Ores-Alloys-Spec.md sections 3 + 5 + 7 B5), the SkyyBazaar half. Skyy 2026-10-17: "Yes -
start the zone ores + alloys + Furnace Charm round right after the current set deploys." + popup "Yes, build with defaults (Recommended)".
  A. THE ZONE METALS ARE PRODUCTS (ids FINAL as in the spec; SkyyWorldGen 0.7.3 B1 makes the items - this build does NOT need that jar: the
     ids, names and recipes below are the spec's, injected as VIRTUAL items / recipes next to the Enchanted ones, so the bag guard, every
     loop check and the SET recipe scan see them; a SkyyWorldGen-0.7.3+ jar in the folder is only CHECKED against them, see ZONE_JAR):
       raw ores (Mining tab, fixed base = the zone partner's price, tools/tier_tags.py ore ladder T4 48 / T5 144 / T6 480 / T7 1440):
         Ore_Lead_SkyWynn 48, Ore_Chromium_SkyWynn 144, Ore_Slag_SkyWynn 480, Ore_Titanium_SkyWynn 1440 (each x the 0.1.15 SCALE like every
         fixed price); placed right after their zone partner (Lead after Thorium, Chromium after Cobalt, Slag after Adamantite, Titanium
         after Mithril = by tier);
       ingots (Smithing tab, AUTO = 1 ore at the Furnace x (1 + premium) like every bar): Ingredient_Bar_{Lead,Chromium,Slag,Titanium}_SkyWynn
         (smelt 18 / 18 / 20 / 30 s);
       alloys (Smithing tab, AUTO): Ingredient_Bar_Dusk_SkyWynn (Thorium + Lead Ingot, 36 s), _Azurvane_ (Cobalt + Chromium, 36 s),
         _Cinder_ (Adamantite + Slag, 40 s), _Lumen_ (Mithril + Titanium, 60 s) - a 2-input recipe on the bench id "SkyyAlloy" (the /craft
         Furnace with a Furnace Charm); the build treats that bench as a Furnace (fuel + best tier time cut) so the price = the two ingots'
         RAW values + fuel for the alloy smelt, x (1 + premium); PREMIUM_BENCHES gets "SkyyAlloy".
       Vanilla Ingredient_Bar_Bronze (Copper Ingot + Iron Ingot, 24 s, the same bench) KEEPS its fixed 40 (x SCALE) price: it is not a
         processed good; the new recipe makes buy-two-ingots -> alloy -> sell pay, so Bronze gets a SELL CAP (the 0.1.14 mechanism: it
         sells for its crafting value, worked out by the sweep; buying it stays at 40).
     Enchanted rows of tools/skyyench.py added later (SkyyCollections 0.2.25: Lead / Chromium / Slag / Titanium Ingot + Charcoal) are
     listed AUTO like every other row and appended once by the same update.
  B. SAVED STATE - a ONE-TIME update at the first 0.1.20 start (Catalog.migrate120 = migrate119's exact code with its own names: NEW0120 =
     the zone metals + any Enchanted id of the live table after the 102 frozen rows, marker migrated.0.1.20, M120_LOG; runs after
     migrate119): each NEW0120 seed line is APPENDED to products.properties when no line holds that id (a hand-edited line is kept byte
     for byte; every other line, its bytes and line endings kept), a verified history copy first, trades.log gets MIGRATE-0.1.20 lines
     with the undo. NEW0119 stays what 0.1.19 appended (the 102 frozen table rows, a literal in the build, asserted against the live table).
  C. detail panel: an alloy reads "... and alloying it yourself" (was the raw bench id).
  Everything else UNCHANGED: every existing price / tab / order, the sell caps, the x4.5 scale, the Eternal seed lock, the menu page.
  ROLLBACK to 0.1.19: the NEW0120 lines stay in products.properties; 0.1.19 loads any well-formed line whose item exists, so while
  SkyyWorldGen ships the items it LISTS them as FIXED products at the seeded price (0.1.19 has no recipe for them). Clean rollback: put
  the migrate120 backup (config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak) back as products.properties and delete the
  migrated.0.1.20 lines from pricing.properties. SET rule: SkyyBazaar 0.1.20 expects SkyyWorldGen >= 0.7.3 (the items it lists; without
  them the rows are simply not shown - Catalog.usable) and SkyySacks >= 0.8.20 (the bags).

0.1.19 (2026-10-16) = round coll24, the SkyyBazaar half (SkyyCollections 0.2.24 is the other half). Skyy (docs/answered/economy.md + gear.md
2026-10-16): "lets lock the eternal seeds with the collection. give them at like collection level 3 or 4" (recorded: each crop's Eternal Seed
bag - recipe AND Bazaar buy - unlocks at that crop's collection tier 4 by default, a Server Setup row in SkyyCollections) + "there was no
need to add the enchanted essence of life. greater essence already exists and is literally the exact same thing. remove the enchanted, and
just use the vanilla version." + the queued C1 follow-ups (RESUME NEXT 0.i, research/Collections-Tools-Redesign-Spec.md): "Bazaar lists the
new Enchanted items - FIRST size the collection gifts to item value".
  A. THE ENCHANTED PRODUCTS FROM THE LIVE TABLE (tools/skyyench.py: 102 rows = the 20 + TABLE_C1's 82; Skyy_Ench_LifeEssence is RETIRED and
     never listed - its collection uses the vanilla Greater Essence of Life, Ingredient_Life_Essence_Concentrated, a product already). The
     0.1.17 freeze to TABLE_20 is lifted for the PRODUCTS: every row whose base is a Bazaar product is an AUTO processed good priced from its
     recipe (RATIO x the input's raw value x (1 + premium), the PROC path; a ResourceTypeId input - Rubble, Sand = "Sands", Crystal =
     "Crystal_Shards" - at the cheapest product of that resource type, as Rubble always was). A row whose base has NO product (EN_OFF: the
     build prints them - today only Enchanted Cactus, Plant_Cactus_1 is a SKIP rule's plant) is left off the market (no invented price; its
     item JSON is not joined either, so the bag guard does not ask for it). Tab = the item's Void category (SkyySacks 0.8.15's SackDefs.catOf
     = skyyench cat_of; C1 adds Combat + Smithing); order: Farming keeps the 0.1.15 rule (crop, Enchanted crop, seeds, Eternal seeds per
     crop by tier, the rest by tier then name - the new Enchanted crops join their crop's group); in every other tab a NEW Enchanted product
     sits right after its base (a resource type: after the last product of it), like the Enchanted Stick after the Stick. The money-loop
     checks (every recipe, premium 0 .. 22, floors 0 .. 5, vanilla + every SET jar) cover all the new rows; no existing price moves.
  B. SAVED STATE - a ONE-TIME update at the first 0.1.19 start (Catalog.migrate119 = migrate116's exact code with its own names: NEW0119 =
     every listed Enchanted id not in NEW0110 + NEW0116, marker migrated.0.1.19 in pricing.properties (kept by writeModes, read by
     loadModes), M119_LOG; runs after migrate116 while pricing.properties has migrated.0.1.4): each NEW0119 seed line is APPENDED to
     products.properties when no line holds that id (a hand-edited or present line is kept byte for byte; every other line, its bytes and
     line endings kept), a verified history copy first (config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak), trades.log gets
     MIGRATE-0.1.19 lines with the undo (delete that line, then /bazaaradmin reload; undo all = put the backup back). NEW0110 (the 19) and
     NEW0116 (["Skyy_Ench_Stick"]) stay frozen, asserted against skyyench TABLE_20 (not the live table), so migrate110 / migrate116 are
     exactly what they were. A product an admin deleted after the update is not added again (the marker).
  C. ETERNAL SEED BUY LOCK (SkyyCollections 0.2.24 bridge, KEY CONTRACT): skyy.bridge "coll:fn:eternal" = java.util.function.Function;
     apply(new Object[] { java.util.UUID player, String itemId }) -> String: "" = allowed (not a locked Eternal seed / already unlocked); a
     non-empty String = LOCKED, the text is the player-facing reason (shown on the result line, the buy refused); null = Collections cannot
     answer now -> refused "Collections are still loading - try again in a moment". The Function absent (SkyyCollections older than 0.2.24 /
     missing) = allowed (no lock exists anywhere then); any Throwable = refused + one WARN a minute. Trader.eterWhy asks it only for
     Plant_Seeds_<Crop>_Eternal ids, on every click (nothing cached); Trader.buy0 - the one core every buy path ends in (Buy 1, Buy <stack>,
     the custom amount Buy, the CONFIRM flow; the jar has no buy bridge) - refuses before any coin or item moves; the page asks it too before
     arming a CONFIRM (Buy 1 / stack) or pricing / arming the custom amount Buy, so a locked seed never shows a CONFIRM button. Selling an
     Eternal seed is never asked (allowed).
  Everything else UNCHANGED: the order book, every existing product's price / tab / order, the sell caps, the x4.5 scale, the Eternal seed
  prices of 2026-10-15, the 0.1.18 menu page (kit 1.7 hub_page, no back button), the commands, the settings.
  ROLLBACK to 0.1.18: the NEW0119 lines stay in products.properties; 0.1.18 loads any well-formed line whose item exists, so while
  SkyyCollections ships the items it LISTS them - as FIXED products at the seeded price (not in 0.1.18's processed-goods table, so they do
  not follow their base any more), at the end of their tab, and its admin / runtime loop warnings do not know their recipes. Clean rollback:
  stop the server, put the migrate119 backup (config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak) back as products.properties
  and delete the migrated.0.1.19 lines from pricing.properties (or delete the Skyy_Ench_* lines of the trades.log MIGRATE-0.1.19 list).
  The Eternal lock goes with 0.1.19 (0.1.18 sells Eternal seeds to anyone). SET rule (tools/deploy_set.py): SkyyBazaar >= 0.1.19 needs
  SkyyCollections >= 0.2.24 (coll:fn:eternal; without it nothing is locked) and SkyySacks >= 0.8.14 (the C1 Void homes; SACKS_MIN).

0.1.18 (2026-10-16) = MENU PATTERN sweep S2, the Market tab (SkyyBazaar part; SkyyAuctions 0.1.10 is the other half,
tools/auctions_0_1_10_patch.py). Skyy (docs/answered/ui.md 2026-10-16): "Double check every menu and make sure it's fully and completely
built out / designed properly in the cohesive menu system we made. I never want to have to use a back button. The menus at the top should
always be there for easy navigation." + "keep this top bar at this size consistent at the top across every menu." + "i dont mind
scrolling, but if there are only a few items try to scale them to all fit." + popups: every hub page 1600 x 980, row 2 big like Teleport.
Spec research/Menu-Pattern.md section 3 (M5: pagers -> scroll lists; rules 7 + 8); recipe tools/HUBS-CONTRACT.md 'Kit 1.7'.
  1. THE KIT 1.7 PAGE (SUI.hub_page, 1600 x 980; was the kit 1.5 hub_shell 1094 x 979): title bar | row 1 = Home + the hubs at Home's size
     | row 2 = the Market hub's tabs at Teleport's size, Market selected (HubBar.page17) | the ONE sub-tab row | the content | the footer.
     No '< Menu' (row 1 Home leads away), clicks go through HubBar.route (row 1 hub:h:<id>, row 2 hub:<tab>, the X hub:close).
  2. THE SUB-TAB ROW = the [BAZAAR] [AUCTION HOUSE] switch (kit small buttons, the open one Primary) + [CREATE BIN] [MANAGE (n)] while
     SkyyAuctions 0.1.10+ publishes ah:fn:view (the same four sub-tabs the Auction House page shows - the row never changes while you
     switch) + the purse at the row's right end. BAZAAR here answers in place; AUCTION HOUSE = ah:fn:open with the search (as 0.1.17);
     CREATE BIN / MANAGE = ah:fn:view (the AH page on that view); MANAGE without ah:fn:view runs /ah manage as the player.
  3. THE CONTENT, three columns (1552 x 676): LEFT the bag tabs as an in-page list (the open one Primary; the same tab:<i> clicks),
     SELL <tab> / SELL ALL TABS, the confirm amount (Confirm buys from [amount] Set + its note - was the footer); MIDDLE the one search of
     both markets (field, Search, Clear), the header + a count, ONE scroll list of product cells (no pages: the PREV / NEXT pager is gone;
     a short list gets bigger cells - 74 / 107 / 148 px, Skyy rule 7; a list over 180 cells shows a Show more row); RIGHT the detail well
     (456 = the kit DETAIL_W): icon + name, the price lines, Buy 1 / Buy <stack>, Sell 1 / Sell <stack> / Sell all, the custom amount
     with Buy / Sell, the limits line - or an Auction House cell's detail with OPEN IN AUCTION HOUSE (as 0.1.17).
  4. THE FOOTER: the result line (coloured by its words, as 0.1.17) + Close.
  Content, coin and item logic UNCHANGED: every 0.1.17 id / binding payload / click path (BzSent tabs, cell:<i>, buy1 ... sellalltabs,
  find / fclear, cfset, mk:ah, ahopen, the CONFIRM flow), the order book, the tier-sorted one search, bazaar:fn:open; only prev / next
  went (and "more" + "mk:bz" / "mk:create" / "mk:manage" came). The Enchanted products stay FROZEN to 0.1.16's 20 rows (TABLE_20, the
  0.1.17 freeze kept as it is). No saved-data change, no command change, no setting.
  ROLLBACK to 0.1.17: safe (no data); roll SkyyAuctions back to 0.1.9 with it (a mixed pair works, the two pages just differ in size).

0.1.17 (2026-10-16) = round hubmkt, the MARKET MERGE (SkyyBazaar part; SkyyAuctions 0.1.9 is the other half, tools/auctions_0_1_9_patch.py).
Skyy LOCKED 2026-10-10 (docs/answered/ui.md, which pages become one tab): "Bazaar + Auction House (one Market tab, one search)"; 2026-10-16
popup "HUBS: ... merge like your 10-10 pick (...; Bank+Vault, Bazaar+Auction House)?" -> "Merge now"; "menu merge first. mod compress later.";
"sort everything by tier in all shops and crafting." (the one tier table tools/tier_tags.py). This merges the PAGE, not the markets: the two
order books, every buy / sell / listing / claim path and every saved file stay exactly as 0.1.16 / SkyyAuctions 0.1.8 had them.
  A. ONE MARKET TAB: the hub tab hub:tab:market:bazaar is labelled "Market" (was "Bazaar"; id, order 10 and command /bazaar unchanged).
     SkyyAuctions 0.1.9 hides its own "Auctions" tab while this jar publishes bazaar:fn:open (so a mixed set never loses the AH tab).
  B. THE SUB-VIEW SWITCH: a new 36 px row at the top of the page body: [BAZAAR] (Primary = you are here) [AUCTION HOUSE] (Secondary) + one
     caption line. AUCTION HOUSE opens the Auction House page (SkyyAuctions' ah:fn:open, with the search text you typed, so the search follows
     you); without SkyyAuctions 0.1.9 the button is not drawn (an empty slot keeps the row's look) and the old Auctions tab is still there.
     The page grows 943 -> 979 px (MAX_PAGE_H 980: still fits 1080p); nothing else moves.
  C. ONE SEARCH: the search row now reads "Search both markets - name or item id" / "Enter finds both markets". A search lists every
     matching Bazaar product AND every matching Auction House item (ah:fn:find: the AH's own search text, each word must match; one cell per
     item id, grouped: listings, lowest Buy It Now each, the cheapest listing, ends soonest), ALL sorted by tier then name (tools/tier_tags.py
     ROWS; AH gear without a table row by its SkyyGear level band TT.tier_for_level; untiered last), the Bazaar product before the AH cell
     of the same item. Clearly labelled: an AH cell shows "AH <listings>" in its corner (Bazaar cells keep the held count), the header says
     "<n> Bazaar + <m> Auction House", and the detail well of an AH cell says "Auction House - <name>" with its Buy It Now prices and ONE
     button OPEN IN AUCTION HOUSE (opens the AH page filtered to that item id; buying happens there, through the AH's own code). An AH cell
     never selects a Bazaar product (sel stays null), so no Bazaar buy / sell button can act on it. Without SkyyAuctions 0.1.9 the search
     is the Bazaar-only search (now tier-sorted) with the old header.
  D. bazaar:fn:open (java.util.function.Function, put in setup, removed in shutdown): apply(Object[]{ UUID, String query }) opens this page
     for that player on its world thread (the caller is a page event), with that search applied when it is not empty -> Boolean.TRUE;
     FALSE when the player is not there. SkyyAuctions 0.1.9's BAZAAR button uses it (the AH search text comes along).
  No saved-data change, no command change (/bazaar, /bz open the Bazaar sub-view; /ah, /auction, /auctionhouse open the AH sub-view), no
  coin / item path change. ROLLBACK to 0.1.16: safe (memory-only bridge keys); roll SkyyAuctions back to 0.1.8 with it, or AH 0.1.9 simply
  shows its own tab again (it hides it only while bazaar:fn:open exists).

0.1.16 (2026-10-16) = round tools01 part B, the ENCHANTED STICK on the Bazaar (docs/answered/gear.md 2026-10-16 ENCHANTED STICKS). Skyy: "make
enchanted sticks too, and require them in the later tool upgrades." -> tools/skyyench.py's 20th row Skyy_Ench_Stick (100 Sticks -> 1, the
Workbench Compressing tab, SkyyCollections 0.2.20; tier tag T1) becomes a product like the other 19 Enchanted materials:
  A. PRODUCT: PRODUCTS already takes every tools/skyyench.py row ("(EN.PREFIX + key, AUTO, name)"), so the Enchanted Stick is an AUTO
     processed good priced from its recipe (100 x Ingredient_Stick at the processed-goods premium, PREMIUM_ITEMS "compressing"), bag /
     tab Foraging (EN.cat_of = SkyySacks' rule). Every loop check the build runs (sell caps, floor exemptions, buy-side raises, every
     premium, every floor 0-5, vanilla + SET jar recipes, the demand-step check, the SkyyMerchants check) sees it; the build prints its
     price. The 0.1.15 x4.5 scale table (PRICE_0115) holds FIXED prices only, so it is not in migrate114 / migrate115.
     The bag guard (every product = a Magic Bag item of SkyySacks' compiled rule): a SkyySacks jar built before the 20th row does not hold
     the Enchanted Stick yet (SkyySacks reads tools/skyyench.py at its next build, the Foraging-bag follow-up); then ONLY that id falls back
     to its table category EN.cat_of (= the rule SkyySacks will compile) and the build says so (SACKS_LATE).
  B. ORDER: in the Foraging tab's display order (0.1.15 DSP_KEY) the Enchanted Stick sits right after the Stick (Ingredient_Stick) instead
     of after the last Enchanted log (where the PRODUCTS order would put it); every other product keeps its 0.1.15 place.
  C. SAVED STATE - a ONE-TIME update at the first 0.1.16 start (Catalog.migrate116 = migrate110's exact code with its own names: NEW0116 =
     ["Skyy_Ench_Stick"], marker migrated.0.1.16 in pricing.properties (kept by writeModes, read by loadModes), M116_LOG; runs after
     migrate115 while pricing.properties has migrated.0.1.4): the product's seed line is APPENDED to products.properties when no line
     holds that id (every existing byte and line ending stays; the file's own newline style); a verified byte copy goes to config-history/
     first; trades.log gets MIGRATE-0.1.16 lines with the undo (delete that line, then /bazaaradmin reload). A fresh install seeds it
     from PRODUCTS (the update then finds it 'already' listed). NEW0110 stays EXACTLY the original 19 ids (frozen), so migrate110 is
     unchanged.
  ROLLBACK to 0.1.15: safe - 0.1.15 reads the Skyy_Ench_Stick line as an ordinary product (the item exists while SkyyCollections 0.2.20+
  is on; without it the line is an unknown item the market skips like any other). To take it off: delete that line + the migrated.0.1.16
  lines, then /bazaaradmin reload.

0.1.15 (2026-10-16) = round bz0115, the Bazaar's FARMING tab order + saplings to FORAGING (docs/answered/economy.md 2026-10-16 BAZAAR FARMING
ORDER + SAPLINGS TO FORAGING). Skyy (screenshot of Market > Bazaar > FARMING, 144 mixed products): "put crops, enchanted crops seeds and
eternal seeds per crop in that order sorted by tier. and place the saplings in foraging not farming."
  A. FARMING ORDER: one group per crop of tools/tier_tags.py CROPS (the one tier table; crops = their tool's tier); inside a group exactly
     the crop, its Enchanted crop, its seeds, its Eternal seeds (a member that is no product is skipped); groups by the crop's tier, then
     by name. Every other Farming product (hay, fruit, herbs + their seeds, mushrooms, moss, petals ...) follows the groups, by tier
     (untiered first) then name. The order is a jar table (Catalog.DSP_KEY: "<tab>|<id>" -> its place) that inCat sorts by; a product
     the table does not know (an admin's own line) keeps the old rule after it (seed order, then file order).
  B. SAPLINGS TO FORAGING: every Plant_Sapling_* product leaves the Farming tab and shows in Foraging (Catalog.MV_ID / MV_SPEC: tabsOf
     drops 'Farming' and adds 'Foraging' for them - SkyySacks' bag rule and the file's category stay as they are, so products.properties
     is NOT rewritten and a rollback to 0.1.14 just shows them in Farming again). In Foraging each sapling sits right after its tree's log
     (Wood_<tree>_Trunk), saplings without a listed log after the last log.
     ('Storm Sapling Seed Bag' = Plant_Seeds_Stamina3 is an herb seed bag, not a sapling: it stays in Farming.)
  A + B change only the listing order / tab: product ids, buy / sell and the search are untouched (the search walks the tabs, so it
  finds the saplings in Foraging).
  C. EVERY PRICE x SCALE_X, EXCEPT THE ETERNAL SEEDS (docs/answered/economy.md 2026-10-16 MINIMUM SELL PRICE = RAISE + SCALE + BAZAAR
     PRICES x SCALE). Skyy: "when i said nothing sells under 2 coins i meant raise the sell price of everything to at least 2 coins, and
     scale everything else accordingly. not remove them from the list." + popup "scale everything except the eternal seeds we set last
     night." -> SCALE_X = the floor row's default (market.minSell, 2) / the cheapest instant sell of 0.1.14 at demand 1.0 (Eternal seeds
     left out; sell caps counted), rounded UP to the next 0.5 so the prices stay round: 2 / 0.45 (Stone Rubble, base 0.5) = 4.44 -> x4.5.
     Every FIXED default price x4.5 (processed goods follow their inputs, so they move by the same factor; Enchanted = N x its base as
     before), every sell cap x4.5 (a capped product still sells for its crafting value), the demand impact (impactCoins, "coins of base
     value per 10 % move") x4.5 so a trade moves the demand exactly as much as before; the 14 Eternal seed bags keep their 2026-10-15
     prices (800 .. 51,200). The floor row stays 2 (it now only matters at low demand / a higher floor). The factor is fixed at BUILD
     time from the floor row's default: a later floor change in Server Setup does not rescale the prices.
     The build re-runs every loop check (sell caps, floor exemptions, buy-side raises worked out again on the scaled prices, every
     premium, every floor 0-5, vanilla + SET jar recipes, the demand-step check, the SkyyMerchants check) and prints the old -> new
     table (PRICE_0115) with 20 samples.
  D. SAVED STATE - a ONE-TIME update at the first 0.1.15 start (Catalog.migrate115 = migrate114's pattern, after it; marker
     migrated.0.1.15 in pricing.properties): a products.properties line whose price is still EXACTLY its 0.1.14 default gets its 0.1.15
     default (the price text only; every other byte + line ending stays); any other price (an admin's /bazaaradmin price or a hand edit)
     is KEPT and logged; market.properties' impactCoins still at the old default 10000 -> 45000 (the value text only), any other value
     kept + logged; a verified byte copy of each changed file goes to config-history/ first; trades.log gets MIGRATE-0.1.15 lines with
     each undo command. Demand factors / bought / sold counts (market.properties f.* ...) are ratios: untouched.
     migrate14 / migrate114 count a line already holding its 0.1.15 default as done (a fresh 0.1.15 install seeds the new prices).
     ROLLBACK to 0.1.14: loop-safe as it is (0.1.14 reads the x4.5 prices with its smaller sell caps = it sells capped goods for less;
     the Eternal seeds are unchanged), but the prices stay x4.5. For the old prices: stop the server, put the newest
     config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak (and ~market.properties.<stamp>.bak) back, remove the
     migrated.0.1.15 line from pricing.properties.
  E. SELL <TAB> + SELL ALL TABS (docs/answered/economy.md 2026-10-16 BAZAAR SELL PER CATEGORY + SELL ALL). Skyy (screenshot of the
     FARMING tab's red SELL INVENTORY button): "make the sell inventory button per category. so its (sell farming.) and it sells all your
     farming stuff. then add a sell all button above that." -> the tab row's button (same id #SkyyBzSellInv, same place, payload
     sellinv) reads SELL <open tab> and sells only the products of the OPEN tab (Catalog.inCat - a product listed in two tabs is sold by
     either); a new SELL ALL TABS button (#SkyyBzSellAllTabs, payload sellalltabs; 'tabs' because each product already has its own
     Sell all) sits right above it at the end of the search row (search field 420 -> 360, Search / Clear 150 -> 130, the hint now
     reads 'Enter searches every tab') and sells every product of every tab = the old Sell inventory. Both work exactly like the old Sell inventory: the same
     sources (storage + hotbar + backpack + the Void bags), the same protections inside sell0 (Void bags never sold, market:veto
     walled gear / stamped stacks never counted or taken, the market wall, profile:busy), always two clicks (preview 'sell N <tab>
     items for about C coins', then the gold Confirm sell within 10 s; the 0.3 s double-click rule; ANY other click - the other sell
     button too - disarms), each product sold through sell0 (count-verified removal, coins only for what left, a failed payment
     returns the items; demand impact per product as before) inside ONE Market lock, one result line + chat copy with the total.
     Trader.preview / preview0 / sellInventory take the tab (null = every tab); the confirm remembers which button and tab it priced.

0.1.14 (2026-10-15) = round bz0114, four of Skyy's asks for the Bazaar (docs/answered/economy.md 2026-10-15):
  A. CONFIRM BUTTON + CONFIRM AMOUNT. Skyy (screenshot: buying 5 Wheat Seed Bag (Eternal) for 205 coins, the yellow 'click Buy again
     within 10 s to confirm'): "id have the buy button change to confirm so its obvious to the player. (and in settings set a confirm
     threshold. so if the purchase is less than X (default like 3,000) so if you arnt spending much buy works first click."
     - Buy 1 / Buy <stack> / the custom Buy: a buy whose total is BELOW the player's amount goes through on the first click (capped at
       the total just worked out: Trader.buyC / buyN refuse and re-ask if the price rose in between); AT or above it the clicked button
       turns into a gold-lettered 'CONFIRM - <total> coins' button for 10 s (the result line says the same); the second click on it buys
       with the shown total as the cap (a price that rose re-asks at the new total; purse / room / profile-busy checks and the atomic
       coins + items move are buy0's, unchanged). A click on it sooner than 0.3 s after it was drawn does not count (review: a
       double-click must not confirm instantly) - it is answered and the CONFIRM stays. Any other click turns it back. When the 10 s
       run out (one delayed task on the player's world thread - BzRevert, never a periodic update) the confirm is cancelled on the
       server and the result line says so - only that LABEL is updated, so text typed in the amount / confirm / search fields is kept
       (review); the button itself turns back at the next redraw, and a click on the stale CONFIRM only asks again, it never buys.
       (Turning the button back without a redraw needs client commands no Skyy page has used yet - insertBeforeInline / remove, or
       b.set on a TextButton Text, kit probe 20.) The custom Sell (always two clicks, as before) and Sell inventory ('Confirm sell') use
       the same gold CONFIRM look, the same 0.3 s rule and the same timeout. 0 = every buy asks.
     - THE AMOUNT: per player (Skyy_SkyyBazaar/confirm.properties, uuid=coins, written only when a player sets one) - the Bazaar page's
       bottom row 'Confirm buys from [amount] Set'; a player who never set one gets Server Setup > Bazaar > 'Confirm purchases above (new
       players)' (confirm.default, default 3,000). SkyyMenu 0.3.28's settings registry only holds ON / OFF switches (settings:fn:register
       takes a Boolean default), so the NUMBER cannot live in SkyWynn Menu > Settings; the Settings page gets the switch 'Bazaar: confirm
       big buys' (bazaar.confirm, Coins & Bank tab, ON by default; OFF = buys never ask) through settings:def / settings:fn:register.
     - Bazaar buy buttons are wider (260; the three Sell buttons 162) and the custom Buy / Sell 230, so the CONFIRM text fits at 1080p.
  B. ETERNAL SEEDS. Skyy: "and instant seeds are OP id make T1 crops start at like 800 coins. cause it lasts forever." -> every Eternal
     seed bag: the first crop pair (Wheat / Lettuce, T2) 800, x2 per later pair (T3 1,600 ... T8 51,200). The vanilla Farmer's Workbench
     still makes them from cheap inputs, so their INSTANT SELL price stays at the 0.1.13 value (the recipe value): SELL_CAP below.
  C. MINIMUM SELL PRICE. Skyy: "and lets set a minimum instant sell price in the bizzar to like 2 coins." -> Server Setup > Bazaar >
     'Minimum instant sell price' (market.minSell, default 2, 0 = off, at most MINSELL_MAX): no instant sale pays less per item, at any
     demand. A product whose value (base x demand) sits under floor / (1 - spread) trades at THAT value on both sides, so its buy price
     stays (1 + s) / (1 - s) above its sell price (a 2-coin sale = a 2.44 -> 3-coin buy). Worked out over every recipe the checks know
     (vanilla + every SET jar, SkyyCollections 0.2.19's stone conversions included) at every floor 0-5: where a junk -> junk conversion
     would pay (1 cobble -> 2 rubble), the INPUTS' buy side is raised just enough (BUY_X, x1.66 for the stone family: cobble sells 2,
     buys 5); where an output's inputs are real-priced (crop -> Essence of Life, essence -> seeds / saplings, petals, wool bolt, raw
     fish) the output never takes the floor (FLOOR_EXEMPT, 21 products). The build prints both lists.
  F. DEMAND STEP CAP (found by the new buy-then-sell check): the per-unit demand step exp(ln 1.1 x base / impact) was only capped at 4,
     so a product over ~19,000 could be bought and sold straight back at a profit (0.1.13: Enchanted Adamantite 57,600 -> step 1.73,
     +26,000 coins a round trip). Market.step now also stops at 1 + 0.9 x ((1 + s) / (1 - s) - 1) = 1.2 at the 10 % spread (5 products:
     Enchanted Adamantite + the T7 / T8 Eternal seeds).
  D. PRICES BY TIER. Skyy: "and make prices all scale by tier. so T2 buy and sell is a good bit higher than T1" -> every tiered product
     (tools/tier_tags.py: ores, logs, crops, seeds, Eternal seeds; bars and Enchanted follow their inputs) takes its family's tier
     ladder (TIER_LADDER, x2 or more per tier); untiered products keep their prices. A raised product a recipe makes for less keeps its
     0.1.13 sell value (SELL_CAP: every normal + Eternal seed but Wheat / Lettuce seeds); a lowered product whose recipe would then pay
     keeps its 0.1.13 price (none needed). Logs follow the tags' forest zones, BUT (Skyy popup 2026-10-15 "Rare woods stay premium
     (Recommended)" = the 2026-10-04 lock, economy.md) where rarity and zone disagree rarity wins: no log drops below its 0.1.13 rarity
     price (Crystalwood, Fire, Frostwood (Ice), Stormbark stay 128; Azure 48, Amber 20, Apple / Windwillow / Wisteria 8).
     SAPLINGS (Skyy popup "Yes, saplings follow log tier (Recommended)"): a sapling's base = SAPLING_X (3.3) x its log's 0.1.14 base,
     rounded up to 0.5 - its buy price is about 4x what one of its logs sells for (a sapling = a few logs; a tree farm pays back over
     several harvests). Saplings the vanilla Farmer's Workbench makes from Essence of Life sell at their 0.1.13 value (SELL_CAP, so
     dropped saplings are no money printer). Spruce / Frozen Spruce have no tiered log: they keep their price.
     Side effects through AUTO prices: every cloth bolt (woven from 1 Cotton, now T7 64) 19.2 -> 76.8; Enchanted crops / logs follow
     their base.
  E. SAVED STATE: products.properties gets a ONE-TIME update at the first 0.1.14 start (Catalog.migrate114 = migrate14's pattern; marker
     migrated.0.1.14 in pricing.properties): a line whose price is still EXACTLY its 0.1.13 default gets its 0.1.14 default (the price
     text only; every other byte and line ending stays); any other price is KEPT and logged. A verified byte copy goes to config-history/
     first; trades.log gets MIGRATE-0.1.14 lines with each undo command. market.properties is never touched.
     ROLLBACK to 0.1.13 is NOT safe as it is: 0.1.13 has no sell caps, so reading 0.1.14's products.properties it would SELL the Eternal
     seeds (and the raised normal seeds / saplings) at their new base - about 21x what their recipe costs (a money loop). Before a
     rollback: stop the server, put the newest Skyy_SkyyBazaar/config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak back as
     products.properties and remove the migrated.0.1.14 line from pricing.properties; then start 0.1.13. (confirm.properties and the two
     new config rows are simply ignored by 0.1.13.)

0.1.13 (2026-10-15) = HUBS H3b, the SkyyBazaar part: the Market > Bazaar tab (research/Hubs-Spec.md 1.2 / 2 / 7; the kit skyyui 1.5 hub
contract tools/HUBS-CONTRACT.md; SkyyMenu 0.3.28 owns the hubs). Skyy 2026-10-10 (docs/answered/ui.md): picked ALL hubs ("/market hub,
/storage hub, /character hub, Accessory Bag v2, + could we tidy and simplify them any more from here?"), "can we design it all with the new
theme"; 2026-10-15 "And when are we condensing menus together?".
  1. THE TAB: the kit's HubBar in this jar (SUI.install_hub_bar); setup() puts hub:tab:market:bazaar = {"SkyyBazaar", "Bazaar", 10,
     "bazaar", BzHubOpen, null = always shown} (SUI.HUB_TABS); shutdown() removes it (HubBar.removeAll: only while the key holds OUR
     array). BzHubOpen opens the bazaar page for the UUID on the player's world thread (the bar's caller), as /bazaar does (with its
     "SkyyCoins is not loaded" chat line); FALSE (the bar then runs /bazaar) when the player / page manager is not there.
  2. THE PAGE: BzPage draws in the kit's hub_shell (Sky Window: the Market frame mood, Header + crest, '< Menu', the close X, the shared
     tab strip filled at runtime by HubBar.build), 1046 px inside as before; the "Bazaar" title bar goes. TO FIT 1080p: 0.1.12 was 955
     px high (the most is 980; the shell needs +66), so the product grid shows 3 rows of 13 = 39 products a page (was 4 rows = 52; the
     pager shows the rest) - 1094 x 943. Every other part (header, search, tabs, detail, buy / sell rows, limits, result line, footer)
     is 0.1.12's. Clicks ask HubBar.handle FIRST: the X closes, '< Menu' opens the SkyWynn Menu, the Bazaar tab itself does nothing (a
     typed amount / search stays), another tab (Auctions, Merchants) opens through its Function or command; a tab that could not open
     says so on the result line.
  3. The jar ships the kit's 59 Sky Window files (IncludesAssetPack true: Common/UI/Custom/SkyyKit/ only).
  4. No saved-data change, no price / trade / coin change, no command change. ROLLBACK to 0.1.12: safe (the tab key is memory only).

  Review fix (2026-10-15): every hub click the page handles is answered (hubAck: the hub title set to itself, only while this page is
     still the open page) - the own tab, '< Menu', a command fallback and a Function that answered TRUE without opening a page no
     longer leave the client on "Loading..." (the SkyyExploration 0.2.3 / SkyyBank 0.1.6 rule: every click is answered).

0.1.12 (2026-10-14) = SOUND PASS ROUND 2, the SkyyBazaar part (research/Sound-Pass-Plan.md; Skyy 2026-10-14 ~18:30 "do 1. 3. 6. 7. 8. and
9." - item 6 = sound pass rounds 2-4 + a per-player sound switch). The round 1 recipe (SkyyQuests 0.3.1), generated by tools/soundpass_gen.py:
  1. TWO SOUNDS, 2D to the trading player only (category UI): BUY DONE (SFX_Coins_Land, a buy that bought something - Buy 1 / stack /
     custom amount) and SELL DONE (SFX_Coins_Land, a sale that paid - Sell 1 / stack / all / custom / Sell inventory). Played at the
     one success return of Trader.buy0 / sell0 (inside the Market lock: one packet write, no lock of ours taken). A refused trade is
     silent. Sell inventory sells product by product - the 0.5 s gate makes it ONE sting.
  2. BzSnd (the one helper; never throws; a missing id = one WARN) + the PER-PLAYER SWITCH: the bridge key settings:sounds:<uuid>
     (Boolean, SkyyMenu 0.3.25 /settings) FALSE = that player hears no SkyWynn sound; absent / TRUE = play.
  3. SERVER SETUP -> Bazaar -> new category "Sounds" (5 rows, all live, KEEP=10): Sounds (master) + per sound on / off + its id
     (check= BzSnd.check). File: Skyy_SkyyBazaar/sounds.properties (written with the defaults when missing).
  4. No saved-data change, no new command, no bridge key written. ROLLBACK to 0.1.11: safe (0.1.11 never reads sounds.properties).

0.1.11 (2026-10-14) = REBIRTH R4 (research/cloud/Rebirth-Spec.md 2.4 / 4.3; KEY CONTRACT + notes: tools/bazaar_0_1_11_patch.py):
bazaar:fn:closeall (Function(String pkey) -> "ok:0": 0.1.x has instant trades only - no orders, no escrow, nothing a rebirth could
strand) + bazaar:fn:wouldclose (read-only, "ok:0:0:0:0"); both removed at shutdown. No price / product / page / file / trade change.

0.1.10 (2026-10-13) = THE ENCHANTED MATERIALS ARE PRODUCTS (research/Gathering-Shards-Spec.md phase 1; tools/skyyench.py; full notes:
tools/bazaar_0_1_10_patch.py): 19 Skyy_Ench_* products (SkyyCollections 0.2.11) in the Mining / Foraging / Farming tabs (SkyySacks 0.8.1's
catOf), priced as PROCESSED goods from their recipe (100 x the input's raw value x (1 + the processed-goods premium); never stacked on
the ingots' own premium) - Skyy's "Enchanted premium ... capped below any loop, like the processed-goods 22% rule"; every loop check
covers them; appended once to a live products.properties by Catalog.migrate110 (history copy, trades.log undo lines, marker
migrated.0.1.10).

0.1.9 (2026-10-13) = BAGS V2 (research/Bags-v2-Spec.md section 5; Skyy's LOCKED rule 2026-10-03 "if it goes in the bag, it goes in a matching
section in the bizzar."). Ships with SkyySacks 0.8.0 (SkyyVoid):
 A. A FISHING TAB: SkyySacks 0.8.0's catOf puts Fish_* and Food_Fish_Raw* in the new Fishing category, so the build's bag tabs are
    Mining / Foraging / Farming / Fishing / Combat / Smithing (BAG_TABS = SackDefs.CATS of the SkyySacks jar it reads; the page already
    fits 6 tabs: BZ_MAXT 6). The build reads max(the SET pin, 0.8.0) of SkyySacks (this Bazaar ships with 0.8.0).
    NO products.properties REWRITE for the fish: a product line whose category is exactly the item's OLD bag (Farming, the 0.1.8 default
    of a fish) no longer adds that category as an extra tab (Catalog.OLDBAG / tabsOf) - the fish leave Farming and show in Fishing, and a
    rollback to 0.1.8 reads the same file as before (fish back in Farming). An admin's own category (anything else) still adds its tab.
 B. CRYSTALS: SkyySacks 0.8.0 puts Ingredient_Crystal_* in Mining, so the build's TOTAL guard needs them: 9 new Mining products (the 8
    coloured Crystal Shards 25 coins, Void Crystal Shards 60 - DECISION, placeholders like every price; no recipe makes or uses them as a
    product, so the money-loop checks stay clean). They reach a LIVE products.properties through a ONE-TIME update (PROJECT-RULES 4,
    the 0.1.4 pattern): Catalog.migrate19 runs once (marker migrated.0.1.9 in pricing.properties, kept by writeModes): a verified byte copy
    of products.properties goes to config-history/ first, then each NEW product whose id is not in the file yet is APPENDED as its seed
    line (every existing byte and line ending kept; the file's own line ending style; a missing final newline added first); nothing else
    changes. One trades.log line per added product with its undo ("delete the line <id>=..." / put the history copy back) + a summary
    line; one INFO line. A failed step writes no marker and retries at the next start. A fresh install is seeded with every product.
 C. Player texts: "from your bags" -> "from the Void" (SkyyVoid is the players' name for the bags since 0.8.0); the locked-item refusal
    says "Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold" (fix round 2).
Rolling back to 0.1.8: safe - the appended crystal lines are ordinary product lines (0.1.8 shows them in their file category, Mining, and
trades them; crystals are not bag items for SkyySacks 0.7.18 - a rollback normally goes with SkyySacks 0.7.18 anyway).

0.1.8 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding #13 + pack-wide pattern 1; Skyy 2026-10-13:
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"). Same prices, same trades, same files - only less work:
 A. LOCK-FREE BRIDGE: BzUtil.bridge() caches the skyy.bridge map in the static volatile BzUtil.BRIDGE (only the first call takes the
    System.class monitor, to create the map exactly as before); the config kit's CfgRows.bridge() does the same (tools/skyycfg.py).
 B. BzTick (every 10 s, scheduler) no longer rewrites market.properties and re-quotes every product forever:
    - decay() still moves every demand factor toward 1.0 exactly as before (same formula, same 1e-4 snap to 1.0, same clamp), but it only
      PUBLISHES the ids whose factor really changed (bazaar:buy:<id> / bazaar:sell:<id>; 0.1.7 re-quoted all ~415 products + rebuilt the
      bazaar:products CSV every tick). An id snapped back to 1.0 is published too. With no factor away from 1.0 a tick publishes nothing.
    - decay() no longer marks market.properties dirty. Decay is a pure function of the saved factors and lastDecayMillis (the next
      start's first decay applies the whole gap since lastDecayMillis, as 0.1.7 did after any stop), so a file written up to 5 minutes
      earlier gives the SAME factors at the next start: decay-only changes (and lastDecayMillis alone) are persisted at most every
      5 minutes (Market.PEND + SAVED). Trades, /bazaaradmin reset and a reload still mark DIRTY and are written by the next tick (<= 10 s,
      as 0.1.7), always together with the current lastDecayMillis. Shutdown writes any pending decay too.
    - publishAll() (catalog / price / spread changes: start, reload, admin price, reset, a premium reprice) only re-puts the
      bazaar:products CSV when its text changed.
    Kept: the Market lock order, every quote / price / spread rule, trades.log, products.properties writes (still only when the catalog is
    dirty), the Catalog.tick premium check. Rolling back to 0.1.7 is safe (same files, same format).

0.1.7 = THE MARKET WALL (docs/answered/economy.md 2026-10-08, Skyy's popup: MARKET WALL -> "Mythic + UT + Sets (Recommended)" - never bought
or sold on the Bazaar / Auctions; built in the UT/Mythic round with SkyyGear 0.2.14). The Bazaar trades by item id and used to take ANY stack
of a product id, whatever its metadata - so a Mythic / Untiered / Set copy of a product id (only possible when an admin lists a gear id as a
product; the default catalog has none) could have been sold. Now it asks the shared market:veto map (the Auction House's contract: owner ->
Function(ItemStack) -> null or a reason; SkyyGear 0.2.14 publishes "SkyyGear"):
 - Inv.veto(stack): every veto in turn, the first reason wins; a veto that throws = a refusal ("could not check this item"); no map = no wall.
 - Inv.countIn / Inv.take skip every stack WITH metadata that a veto refuses: a walled stack is never counted as held, never sold, never taken
   by Sell / Sell all / Sell inventory, and never counted by give()'s before / after measure (plain stacks are never asked - no cost for
   ordinary materials).
 - buy0 / sell0 refuse a product whose PLAIN stack a veto refuses (an Untiered-table id listed as a product): "Mythic, Untiered and Set gear
   never goes on the market - trade it directly with another player." (SkyyGear's reason text), before any coin or item moves.
Without SkyyGear 0.2.14 (no market:veto) everything is exactly 0.1.6. No price / page / saved-data change. Rolling back to 0.1.6 is safe.

0.1.6 (2026-10-09) - A SEARCH BAR (Skyy 2026-10-09: "bizzar needs a search bar too"; details in the tools/bazaar_0_1_6_patch.py docstring):
 - a search row under the purse line: the kit's vanilla search field (magnifier, clear x, placeholder) + Search + Clear. Enter or Search
   filters EVERY tab's products by display name or item id (case-insensitive, parts of words, every typed word must match); the results
   page with the normal grid / pager and a 'Search: <text>' line; Clear, an empty search or a tab click goes back to the tab you were on.
 - only BzPage changes: no price / trade / saved-data change.

0.1.5 (2026-10-06) - SELL FROM THE BAGS, HYTALE STACKS, SAP 12 (Skyy 2026-10-05, docs/answered/economy.md 'New answers'; details in the
tools/bazaar_0_1_5_patch.py docstring):
 - (A) "you should be able to sell from your bags": Sell 1 / Sell <stack> / Sell all / the custom Sell / Sell inventory take the inventory
   first, then the Magic Bags the player carries, through SkyySacks 0.7.13's bridge (sacks:fn:count / all / take / put; world thread,
   per profile, live-mirror rule, saved like any bag change). Coins only for what really left (inventory re-counted, bags = what
   sacks:fn:take reports); a failed payment puts the bag part back through sacks:fn:put (only what a take removed) and the rest into the
   inventory. No SkyySacks / an older one = 0.1.4 behaviour. Magic Bags (Skyy_Sack_*) are refused by buy0 / sell0 (locked rule). The page
   counts inventory + bags (cells, "You hold N (M in your bags)", limits, max / all); trades.log SELL lines end " bags=<n>" when bags paid.
 - (B) Tree Sap default 4 -> 12 (PRICE_015): the pack default only; saved prices (Skyy's live /bazaaradmin price ... 12, any hand edit) stay.
 - (C) Buy 64 / Sell 64 -> Buy <stack> / Sell <stack> = the item's real Hytale max stack (Item.getMaxStack at run time: ores 25, most
   blocks 100, food 25 ...; 0 / unknown -> 100, the engine's plain-item default), shown on the button and in the price lines.

0.1.4 (2026-10-05) - PROGRESSION PRICES (Skyy 2026-10-04, LOCKED in docs/answered/economy.md: "id probbly 2x each material. so copper
stays. iron gets 2x. thorium gets 4x ect" / "same fore the more rare woods. we are building a progresson tree" / "the crops in the
vanilla expansion path ... especially for the eternal seeds" / hides "just double the price of all of them"; cloth + gems: the open
question's default, x2 per tier step). Only DEFAULT prices change: the trade core, the page, the commands, the tick, the tabs and every
name are 0.1.3's (asserted byte-identical by tools/bazaar_0_1_4_patch.py).
 - PRICE_014 (the table below PRODUCTS): ores x2 per tier step of the tool ladder (Copper 5, Iron 16, Thorium 48, Cobalt 144,
   Adamantite 480, Mithril 1,440, Onyxium 3,712; ingots stay AUTO = ore + fuel x (1 + premium); Silver, Gold, Prisma unchanged); logs x2
   per tier step (T1 3 / Bamboo, Burnt 2 stay; T2 8; T3 Amber, Redwood 20; T4 Azure, Petrified 48; T5 Crystalwood, Fire, Frostwood,
   Stormbark 128; planks unchanged); hides x2 flat (Soft 8 ... Prismatic 90; leathers AUTO); cloth scraps x2 per tier step
   (Wool / Linen / Cotton 4, Silk 16, Shadoweave 40, Cindercloth 96, Stormsilk 256, Prismaloom 640; bolts AUTO from 1 Cotton / Wool
   Scraps - the vanilla Loombench weaves EVERY bolt but Wool from 1 Cotton, so a bolt can never cost more than ~1.22 x Cotton);
   Diamond / Voidstone 60 -> 120 (the 40 gems stay). Bronze Ingot 21 -> 40 (Bazaar-only: from 38.5 the latent buy Bronze + log +
   Light Leather -> Ancient Steel armor -> salvage -> smelt / tan -> sell chain stays closed at every premium 0-22 with the new Iron
   Ore / hide prices; at 21 it paid x1.25).
 - CROPS on the VANILLA farming path: the build reads the Farmingbench RequiredTierLevel of each normal seed recipe (Assets.zip) and
   stops when it differs from VANILLA_SEED_TIER: Lettuce, Wheat 1 | Carrot, Corn 2 | Cauliflower, Turnip 3 | Aubergine, Pumpkin 4 |
   Chilli, Tomato 5 | Cotton, Rice 6 | Onion, Potato 7 (eternal seeds one tier higher). Two vanilla tiers = one price tier: crops
   2 / 6 / 16 / 40, normal seeds 1 / 2 / 4 / 8, eternal seeds 50 / 200 / 800 / 3,200 - each held under its no-loop cap where the
   vanilla recipe needs it (Essence of Life 0.5: seed <= essence x 0.5 x 1.1 / 0.9; eternal <= its recipe cost x 1.1 / 0.9):
   Chilli / Tomato seeds 3.5, Onion / Potato seeds 6, Lettuce / Wheat eternal 37, Chilli / Tomato eternal 600, Onion / Potato eternal
   2,400. NOTE: the vanilla path is NOT today's price order (Potato / Onion are the LAST vanilla tier but were 2 / 3 coins).
 - SAPLINGS (Skyy 2026-10-05 LOCKED: seeds + saplings "Raise with their tier"): x2 per tier step of their log (today a sapling costs
   what its log costs, so this is also the same sapling:log ratio), capped where the vanilla Farmingbench recipe (N Essence of Life -> 1;
   SAPLING_ESSENCE, checked against Assets.zip) would let buy -> craft -> sell pay. ONE cap rule for seeds and saplings: floor to 0.5 of
   0.6 x N (the loop bound is 0.611 x N). Crystal / Poisoned inherit Oak's 15-essence recipe; Apple's needs Greater Essence + Apples: uncapped.
 - MONEY LOOPS: everything 0.1.3 checks (check_assets at premium 0 / 15 / 20 / 22, loop_check at every premium 0..22 - fuel, charcoal,
   co-products, liquidation - and the admin price guard) on the new table, PLUS (0.1.4) the same loop_check over the vanilla recipes
   UNIONED with the item / recipe assets of every tools/deploy_set.py SET jar (their recipes added, their items' resource types added -
   never removing a vanilla recipe, so the union is at least as strict); the build prints the tightest recipe margins.
 - SAVED STATE: products.properties gets a ONE-TIME update at the first 0.1.4 start (Catalog.migrate14, after 0.1.3's migrate; marker
   migrated.0.1.4 appended to pricing.properties, whose other bytes stay): a product line whose price is still EXACTLY its 0.1.3
   default (numerically: "16" = "16.0") gets its 0.1.4 default - the price text only; id, category, name, spacing, every other line and
   each line ending stay byte for byte. A price that is not the 0.1.3 default (set live with /bazaaradmin price, or a hand edit) is
   KEPT and logged. Before the file is written a byte copy goes to Skyy_SkyyBazaar/config-history/Skyy_SkyyBazaar~products.properties.
   <yyyyMMdd-HHmmss-SSS>.bak and is read back and compared (a mismatch changes nothing; the next start retries). trades.log gets one
   MIGRATE-0.1.4 summary line + one line per changed price with its undo command (/bazaaradmin price <id> <old>) + one per kept
   price; one server INFO line. A failed step writes no marker and retries at the next start (idempotent: a moved line no longer holds
   its 0.1.3 default). market.properties (demand factors, counters) is never touched; processed goods stay auto / fixed as they were.
   0.1.3's own update (kept for a server coming from 0.1.2, or one whose migrated.0.1.3 marker was lost) now also counts a 0.1.3 seed
   line (SEED013) as a default, so a re-run moves it to its 0.1.4 line instead of taking a bar at its 0.1.3 auto price for a hand
   price and making it FIXED.
   Undo all: put the config-history copy back as products.properties and remove the migrated.0.1.4 line (or roll back to 0.1.3).

0.1.3 (2026-10-03, Skyy LOCKED: "small medium and large leather, (allong with everything else the combat sack holds.) in the combat
section, and a new smithing section with everything the smithing sack holds (and for things like orevs smelted bars, make the smelted
bars and tanned leather a good bit more expensive like +15%-25% so so it actually costs you to save time and buy processed materials"
+ GENERAL RULE: "if it goes in the bag, it goes in a matching section in the bizzar.")
 - PRODUCTS = 415 rows (item id, base price or AUTO, official en-US name) in display order. The TAB is derived at BUILD time from
   SkyySacks' own bag rule: the SkyySacks jar of the tools/deploy_set.py SET (0.7.12 today) is loaded in the build JVM and its
   SackDefs.catOf(id) (= what a bag takes; cooked food off = Skyy's default) runs over every Assets.zip item. EVERY bag item is either
   listed in the matching tab (Mining / Foraging / Farming / Combat / Smithing) or matched by a written SKIP rule (fix round: the guard
   is total - before it only covered Combat + Smithing):
     Combat + Smithing: EVERY item the rule puts in the bag (Skyy: "everything the ... sack holds"; 14 + 46);
     Mining / Foraging / Farming: the rule matches ~2,000 ids there; listed = every one that is not on a SKIP rule (123 / 49 / 183:
       ores, gems, cobbles, the Furnace stones, rubble, terrain, gravel, clays, logs, planks, sticks, sap, crops, seeds, saplings, fruit,
       herbs, mushrooms, moss, petals, meat, fish, essences). SKIP (each with its written reason, counted in the build output):
       building shapes / decorative variants (Builders bench, cracked, smooth, stairs, half ...), the world form of a block (ore in
       rock, planted crops, bedrock, tilled soil), decoration plants and formations (grass, flowers - their petals are listed -, leaves,
       coral, cactus, crystals, branches), items never made in survival, and NOSRC = no drop list, block or recipe gives the item, so it
       never goes in a bag (tree seed bags, crop-named essences, medium rubble, smooth Stone ...).
   The build FAILS when a bag item is neither a row nor skipped, when a row's item is in no bag (or skipped), when an AUTO row is not a
   processed good (or a processed good is not AUTO) and when a 0.1.2 product went missing or changed its raw price - so a new bag item
   shows up on the next build as a build stop that asks for its price. Names are checked against server.lang (a mismatch is a WARNING).
   Skyy's adds (EXTRA_TABS): light / medium / heavy hides and leathers are also listed in Combat - one market, one price, two tabs.
 - PROCESSED GOODS (PREMIUM_BENCHES Furnace + Tannery: the bars, the leathers, Slate and the other Furnace stones, Orange Clay Cobble;
   charcoal, the Furnace's fuel by-product; PREMIUM_ITEMS: the cloth bolts, woven from Cotton at the Loombench / Wool Scraps at the
   Furniture bench - Skyy's "processed materials"): base = (raw inputs per the vanilla recipe: input quantity x the cheapest listed
   product of that input / output quantity + fuel: the recipe time after the best tier's time cut x the cheapest listed fuel per second
   net of the charcoal it gives back) x (1 + premium), floored to 0.01 (never above the exact value). Charcoal = 2 x its cheapest listed
   fuel (PerFuelItemsConsumed). A processed good made from another (Dawnstone from Quartzite) is priced after it (proc_order) and
   counts that input at its RAW value (fix round: the premium is never stacked - 2 smelts at (1 + p) each would let buy cobble ->
   smelt -> smelt -> sell pay from p = 11 %; the every-premium loop check below caught it).
   premium = Server Setup -> Bazaar -> "Processed goods premium" (row processed.premium, int %, default 20, 0-22; config kit
   tools/skyycfg.py 1.1, file Skyy_SkyyBazaar/config.properties, node skyybazaar.admin). 22 is the top because at the 10 % spread
   (1 + p) x 0.9 must stay below 1.1 (p < 22.2 %) or buying the inputs, processing and selling pays; at run time the premium is also
   capped below (1 + spread) / (1 - spread) - 1 when an admin lowers the spread in market.properties. The prices are computed at RUN
   time (Catalog.reprice: at start, /bazaaradmin reload, a premium change - the row's after= hook, or the 10 s tick for a hand edit -
   and every admin price change), so processed goods follow their inputs; products.properties shows the result (rewritten by the tick).
   /bazaaradmin price <id> <base> on a processed good makes it FIXED (refused above the price that would let buy -> process -> sell
   pay); /bazaaradmin price <id> auto puts it back. Mode file: Skyy_SkyyBazaar/pricing.properties (mode.<id>=auto|fixed). A FIXED
   price above that limit (a hand edit of products.properties, or an input an admin made cheaper) is held at the limit by every
   reprice, with one warning line (fix round). ADMIN PRICE GUARD (fix round): the build writes every recipe whose inputs all have a
   listed product and that makes a listed product (+ the fuel -> charcoal burns) into the jar (Catalog.EDGES); /bazaaradmin price
   (also "auto") is applied under the Market lock and REFUSED, changing nothing, when it makes such a recipe pay in one step that did
   not pay before (inputs at their cheapest listed product x (1 + spread) + fuel, listed outputs x (1 - spread)) - so moving an input
   can no longer turn a fixed crafted good (planks, gravel, saplings, seeds, Greater Essence of Life ...) into a money loop. Start and
   /bazaaradmin reload warn (one line each) about recipes that pay at the prices on disk.
 - MONEY LOOPS: the 0.1.2 check_assets runs UNCHANGED over the 0.1.3 prices at premium 0, 15, the default and the maximum (it raises
   on a loop), then loop_check (at EVERY whole premium 0..22) adds what 0.1.2 did not know: Furnace / Campfire recipes pay their
   fuel, burning 2 fuel items into 1 charcoal is a recipe of its own (every Fuel item, also crafted ones like planks), and (fix
   round) every recipe runs on two values per item to a joint fixed point - cost = the cheapest way to GET it from coins (buy, or
   craft it with a co-product's value
   credited), liq = the best way to TURN it into coins (sell, or put it through another recipe and liquidate what comes out: salvage
   gear, smelt the ore, tan the hide). Both must find no loop. The old extension saw no loop in buy Bronze + logs + hides -> tan ->
   Ancient Steel gloves -> salvage -> smelt the ore + tan the hides -> sell (+16.7 % at 20 %; latent: its bench "TODO" exists in no
   block yet), so Bronze Ingot is 21 (>= 20.3 closes it at every premium 0-22); a synthetic self-test proves the check sees such a chain.
 - SAVED STATE: market.properties is never touched (demand factors, lifetime counters; new products start at factor 1.0).
   products.properties gets a ONE-TIME update at the first 0.1.3 start (marker migrated.0.1.3 in pricing.properties; a verified copy
   products.properties.v012bak is written first; a failed step writes no marker and retries at the next start): a line still holding
   its 0.1.2 default (same category, price and name - "6" and "6.0" both count) becomes its 0.1.3 line where that differs (the 3 bars
   -> Smithing + their auto price, Light Leather -> Smithing 7.2, Light / Medium Hide -> Smithing, Essence of Life -> Farming); a line
   that only spells a number differently keeps its bytes; a hand-edited line stays byte for byte (a hand-priced bar / leather becomes
   FIXED, logged); every 0.1.3 product the file lacks is appended (seed order) - a product line load() would refuse (category over 16
   characters, a price outside 0.01 .. 1000000000; the same rules as Catalog.parse) counts as lacking, so the product is never lost;
   comments, blank lines, unknown lines and each line's own line ending are kept. One server line + one trades.log line (MIGRATE-0.1.3
   added N rewrote N fixed N) say what changed. A fresh install is seeded with the 415 lines. To undo: put products.properties.v012bak
   back and remove pricing.properties (with 0.1.2). Later saves (an admin price, a moved auto price) rewrite only the product lines
   whose category / price / name changed; comments, blank / unknown lines, the number spelling of the others and every line ending
   stay (0.1.2 rewrote the whole file).
 - CHECKED offline (SkyyBazaar/test_skyybazaar_0.1.3.py, one -Xverify:all JVM on the real engine classes; plus the build's own checks
   above): every class loads; class compare 0.1.2 -> 0.1.3; the engine-access audit; a fresh start; every bag item a product or
   skipped (the build's derivation re-run with the real SkyySacks rule); the processed prices in Java = the build's at premium 0 / 20 /
   22 and with a fuel cost; the loop cap, fixed / auto, the hold at the limit, the spread cap, the Server Setup row through the config
   kit; both money-loop checks on the runtime table (and the new one catches the Bronze 16 chain); every one of the 415 products bought
   and sold through the real Trader; the one-time update and two starts on scratch copies of the live data (+ hand edits, "6.0"
   numbers, CRLF, lines load() refuses, an unreadable pricing.properties, a re-run, the 0.1.2 Catalog reading the result); a
   line-keeping save; the admin price guard (refusals, Java = build, warnings); the page in 11 states on real data (kit checks,
   widths, the 835 px body, bindings, clicks).
 - UNVERIFIED until Skyy opens it in game: the kit page on the real client (only properties the deployed vanilla-look pages use);
   SkyyMenu's Server Setup page showing the new Bazaar row; the in-game feel of the prices.
 - PAGE (vanilla kit, research/Vanilla-UI-Style-Guide.md): plain window "Bazaar" 1080 x 907 (#SkyyBz = the body, so every 0.1.2
   id stays): purse line, tab row (up to 6 tabs, the open one Primary, + Sell inventory - Destructive), a 13 x 4 grid of icon cells
   (52 per page) with the kit pager (Prev / Next, still bound at the ends), the detail well (icon, name, buy / sell / hold / demand and
   a processed-goods line), Buy 1 / Buy 64 (Primary), Sell 1 / Sell 64 / Sell all (Destructive), the amount field with Buy / Sell, the
   limits line, a result line coloured by its words and a footer with Close (Secondary + the cancel sound, = CustomUIPage.close()).
   Tab names are drawn inline after a letters-digits-space filter (BzPage.tabText). New payloads: prev, next, close.
 - Unchanged and asserted byte-identical: the trade core (Coins, Inv, TradeResult, Trader: buy0 / sell0 / buyN0 / sellN0 / preview /
   sellInventory), Market (quote, step, decay, files, bridge), Product, BzUtil, BzPageFactory, BzCmd, the /bazaaradmin subcommands,
   BzPage.amountAction / limits / buyWhy / sellWhy / evd / disarm / build.

0.1.2 (2026-09-24, Skyy's beta backlog item 8) - custom amounts + a bigger page. Pricing (quote / unit / step / spread), the demand
factor, decay, anti-dupe trade core (buy0 / sell0 / sellInventory), files, trades.log, the bridge keys and /bazaaradmin are the
0.1.1 logic unchanged.
 - Custom amount row under the product's Buy / Sell buttons: "Custom amount" [TextField #SkyyBzAmt] [Buy] [Sell] + a hint, and a
   limits line under it ("You can buy up to N (your purse | inventory room | the per-trade limit) and sell up to H").
   TextField pattern copied from SkyyGuilds 0.1 (Amount field, in game on the beta test) / SkyySacks 0.7.3 (search, verified in game):
   Enter = Validating binding, the buttons = Activating bindings, every binding carries EventData .append("@BzAmount",
   "#SkyyBzAmt.Value") and the value is read back with jsonStr (SkyySacks CraftPage.jsonStr); the rebuild puts the last submitted
   text back with set("#SkyyBzAmt.Value"). While the field is on the page (a product is selected) the tab / product / 1 / 64 /
   Sell all / Sell inventory bindings carry the field value too, so typed text survives picking another product.
   Amounts: a whole number (500), k / m suffixes (2k, 1.5k, 1m), commas and spaces ignored, max / all = the limit of that side.
 - Validation (inside the Market lock at trade time, again in the page for the messages): Buy 1 .. min(what the purse affords
   (one walk with quote()'s exact arithmetic, stopping at the first unit the purse cannot cover), inventory room (empty slots x the item's max stack +
   the free part of partial stacks, storage + hotbar + backpack like Inv.give), 100000 per trade). Sell 1 .. what you hold
   (storage + hotbar + backpack). A refused amount says why and moves nothing.
 - The total price is always shown before a custom trade: Enter prices BOTH sides ("500 Copper Ore - buy for X coins - sell for Y
   coins") and arms them for 15 s; a Buy / Sell click that was not priced first only shows the price and arms that side for 10 s
   ("click Buy again within 10 s to confirm"). The trade then runs with the price the player saw as a cap: a buy that now costs
   MORE, or a sell that now pays LESS (someone else traded in between), is refused and re-armed at the new price. A sell that
   is now worth 0 coins is refused outright (like sell0). max / all is worked out again on every click; when the armed max
   changed the page says "your max changed from A to B" and asks for one more click at the new amount and price.
   Any other click disarms (like the Sell inventory confirm).
 - Page actions are matched exactly with jsonStr(data, "a") (SkyyGuilds pattern) instead of 0.1.1's has(data, key) substring test,
   so text typed into the amount field can never be read as another button's payload.
 - profile:busy:<uuid> (tools/PROFILES-CONTRACT.md rule 5, crash recovery at join): buy0 and sell0 refuse to move items while it is
   present ("your profile is still loading"), so no path (buttons, custom amount, Sell inventory) can dupe against the recovery.
   The page says so too: the limits line reads "trading is paused", and neither the custom amount nor Sell inventory shows a
   price or a Confirm prompt while it is set.
 - The 6-tab / 27-product caps are 0.1.1's (more rows or tabs need a client check first); anything past them is named in the
   line under the tabs ("N more products in this tab ... do not fit the page - tell an admin") instead of vanishing silently.
 - Page about 1.4x: root 1080 wide (was 760), 640 high with one grid row (+94 per extra row, 828 with the maximum 3 rows - fits a
   1080-high screen like the verified 830-930 pages); every font, button, cell (87 px, was 62), icon and row scaled ~1.4x; the grid
   is centred. The root height follows the grid rows (0.1.1 kept 560 even with 1 row) and does not change when a product is selected
   (the empty detail box takes the height of the detail + trade rows).
 - Offline checks only (session harness in tools/dev/scratch, deleted afterwards): -Xverify:all load of every class, parseAmt /
   jsonStr / maxBuyable / buyWhy / sellWhy cases, render() markup (balanced braces / parentheses / quotes, no underscore ids,
   root anchor only Width + Height, heights) and the amount click flow with fake SkyyCoins bridge functions. The page itself on a
   real client is UNVERIFIED until Skyy opens it.

0.1.1 (2026-09-23) - command access fixes only; pricing, trades, anti-dupe, files, log and bridge are byte-for-byte the 0.1 logic.
 - /bazaar (/bz) is usable by ordinary players. 0.1 never called requirePermission(), so CommandRegistry -> AbstractCommand.setOwner()
   generated the node "skyy.0.1_skyybazaar.command.bazaar" (PluginBase base permission "<group>.<name>" lower-cased, spaces -> "_",
   so it even changes with every version) and players in the default group hytale:Adventurer have no permissions -> only "*" admins
   could open it. Now BzCmd calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as
   SkyyEssentials 0.1): CommandManager.createVirtualPermissionGroups -> PermissionsModule virtual group grants that node to Adventurer.
 - /bazaaradmin positional forms work. In 0.1 all three arguments were withOptionalArg, and optional args are NOT positional:
   AbstractCommand.acceptCall0 requires (positional tokens) == totalNumRequiredParameters unless setAllowsExtraArguments(true), so
   "/bazaaradmin price Ore_Copper 5" failed with server.commands.parsing.error.wrongNumberRequiredParameters and only
   "--action price --item Ore_Copper --value 5" worked. 0.1.1 adds real subcommands with withRequiredArg:
       /bazaaradmin                      status line + usage (root execute, unchanged)
       /bazaaradmin price <itemId> <base>   set a base price           /bazaaradmin price <itemId>   show the current base (usage variant)
       /bazaaradmin reload                 /bazaaradmin reset <itemId|all>          /bazaaradmin info <itemId>
   Engine (bytecode, AbstractCommand.checkForExecutingSubcommands): the first positional token is looked up as a subcommand name
   (lower-cased, aliases too) and dispatched; otherwise a usage variant is picked from variantCommands by the positional-token count,
   only when that count differs from the command's own required count (addUsageVariant keys the variant by ITS required count at add
   time, so a variant declares its args in its own constructor). With no positional tokens and no match the root runs its own
   execute (0 == 0 required), so plain /bazaaradmin and the old --action/--item/--value flags still work on the root.
   The subcommand is dispatched BEFORE the root's hasPermission check, so every subcommand and the variant call
   requirePermission("skyybazaar.admin") themselves (hasPermission then also walks up to the parent, which needs the same node).
   All forms go through one static BzAdminCmd.run(pr, action, item, value) = the 0.1 execute body with ctx reads replaced by params.
 - What proved what (offline only; nothing here is a live-server test - Skyy's in-game test is the real check):
   (a) Offline parser harness (session scratchpad bz/bz011_parsetest.py, not shipped: real Tokenizer / ParserContext / acceptCall on
       the built classes, fake console sender holding an explicit node list). It covers ONLY /bazaaradmin: the positional forms parse
       (price <id> <base>, price <id>, reload, RELOAD, reset <id|all>, info <id>, old --action/--item/--value), wrong token counts give
       wrongNumberRequiredParameters, and without skyybazaar.admin every form gives noPermissionForCommand. It builds commands directly
       and never calls setOwner(), so BzCmd.permission stays null there and /bazaar runs for anyone on 0.1 AND 0.1.1: it is no
       evidence for the /bazaar fix. Its sender is not a player, so every "ran" stops at AbstractPlayerCommand's playerOrArg reply
       (the run() bodies are not exercised).
   (b) The /bazaar Adventurer grant rests on bytecode: setOwner() fills in permission only when it is null (and not openToEveryone)
       with generatePermission() = PluginBase.getBasePermission() + ".command.bazaar"; PluginManager.setup() runs every plugin's
       setup() (our registerCommand) before PluginManager.start() runs PermissionsModule.start() -> refreshVirtualGroups() ->
       CommandManager.createVirtualPermissionGroups() -> setVirtualGroups(); PlayerRef.hasPermission -> PermissionsModule.hasPermission
       checks the user's nodes, then for each group (default hytale:Adventurer) that group's nodes, then virtualGroups.get(group).
       Offline replay bz/bz011_advtest.py (scratchpad) runs those real engine methods with only object construction stubbed (plugin,
       CommandManager and PermissionsModule allocated without constructors, in-memory HytalePermissionsProvider): 0.1 Adventurer
       /bazaar -> noPermissionForCommand; 0.1.1 Adventurer /bazaar and /bz -> ran; hytale:None player -> denied; Adventurer
       /bazaaradmin (plain, reload, price, info) -> denied; a user granted skyybazaar.admin -> reload and price <id> <base> ran.
       Not covered offline: the real boot, and a hot /plugin load - virtual groups are rebuilt only by PermissionsModule.start() and
       reload(), so a version loaded after boot needs /perm reload or a restart before Adventurers can use /bazaar.

WHAT 0.1 DOES
 - /bazaar (alias /bz) opens an inline page: category tabs, a 9-wide ItemIcon grid (Sacks grid pattern), click a product to select it,
   detail area = instant-buy / instant-sell prices for 1 and 64, how many you hold, demand factor; buttons Buy 1, Buy 64, Sell 1,
   Sell 64, Sell all (of the selected item); a global "Sell inventory" button (two clicks: preview, then Confirm sell within 10 s)
   sells every bazaar product found in storage + hotbar + backpack. The page can also be opened by any item / NPC interaction with
   OpenCustomUI page id "SkyyBazaar" (registered, nothing ships with it yet).
 - Products: Skyy_SkyyBazaar/products.properties, seeded on first run with 36 commodities in 4 categories (tab order = file order):
       <ItemId>=<Category>,<basePrice>,<Display Name>          e.g.  Ore_Copper=Mining,5,Copper Ore
   basePrice may be fractional (0.5); every item id is checked against Assets.zip at BUILD time and against the live Item asset map
   at RUN time (unknown ids are hidden and logged once, never traded).
 - Pricing (per unit, walked unit by unit through the trade so a big order pays the price it pushes):
       instant buy  = base * factor * (1 + spread)       instant sell = base * factor * (1 - spread)
   factor starts at 1.0; every unit bought multiplies it by step, every unit sold divides it by step,
       step = exp(ln(1.10) * base / impactCoins)       (impactCoins of base value traded moves the price 10 pct)
   clamped 0.25 .. 4.0; decays toward 1.0 in log space with a half-life of halfLifeMinutes (every 10 s tick).
   Totals are rounded ONCE per trade to whole coins: buys round up, sells round down (the house never loses a fraction).
   Buying N then selling the same N back always loses about 2*spread (the sell walks the same path back down).
   Settings + state: Skyy_SkyyBazaar/market.properties (spread=0.10, impactCoins=10000, halfLifeMinutes=120, lastDecayMillis,
   f.<id> factor, bought.<id> / sold.<id> lifetime units). Written atomically (.tmp + move) by the 10 s tick and on shutdown.
 - ANTI-DUPE (economy - paranoid):
   * every trade runs on the player's world thread (page events arrive through world.execute - verified in GamePacketHandler)
     and inside synchronized (Market.class), so quote -> coins -> items -> market move is one atomic step across all worlds.
   * BUY: quote -> coins:fn:take(cost) FIRST -> add items container by container (storage, hotbar, backpack), each add measured by
     re-counting the container (never trusting the transaction) -> real = count after - count before -> charge = quote(real),
     refund = cost - charge via coins:fn:add -> market moves by real units only.
   * SELL: remove slot by slot, each removal measured by re-reading the slot -> removed = count before - count after (authoritative)
     -> pay = quote(removed) via coins:fn:add -> market moves. Never pays before removing. If the pay is 0 or the coins bridge
     refuses, the removed items are put back. A sale that would be worth 0 coins is refused before anything is removed.
   * overflow: base <= 1e9, qty <= 100000 per trade, totals > 1e15 refused, purse overflow checked before paying.
   * coins bridge faults: every coins:fn:* apply() is wrapped. get() failing -> the trade is refused before anything moves.
     take() throwing -> nothing is given, TAKE-ERROR logged, the player is told to contact an admin if their purse dropped.
     A refund / pay / give-back that fails is never reported as done: REFUND-FAILED|ERROR, PAY-FAILED|ERROR lines go to
     trades.log and the player gets the "you are owed ..." message in the page AND in chat.
   * Sell inventory confirm: armed for 10 s by the first click; ANY other click (tab, product, buy, sell) disarms it.
   * build-time ARBITRAGE CHECK: every recipe in Assets.zip (item Recipe blocks incl. ones inherited through Parent +
     Server/Item/Recipes, resource types with unbounded, cycle-checked parent inheritance, multi-step via cheapest acquisition
     cost relaxed to a real fixed point - non-convergence fails the build) is checked; the build FAILS if buying inputs at instant-buy, crafting
     and instant-selling the outputs makes coins at factor 1.0 (it caught crops -> Essence of Life x4 and cobble -> rubble x2).
     Rule of thumb for admins: for a recipe A -> B keep base(B) < 1.22 * base(A) (1.1 / 0.9). Factors can still drift apart
     (someone dumps ore, someone else buys bars) - that is market arbitrage and it corrects itself (it moves both factors back).
 - Coins ONLY through the SkyyCoins bridge (coins:fn:get / take / add). Without SkyyCoins the page says so and every trade is refused.
 - Log: Skyy_SkyyBazaar/trades.log, one line per trade (ISO time, BUY/SELL, player name, uuid, item, qty, coins, factor after);
   refund / payment failures and admin price changes are logged there too. Lines are queued and appended by the 10 s tick.
 - Bridge (JVM map System.getProperties().get("skyy.bridge")): bazaar:sell:<itemId> -> Long current instant-sell price for 1,
   bazaar:buy:<itemId> -> Long current instant-buy price for 1, bazaar:products -> "id,id,..." (republished after every trade and tick;
   removed on shutdown).
 - Admin (permission skyybazaar.admin): /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>
   (positional subcommands since 0.1.1; 0.1 only accepted --action/--item/--value).
   reload re-reads products.properties and market.properties AS THEY ARE ON DISK (factor moves from the last <10 s that were not
   saved yet are dropped - that is what lets hand edits of market.properties take effect).

PLANNED 0.2 - player buy orders / sell offers (order book), design:
 - Orders per product in Skyy_SkyyBazaar/orders/<itemId>.properties (atomic writes): order id, owner uuid, side (BID/ASK),
   unit price (whole coins), qty, filled, created millis. Max 14 open orders per player; an order expires after 7 days (refunded).
 - Escrow up front: a buy order takes qty * price with coins:fn:take before it is saved; a sell offer removes the items with the
   same count-verified slot removal as 0.1 before it is saved. Cancel returns only the UNFILLED remainder. A write-ahead journal
   (Skyy_SkyyBazaar/journal.log: intent line before the escrow move, commit line after the order file is written) is replayed on
   startup so a crash between "coins taken" and "order saved" refunds instead of losing coins.
 - Matching: instant buy fills from the cheapest sell offers first, then the market maker at its instant-buy price; instant sell
   fills the highest buy orders first, then the market maker. Bids must be < market-maker instant-buy and asks > market-maker
   instant-sell (otherwise the player just uses the instant button), so the market maker can never be walked into a money loop.
   Order fills also move the demand factor (same step as 0.1).
 - Fills for offline players land in a per-player claim stash Skyy_SkyyBazaar/claims/<uuid>.properties (coins + items), claimed
   from a "Manage orders" tab (items go through the same count-verified add; whatever does not fit stays in the stash).
 - 1.25 pct tax on filled sell offers (coin sink). Price history (hourly OHLC per product) for a chart tab later.
 - UI: "Manage orders" tab + per-product "Create buy order" / "Create sell offer" with qty and price stepper TextButtons
   (+1 / +10 / +64, price -1 / +1 / best+1) - no text input needed.
 - Bridge additions: bazaar:bid:<id>, bazaar:ask:<id> (best prices), bazaar:fn:sell apply(Object[]{UUID, itemId, Long qty}) ->
   Long coins, so SkyySacks can offer "sell bag contents" (bag pools are not inventory, 0.1 cannot see them).
"""
import sys, os, json, zipfile, re, ast, math, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI       # 0.1.3: the vanilla look kit (research/Vanilla-UI-Style-Guide.md)
import skyycfg as CFG      # 0.1.3: Server Setup (tools/CONFIG-CONTRACT.md)
import skyyench as EN      # 0.1.10: the Enchanted materials table (one source with SkyyCollections 0.2.11 + SkyySacks 0.8.1)
# 0.1.17: FROZEN to the 20 rows of 0.1.16 (tools/skyyench.py TABLE_20); the 83 C1 rows are listed by a later Bazaar round, not here
# (0.1.18 = the menu pattern round: the freeze is kept exactly - no Enchanted listing added)
# 0.1.19 (round coll24): the PRODUCTS come from the LIVE table again (102 rows; LifeEssence retired - its collection uses the vanilla
# Greater Essence of Life); rows whose base has no product (EN_OFF) are taken out at PRODUCTS. The one-time updates of older rounds keep
# their frozen lists, asserted against TABLE_20 (EN20_IDS), never against the live table.
import types as _types17
_EN_ALL = EN
assert len(_EN_ALL.TABLE_20) == 20 and _EN_ALL.TABLE[:20] == _EN_ALL.TABLE_20 and _EN_ALL.KEYS[19] == "Stick", "0.1.17: skyyench TABLE_20"
# 0.1.20: the 102 rows of 0.1.19 (migrate119's list) are FROZEN here as a literal; the live table may grow AFTER them (SkyyCollections 0.2.25's
# Enchanted Lead / Chromium / Slag / Titanium Ingot + Charcoal), those rows join NEW0120
EN102_IDS = ["Skyy_Ench_Cobblestone", "Skyy_Ench_Rubble", "Skyy_Ench_Copper", "Skyy_Ench_Iron",
         "Skyy_Ench_Thorium", "Skyy_Ench_Cobalt", "Skyy_Ench_Adamantite", "Skyy_Ench_Oak",
         "Skyy_Ench_Maple", "Skyy_Ench_Gumboab", "Skyy_Ench_Redwood", "Skyy_Ench_Sallow",
         "Skyy_Ench_Wheat", "Skyy_Ench_Carrot", "Skyy_Ench_Cauliflower", "Skyy_Ench_Pumpkin",
         "Skyy_Ench_Tomato", "Skyy_Ench_Cotton", "Skyy_Ench_Potato", "Skyy_Ench_Stick",
         "Skyy_Ench_Corn", "Skyy_Ench_Lettuce", "Skyy_Ench_Onion", "Skyy_Ench_Turnip",
         "Skyy_Ench_Aubergine", "Skyy_Ench_Chilli", "Skyy_Ench_Rice", "Skyy_Ench_Berries",
         "Skyy_Ench_Apple", "Skyy_Ench_WildFruit", "Skyy_Ench_Mushroom", "Skyy_Ench_Cactus",
         "Skyy_Ench_Seeds", "Skyy_Ench_Petals", "Skyy_Ench_RawChicken", "Skyy_Ench_RawBeef",
         "Skyy_Ench_RawPork", "Skyy_Ench_Wildmeat", "Skyy_Ench_Fiber", "Skyy_Ench_TreeSap",
         "Skyy_Ench_AppleLog", "Skyy_Ench_Ash", "Skyy_Ench_Aspen", "Skyy_Ench_Bamboo",
         "Skyy_Ench_Banyan", "Skyy_Ench_Beech", "Skyy_Ench_Birch", "Skyy_Ench_Bottletree",
         "Skyy_Ench_Burnt", "Skyy_Ench_Camphor", "Skyy_Ench_Cedar", "Skyy_Ench_Dry",
         "Skyy_Ench_FigBlue", "Skyy_Ench_Fir", "Skyy_Ench_Jungle", "Skyy_Ench_Palm",
         "Skyy_Ench_Palo", "Skyy_Ench_Windwillow", "Skyy_Ench_WisteriaWild", "Skyy_Ench_Amber",
         "Skyy_Ench_Azure", "Skyy_Ench_CrystalLog", "Skyy_Ench_Fire", "Skyy_Ench_IceLog",
         "Skyy_Ench_Petrified", "Skyy_Ench_Poisoned", "Skyy_Ench_Spiral", "Skyy_Ench_Stormbark",
         "Skyy_Ench_Sandstone", "Skyy_Ench_Shale", "Skyy_Ench_Slate", "Skyy_Ench_Basalt",
         "Skyy_Ench_Volcanic", "Skyy_Ench_Marble", "Skyy_Ench_Quartzite", "Skyy_Ench_Limestone",
         "Skyy_Ench_Ice", "Skyy_Ench_Salt", "Skyy_Ench_Sand", "Skyy_Ench_Clay",
         "Skyy_Ench_Silver", "Skyy_Ench_Gold", "Skyy_Ench_Mithril", "Skyy_Ench_Crystal",
         "Skyy_Ench_Gemstone", "Skyy_Ench_Bone", "Skyy_Ench_Linen", "Skyy_Ench_HideLight",
         "Skyy_Ench_HideMedium", "Skyy_Ench_HideHeavy", "Skyy_Ench_Wool", "Skyy_Ench_Feathers",
         "Skyy_Ench_Chitin", "Skyy_Ench_Venom", "Skyy_Ench_Shadoweave", "Skyy_Ench_Cindercloth",
         "Skyy_Ench_FireEssence", "Skyy_Ench_IceEssence", "Skyy_Ench_VoidEssence", "Skyy_Ench_LightningEssence",
         "Skyy_Ench_Voidheart", "Skyy_Ench_BoomPowder"]
assert len(EN102_IDS) == 102 and len(_EN_ALL.TABLE) >= 102 and [_EN_ALL.PREFIX + _t[0] for _t in _EN_ALL.TABLE[:102]] == EN102_IDS, "0.1.20: skyyench keeps its first 102 rows"
assert "Skyy_Ench_LifeEssence" not in _EN_ALL.IDS and "Skyy_Ench_LifeEssence" in _EN_ALL.RETIRED_TO, "0.1.19: skyyench coll24"
EN20_IDS = [_EN_ALL.PREFIX + _t[0] for _t in _EN_ALL.TABLE_20]     # 0.1.19: the frozen 20 (NEW0110 + NEW0116)
EN = _types17.SimpleNamespace(**dict((k, getattr(_EN_ALL, k)) for k in dir(_EN_ALL) if not k.startswith("__")))
EN.TABLE = list(_EN_ALL.TABLE)     # 0.1.19: the live table (EN_OFF taken out at PRODUCTS)
EN.KEYS = [t[0] for t in EN.TABLE]
EN.IDS = [EN.PREFIX + k for k in EN.KEYS]
EN.RIDS = [i + EN.RECIPE_SUFFIX for i in EN.IDS]


def _ench_assets20(z, SA_):
    """tools/skyyench.py build_assets (all rows) with only the LISTED items' JSONs kept (their recipes are inside the item JSON; 0.1.19: the
    live table minus EN_OFF, read at call time - was the 20 frozen ones)"""
    fs, lang = _EN_ALL.build_assets(z, SA_)
    keep = set(EN.IDS)
    return dict((p, t) for p, t in fs.items() if not (p.startswith("Server/Item/Items/") and p.rsplit("/", 1)[1][:-5] not in keep)), lang


EN.build_assets = _ench_assets20
import skyyart as SA       # 0.1.10: only to build the Enchanted item JSONs the same way SkyyCollections does (read-only Assets.zip)
SUI.verify()
KIT_ID = SUI.kit_id()

VERSION = "0.1.20"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SPREAD = 0.10

# ================= 0.1.3 products: EVERY item a Magic Bag holds, in the matching tab (Skyy 2026-10-03, LOCKED) =================
# "if it goes in the bag, it goes in a matching section in the bizzar." The tab of a product is not written here: the build runs
# SkyySacks' own compiled rule (SackDefs.catOf of the SET jar) over Assets.zip and checks this table against it (see the pipeline below).
BAG_TABS = ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing")   # tab order = SkyySacks 0.8.0's categories (0.1.9: + Fishing)
# 0.1.9: the bag of a product in 0.1.8 when it differs now (the fish were Farming): the file category that is exactly this OLD default adds no
# extra tab (Catalog.OLDBAG) - no products.properties rewrite; the 0.1.3 seed lines (SEED013, the one-time updates' "untouched default"
# test) keep their old category too
OLD_BAG_OF = {"Fishing": "Farming"}
ALL_OF_BAG = ("Combat", "Smithing")          # Skyy: "everything the combat sack holds" / "everything the smithing sack holds"
# fix round (review 2026-10-03): the guard is TOTAL. Every Mining / Foraging / Farming bag item is a product row unless a SKIP rule
# matches it (first match wins, the reason is printed with the counts) or no drop list, block or recipe gives it (NOSRC: it can never
# go in a bag); anything else stops the build - so a new bag item shows up on the next build as a build stop that asks for its price.
SKIP = [  # (regex on the id, reason) - Mining / Foraging / Farming bag items that are not Bazaar commodities
    (r"_Brick|_Smooth|_Processed|_Cracked|_Stairs|_Half$|_Half_|_Roof|_Wall$|_Wall_|^Wood_Village_Wall|_Beam$|_Pillar_|_Decorative|_Ornate"
     r"|_Fence|_Corner$|_Pipe_|_Quarter$|_ThreeQuarter$|_Stalactite|_Trunk_Full|_Trunk_Half|_Trunk_Stairs|^Soil_Pathway|_Path_|_Deco$|_Deco_"
     r"|^Rock_Stone_Aqua$",
     "a building shape or decorative variant (Builders bench, cracked, smooth, stairs, half, roof ...) - its raw block is listed"),
    (r"^Ore_(Copper|Iron|Thorium|Silver|Cobalt|Gold|Adamantite|Mithril)_[A-Za-z_]+$|^Rock_Bedrock$|^Soil_Dirt_Tilled$|^Plant_Crop_.*_Block"
     r"|_Stage_[0-9]|^Plant_Lavender_|^Plant_Sunflower_Block$|^Plant_Fern(_[A-Za-z]+)*_Trunk$|^Wood_Torch_",
     "the placed / world form of a block (ore in rock, a planted crop, bedrock, tilled soil) - breaking it gives the listed item"),
    (r"^Plant_(Grass|Bush|Bramble|Fern|Flower|Leaves|Vine|Reeds|Roots|Coral|Seaweed|Barnacles|Cactus)|^Plant_Moss_(Block|Cave|Rug|Short|Wall)_"
     r"|^Rock_Crystal_|^Rock_Ice_Icicles$|^Wood_[A-Za-z_]+_Branch_|^Wood_[A-Za-z_]+_Roots|^Soil_Grass|^Soil_Leaves|^Soil_Needles$|^Soil_Roots_"
     r"|^Soil_Seaweed_",
     "a decoration plant or formation (grass, flowers, leaves, coral, cactus, crystals, branches) - moss, petals, logs and saplings are listed"),
    (r"^Food_Fish_Raw_(Rare|Epic|Legendary)$|^Plant_Seeds_Test_|^Plant_Test_",
     "never made in survival (their fish-gutting recipes give plain Raw Fish, which is listed; test items)"),
    (r"^Ore_(Lead|Chromium|Slag|Titanium)_(Sandstone|Shale|Volcanic|Basalt)_SkyWynn$",
     "the placed / world form of a SkyWynn zone ore (ore in rock) - breaking it gives the listed raw ore"),
    (r"^Rock_Kenolite$|^Wood_Sadwillow_Trunk$|^Plant_Crop_Mushroom_Boomshroom_Small$|^Plant_Crop_Mushroom_Common_Lime_Large$|^Plant_Liana_Void$"
     r"|^Plant_Sapling_Sadwillow$",
     "new in Hytale 0.7.0 - not priced yet (0.1.8 keeps 0.1.7's catalog; a later Bazaar round prices them)"),
]
NOSRC = "never obtainable in survival: no drop list, block or recipe gives it, so it never goes in a bag"
PREMIUM_BENCHES = ("Furnace", "Tannery", "SkyyAlloy")      # 0.1.20: + the alloy bench id (the /craft Furnace with a Furnace Charm)
_UNUSED_PB = ("Furnace", "Tannery")     # Skyy: "smelted bars and tanned leather" (+ the Furnace's charcoal and smelted stones)
# fix round: crafted processed goods (Skyy's "processed materials") whatever bench makes them: (regex on the id, what the player does).
# Their recipe = the one non-salvage recipe whose every input is a product (the build stops on two)
PREMIUM_ITEMS = ((r"^Ingredient_Bolt_", "weaving"), (r"^%s" % EN.PREFIX, "compressing"))   # 0.1.10: + the Enchanted materials
PREMIUM_DEF, PREMIUM_MIN, PREMIUM_MAX = 20, 0, 22   # Server Setup row processed.premium (%); 22: see the pipeline's premium bound
AUTO = None                                  # a processed good: priced from its raw inputs at run time
PRODUCTS = [  # (item id, base price or AUTO, official en-US name) - display order; the tab comes from the bag (build time)
    # ---- Mining bag
    ("Ore_Copper", 5, "Copper Ore"),
    ("Ore_Iron", 16, "Iron Ore"),
    ("Ore_Thorium", 48, "Thorium Ore"),
    ("Ore_Lead_SkyWynn", 48, "Lead Ore"),            # 0.1.20: Zone 2, T4 like Thorium (tier ladder 48)
    ("Ore_Silver", 14, "Silver Ore"),
    ("Ore_Cobalt", 144, "Cobalt Ore"),
    ("Ore_Chromium_SkyWynn", 144, "Chromium Ore"),   # 0.1.20: Zone 3, T5 like Cobalt
    ("Ore_Gold", 20, "Gold Ore"),
    ("Ore_Adamantite", 480, "Adamantite Ore"),
    ("Ore_Slag_SkyWynn", 480, "Slag Ore"),           # 0.1.20: Zone 4, T6 like Adamantite
    ("Ore_Mithril", 1440, "Mithril Ore"),
    ("Ore_Titanium_SkyWynn", 1440, "Titanium Ore"),  # 0.1.20: Zone 5, T7 like Mithril
    ("Ore_Onyxium", 3712, "Onyxium Ore"),            # fix round: only salvage gives it in vanilla; its ingot follows it (AUTO)
    ("Ore_Prisma", 75, "Prisma Ore"),
    ("Rock_Gem_Ruby", 40, "Ruby"),
    ("Rock_Gem_Sapphire", 40, "Sapphire"),
    ("Rock_Gem_Emerald", 40, "Emerald"),           # fix round: the gems no recipe uses (golem drops, gem blocks)
    ("Rock_Gem_Topaz", 40, "Topaz"),
    ("Rock_Gem_Zephyr", 40, "Zephyr"),
    ("Rock_Gem_Diamond", 120, "Diamond"),
    ("Rock_Gem_Voidstone", 120, "Voidstone"),
    # 0.1.9 (SkyySacks 0.8.0 puts the crystal shards in Mining): crystal rocks and golems drop them; no recipe makes one (DECISION prices)
    ("Ingredient_Crystal_Blue", 25, "Blue Crystal Shards"),
    ("Ingredient_Crystal_Cyan", 25, "Cyan Crystal Shards"),
    ("Ingredient_Crystal_Green", 25, "Green Crystal Shards"),
    ("Ingredient_Crystal_Pink", 25, "Pink Crystal Shards"),
    ("Ingredient_Crystal_Purple", 25, "Purple Crystal Shards"),
    ("Ingredient_Crystal_Red", 25, "Red Crystal Shards"),
    ("Ingredient_Crystal_White", 25, "White Crystal Shards"),
    ("Ingredient_Crystal_Yellow", 25, "Yellow Crystal Shards"),
    ("Ingredient_Crystal_Void", 60, "Void Crystal Shards"),
    ("Rock_Stone_Cobble", 1, "Cobblestone"),
    ("Rock_Stone_Cobble_Mossy", 1, "Mossy Cobblestone"),
    ("Rock_Basalt_Cobble", 1, "Basalt Cobble"),
    ("Rock_Basalt", AUTO, "Basalt"),               # fix round: the Furnace stones (2 cobble -> 1, like Slate)
    ("Rock_Shale_Cobble", 1, "Shale Cobble"),
    ("Rock_Shale", AUTO, "Shale"),
    ("Rock_Slate_Cobble", 1, "Slate Cobble"),
    ("Rock_Slate", AUTO, "Slate"),
    ("Rock_Volcanic_Cobble", 1, "Volcanic Cobble"),
    ("Rock_Volcanic", AUTO, "Volcanic Rock"),
    ("Rock_Marble_Cobble", 1, "Marble Cobble"),
    ("Rock_Marble", AUTO, "Marble"),
    ("Rock_Quartzite_Cobble", 1, "Quartzite Cobble"),
    ("Rock_Quartzite", AUTO, "Quartzite"),
    ("Rock_Dawnstone", AUTO, "Dawnstone"),         # smelted from 2 Quartzite
    ("Rock_Dawnstone_Cobble", AUTO, "Dawnstone Cobble"),
    ("Rock_Sandstone_Cobble", 1, "Sandstone Cobble"),
    ("Rock_Sandstone", AUTO, "Sandstone"),
    ("Rock_Sandstone_Red_Cobble", 1, "Red Sandstone Cobble"),
    ("Rock_Sandstone_Red", AUTO, "Red Sandstone"),
    ("Rock_Sandstone_White_Cobble", 1, "White Sandstone Cobble"),
    ("Rock_Sandstone_White", AUTO, "White Sandstone"),
    ("Rock_Aqua_Cobble", 1, "Aqua Cobble"),
    ("Rock_Aqua", AUTO, "Aqua Stone"),
    ("Rock_Calcite_Cobble", 1, "Calcite Cobble"),
    ("Rock_Calcite", 1, "Calcite"),
    ("Rock_Chalk_Cobble", 1, "Chalk Cobble"),
    ("Rock_Chalk", 1, "Chalk"),
    ("Rock_Lime_Cobble", 1, "Limestone Cobble"),
    ("Rock_Lime", AUTO, "Limestone"),
    ("Rock_Ledge_Cobble", 1, "Ledgestone Cobble"),
    ("Rock_Peach_Cobble", 1, "Peachstone Cobble"),
    ("Rock_Runic_Cobble", 2, "Runic Cobble"),
    ("Rock_Magma_Cooled_Cobble", 1.5, "Cooled Magma Cobble"),
    ("Rock_Magma_Cooled", 1.5, "Cooled Magma"),
    ("Rock_Ice", 1, "Ice"),
    ("Rock_Ice_Permafrost", 1, "Blue Ice"),
    ("Rock_Salt", 2, "Salt Block"),
    ("Rubble_Stone", 0.5, "Stone Rubble"),
    ("Rubble_Stone_Mossy", 0.5, "Mossy Stone Rubble"),
    ("Rubble_Basalt", 0.5, "Basalt Rubble"),
    ("Rubble_Shale", 0.5, "Shale Rubble"),
    ("Rubble_Slate", 0.5, "Slate Rubble"),
    ("Rubble_Volcanic", 0.5, "Volcanic Rubble"),
    ("Rubble_Marble", 0.5, "Marble Rubble"),
    ("Rubble_Quartzite", 0.5, "Quartzite Rubble"),
    ("Rubble_Sandstone", 0.5, "Sandstone Rubble"),
    ("Rubble_Sandstone_Red", 0.5, "Red Sandstone Rubble"),
    ("Rubble_Sandstone_White", 0.5, "White Sandstone Rubble"),
    ("Rubble_Aqua", 0.5, "Aqua Rubble"),
    ("Rubble_Calcite", 0.5, "Calcite Rubble"),
    ("Rubble_Chalk", 0.5, "Chalk Rubble"),
    ("Rubble_Lime", 0.5, "Limestone Rubble"),
    ("Rubble_Magma_Cooled", 0.5, "Cooled Magma Rubble"),
    ("Rubble_Ice", 0.5, "Ice Chunks"),
    ("Soil_Dirt", 0.5, "Dirt"),
    ("Soil_Dirt_Burnt", 0.5, "Burnt Dirt"),
    ("Soil_Dirt_Lush", 0.5, "Lush Dirt"),
    ("Soil_Dirt_Wet", 0.5, "Wet Dirt"),
    ("Soil_Dirt_Cold", 0.5, "Cold Dirt"),
    ("Soil_Dirt_Dry", 0.5, "Dry Dirt"),
    ("Soil_Dirt_Poisoned", 0.5, "Poisoned Dirt"),
    ("Soil_Ash", 0.5, "Ashen Soil"),
    ("Soil_Hive", 0.5, "Hive Soil"),
    ("Soil_Hive_Corrupted", 0.5, "Corrupted Hive Soil"),
    ("Soil_Mud", 1.5, "Mud"),                      # Farmingbench: soil + Plant Fiber
    ("Soil_Mud_Dry", 1.5, "Dry Mud"),
    ("Soil_Gravel", 0.5, "Gravel"),                # Farmingbench: 3 rubble -> 1 (and world blocks)
    ("Soil_Gravel_Mossy", 0.5, "Mossy Gravel"),
    ("Soil_Gravel_Lime", 0.5, "Limestone Gravel"),
    ("Soil_Gravel_Sand", 0.5, "Sandy Gravel"),
    ("Soil_Gravel_Sand_Red", 0.5, "Red Sandy Gravel"),
    ("Soil_Gravel_Sand_White", 0.5, "White Sandy Gravel"),
    ("Soil_Aqua_Gravel", 0.5, "Aqua Gravel"),
    ("Soil_Basalt_Gravel", 0.5, "Basalt Gravel"),
    ("Soil_Calcite_Gravel", 0.5, "Calcite Gravel"),
    ("Soil_Chalk_Gravel", 0.5, "Chalk Gravel"),
    ("Soil_Magma_Cooled_Gravel", 0.5, "Cooled Magma Gravel"),
    ("Soil_Quartzite_Gravel", 0.5, "Quartzite Gravel"),
    ("Soil_Slate_Gravel", 0.5, "Slate Gravel"),
    ("Soil_Volcanic_Gravel", 0.5, "Volcanic Gravel"),
    ("Soil_Pebbles", 0.5, "Marble Gravel"),
    ("Soil_Pebbles_Frozen", 0.5, "Shale Gravel"),
    ("Soil_Sand", 0.5, "Sand"),
    ("Soil_Sand_Ashen", 0.5, "Ashen Sand"),
    ("Soil_Sand_Red", 0.5, "Red Sand"),
    ("Soil_Sand_White", 0.5, "White Sand"),
    ("Soil_Snow", 0.5, "Snow"),
    ("Soil_Clay", 1, "Clay"),
    ("Soil_Clay_Beige", 1, "Beige Clay"),
    ("Soil_Clay_Black", 1, "Black Clay"),
    ("Soil_Clay_Blue", 1, "Blue Clay"),
    ("Soil_Clay_Cyan", 1, "Cyan Clay"),
    ("Soil_Clay_Green", 1, "Green Clay"),
    ("Soil_Clay_Grey", 1, "Gray Clay"),
    ("Soil_Clay_GreyLight", 1, "Light Gray Clay"),
    ("Soil_Clay_Lime", 1, "Lime Clay"),
    ("Soil_Clay_Ocean", 1, "Ocean Clay"),
    ("Soil_Clay_Orange", 1, "Orange Clay"),
    ("Soil_Clay_Pink", 1, "Pink Clay"),
    ("Soil_Clay_Purple", 1, "Purple Clay"),
    ("Soil_Clay_Red", 1, "Red Clay"),
    ("Soil_Clay_Scarlet", 1, "Scarlet Clay"),
    ("Soil_Clay_White", 1, "White Clay"),
    ("Soil_Clay_Yellow", 1, "Yellow Clay"),
    ("Soil_Clay_Cobble_Orange", AUTO, "Orange Clay Cobble"),   # Furnace: 2 Clay -> 1
    # ---- Foraging bag
    ("Ingredient_Stick", 1, "Stick"),
    ("Wood_Sticks", 5, "Pile of Sticks"),          # fix round: Farmingbench, 5 sticks -> 1
    ("Ingredient_Fibre", 1, "Plant Fiber"),
    ("Ingredient_Tree_Bark", 2, "Tree Bark"),
    ("Ingredient_Tree_Sap", 12, "Tree Sap"),     # 0.1.5 (Skyy 2026-10-05): 4 -> 12 (PRICE_015)
    ("Wood_Bamboo_Trunk", 2, "Bamboo Log"),
    ("Wood_Burnt_Trunk", 2, "Burnt Log"),
    ("Wood_Ash_Trunk", 3, "Ash Log"),
    ("Wood_Aspen_Trunk", 3, "Aspen Log"),
    ("Wood_Beech_Trunk", 3, "Beech Log"),
    ("Wood_Birch_Trunk", 3, "Birch Log"),
    ("Wood_Cedar_Trunk", 3, "Cedar Log"),
    ("Wood_Dry_Trunk", 3, "Dry Log"),
    ("Wood_Fir_Trunk", 3, "Fir Log"),
    ("Wood_Jungle_Trunk", 3, "Jungle Log"),
    ("Wood_Oak_Trunk", 3, "Oak Log"),
    ("Wood_Palm_Trunk", 3, "Palm Tree Log"),
    ("Wood_Apple_Trunk", 8, "Apple Log"),
    ("Wood_Banyan_Trunk", 8, "Banyan Log"),
    ("Wood_Bottletree_Trunk", 8, "Bottletree Log"),
    ("Wood_Camphor_Trunk", 8, "Camphor Log"),
    ("Wood_Fig_Blue_Trunk", 8, "Blue Fig Log"),
    ("Wood_Gumboab_Trunk", 8, "Gumboab Log"),
    ("Wood_Maple_Trunk", 8, "Maple Log"),
    ("Wood_Palo_Trunk", 8, "Palo Log"),
    ("Wood_Poisoned_Trunk", 8, "Poisoned Log"),
    ("Wood_Sallow_Trunk", 8, "Sallow Log"),
    ("Wood_Spiral_Trunk", 8, "Spiral Log"),
    ("Wood_Windwillow_Trunk", 8, "Windwillow Log"),
    ("Wood_Wisteria_Wild_Trunk", 8, "Wild Wisteria Log"),
    ("Wood_Amber_Trunk", 20, "Amber Log"),
    ("Wood_Redwood_Trunk", 20, "Redwood Log"),
    ("Wood_Azure_Trunk", 48, "Azure Log"),
    ("Wood_Petrified_Trunk", 48, "Petrified Log"),
    ("Wood_Crystal_Trunk", 128, "Crystalwood Log"),
    ("Wood_Fire_Trunk", 128, "Fire Log"),
    ("Wood_Ice_Trunk", 128, "Frostwood Log"),
    ("Wood_Stormbark_Trunk", 128, "Stormbark Log"),
    # fix round: planks (the bag text says "logs, planks"): Builders bench, 1 log of the family -> 1 plank = its cheapest log
    ("Wood_Hardwood_Planks", 2, "Hardwood Planks"),
    ("Wood_Tropicalwood_Planks", 2, "Tropical Wood Planks"),
    ("Wood_Blackwood_Planks", 2, "Blackwood Planks"),
    ("Wood_Softwood_Planks", 3, "Softwood Planks"),
    ("Wood_Lightwood_Planks", 3, "Lightwood Planks"),
    ("Wood_Darkwood_Planks", 3, "Darkwood Planks"),
    ("Wood_Drywood_Planks", 3, "Drywood Planks"),
    ("Wood_Goldenwood_Planks", 3, "Goldenwood Planks"),
    ("Wood_Greenwood_Planks", 3, "Greenwood Planks"),
    ("Wood_Redwood_Planks", 4, "Redwood Planks"),
    ("Wood_Deadwood_Planks", 6, "Deadwood Planks"),
    # ---- Farming bag
    ("Plant_Crop_Carrot_Item", 2, "Carrot"),
    ("Plant_Crop_Lettuce_Item", 2, "Lettuce"),
    ("Plant_Crop_Potato_Item", 40, "Potato"),
    ("Plant_Crop_Wheat_Item", 2, "Wheat"),
    ("Plant_Crop_Corn_Item", 2, "Corn"),
    ("Plant_Crop_Cotton_Item", 16, "Cotton"),
    ("Plant_Crop_Onion_Item", 40, "Onion"),
    ("Plant_Crop_Rice_Item", 16, "Rice"),
    ("Plant_Crop_Tomato_Item", 16, "Tomato"),
    ("Plant_Crop_Turnip_Item", 6, "Turnip"),
    ("Plant_Crop_Aubergine_Item", 6, "Aubergine"),
    ("Plant_Crop_Cauliflower_Item", 6, "Cauliflower"),
    ("Plant_Crop_Chilli_Item", 16, "Chilli"),
    ("Plant_Crop_Pumpkin_Item", 6, "Pumpkin"),
    ("Plant_Hay_Bundle", 1, "Bundle of Hay"),      # fix round
    ("Plant_Seeds_Aubergine", 2, "Aubergine Seed Bag"),
    ("Plant_Seeds_Carrot", 1, "Carrot Seed Bag"),
    ("Plant_Seeds_Cauliflower", 2, "Cauliflower Seed Bag"),
    ("Plant_Seeds_Chilli", 3.5, "Chilli Seed Bag"),
    ("Plant_Seeds_Corn", 1, "Corn Seed Bag"),
    ("Plant_Seeds_Cotton", 4, "Cotton Seed Bag"),
    ("Plant_Seeds_Lettuce", 1, "Lettuce Seed Bag"),
    ("Plant_Seeds_Onion", 6, "Onion Bulb"),
    ("Plant_Seeds_Pine", 1, "Pinecone"),
    ("Plant_Seeds_Potato", 6, "Potato Sprout"),
    ("Plant_Seeds_Pumpkin", 2, "Pumpkin Seed Bag"),
    ("Plant_Seeds_Rice", 4, "Rice Seed Bag"),
    ("Plant_Seeds_Tomato", 3.5, "Tomato Seed Bag"),
    ("Plant_Seeds_Turnip", 2, "Turnip Seed Bag"),
    ("Plant_Seeds_Wheat", 1, "Wheat Seed Bag"),
    ("Plant_Seeds_Wild", 1, "Wild Grass Seed Bag"),          # fix round
    ("Plant_Seeds_Sunflower", 1, "Sunflower Seed Bag"),
    # fix round: Eternal seeds = the value of their Farmingbench recipe (Essence of Life + crops + the seed)
    ("Plant_Seeds_Carrot_Eternal", 50, "Carrot Seed Bag (Eternal)"),
    ("Plant_Seeds_Lettuce_Eternal", 37, "Lettuce Seed Bag (Eternal)"),
    ("Plant_Seeds_Potato_Eternal", 2400, "Potato Sprout (Eternal)"),
    ("Plant_Seeds_Wheat_Eternal", 37, "Wheat Seed Bag (Eternal)"),
    ("Plant_Seeds_Corn_Eternal", 50, "Corn Seed Bag (Eternal)"),
    ("Plant_Seeds_Cotton_Eternal", 800, "Cotton Seed Bag (Eternal)"),
    ("Plant_Seeds_Onion_Eternal", 2400, "Onion Bulb (Eternal)"),
    ("Plant_Seeds_Rice_Eternal", 800, "Rice Seed Bag (Eternal)"),
    ("Plant_Seeds_Tomato_Eternal", 600, "Tomato Seed Bag (Eternal)"),
    ("Plant_Seeds_Turnip_Eternal", 200, "Turnip Seed Bag (Eternal)"),
    ("Plant_Seeds_Aubergine_Eternal", 200, "Aubergine Seed Bag (Eternal)"),
    ("Plant_Seeds_Cauliflower_Eternal", 200, "Cauliflower Seed Bag (Eternal)"),
    ("Plant_Seeds_Chilli_Eternal", 600, "Chilli Seed Bag (Eternal)"),
    ("Plant_Seeds_Pumpkin_Eternal", 200, "Pumpkin Seed Bag (Eternal)"),
    # fix round: saplings = their tree's log price (Farmingbench: 15 Essence of Life -> 1)
    ("Plant_Sapling_Bamboo", 2, "Bamboo Sapling"),
    ("Plant_Sapling_Ash", 3, "Ash Sapling"),
    ("Plant_Sapling_Aspen", 3, "Aspen Sapling"),
    ("Plant_Sapling_Beech", 3, "Beech Sapling"),
    ("Plant_Sapling_Birch", 3, "Birch Sapling"),
    ("Plant_Sapling_Cedar", 3, "Cedar Sapling"),
    ("Plant_Sapling_Dry", 3, "Dry Sapling"),
    ("Plant_Sapling_Jungle", 3, "Jungle Sapling"),
    ("Plant_Sapling_Oak", 3, "Oak Sapling"),
    ("Plant_Sapling_Palm", 3, "Palm Sapling"),
    ("Plant_Sapling_Spruce", 3, "Spruce Sapling"),
    ("Plant_Sapling_Spruce_Frozen", 3, "Frozen Spruce Sapling"),
    ("Plant_Sapling_Apple", 8, "Apple Sapling"),
    ("Plant_Sapling_Banyan", 8, "Banyan Sapling"),
    ("Plant_Sapling_Bottletree", 8, "Bottletree Sapling"),
    ("Plant_Sapling_Camphor", 6, "Camphor Sapling"),
    ("Plant_Sapling_Fig_Blue", 8, "Blue Fig Sapling"),
    ("Plant_Sapling_Gumboab", 6, "Gumboab Sapling"),
    ("Plant_Sapling_Maple", 8, "Maple Sapling"),
    ("Plant_Sapling_Palo", 8, "Palo Sapling"),
    ("Plant_Sapling_Poisoned", 8, "Poisoned Sapling"),
    ("Plant_Sapling_Sallow", 8, "Sallow Sapling"),
    ("Plant_Sapling_Spiral", 8, "Spiral Sapling"),
    ("Plant_Sapling_Windwillow", 8, "Willow Sapling"),
    ("Plant_Sapling_Wisteria_Wild", 8, "Wild Wisteria Sapling"),
    ("Plant_Sapling_Amber", 9, "Amber Sapling"),
    ("Plant_Sapling_Redwood", 12, "Redwood Sapling"),
    ("Plant_Sapling_Azure", 12, "Azure Sapling"),
    ("Plant_Sapling_Petrified", 18, "Petrified Pine Sapling"),
    ("Plant_Sapling_Crystal", 9, "Crystal Sapling"),
    ("Plant_Sapling_Fire", 18, "Fire Sapling"),
    ("Plant_Sapling_Ice", 9, "Frostwood Sapling"),
    ("Plant_Sapling_Stormbark", 9, "Stormbark Sapling"),
    ("Plant_Fruit_Berries_Red", 1, "Wild Berries"),
    ("Plant_Fruit_Apple", 2, "Apple"),
    ("Plant_Fruit_Pinkberry", 2, "Pinkberry"),
    ("Plant_Fruit_Coconut", 3, "Coconut"),
    ("Plant_Fruit_Poison", 3, "Poison Tree Fruit"),
    ("Plant_Fruit_Azure", 4, "Azure Fruit"),
    ("Plant_Fruit_Spiral", 4, "Spiral Tree Fruit"),
    ("Plant_Fruit_Windwillow", 4, "Windwillow Fruit"),
    ("Plant_Fruit_Mango", 6, "Magic Mango"),
    ("Plant_Crop_Health1", 4, "Blood Rose"),
    ("Plant_Crop_Mana1", 4, "Azure Fern"),
    ("Plant_Crop_Stamina1", 4, "Storm Thistle"),
    ("Plant_Crop_Health2", 6, "Bloodcap Mushroom"),
    ("Plant_Crop_Mana2", 6, "Azurecap Mushroom"),
    ("Plant_Crop_Stamina2", 6, "Stormcap Mushroom"),
    ("Plant_Crop_Health3", 8, "Blood Leaf"),
    ("Plant_Crop_Mana3", 8, "Azure Kelp"),
    ("Plant_Crop_Stamina3", 8, "Storm Rush"),
    # fix round: the herb seed bags (Alchemybench from Essence of the Void, also dropped by the herbs) - half the herb
    ("Plant_Seeds_Health1", 2, "Blood Rose Seed Bag"),
    ("Plant_Seeds_Mana1", 2, "Azure Fern Seed Bag"),
    ("Plant_Seeds_Stamina1", 2, "Storm Thistle Seed Bag"),
    ("Plant_Seeds_Health2", 3, "Bloodcap Spawn Bag"),
    ("Plant_Seeds_Mana2", 3, "Azurecap Spawn Bag"),
    ("Plant_Seeds_Stamina2", 3, "Stormcap Spawn Bag"),
    ("Plant_Seeds_Health3", 4, "Blood Leaf Seed Bag"),
    ("Plant_Seeds_Mana3", 4, "Azure Kelp Seed Bag"),
    ("Plant_Seeds_Stamina3", 4, "Storm Sapling Seed Bag"),
    ("Plant_Crop_Mushroom_Cap_Brown", 2, "Brown Cap Mushroom"),
    ("Plant_Crop_Mushroom_Cap_Green", 2, "Spotted Green Cap Mushroom"),
    ("Plant_Crop_Mushroom_Cap_Poison", 2, "Spotted Allium Cap Mushroom"),
    ("Plant_Crop_Mushroom_Cap_Red", 2, "Red Cap Mushroom"),
    ("Plant_Crop_Mushroom_Cap_White", 2, "White Cap Mushroom"),
    ("Plant_Crop_Mushroom_Common_Blue", 2, "Blue Common Mushroom"),
    ("Plant_Crop_Mushroom_Common_Brown", 2, "Brown Common Mushroom"),
    ("Plant_Crop_Mushroom_Common_Lime", 2, "Puffy Green Common Mushroom"),
    ("Plant_Crop_Mushroom_Flatcap_Blue", 2, "Blue Flatcap Mushroom"),
    ("Plant_Crop_Mushroom_Flatcap_Green", 2, "Green Flatcap Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Blue", 3, "Blue Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Green", 3, "Green Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Orange", 3, "Orange Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Purple", 3, "Purple Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Red", 3, "Red Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Glowing_Violet", 3, "Violet Glowing Mushroom"),
    ("Plant_Crop_Mushroom_Shelve_Brown", 2, "Brown Mushroom Shelf"),
    ("Plant_Crop_Mushroom_Shelve_Green", 2, "Green Mushroom Shelf"),
    ("Plant_Crop_Mushroom_Shelve_Yellow", 2, "Yellow Mushroom Shelf"),
    ("Plant_Moss_Blue", 1, "Blue Moss"),
    ("Plant_Moss_Green", 1, "Moss"),
    ("Plant_Moss_Green_Dark", 1, "Dark Green Moss"),
    ("Plant_Moss_Red", 1, "Red Moss"),
    ("Plant_Moss_Yellow", 1, "Yellow Moss"),
    ("Plant_Petals_Azure", 1, "Azure Petals"),
    ("Plant_Petals_Black", 1, "Black Petals"),
    ("Plant_Petals_Blood", 1, "Blood Petals"),
    ("Plant_Petals_Blue", 1, "Blue Petals"),
    ("Plant_Petals_Cyan", 1, "Cyan Petals"),
    ("Plant_Petals_Green", 1, "Green Petals"),
    ("Plant_Petals_Orange", 1, "Orange Petals"),
    ("Plant_Petals_Pink", 1, "Pink Petals"),
    ("Plant_Petals_Purple", 1, "Purple Petals"),
    ("Plant_Petals_Red", 1, "Red Petals"),
    ("Plant_Petals_Storm", 1, "Storm Petals"),
    ("Plant_Petals_White", 1, "White Petals"),
    ("Plant_Petals_Yellow", 1, "Yellow Petals"),
    ("Food_Beef_Raw", 4, "Raw Beef"),
    ("Food_Pork_Raw", 4, "Raw Pork"),
    ("Food_Chicken_Raw", 3, "Raw Chicken"),
    ("Food_Wildmeat_Raw", 3, "Raw Wildmeat"),
    ("Food_Egg", 2, "Egg"),
    ("Food_Fish_Raw", 2, "Raw Fish"),
    ("Food_Fish_Raw_Uncommon", 2.5, "Raw Fish"),    # fix round: Cookingbench, 1 uncommon fish -> 2 (the official name is also "Raw Fish")
    ("Fish_Bluegill_Item", 3, "Bluegill"),
    ("Fish_Catfish_Item", 3, "Catfish"),
    ("Fish_Minnow_Item", 3, "Minnow"),
    ("Fish_Tang_Blue_Item", 5, "Blue Tang"),
    ("Fish_Tang_Chevron_Item", 5, "Chevron Tang"),
    ("Fish_Tang_Lemon_Peel_Item", 5, "Lemon Peel Tang"),
    ("Fish_Tang_Sailfin_Item", 5, "Sailfin Tang"),
    ("Fish_Clownfish_Item", 8, "Clownfish"),
    ("Fish_Pufferfish_Item", 8, "Pufferfish"),
    ("Fish_Salmon_Item", 8, "Salmon"),
    ("Fish_Trout_Rainbow_Item", 8, "Rainbow Trout"),
    ("Fish_Jellyfish_Blue_Item", 15, "Blue Jellyfish"),
    ("Fish_Jellyfish_Cyan_Item", 15, "Cyan Jellyfish"),
    ("Fish_Jellyfish_Green_Item", 15, "Green Jellyfish"),
    ("Fish_Jellyfish_Red_Item", 15, "Red Jellyfish"),
    ("Fish_Jellyfish_Yellow_Item", 15, "Yellow Jellyfish"),
    ("Fish_Crab_Item", 30, "Crab"),
    ("Fish_Eel_Moray_Item", 30, "Moray Eel"),
    ("Fish_Frostgill_Item", 30, "Frostgill"),
    ("Fish_Jellyfish_Man_Of_War_Item", 30, "Man Of War"),
    ("Fish_Lobster_Item", 30, "Lobster"),
    ("Fish_Pike_Item", 30, "Pike"),
    ("Fish_Piranha_Black_Item", 30, "Black Piranha"),
    ("Fish_Piranha_Item", 30, "Piranha"),
    ("Fish_Shark_Hammerhead_Item", 30, "Hammerhead Shark"),
    ("Fish_Shellfish_Lava_Item", 30, "Lava Coelacanth"),
    ("Fish_Snapjaw_Item", 30, "Snapjaw"),
    ("Fish_Trilobite_Black_Item", 30, "Black Trilobite"),
    ("Fish_Trilobite_Item", 30, "Trilobite"),
    ("Fish_Whale_Humpback_Item", 30, "Humpback Whale"),
    ("Ingredient_Life_Essence", 0.5, "Essence of Life"),
    ("Ingredient_Life_Essence_Concentrated", 50, "Greater Essence of Life"),   # fix round: 100 Essence of Life <-> 1 (both ways)
    ("Ingredient_Poop", 0.5, "Poop"),
    # ---- Combat bag
    ("Ingredient_Bone_Fragment", 3, "Bone Fragments"),
    ("Ingredient_Chitin_Sturdy", 15, "Sturdy Chitin"),
    ("Ingredient_Feathers_Light", 4, "White Feathers"),
    ("Ingredient_Feathers_Blue", 5, "Blue Feathers"),
    ("Ingredient_Feathers_Dark", 6, "Dark Feathers"),
    ("Ingredient_Feathers_Red", 6, "Red Feathers"),
    ("Ingredient_Sac_Venom", 15, "Venom Sac"),
    ("Ingredient_Powder_Boom", 8, "Boom Powder"),
    ("Ingredient_Fire_Essence", 25, "Essence of Fire"),
    ("Ingredient_Ice_Essence", 25, "Essence of Ice"),
    ("Ingredient_Water_Essence", 25, "Essence of Water"),
    ("Ingredient_Lightning_Essence", 30, "Essence of Lightning"),
    ("Ingredient_Void_Essence", 40, "Essence of the Void"),
    ("Ingredient_Voidheart", 120, "Voidheart"),
    # ---- Smithing bag
    ("Ingredient_Bar_Copper", AUTO, "Copper Ingot"),
    ("Ingredient_Bar_Bronze", 40, "Bronze Ingot"),  # fix round: 16 -> 21 (>= 20.3 or buy -> Ancient Steel gloves -> salvage -> smelt / tan -> sell pays)
    ("Ingredient_Bar_Iron", AUTO, "Iron Ingot"),
    ("Ingredient_Bar_Thorium", AUTO, "Thorium Ingot"),
    ("Ingredient_Bar_Lead_SkyWynn", AUTO, "Lead Ingot"),            # 0.1.20: 1 Lead Ore at the Furnace (18 s)
    ("Ingredient_Bar_Dusk_SkyWynn", AUTO, "Dusk Ingot"),            # 0.1.20: alloy Thorium + Lead Ingot (SkyyAlloy, 36 s)
    ("Ingredient_Bar_Silver", AUTO, "Silver Ingot"),
    ("Ingredient_Bar_Cobalt", AUTO, "Cobalt Ingot"),
    ("Ingredient_Bar_Chromium_SkyWynn", AUTO, "Chromium Ingot"),    # 0.1.20: 1 Chromium Ore (18 s)
    ("Ingredient_Bar_Azurvane_SkyWynn", AUTO, "Azurvane Ingot"),    # 0.1.20: alloy Cobalt + Chromium Ingot (36 s)
    ("Ingredient_Bar_Gold", AUTO, "Gold Ingot"),
    ("Ingredient_Bar_Electrum_SkyWynn", AUTO, "Electrum Ingot"),    # 0.1.20: alloy Gold + Silver Ingot (SkyyAlloy, 14 s), a charm metal
    ("Ingredient_Bar_Adamantite", AUTO, "Adamantite Ingot"),
    ("Ingredient_Bar_Slag_SkyWynn", AUTO, "Slag Ingot"),            # 0.1.20: 1 Slag Ore (20 s)
    ("Ingredient_Bar_Cinder_SkyWynn", AUTO, "Cinder Ingot"),        # 0.1.20: alloy Adamantite + Slag Ingot (40 s)
    ("Ingredient_Bar_Mithril", AUTO, "Mithril Ingot"),
    ("Ingredient_Bar_Titanium_SkyWynn", AUTO, "Titanium Ingot"),    # 0.1.20: 1 Titanium Ore (30 s)
    ("Ingredient_Bar_Lumen_SkyWynn", AUTO, "Lumen Ingot"),          # 0.1.20: alloy Mithril + Titanium Ingot (60 s)
    ("Ingredient_Bar_Onyxium", AUTO, "Onyxium Ingot"),  # fix round: follows Onyxium Ore (was a fixed 70)
    ("Ingredient_Bar_Prisma", AUTO, "Prisma Ingot"),    # fix round: follows Prisma Ore (was a fixed 90)
    ("Ingredient_Charcoal", AUTO, "Charcoal"),
    ("Ingredient_Hide_Soft", 8, "Soft Hide"),
    ("Ingredient_Hide_Light", 12, "Light Hide"),
    ("Ingredient_Hide_Medium", 24, "Medium Hide"),
    ("Ingredient_Hide_Heavy", 36, "Heavy Hide"),
    ("Ingredient_Hide_Scaled", 48, "Scaled Hide"),
    ("Ingredient_Hide_Storm", 60, "Storm Hide"),
    ("Ingredient_Hide_Dark", 72, "Dark Hide"),
    ("Ingredient_Hide_Prismic", 90, "Prismatic Hide"),
    ("Ingredient_Leather_Soft", AUTO, "Soft Leather"),
    ("Ingredient_Leather_Light", AUTO, "Light Leather"),
    ("Ingredient_Leather_Medium", AUTO, "Medium Leather"),
    ("Ingredient_Leather_Heavy", AUTO, "Heavy Leather"),
    ("Ingredient_Leather_Scaled", AUTO, "Scaled Leather"),
    ("Ingredient_Leather_Storm", AUTO, "Storm Leather"),
    ("Ingredient_Leather_Dark", AUTO, "Dark Leather"),
    ("Ingredient_Leather_Prismic", AUTO, "Prismatic Leather"),
    ("Ingredient_Fabric_Scrap_Wool", 4, "Wool Scraps"),
    ("Ingredient_Fabric_Scrap_Linen", 4, "Linen Scraps"),
    ("Ingredient_Fabric_Scrap_Cotton", 4, "Cotton Scraps"),
    ("Ingredient_Fabric_Scrap_Silk", 16, "Silk Scraps"),
    ("Ingredient_Fabric_Scrap_Shadoweave", 40, "Shadoweave Scraps"),
    ("Ingredient_Fabric_Scrap_Cindercloth", 96, "Cindercloth Scraps"),
    ("Ingredient_Fabric_Scrap_Stormsilk", 256, "Stormsilk Scraps"),
    ("Ingredient_Fabric_Scrap_Prismaloom", 640, "Prismaloom Scraps"),
    # fix round: the bolts are processed goods (PREMIUM_ITEMS): woven at the Loombench from 1 Cotton (Wool: 1 Wool Scraps -> 4 at the
    # Furniture bench), priced from that input x (1 + premium) - they follow it (were a fixed 1.1 / 3.5)
    ("Ingredient_Bolt_Wool", AUTO, "Bolt of Wool"),
    ("Ingredient_Bolt_Linen", AUTO, "Bolt of Linen"),
    ("Ingredient_Bolt_Cotton", AUTO, "Bolt of Cotton"),
    ("Ingredient_Bolt_Silk", AUTO, "Bolt of Silk"),
    ("Ingredient_Bolt_Shadoweave", AUTO, "Bolt of Shadoweave"),
    ("Ingredient_Bolt_Cindercloth", AUTO, "Bolt of Cindercloth"),
    ("Ingredient_Bolt_Stormsilk", AUTO, "Bolt of Stormsilk"),
    ("Ingredient_Bolt_Prismaloom", AUTO, "Bolt of Prismaloom"),
    ("Ingredient_Strap_Leather", 6, "Leather Strap"),
    ("Ingredient_Stud_Iron", 4, "Iron Stud"),
] + [(EN.PREFIX + _t[0], AUTO, _t[6]) for _t in EN.TABLE]   # 0.1.10: the 19 Enchanted materials (priced from their recipe)
# 0.1.19: every row of the live table whose base is a product (a resource-type row: its cheapest product, checked by the PROC == AUTO rule);
# a row whose base item has NO product is left off the market (no invented price) - EN_OFF, printed; its item JSON is not joined either
_PIDS0 = set(_r[0] for _r in PRODUCTS if not _r[0].startswith(EN.PREFIX))
EN_OFF = [_t for _t in EN.TABLE if _t[1] == "I" and _t[2] not in _PIDS0]
PRODUCTS = [_r for _r in PRODUCTS if _r[0] not in set(EN.PREFIX + _t[0] for _t in EN_OFF)]
EN.TABLE = [_t for _t in EN.TABLE if _t not in EN_OFF]
EN.KEYS = [_t[0] for _t in EN.TABLE]
EN.IDS = [EN.PREFIX + _k for _k in EN.KEYS]
EN.RIDS = [_i + EN.RECIPE_SUFFIX for _i in EN.IDS]
assert EN.IDS[:20] == EN20_IDS and [_r[0] for _r in PRODUCTS if _r[0].startswith(EN.PREFIX)] == EN.IDS and len(EN.IDS) + len(EN_OFF) == len(_EN_ALL.TABLE), "0.1.19: the 20 frozen rows stay first and listed"
print("0.1.19: %d Enchanted products from tools/skyyench.py (%d rows); left off the market (base not a Bazaar product, no invented price): %s"
      % (len(EN.IDS), len(_EN_ALL.TABLE), ", ".join("%s%s (base %s)" % (EN.PREFIX, _t[0], _t[2]) for _t in EN_OFF) or "none"))

# Skyy 2026-10-03: "small medium and large leather ... in the combat section" - light / medium / heavy hides and leathers are Smithing-bag
# items that are ALSO listed in Combat (one market, one price, two tabs)
EXTRA_TABS = {"Ingredient_Hide_Light": ("Combat",), "Ingredient_Hide_Medium": ("Combat",), "Ingredient_Hide_Heavy": ("Combat",),
              "Ingredient_Leather_Light": ("Combat",), "Ingredient_Leather_Medium": ("Combat",), "Ingredient_Leather_Heavy": ("Combat",)}

# 0.1.4: every product whose DEFAULT price moved: id -> (0.1.3 default, 0.1.4 default). The one-time update (Catalog.migrate14) moves a
# line still holding the 0.1.3 value; the build checks the PRODUCTS rows against it (tools/bazaar_0_1_4_patch.py holds the families)
PRICE_014 = {
    "Ingredient_Bar_Bronze": (21, 40),
    "Ingredient_Fabric_Scrap_Cindercloth": (12, 96),
    "Ingredient_Fabric_Scrap_Prismaloom": (20, 640),
    "Ingredient_Fabric_Scrap_Shadoweave": (10, 40),
    "Ingredient_Fabric_Scrap_Silk": (8, 16),
    "Ingredient_Fabric_Scrap_Stormsilk": (16, 256),
    "Ingredient_Hide_Dark": (36, 72),
    "Ingredient_Hide_Heavy": (18, 36),
    "Ingredient_Hide_Light": (6, 12),
    "Ingredient_Hide_Medium": (12, 24),
    "Ingredient_Hide_Prismic": (45, 90),
    "Ingredient_Hide_Scaled": (24, 48),
    "Ingredient_Hide_Soft": (4, 8),
    "Ingredient_Hide_Storm": (30, 60),
    "Ore_Adamantite": (30, 480),
    "Ore_Cobalt": (18, 144),
    "Ore_Iron": (8, 16),
    "Ore_Mithril": (45, 1440),
    "Ore_Onyxium": (58, 3712),
    "Ore_Thorium": (12, 48),
    "Plant_Crop_Aubergine_Item": (4, 6),
    "Plant_Crop_Cauliflower_Item": (4, 6),
    "Plant_Crop_Chilli_Item": (4, 16),
    "Plant_Crop_Corn_Item": (3, 2),
    "Plant_Crop_Cotton_Item": (3, 16),
    "Plant_Crop_Onion_Item": (3, 40),
    "Plant_Crop_Potato_Item": (2, 40),
    "Plant_Crop_Pumpkin_Item": (5, 6),
    "Plant_Crop_Rice_Item": (3, 16),
    "Plant_Crop_Tomato_Item": (3, 16),
    "Plant_Crop_Turnip_Item": (3, 6),
    "Plant_Sapling_Amber": (5, 9),
    "Plant_Sapling_Apple": (4, 8),
    "Plant_Sapling_Azure": (6, 12),
    "Plant_Sapling_Banyan": (4, 8),
    "Plant_Sapling_Bottletree": (4, 8),
    "Plant_Sapling_Camphor": (4, 6),
    "Plant_Sapling_Crystal": (8, 9),
    "Plant_Sapling_Fig_Blue": (4, 8),
    "Plant_Sapling_Fire": (8, 18),
    "Plant_Sapling_Gumboab": (4, 6),
    "Plant_Sapling_Ice": (8, 9),
    "Plant_Sapling_Maple": (4, 8),
    "Plant_Sapling_Palo": (4, 8),
    "Plant_Sapling_Petrified": (6, 18),
    "Plant_Sapling_Poisoned": (4, 8),
    "Plant_Sapling_Redwood": (5, 12),
    "Plant_Sapling_Sallow": (4, 8),
    "Plant_Sapling_Spiral": (4, 8),
    "Plant_Sapling_Stormbark": (8, 9),
    "Plant_Sapling_Windwillow": (4, 8),
    "Plant_Sapling_Wisteria_Wild": (4, 8),
    "Plant_Seeds_Aubergine": (1, 2),
    "Plant_Seeds_Aubergine_Eternal": (151, 200),
    "Plant_Seeds_Carrot_Eternal": (46, 50),
    "Plant_Seeds_Cauliflower": (1, 2),
    "Plant_Seeds_Cauliflower_Eternal": (126, 200),
    "Plant_Seeds_Chilli": (1, 3.5),
    "Plant_Seeds_Chilli_Eternal": (151, 600),
    "Plant_Seeds_Corn_Eternal": (61, 50),
    "Plant_Seeds_Cotton": (1, 4),
    "Plant_Seeds_Cotton_Eternal": (161, 800),
    "Plant_Seeds_Lettuce_Eternal": (31, 37),
    "Plant_Seeds_Onion": (1, 6),
    "Plant_Seeds_Onion_Eternal": (201, 2400),
    "Plant_Seeds_Potato": (1, 6),
    "Plant_Seeds_Potato_Eternal": (151, 2400),
    "Plant_Seeds_Pumpkin": (1, 2),
    "Plant_Seeds_Pumpkin_Eternal": (181, 200),
    "Plant_Seeds_Rice": (1, 4),
    "Plant_Seeds_Rice_Eternal": (161, 800),
    "Plant_Seeds_Tomato": (1, 3.5),
    "Plant_Seeds_Tomato_Eternal": (121, 600),
    "Plant_Seeds_Turnip": (1, 2),
    "Plant_Seeds_Turnip_Eternal": (101, 200),
    "Plant_Seeds_Wheat_Eternal": (31, 37),
    "Rock_Gem_Diamond": (60, 120),
    "Rock_Gem_Voidstone": (60, 120),
    "Wood_Amber_Trunk": (5, 20),
    "Wood_Apple_Trunk": (4, 8),
    "Wood_Azure_Trunk": (6, 48),
    "Wood_Banyan_Trunk": (4, 8),
    "Wood_Bottletree_Trunk": (4, 8),
    "Wood_Camphor_Trunk": (4, 8),
    "Wood_Crystal_Trunk": (8, 128),
    "Wood_Fig_Blue_Trunk": (4, 8),
    "Wood_Fire_Trunk": (8, 128),
    "Wood_Gumboab_Trunk": (4, 8),
    "Wood_Ice_Trunk": (8, 128),
    "Wood_Maple_Trunk": (4, 8),
    "Wood_Palo_Trunk": (4, 8),
    "Wood_Petrified_Trunk": (6, 48),
    "Wood_Poisoned_Trunk": (4, 8),
    "Wood_Redwood_Trunk": (5, 20),
    "Wood_Sallow_Trunk": (4, 8),
    "Wood_Spiral_Trunk": (4, 8),
    "Wood_Stormbark_Trunk": (8, 128),
    "Wood_Windwillow_Trunk": (4, 8),
    "Wood_Wisteria_Wild_Trunk": (4, 8),
}
# 0.1.5: default prices that moved in 0.1.5: id -> (0.1.4 default, 0.1.5 default). NO one-time update: products.properties keeps every
# saved price (Skyy set Tree Sap 12 live already); only the seed line of a fresh install / a missing line changes. The 0.1.2 -> 0.1.3
# update (servers still on 0.1.2 data) moves a 0.1.2 default line to the current seed line, as it does for every product.
PRICE_015 = {
    "Ingredient_Tree_Sap": (4, 12),     # Skyy: "with how little seems to drop, id raise the price on sap"
}
# the vanilla farming path (Farmingbench RequiredTierLevel of the normal seed recipe; checked against Assets.zip below) -> price tier
VANILLA_SEED_TIER = {'Lettuce': 1, 'Wheat': 1, 'Carrot': 2, 'Corn': 2, 'Cauliflower': 3, 'Turnip': 3, 'Aubergine': 4, 'Pumpkin': 4, 'Chilli': 5, 'Tomato': 5, 'Cotton': 6, 'Rice': 6, 'Onion': 7, 'Potato': 7}
PRICE_TIER = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
CROP_PRICE, SEED_PRICE, ETERNAL_PRICE = {1: 2, 2: 6, 3: 16, 4: 40}, {1: 1, 2: 2, 3: 4, 4: 8}, {1: 50, 2: 200, 3: 800, 4: 3200}
SEED_CAP = {'Chilli': 3.5, 'Tomato': 3.5, 'Onion': 6, 'Potato': 6}
ETERNAL_CAP = {'Lettuce': 37, 'Wheat': 37, 'Chilli': 600, 'Tomato': 600, 'Onion': 2400, 'Potato': 2400}
SAPLING_TIER = {'Bamboo': 1, 'Ash': 1, 'Aspen': 1, 'Beech': 1, 'Birch': 1, 'Cedar': 1, 'Dry': 1, 'Jungle': 1, 'Oak': 1, 'Palm': 1, 'Spruce': 1, 'Spruce_Frozen': 1, 'Apple': 2, 'Banyan': 2, 'Bottletree': 2, 'Camphor': 2, 'Fig_Blue': 2, 'Gumboab': 2, 'Maple': 2, 'Palo': 2, 'Poisoned': 2, 'Sallow': 2, 'Spiral': 2, 'Windwillow': 2, 'Wisteria_Wild': 2, 'Amber': 3, 'Redwood': 3, 'Azure': 4, 'Petrified': 4, 'Crystal': 5, 'Fire': 5, 'Ice': 5, 'Stormbark': 5}
SAPLING_ESSENCE = {'Bamboo': 15, 'Ash': 15, 'Aspen': 5, 'Beech': 5, 'Birch': 10, 'Cedar': 25, 'Dry': 30, 'Jungle': 15, 'Oak': 15, 'Palm': 35, 'Spruce': 15, 'Spruce_Frozen': 15, 'Apple': None, 'Banyan': 15, 'Bottletree': 30, 'Camphor': 10, 'Fig_Blue': 20, 'Gumboab': 10, 'Maple': 20, 'Palo': 15, 'Poisoned': 15, 'Sallow': 15, 'Spiral': 20, 'Windwillow': 15, 'Wisteria_Wild': 25, 'Amber': 15, 'Redwood': 20, 'Azure': 20, 'Petrified': 30, 'Crystal': 15, 'Fire': 30, 'Ice': 15, 'Stormbark': 15}

# 0.1.2's product table, VERBATIM (renamed): the one-time update tells a 0.1.2 default line from a hand-edited one with it
PRODUCTS_012 = [
    ("Rock_Stone_Cobble",        "Mining",   1,   "Cobblestone"),
    ("Rubble_Stone",             "Mining",   0.5, "Stone Rubble"),
    ("Ore_Copper",               "Mining",   5,   "Copper Ore"),
    ("Ore_Iron",                 "Mining",   8,   "Iron Ore"),
    ("Ore_Silver",               "Mining",   14,  "Silver Ore"),
    ("Ore_Gold",                 "Mining",   20,  "Gold Ore"),
    ("Ingredient_Bar_Copper",    "Mining",   6,   "Copper Ingot"),
    ("Ingredient_Bar_Iron",      "Mining",   9,   "Iron Ingot"),
    ("Ingredient_Bar_Gold",      "Mining",   24,  "Gold Ingot"),
    ("Wood_Oak_Trunk",           "Foraging", 3,   "Oak Log"),
    ("Wood_Birch_Trunk",         "Foraging", 3,   "Birch Log"),
    ("Wood_Maple_Trunk",         "Foraging", 4,   "Maple Log"),
    ("Wood_Fir_Trunk",           "Foraging", 3,   "Fir Log"),
    ("Wood_Redwood_Trunk",       "Foraging", 5,   "Redwood Log"),
    ("Ingredient_Stick",         "Foraging", 1,   "Stick"),
    ("Ingredient_Fibre",         "Foraging", 1,   "Plant Fiber"),
    ("Ingredient_Tree_Bark",     "Foraging", 2,   "Tree Bark"),
    ("Ingredient_Tree_Sap",      "Foraging", 4,   "Tree Sap"),
    ("Plant_Crop_Wheat_Item",    "Farming",  2,   "Wheat"),
    ("Plant_Crop_Carrot_Item",   "Farming",  2,   "Carrot"),
    ("Plant_Crop_Potato_Item",   "Farming",  2,   "Potato"),
    ("Plant_Crop_Lettuce_Item",  "Farming",  2,   "Lettuce"),
    ("Plant_Crop_Corn_Item",     "Farming",  3,   "Corn"),
    ("Plant_Crop_Tomato_Item",   "Farming",  3,   "Tomato"),
    ("Plant_Crop_Pumpkin_Item",  "Farming",  5,   "Pumpkin"),
    ("Plant_Crop_Cotton_Item",   "Farming",  3,   "Cotton"),
    ("Plant_Crop_Rice_Item",     "Farming",  3,   "Rice"),
    ("Ingredient_Bone_Fragment", "Combat",   3,   "Bone Fragments"),
    ("Ingredient_Hide_Light",    "Combat",   6,   "Light Hide"),
    ("Ingredient_Leather_Light", "Combat",   7,   "Light Leather"),
    ("Ingredient_Hide_Medium",   "Combat",   12,  "Medium Hide"),
    ("Ingredient_Feathers_Light","Combat",   4,   "White Feathers"),
    ("Ingredient_Sac_Venom",     "Combat",   15,  "Venom Sac"),
    ("Ingredient_Chitin_Sturdy", "Combat",   15,  "Sturdy Chitin"),
    ("Ingredient_Life_Essence",  "Combat",   0.5, "Essence of Life"),
    ("Ingredient_Fire_Essence",  "Combat",   25,  "Essence of Fire"),
]

# ================= build-time checks: every id exists + no buy -> craft -> sell money loop =================
def _load_json(z, n):
    try: return json.loads(z.read(n).decode("utf-8", "replace"))
    except Exception: return None

# 0.1.14: what a product really trades at, at demand 1.0 - the BASE (buy side), the sell cap (SELL_CAP: a raised product a recipe makes
# for less keeps its 0.1.13 sell value) and the minimum instant sell price (market.minSell: a value under floor / (1 - spread) trades at
# that value on BOTH sides - the buy side times BUY_X where a cheap conversion would pay otherwise; FLOOR_EXEMPT products never take
# it). Every money-loop check below reads it; Catalog.buyVal / sellVal are the same rule in the jar.
EFF = {"floor": 0.0, "caps": {}, "exempt": set(), "bx": {}}


def eff_prices(prices, spread):
    """({product: buy base}, {product: sell base}) at demand 1.0 under EFF"""
    fl = EFF["floor"]
    fb = fl / (1.0 - spread) if fl > 0 else 0.0
    caps, ex, bx = EFF["caps"], EFF["exempt"], EFF["bx"]
    buy, sell = {}, {}
    for p, b in prices.items():
        sb = min(b, caps[p]) if p in caps else b
        if fb > 0 and p not in ex:
            buy[p], sell[p] = max(b, fb * bx.get(p, 1.0)), max(sb, fb)
        else:
            buy[p], sell[p] = b, sb
    return buy, sell


def check_assets(products, spread, extra=None, extra_recipes=None):
    z = zipfile.ZipFile(ASSETS)
    items = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[n.rsplit("/", 1)[1][:-5]] = n
    for k in (extra or {}):   # 0.1.10: the Enchanted items (SkyyCollections 0.2.11's asset pack, built by tools/skyyench.py)
        assert k not in items, k
        items[k] = None
    missing = [p for p in products if p not in items]
    if missing:
        raise SystemExit("unknown item ids (not in Assets.zip Server/Item/Items): %s" % missing)
    data = {k: _load_json(z, v) for k, v in items.items() if v is not None}
    data.update(extra or {})
    def chain(k):
        # k, parent, grandparent, ... - unbounded (a Parent cycle fails the build instead of being cut off silently)
        out = [k]
        while True:
            p = (data.get(out[-1]) or {}).get("Parent")
            if not p or p not in data: return out
            if p in out: raise SystemExit("Parent cycle in item assets: %s" % " -> ".join(out + [p]))
            out.append(p)
    def inherited(k, field):
        for a in chain(k):
            v = (data.get(a) or {}).get(field)
            if v is not None: return v
        return None
    def rtypes(k):
        # UNION of own + every ancestor's ResourceTypes: a superset of "child overrides parent", so the check holds whichever
        # way the engine resolves it (more memberships can only make recipes cheaper to cost = stricter)
        out = []
        for a in chain(k):
            for r in ((data.get(a) or {}).get("ResourceTypes") or []):
                if isinstance(r, dict) and r.get("Id") and r.get("Id") not in out: out.append(r.get("Id"))
        return out
    rt_items = {}
    for k in data:
        for r in rtypes(k): rt_items.setdefault(r, []).append(k)
    def norm_in(lst):
        out = []
        for i in lst or []:
            if not isinstance(i, dict): continue
            q = i.get("Quantity", 1) or 1
            if i.get("ItemId"): out.append(("I", i["ItemId"], q))
            elif i.get("ResourceTypeId"): out.append(("R", i["ResourceTypeId"], q))
        return out
    def norm_out(lst):
        return [(o["ItemId"], o.get("Quantity", 1) or 1) for o in lst or [] if isinstance(o, dict) and o.get("ItemId")]
    recipes = []
    n_inh = 0
    for k in data:
        # a Recipe inherited through Parent is checked too (paranoid: an extra recipe can only make the check stricter)
        r = inherited(k, "Recipe")
        if isinstance(r, dict) and r.get("Input"):
            recipes.append((k, norm_in(r["Input"]), norm_out(r.get("Output")) or [(k, r.get("OutputQuantity", 1) or 1)]))
            if (data.get(k) or {}).get("Recipe") is None: n_inh += 1
    for n in z.namelist():
        if n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
            d = _load_json(z, n) or {}
            outs = norm_out(d.get("Output")) or norm_out([d.get("PrimaryOutput")] if d.get("PrimaryOutput") else [])
            if d.get("Input") and outs: recipes.append((n, norm_in(d["Input"]), outs))
    for _n, _ins, _outs, _bks, _t in (extra_recipes or []):    # 0.1.20: the zone metals' recipes (no Assets.zip file yet)
        recipes.append((_n, list(_ins), list(_outs)))
    INF = float("inf")
    _eb, _es = eff_prices(products, spread)      # 0.1.14: sell caps + the minimum sell price
    cost = {p: b * (1 + spread) for p, b in _eb.items()}
    sell = {p: b * (1 - spread) for p, b in _es.items()}
    def c_in(kind, key):
        if kind == "I": return cost.get(key, INF)
        return min([cost.get(i, INF) for i in rt_items.get(key, [])] or [INF])
    # cheapest-acquisition relaxation run to a REAL fixed point. Costs only ever go down; without a self-feeding craft cycle it
    # settles in at most (#recipes + 1) passes (Bellman-Ford bound). Still changing after that -> the build fails loudly
    # instead of silently stopping early with costs that were not fully propagated.
    limit = len(recipes) + 2
    passes = 0
    while True:
        passes += 1
        changed = []
        for name, ins, outs in recipes:
            tot = sum(q * c_in(kd, key) for kd, key, q in ins)
            if tot == INF or not outs: continue
            o, q = outs[0]
            if tot / q < cost.get(o, INF) - 1e-9: cost[o] = tot / q; changed.append(o)
        if not changed: break
        if passes >= limit:
            raise SystemExit("arbitrage check did not converge after %d passes (self-feeding craft cycle?) still dropping: %s"
                             % (passes, sorted(set(changed))[:30]))
    loops = []
    costable = 0
    for name, ins, outs in recipes:
        tot = sum(q * c_in(kd, key) for kd, key, q in ins)
        if tot == INF: continue
        costable += 1
        val = sum(q * sell[o] for o, q in outs if o in sell)
        if val > tot + 1e-9: loops.append((val / tot, name, ins, outs))
    if loops:
        for ratio, name, ins, outs in sorted(loops, reverse=True)[:30]:
            print("MONEY LOOP x%.2f  %s  in=%s -> out=%s" % (ratio, name, ins, outs))
        raise SystemExit("%d buy->craft->sell money loops at factor 1.0 - fix the base prices" % len(loops))
    print("asset check: %d products exist, %d recipes checked (%d inherited via Parent, %d fully buyable from the bazaar), "
          "costs converged in %d passes, no money loops" % (len(products), len(recipes), n_inh, costable, passes))

# ================= 0.1.3 build-time pipeline: bags -> products, processed prices, the money-loop checks, runtime tables =================
J = B.start()        # moved up from the javassist section: SkyySacks' SackDefs runs in this JVM
import jpype as _jp


def sacks_pin():
    """the SkyySacks version of the tools/deploy_set.py SET (read as a literal, never imported)"""
    t = ast.parse(open(os.path.join(HERE, "..", "tools", "deploy_set.py"), encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets):
            return dict(ast.literal_eval(n.value))["SkyySacks"]
    raise SystemExit("tools/deploy_set.py has no SET - cannot find the SkyySacks bag rule")


# 0.1.9: the Fishing tab and the crystals come from SkyySacks 0.8.0's rule - read max(the SET pin, 0.8.0) (this Bazaar ships with 0.8.0)
SACKS_MIN = "0.8.14"   # 0.1.10: SkyySacks 0.8.1 puts the Enchanted materials in Mining / Foraging / Farming; 0.1.19: 0.8.14 homes the C1 rows (Combat / Smithing too)
SACKS_VER = max(sacks_pin(), SACKS_MIN, key=lambda v: tuple(int(x) for x in v.split(".")))
SACKS_JAR = os.path.normpath(os.path.join(HERE, "..", "SkyySacks", "SkyySacks-%s.jar" % SACKS_VER))
if not os.path.isfile(SACKS_JAR):
    raise SystemExit("the SET's SkyySacks jar is missing (%s) - build it first: the Bazaar tabs come from its bag rule" % SACKS_JAR)
_jc = _jp.JClass
_sacks_loader = _jc("java.net.URLClassLoader")(_jp.JArray(_jc("java.net.URL"))([_jc("java.io.File")(SACKS_JAR).toURI().toURL()]),
                                               _jc("java.lang.ClassLoader").getPlatformClassLoader())
SACK_DEFS = _jc(_jc("java.lang.Class").forName("com.skyy.sacks.SackDefs", True, _sacks_loader))
if list(SACK_DEFS.CATS) != list(BAG_TABS):
    raise SystemExit("SkyySacks %s has the bags %s, the Bazaar tabs are %s - update BAG_TABS" % (SACKS_VER, list(SACK_DEFS.CATS), BAG_TABS))
if bool(SACK_DEFS.COOKED_FARM):
    raise SystemExit("SkyySacks %s starts with cooked food in the Farming bag - re-check the Farming tab" % SACKS_VER)


def bag_of(i):
    c = SACK_DEFS.catOf(i)              # SkyySacks' own rule: the bag a NEW item goes into (cooked food off = Skyy's default)
    return None if c is None else str(c)


def load_assets():
    z = zipfile.ZipFile(ASSETS)
    names = z.namelist()

    def js(n):
        try:
            return json.loads(z.read(n).decode("utf-8-sig"))
        except Exception:
            return None
    items = dict((n.rsplit("/", 1)[1][:-5], n) for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    data = dict((k, js(v)) for k, v in items.items())
    drops = dict((n[len("Server/Drops/"):-5], n) for n in names if n.startswith("Server/Drops/") and n.endswith(".json"))
    recfiles = [n for n in names if n.startswith("Server/Item/Recipes/") and n.endswith(".json")]
    lang = {}
    for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
        m = re.match(r"([A-Za-z0-9_.]+)\s*=\s*(.*)", line)
        if m:
            lang[m.group(1)] = m.group(2).strip()
    return js, data, drops, recfiles, lang


def asset_model(js, data, drops, recfiles):
    """recipes (+ benches, times), processing benches (fuel, extra output, best tier time cut), fuel items, resource types"""
    def chain(k):
        out = [k]
        while True:
            p = (data.get(out[-1]) or {}).get("Parent")
            if not p or p not in data or p in out:
                return out
            out.append(p)

    def inh(k, f):
        for a in chain(k):
            v = (data.get(a) or {}).get(f)
            if v is not None:
                return v
        return None

    def rtypes(k):
        out = []
        for a in chain(k):
            for r in ((data.get(a) or {}).get("ResourceTypes") or []):
                if isinstance(r, dict) and r.get("Id") and r["Id"] not in out:
                    out.append(r["Id"])
        return out
    rt_items = collections.defaultdict(list)
    for k in data:
        for r in rtypes(k):
            rt_items[r].append(k)

    def norm_in(lst):
        out = []
        for i in lst or []:
            if not isinstance(i, dict):
                continue
            q = i.get("Quantity", 1) or 1
            if i.get("ItemId"):
                out.append(("I", i["ItemId"], q))
            elif i.get("ResourceTypeId"):
                out.append(("R", i["ResourceTypeId"], q))
        return out

    def norm_out(lst):
        return [(o["ItemId"], o.get("Quantity", 1) or 1) for o in lst or [] if isinstance(o, dict) and o.get("ItemId")]

    def bench_ids(r):
        br = r.get("BenchRequirement") or []
        if isinstance(br, dict):
            br = [br]
        return [(b.get("Type"), b.get("Id")) for b in br if isinstance(b, dict)]
    recipes = []
    for k in data:
        r = inh(k, "Recipe")
        if isinstance(r, dict) and r.get("Input"):
            recipes.append((k, norm_in(r["Input"]), norm_out(r.get("Output")) or [(k, r.get("OutputQuantity", 1) or 1)],
                            bench_ids(r), r.get("TimeSeconds")))
    for n in recfiles:
        d = js(n) or {}
        outs = norm_out(d.get("Output")) or norm_out([d.get("PrimaryOutput")] if d.get("PrimaryOutput") else [])
        if d.get("Input") and outs:
            recipes.append((n, norm_in(d["Input"]), outs, bench_ids(d), d.get("TimeSeconds")))
    benches = {}
    for k in data:
        bt = inh(k, "BlockType")
        b = bt.get("Bench") if isinstance(bt, dict) else None
        if isinstance(b, dict) and b.get("Type") == "Processing" and b.get("Id"):
            red = 0.0
            for t in b.get("TierLevels") or []:
                if isinstance(t, dict):
                    red = max(red, float(t.get("CraftingTimeReductionModifier") or 0.0))
            eo = b.get("ExtraOutput") or {}
            benches[b["Id"]] = {"fuel": bool(b.get("Fuel")), "reduction": red, "extra": norm_out(eo.get("Outputs")),
                                "per": int(eo.get("PerFuelItemsConsumed") or 0),
                                "ignored": set(x.get("ItemId") for x in (eo.get("IgnoredFuelSources") or []) if isinstance(x, dict))}
    fuels = []
    for k in sorted(data):
        if "Fuel" in rtypes(k):
            q = inh(k, "FuelQuality")
            if isinstance(q, (int, float)) and q > 0:
                fuels.append((k, float(q)))
    return {"inh": inh, "rtypes": rtypes, "rt_items": rt_items, "recipes": recipes, "benches": benches, "fuels": fuels}


def bag_items(js, data, drops, M, lang):
    """{bag: [ids]} - what each Magic Bag holds that the Bazaar lists, + {id: why}, + the skipped [(bag, id, reason)], + {id: name}.
    Fix round: TOTAL - every bag item is listed (Combat + Smithing: all of it; Mining / Foraging / Farming: unless a SKIP rule matches or
    no drop list, block or recipe gives it) or skipped with its reason; the pipeline stops on a listed item without a product row."""
    inh = M["inh"]

    def ids_in(o, out):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "ItemId" and isinstance(v, str):
                    out.add(v)
                else:
                    ids_in(v, out)
        elif isinstance(o, list):
            for v in o:
                ids_in(v, out)
    by_base = collections.defaultdict(list)
    for k, n in drops.items():
        by_base[k.rsplit("/", 1)[-1]].append(n)
    # what a player can ever get: any drop list (mobs, crops, plants, rocks, fishing, loot), any recipe output (salvage too), the
    # Gathering drop of any block (a block without one drops itself)
    source = collections.defaultdict(set)
    for k, n in drops.items():
        got = set()
        ids_in(js(n), got)
        for i in got:
            source[i].add("drop:" + k.split("/", 1)[0])
    for _n, _i, outs, _b, _t in M["recipes"]:
        for o, _q in outs:
            source[o].add("recipe")
    for k in data:
        bt = inh(k, "BlockType")
        if not isinstance(bt, dict):
            continue
        g = bt.get("Gathering")
        got = set()
        if isinstance(g, dict):
            for spec in g.values():
                if not isinstance(spec, dict):
                    continue
                if isinstance(spec.get("ItemId"), str):
                    got.add(spec["ItemId"])
                dl = spec.get("DropList")
                if isinstance(dl, str):
                    for n in ([drops[dl]] if dl in drops else by_base.get(dl, [])):
                        ids_in(js(n), got)
                elif isinstance(dl, dict):
                    ids_in(dl, got)
        if not got:
            got.add(k)
        for i in got:
            source[i].add("block")

    def name_of(i):
        tp = inh(i, "TranslationProperties") or {}
        key = tp.get("Name") if isinstance(tp, dict) else None
        if isinstance(key, str):
            k = key[len("server."):] if key.startswith("server.") else key
            if k in lang:
                return lang[k]
        return lang.get("items.%s.name" % i)
    bags, why, skipped, names = collections.OrderedDict((b, []) for b in BAG_TABS), {}, [], {}
    for i in sorted(data):
        b = bag_of(i)
        if b is None:
            continue
        if b not in bags:
            raise SystemExit("SkyySacks put %s in an unknown bag %s" % (i, b))
        if b in ALL_OF_BAG:
            w = "every %s bag item" % b
        else:
            hit = [r for rx, r in SKIP if re.search(rx, i)]
            if hit:
                skipped.append((b, i, hit[0]))
                continue
            if i not in source:
                skipped.append((b, i, NOSRC))
                continue
            w = "a %s bag item (%s)" % (b, ",".join(sorted(source[i])))
        nm = name_of(i)
        if not nm:
            raise SystemExit("bag item %s (%s) has no en-US name in server.lang - name it in PRODUCTS by hand or add a SKIP rule" % (i, b))
        bags[b].append(i)
        why[i] = w
        names[i] = nm
    return bags, why, skipped, names


def processed_table(M, products):
    """{id: {bench, outq, inputs [(qty, [candidate product ids])], secs}} - outputs of a PREMIUM_BENCHES recipe whose every input has
    a product to buy, + charcoal (the Furnace's extra output: 1 per PerFuelItemsConsumed burned fuel items that are not ignored),
    + (fix round) PREMIUM_ITEMS: the one non-processing recipe of such a product whose every input has a product (bench = the verb)"""
    out = {}

    def need_of(ins, o):
        need = []
        for kd, key, q in ins:
            cand = [key] if kd == "I" else sorted(x for x in M["rt_items"].get(key, ()))
            cand = [c for c in cand if c in products and c != o]
            if not cand:
                return None
            need.append((q, cand))
        return need
    for name, ins, outs, bks, t in M["recipes"]:
        pb = [bid for typ, bid in bks if typ == "Processing" and bid in PREMIUM_BENCHES]
        if not pb or len(outs) != 1 or outs[0][0] not in products or outs[0][0] in ALLOY_FIXED:   # 0.1.20: vanilla Bronze keeps its fixed price
            continue
        o, oq = outs[0]
        bench = M["benches"].get(pb[0], {})
        need = need_of(ins, o)
        if need is None:
            continue
        if o in out:
            raise SystemExit("two %s recipes make %s - pick one for its price" % ("/".join(PREMIUM_BENCHES), o))
        out[o] = {"bench": pb[0], "outq": oq, "inputs": need,
                  "secs": float(t or 0.0) * (1.0 - bench.get("reduction", 0.0)) if bench.get("fuel") else 0.0}
    for name, ins, outs, bks, t in M["recipes"]:
        if len(outs) != 1 or outs[0][0] not in products or any(typ == "Processing" for typ, _bid in bks):
            continue
        o, oq = outs[0]
        verb = [v for rx, v in PREMIUM_ITEMS if re.search(rx, o)]
        need = need_of(ins, o) if verb else None
        if need is None:
            continue
        if o in out:
            raise SystemExit("two recipes make the processed good %s (%s) - pick one for its price" % (o, verb[0]))
        out[o] = {"bench": verb[0], "outq": oq, "inputs": need, "secs": 0.0}
    fb = M["benches"].get("Furnace", {})
    for eid, eq in fb.get("extra", []):
        if eid in products and fb.get("per"):
            cand = [f for f, q in M["fuels"] if f in products and f not in fb["ignored"] and f != eid]
            if cand:
                out[eid] = {"bench": "Furnace fuel", "outq": eq, "inputs": [(fb["per"], cand)], "secs": 0.0}
    return out


def proc_order(proc, charcoal):
    """the processed goods with every processed input before it (charcoal before every fuel recipe: it prices the fuel), ties by id -
    the order Catalog.reprice0 runs in (PROC_SPEC), so a good made from another (Dawnstone from Quartzite) follows it in one pass"""
    deps = {}
    for i, e in proc.items():
        d = set(c for _q, cand in e["inputs"] for c in cand if c in proc and c != i)
        if e["secs"] > 0 and charcoal in proc and i != charcoal:
            d.add(charcoal)
        deps[i] = d
    out, done = [], set()
    while len(out) < len(proc):
        ready = sorted(i for i in proc if i not in done and deps[i] <= done)
        if not ready:
            raise SystemExit("processed goods made from each other in a circle: %s" % sorted(set(proc) - done))
        nxt = charcoal if charcoal in ready else ready[0]
        out.append(nxt)
        done.add(nxt)
    return out


def fuel_list(M, products):
    """[(fuel product, seconds per item, charcoal back per item)] + the charcoal id"""
    fb = M["benches"].get("Furnace", {})
    share = (1.0 / fb["per"]) if fb.get("per") else 0.0
    charcoal = fb["extra"][0][0] if fb.get("extra") else None
    return [(f, q, 0.0 if f in fb.get("ignored", ()) else share) for f, q in M["fuels"] if f in products], charcoal


def auto_prices(base, proc, fuels, charcoal, premium):
    """the processed products' base prices = Catalog.reprice0 (the Java runs the same arithmetic on the same tables) in proc_order
    (charcoal first, inputs before what is made from them, then id order); floor to 0.01, at least 0.01.
    Fix round: an input that is itself a processed good counts at its RAW value (min(its price, its own inputs' value) - the premium is
    never stacked): Dawnstone = 4 cobble x (1 + premium), not 2 Quartzite x (1 + premium) = 4 cobble x (1 + premium)^2, which let
    buy cobble -> smelt -> smelt -> sell pay from a premium of 11 %."""
    got, raw = {}, {}

    def price(i):
        return got[i] if i in got else base.get(i)

    def acq(c):
        p = price(c)
        if p is not None and c in raw:
            p = min(p, raw[c])
        return p
    order = proc_order(proc, charcoal)
    for i in order:
        e = proc[i]
        tot, ok = 0.0, True
        for q, cand in e["inputs"]:
            ps = [acq(c) for c in cand if acq(c) is not None]
            if not ps:
                ok = False
                break
            tot += q * min(ps)
        if not ok:
            continue
        if e["secs"] > 0:
            per = None
            for f, fq, sh in fuels:
                pf = price(f)
                if pf is None:
                    continue
                pc = price(charcoal) if (sh > 0 and charcoal) else 0.0
                c = (pf - sh * (pc or 0.0)) / fq
                per = c if per is None else min(per, c)
            tot += max(0.0, per or 0.0) * e["secs"]
        v = tot / e["outq"]
        raw[i] = v
        got[i] = max(0.01, math.floor(v * (1.0 + premium) * 100.0 + 1e-9) / 100.0)
    return got


def loop_check(M, prices, spread, margins=None, values=None):
    """0.1.3 money-loop check on top of check_assets: every recipe 0.1.2 checks, plus what 0.1.2 did not know - Furnace / Campfire
    recipes pay for fuel (the cheapest fuel item per second after the best tier's time cut, net of the charcoal it gives back) and
    burning PerFuelItemsConsumed fuel items into charcoal is a recipe of its own (every Fuel item, also crafted ones).
    Fix round (review 2026-10-03): two values per item run to ONE fixed point -
      cost[i] = the cheapest way to GET i from coins: its instant-buy price, or a recipe's inputs at their cost (+ fuel) MINUS what the
                recipe's other outputs liquidate for (a salvage recipe's co-products), per unit;
      liq[i]  = the best way to TURN i into coins: its instant-sell price, or any recipe that takes i with every other input at its
                cost (+ fuel), its outputs at their liq (salvage the gear, smelt the ore, tan the hide, then sell), per unit of i.
    The old extension gave a recipe's whole cost to its first output and valued outputs at their bare sell price, so a buy -> craft ->
    salvage -> smelt / tan -> sell chain stayed invisible. A recipe whose outputs liquidate for more than its inputs cost (at factor
    1.0) is a money loop. Returns (loops, costable recipes, recipes, passes); a fixed point not reached stops the build."""
    INF = float("inf")
    rt_items, benches = M["rt_items"], M["benches"]
    _eb, _es = eff_prices(prices, spread)        # 0.1.14: sell caps + the minimum sell price
    cost = dict((p, b * (1 + spread)) for p, b in _eb.items())
    liq = dict((p, b * (1 - spread)) for p, b in _es.items())
    fb = benches.get("Furnace", {})
    charcoal = fb["extra"][0][0] if fb.get("extra") else None
    per = fb.get("per") or 0
    ignored = fb.get("ignored", set())
    recipes = []
    for name, ins, outs, bks, t in M["recipes"]:
        fuel_s = 0.0
        for typ, bid in bks:
            b = benches.get(bid)
            if typ == "Processing" and b and b["fuel"]:
                fuel_s = max(fuel_s, float(t or 0.0) * (1.0 - b["reduction"]))
        if outs:
            recipes.append((name, ins, outs, fuel_s))
    if charcoal and per:
        for f, fq in M["fuels"]:
            if f not in ignored:
                recipes.append(("burn " + f, [("I", f, per)], [(charcoal, 1)], 0.0))

    def c_in(kind, key):
        if kind == "I":
            return cost.get(key, INF)
        return min([cost.get(i, INF) for i in rt_items.get(key, [])] or [INF])

    def fuel_cost_s():
        best = INF
        lc = liq.get(charcoal, 0.0) if charcoal else 0.0
        for f, fq in M["fuels"]:
            cf = cost.get(f, INF)
            if cf == INF:
                continue
            sh = 0.0 if f in ignored else (1.0 / per if per else 0.0)
            best = min(best, (cf - sh * lc) / fq)
        return max(0.0, best) if best < INF else INF

    def worth(outs):
        return sum(q * liq.get(o, 0.0) for o, q in outs)
    limit = len(recipes) + 2
    passes = 0
    while True:
        passes += 1
        changed = set()
        fs = fuel_cost_s()
        for name, ins, outs, fuel_s in recipes:
            fc = fs * fuel_s if fuel_s else 0.0
            cins = [q * c_in(kd, key) for kd, key, q in ins]
            tot = sum(cins) + fc
            if tot < INF:
                for k, (o, q) in enumerate(outs):
                    credit = sum(q2 * liq.get(o2, 0.0) for k2, (o2, q2) in enumerate(outs) if k2 != k)
                    c = max(0.0, tot - credit) / q
                    if c < cost.get(o, INF) - 1e-9:
                        cost[o] = c
                        changed.add(o)
            v = worth(outs)
            for j, (kd, key, q) in enumerate(ins):
                other = sum(cins[k] for k in range(len(ins)) if k != j) + fc
                if other == INF:
                    continue
                cand = (v - other) / q
                for i in ([key] if kd == "I" else rt_items.get(key, [])):
                    if cand > liq.get(i, 0.0) + 1e-9:
                        liq[i] = cand
                        changed.add(i)
        if not changed:
            break
        if passes >= limit:
            raise SystemExit("money-loop check did not reach a fixed point after %d passes (a self-feeding recipe circle pays): %s"
                             % (passes, sorted(changed)[:30]))
    fs = fuel_cost_s()
    loops, costable = [], 0
    for name, ins, outs, fuel_s in recipes:
        tot = sum(q * c_in(kd, key) for kd, key, q in ins) + (fs * fuel_s if fuel_s else 0.0)
        if tot == INF:
            continue
        costable += 1
        v = worth(outs)
        if v > tot + 1e-9:
            loops.append((v / tot if tot > 0 else INF, name, ins, outs, fuel_s))
        if margins is not None and tot > 0 and v > 0:
            margins.append((v / tot, name, ins, outs, fuel_s))
    if values is not None:      # 0.1.14: the fixed point itself (the SkyyMerchants check reads liq)
        values["cost"], values["liq"] = cost, liq
    return loops, costable, len(recipes), passes


def loop_check_selftest():
    """a chain only the fix-round check sees: buy 2 A -> craft Gear (no product) -> salvage -> 3 B + 1 C -> smelt each B into D -> sell D
    and C. No single recipe pays at bare sell prices (B -> D alone is within the spread), the chain does (22.05 > 22)."""
    m = {"rt_items": {}, "benches": {}, "fuels": [], "recipes": [
        ("craft Gear", [("I", "A", 2)], [("Gear", 1)], [("Crafting", "TestBench")], None),
        ("salvage Gear", [("I", "Gear", 1)], [("B", 3), ("C", 1)], [("Processing", "Salvagebench")], None),
        ("smelt B", [("I", "B", 1)], [("D", 1)], [("Processing", "TestFurnace")], None)]}
    px = {"A": 10.0, "B": 4.0, "C": 10.1, "D": 4.8}
    loops = loop_check(m, px, 0.10)[0]
    names = sorted(n for _r, n, _i, _o, _f in loops)
    assert "craft Gear" in names and "salvage Gear" in names, "loop check self-test: the craft -> salvage -> smelt chain was not seen: %s" % names
    bare = 3 * px["B"] * 0.9 + px["C"] * 0.9          # what the old extension valued the salvage at
    assert bare < 2 * px["A"] * 1.1 and px["D"] * 0.9 <= px["B"] * 1.1, "loop check self-test: the example is not old-check-blind"
    px["C"] = 10.0                                     # 21.96 < 22: no loop - the check must not cry wolf
    assert not loop_check(m, px, 0.10)[0], "loop check self-test: a chain that does not pay was flagged"
    return names


# ---- 1. the bags (SkyySacks' rule over Assets.zip) against the table
JS, DATA, DROPS, RECFILES, LANG = load_assets()
# 0.1.10: the 19 Enchanted item JSONs (with their recipes) + names, built by tools/skyyench.py exactly as SkyyCollections 0.2.11 ships them,
# join the vanilla items BEFORE the model: their recipes are processed-goods recipes (PREMIUM_ITEMS), every loop check sees them, the bag
# guard lists them (SackDefs.catOf), the name check reads their en-US names
with SA.assets() as _ez:
    _EF, _EL = EN.build_assets(_ez, SA)
_ench_n = 0
ENCH_DATA = {}
for _p, _t in _EF.items():
    if _p.startswith("Server/Item/Items/"):
        _i = _p.rsplit("/", 1)[1][:-5]
        assert _i not in DATA, "an Enchanted id clashes with an Assets.zip item: " + _i
        DATA[_i] = json.loads(_t)
        ENCH_DATA[_i] = json.loads(_t)
        _ench_n += 1
for _ln in _EL:
    _m = re.match(r"([A-Za-z0-9_.]+)\s*=\s*(.*)", _ln)
    if _m and _m.group(1) not in LANG:
        LANG[_m.group(1)] = _m.group(2).strip()
assert _ench_n == len(EN.IDS) == len(_EN_ALL.TABLE) - len(EN_OFF)          # 0.1.16: + the Enchanted Stick (was 19); 0.1.19: the live table minus EN_OFF
# ---- 0.1.20 THE ZONE METALS (research/Zone-Ores-Alloys-Spec.md sections 2.3 + 3; SkyyWorldGen 0.7.3 makes the real items - ids FINAL):
#      virtual item JSONs (names, Metal_Bars, the ore blocks' drop) + the recipes join the model BEFORE the bag guard and every loop check
ZONE_METALS = [   # (key, zone, raw ore smelt seconds, host-rock block word)
    ("Lead", 2, 18, "Sandstone"), ("Chromium", 3, 18, "Shale"), ("Slag", 4, 20, "Volcanic"), ("Titanium", 5, 30, "Basalt")]
ZONE_ALLOYS = [   # (alloy key, vanilla ingot A, ingot B, seconds = both smelts added)
    ("Dusk", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn", 36), ("Azurvane", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn", 36),
    ("Cinder", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn", 40), ("Lumen", "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn", 60),
    ("Electrum", "Ingredient_Bar_Gold", "Ingredient_Bar_Silver", 14)]   # spec section 8 (Skyy 2026-10-17): Gold + Silver Ingot, a charm metal unlocked at Furnace Charm T1
BRONZE_ID, BRONZE_RECIPE = "Ingredient_Bar_Bronze", ("Ingredient_Bar_Copper", "Ingredient_Bar_Iron", 24)
ZONE_DATA, ZONE_RECS, ZONE_NAMES = {}, [], {}
for _k, _z, _s, _host in ZONE_METALS:
    _ore, _bar, _blk = "Ore_%s_SkyWynn" % _k, "Ingredient_Bar_%s_SkyWynn" % _k, "Ore_%s_%s_SkyWynn" % (_k, _host)
    ZONE_DATA[_ore] = {"TranslationProperties": {"Name": "server.items.%s.name" % _ore}}
    ZONE_DATA[_blk] = {"TranslationProperties": {"Name": "server.items.%s.name" % _blk}, "BlockType": {"Gathering": {"Breaking": {"ItemId": _ore}}}}
    ZONE_DATA[_bar] = {"TranslationProperties": {"Name": "server.items.%s.name" % _bar}, "ResourceTypes": [{"Id": "Metal_Bars"}]}
    ZONE_NAMES[_ore], ZONE_NAMES[_blk], ZONE_NAMES[_bar] = "%s Ore" % _k, "%s Ore" % _k, "%s Ingot" % _k
    ZONE_RECS.append(("SkyWynn:%s" % _bar, [("I", _ore, 1)], [(_bar, 1)], [("Processing", "Furnace")], _s))
for _k, _a, _b, _s in ZONE_ALLOYS:
    _id = "Ingredient_Bar_%s_SkyWynn" % _k
    ZONE_DATA[_id] = {"TranslationProperties": {"Name": "server.items.%s.name" % _id}}
    ZONE_NAMES[_id] = "%s Ingot" % _k
    ZONE_RECS.append(("SkyWynn:Alloy_%s" % _k, [("I", _a, 1), ("I", _b, 1)], [(_id, 1)], [("Processing", "SkyyAlloy")], _s))
ZONE_RECS.append(("SkyWynn:Alloy_Bronze", [("I", BRONZE_RECIPE[0], 1), ("I", BRONZE_RECIPE[1], 1)], [(BRONZE_ID, 1)], [("Processing", "SkyyAlloy")], BRONZE_RECIPE[2]))
ALLOY_FIXED = set([BRONZE_ID])      # a vanilla alloy with a FIXED price (not a processed good): its sell side is capped to its crafting value
ZONE_PRODUCT_IDS = ["Ore_%s_SkyWynn" % _k for _k, _z, _s, _h in ZONE_METALS] + ["Ingredient_Bar_%s_SkyWynn" % _k for _k, _z, _s, _h in ZONE_METALS] + \
                   ["Ingredient_Bar_%s_SkyWynn" % _k for _k, _a, _b, _s in ZONE_ALLOYS]
for _i, _d in ZONE_DATA.items():
    assert _i not in DATA, "0.1.20: a zone metal id clashes with an Assets.zip item: " + _i
    DATA[_i] = _d
    LANG["items.%s.name" % _i] = ZONE_NAMES[_i]
for _i in [BRONZE_ID, "Ingredient_Bar_Copper", "Ingredient_Bar_Iron", "Ingredient_Bar_Thorium", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Mithril"]:
    assert _i in DATA, "0.1.20: the vanilla ingot %s is not in Assets.zip" % _i
assert not [r for r in RECFILES if "Bronze" in r], "0.1.20: Assets.zip has a Bronze recipe file now - Bronze is no longer recipe-less"
assert "Recipe" not in (DATA[BRONZE_ID] or {}), "0.1.20: vanilla Bronze has a Recipe now"
# Bronze as an alloy would make the vanilla Ancient Steel armor (3 / 6 Bronze + wood + leather) cheaper to craft than its salvage is worth - but
# that recipe's bench is "TODO" (no block has it) and needs KnowledgeRequired: unreachable. The build re-checks that; if vanilla ever fixes it, this stops.
_zz = zipfile.ZipFile(ASSETS)
for _n in _zz.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        _r = (json.loads(_zz.read(_n).decode("utf-8-sig")) or {}).get("Recipe")
        if isinstance(_r, dict) and any(isinstance(_i, dict) and _i.get("ItemId") == BRONZE_ID for _i in (_r.get("Input") or [])):
            _bn = [b.get("Id") for b in ([_r.get("BenchRequirement")] if isinstance(_r.get("BenchRequirement"), dict) else (_r.get("BenchRequirement") or []))]
            assert _bn and all(_b == "TODO" for _b in _bn), "0.1.20: %s uses Bronze at a REAL bench %s - the Bronze alloy would open a craft -> salvage loop; price it first" % (_n, _bn)
# ZONE_JAR: a SkyyWorldGen jar that already carries the items (0.7.3+) is CHECKED against these ids (the spec list is the source of truth)
ZONE_JAR = None
for _jn in sorted(os.listdir(os.path.join(HERE, "..", "SkyyWorldGen"))):
    if _jn.startswith("SkyyWorldGen-") and _jn.endswith(".jar"):
        _zf = zipfile.ZipFile(os.path.join(HERE, "..", "SkyyWorldGen", _jn))
        _have = set(n.rsplit("/", 1)[-1][:-5] for n in _zf.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        if "Ore_Lead_SkyWynn" in _have:
            ZONE_JAR = _jn
            _miss = [i for i in ZONE_DATA if i not in _have and i != "Ingredient_Bar_Electrum_SkyWynn"]      # Electrum (spec section 8) may be later than the jar
            assert not _miss, "0.1.20: %s misses zone metal ids the spec lists: %s" % (_jn, _miss)
            print("0.1.20: %s %s Ingredient_Bar_Electrum_SkyWynn" % (_jn, "has" if "Ingredient_Bar_Electrum_SkyWynn" in _have else "does NOT have yet"))
print("0.1.20: %d zone metal items / %d recipes (ids from the spec, %s)" % (len(ZONE_DATA), len(ZONE_RECS),
      ("checked against " + ZONE_JAR) if ZONE_JAR else "SkyyWorldGen 0.7.3 not built yet - the spec list is the source"))
MODEL = asset_model(JS, DATA, DROPS, RECFILES)
MODEL["recipes"].extend([r for r in ZONE_RECS if r[0] != "SkyWynn:Alloy_Bronze"])   # Bronze: see BRONZE_CAP below (its recipe in the model turns Bronze-salvage cycles into endless sources)
MODEL["rt_items"]["Metal_Bars"].extend(i for i in ZONE_DATA if i.startswith("Ingredient_Bar_") and i.endswith("_SkyWynn") and i.split("_")[2] in [m[0] for m in ZONE_METALS])
MODEL["benches"]["SkyyAlloy"] = dict(MODEL["benches"]["Furnace"], extra=[], per=0)   # the alloy bench burns fuel at the best Furnace tier's speed
BAGS, WHY, SKIPPED, BAG_NAMES = bag_items(JS, DATA, DROPS, MODEL, LANG)
ids = [p[0] for p in PRODUCTS]
if len(set(ids)) != len(ids):
    raise SystemExit("duplicate product rows: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
BAG_OF = {}
for _b, _l in BAGS.items():
    for _i in _l:
        BAG_OF[_i] = _b
for _i in list(BAG_OF):
    if _i.startswith("Plant_Sapling_") and BAG_OF[_i] == "Foraging":      # 0.1.20: SkyySacks 0.8.19 homes saplings in Foraging; the file category stays Farming
        BAG_OF[_i] = "Farming"
missing = [(BAG_OF[i], i, BAG_NAMES[i]) for b in BAG_TABS for i in BAGS[b] if i not in set(ids)]
if missing:
    raise SystemExit("%d bag item(s) have no product row - add each to PRODUCTS (price + official name) or a SKIP rule with a reason:\n  %s"
                     % (len(missing), "\n  ".join("%s  %s  (%s)" % m for m in missing)))
_skip_of = dict((i, (b, r)) for b, i, r in SKIPPED)
_both = [(i, _skip_of[i][1]) for i in ids if i in _skip_of]
if _both:
    raise SystemExit("product row(s) for bag items a SKIP rule takes out - remove the row or narrow the rule: %s" % _both)
# 0.1.16: a SkyySacks jar built before tools/skyyench.py's 20th row does not hold the Enchanted Stick yet (it reads that table at its
# next build and then puts it in the Foraging bag); only an Enchanted id may fall back to its table category EN.cat_of (SkyySacks' rule)
SACKS_LATE = [i for i in EN.IDS if i in ids and i not in BAG_OF]
assert set(SACKS_LATE) <= set(["Skyy_Ench_Stick"]) | set(i for i in EN.IDS if i not in EN102_IDS), "0.1.16: SkyySacks %s misses Enchanted ids it should hold: %s" % (SACKS_VER, SACKS_LATE)   # 0.1.20: + the rows after the frozen 102
for _i in SACKS_LATE:
    BAG_OF[_i] = EN.cat_of(_i)
print("0.1.16: SkyySacks %s %s" % (SACKS_VER, ("does not hold %s yet - its bag rule gets it at its next build; listed in %s from tools/skyyench.py"
                                               % (", ".join(SACKS_LATE), ", ".join(EN.cat_of(i) for i in SACKS_LATE))) if SACKS_LATE else "holds every Enchanted id"))
nobag = [i for i in ids if i not in BAG_OF]
if nobag:
    raise SystemExit("product row(s) for items no Magic Bag holds (SkyySacks %s) - remove them or fix the bag rule: %s" % (SACKS_VER, nobag))
# the guard is total: every item SackDefs.catOf puts in a bag is listed or skipped (a bag item can never fall through)
_catof_all = [i for i in sorted(DATA) if bag_of(i) is not None]
_unaccounted = [i for i in _catof_all if i not in BAG_OF and i not in _skip_of]
if _unaccounted:
    raise SystemExit("bag items neither listed nor skipped: %s" % _unaccounted[:40])
assert len(_catof_all) + len(SACKS_LATE) == len(BAG_OF) + len(_skip_of), (len(_catof_all), len(SACKS_LATE), len(BAG_OF), len(_skip_of))   # 0.1.16: + SACKS_LATE
for pid, base, name in PRODUCTS:
    assert all(c.isalnum() or c == "_" for c in pid), pid
    assert name and "," not in name and "=" not in name and '"' not in name and "\\" not in name, pid
    if base is not AUTO and not (0.01 <= float(base) <= 1e9):
        raise SystemExit("%s: base price %s outside 0.01 .. 1000000000" % (pid, base))
    if BAG_NAMES.get(pid) and BAG_NAMES[pid] != name:
        print("WARNING: %s is called %r in server.lang, the Bazaar says %r" % (pid, BAG_NAMES[pid], name))
for pid, tabs in EXTRA_TABS.items():
    assert pid in BAG_OF and all(t in BAG_TABS for t in tabs) and BAG_OF[pid] not in tabs, pid
# every 0.1.2 product stays, with its 0.1.2 raw price unless 0.1.4 moved its default (PRICE_014; the one-time updates rewrite a
# 0.1.2 / 0.1.3 default line to its current line)
_old = dict((p, (c, float(b), n)) for p, c, b, n in PRODUCTS_012)
_new = dict((p[0], p) for p in PRODUCTS)
assert set(_old) <= set(_new), "0.1.2 products missing in 0.1.3: %s" % sorted(set(_old) - set(_new))
# ---- 2. processed goods (AUTO) = the PREMIUM_BENCHES outputs + charcoal + the PREMIUM_ITEMS; their seed prices at the default premium
PROC = processed_table(MODEL, set(ids))
_auto_rows = set(p[0] for p in PRODUCTS if p[1] is AUTO)
if _auto_rows != set(PROC):
    raise SystemExit("AUTO rows %s differ from the processed goods %s - a %s output or a PREMIUM_ITEMS product must be AUTO and only those"
                     % (sorted(_auto_rows - set(PROC)), sorted(set(PROC) - _auto_rows), "/".join(PREMIUM_BENCHES)))
for p, (c, b, n) in _old.items():
    if p not in PROC and p not in PRICE_014 and p not in PRICE_015 and abs(float(_new[p][1]) - b) > 1e-9:
        raise SystemExit("0.1.2 product %s changed its raw price %s -> %s: keep it (existing markets)" % (p, b, _new[p][1]))
    if _new[p][2] != n:
        raise SystemExit("0.1.2 product %s changed its name %r -> %r" % (p, n, _new[p][2]))
# ---- 0.1.4: the PRODUCTS rows carry the 0.1.4 defaults, and the crops follow the vanilla farming path
for _i, (_o, _n) in PRICE_014.items():
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9, "PRICE_014 %s: row %s" % (_i, _new.get(_i))
for _i, (_o, _n) in PRICE_015.items():   # 0.1.5: the rows carry the 0.1.5 default; the 0.1.4 default was the 0.1.2 one (never in PRICE_014)
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9 and _i not in PRICE_014 and _i not in PROC, _i
    assert abs(_old[_i][1] - _o) < 1e-9, "PRICE_015 %s: the 0.1.2 / 0.1.3 / 0.1.4 default was %s" % (_i, _old[_i][1])
    assert abs(_o - _n) > 1e-9 and _i not in PROC, _i


def farming_path(data):
    """{crop: Farmingbench RequiredTierLevel of its normal seed recipe} from the item assets (1 when the recipe names no tier)"""
    out = {}
    for c in VANILLA_SEED_TIER:
        for sid, extra in (("Plant_Seeds_%s" % c, 0), ("Plant_Seeds_%s_Eternal" % c, 1)):
            r = (data.get(sid) or {}).get("Recipe") or {}
            br = r.get("BenchRequirement") or []
            br = [br] if isinstance(br, dict) else br
            t = [int(b.get("RequiredTierLevel") or 1) for b in br if isinstance(b, dict) and b.get("Id") == "Farmingbench"]
            if len(t) != 1:
                raise SystemExit("0.1.4 farming path: %s has no single Farmingbench recipe (%s) - Assets.zip changed?" % (sid, br))
            if extra == 0:
                out[c] = t[0]
            elif t[0] != out[c] + 1:
                raise SystemExit("0.1.4 farming path: %s is Farmingbench tier %d, not its seed's %d + 1" % (sid, t[0], out[c]))
    return out


def sapling_essence(data):
    """{sapling: Essence of Life count of its Recipe, own or inherited (None: another input)} from the item assets"""
    out = {}
    for sname in SAPLING_TIER:
        k, r, seen = "Plant_Sapling_%s" % sname, None, set()
        while k in data and k not in seen and r is None:          # a recipe inherited through Parent counts (Crystal, Poisoned: Oak's)
            seen.add(k)
            r = (data.get(k) or {}).get("Recipe")
            k = (data.get(k) or {}).get("Parent")
        ins = (r or {}).get("Input") or []
        e = [int(i.get("Quantity", 1) or 1) for i in ins if isinstance(i, dict) and i.get("ItemId") == "Ingredient_Life_Essence"]
        out[sname] = e[0] if (len(ins) == 1 and len(e) == 1) else None
    return out


_se = sapling_essence(DATA)
if _se != SAPLING_ESSENCE:
    raise SystemExit("0.1.4: the vanilla sapling recipes changed - %s, the table says %s" % (_se, SAPLING_ESSENCE))
for _s, _t in SAPLING_TIER.items():
    _i = "Plant_Sapling_%s" % _s
    _cap = None if _se[_s] is None else math.floor(0.6 * _se[_s] * 2 + 1e-9) / 2.0
    _old = PRICE_014[_i][0] if _i in PRICE_014 else float(_new[_i][1])
    _want = _old * 2 ** (_t - 1)
    assert float(_new[_i][1]) == (_want if _cap is None or _want <= _cap else _cap), (_i, _new[_i], _want, _cap)
_fp = farming_path(DATA)
if _fp != VANILLA_SEED_TIER:
    raise SystemExit("0.1.4: the vanilla farming path changed - Farmingbench seed tiers %s, the table says %s" % (_fp, VANILLA_SEED_TIER))
for _c, _vt in VANILLA_SEED_TIER.items():
    _t = PRICE_TIER[_vt]
    for _i, _want, _cap in (("Plant_Crop_%s_Item" % _c, CROP_PRICE[_t], None), ("Plant_Seeds_%s" % _c, SEED_PRICE[_t], SEED_CAP.get(_c)),
                            ("Plant_Seeds_%s_Eternal" % _c, ETERNAL_PRICE[_t], ETERNAL_CAP.get(_c))):
        _have = float(_new[_i][1])
        assert _have == (_want if _cap is None else _cap) and (_cap is None or _cap < _want), (_i, _have, _want, _cap)
print("0.1.4 farming path (Farmingbench seed tiers, Assets.zip): " + ", ".join("%s %d" % (c, t) for c, t in sorted(_fp.items(), key=lambda x: (x[1], x[0]))))
# ---- 0.1.14 PRICES BY TIER (Skyy 2026-10-15: "and make prices all scale by tier. so T2 buy and sell is a good bit higher than T1";
#      Eternal seeds: "id make T1 crops start at like 800 coins. cause it lasts forever."). THE tier table is tools/tier_tags.py (what the
#      items' 'T2 Copper - ...' tags say); every tiered product with a FIXED price takes its family's ladder, x2 or more per tier. Bars
#      (AUTO from their ore) and Enchanted materials (AUTO from their base) follow their inputs. Untiered products keep their prices.
import tier_tags as TT
TIER_LADDER = {
    "ore": {2: 5, 3: 16, 4: 48, 5: 144, 6: 480, 7: 1440, 8: 3712},          # the 0.1.4 ore ladder (economy.md 2026-10-04) - unchanged
    "log": {2: 3, 3: 8, 4: 20, 5: 48, 6: 128},                              # the 0.1.4 log ladder 3 / 8 / 20 / 48 / 128 on the tags' zones
    "crop": {2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 64, 8: 128},                # x2 per Farmer's Workbench pair (was 2 / 6 / 16 / 40 per 2 pairs)
    "seed": {2: 1, 3: 2, 4: 4, 5: 8, 6: 16, 7: 32, 8: 64},                  # normal seeds follow their crop (economy.md 2026-10-05)
    "eternal": {2: 800, 3: 1600, 4: 3200, 5: 6400, 6: 12800, 7: 25600, 8: 51200},   # Skyy: T2 800, x2 per later pair
}
for _f, _l in TIER_LADDER.items():
    _ts = sorted(_l)
    assert all(_l[b] >= 2 * _l[a] for a, b in zip(_ts, _ts[1:])), "0.1.14: the %s ladder must at least double per tier: %s" % (_f, _l)


def tier_family(pid):
    """the tier_tags family of a product, with the Eternal seeds as their own family; None = untiered"""
    f = TT.family(pid)
    if f == "seed" and pid.endswith("_Eternal"):
        return "eternal"
    if f == "zone_ore":      # 0.1.20: SkyyWorldGen's raw ores follow the ore ladder like their zone partner
        return "ore"
    return f


OLD_0113 = dict((_p, float(_b)) for _p, _b, _n in PRODUCTS if _b is not AUTO)   # every 0.1.13 fixed default
PRICE_0114 = {}       # id -> (0.1.13 default, 0.1.14 default): the one-time update (Catalog.migrate114) moves a line still at the old one
TIERED = {}
for _p, _b, _n in PRODUCTS:
    _f = tier_family(_p)
    if _f is None:
        continue
    TIERED[_p] = (_f, TT.tier(_p))
    if _f not in TIER_LADDER:
        assert (_b is AUTO or _p == "Ingredient_Bar_Bronze"), "0.1.14: %s (%s) has no ladder" % (_p, _f)      # 0.1.20: + the alloy family tools/tier_tags.py may add
        continue
    assert _b is not AUTO, _p
    _nb = float(TIER_LADDER[_f][TT.tier(_p)])
    if _f == "log":
        _nb = max(_nb, float(_b))      # Skyy 2026-10-15 "Rare woods stay premium": rarity wins - no log below its 0.1.13 (10-04) price
    if abs(_nb - float(_b)) > 1e-9:
        PRICE_0114[_p] = (float(_b), _nb)
# saplings follow their log (Skyy 2026-10-15 "Yes, saplings follow log tier"): base = SAPLING_X x the log's 0.1.14 base, up to 0.5
SAPLING_X = 3.3
_lognew = dict((_p, PRICE_0114[_p][1] if _p in PRICE_0114 else float(_b)) for _p, _b, _n in PRODUCTS if tier_family(_p) == "log")
SAPLING_LOG = {}
for _p, _b, _n in PRODUCTS:
    if not _p.startswith("Plant_Sapling_") or _b is AUTO:
        continue
    _lg = "Wood_%s_Trunk" % _p[len("Plant_Sapling_"):]
    if _lg not in _lognew:
        continue
    SAPLING_LOG[_p] = _lg
    _nb = math.ceil(SAPLING_X * _lognew[_lg] * 2.0 - 1e-9) / 2.0
    if abs(_nb - float(_b)) > 1e-9:
        PRICE_0114[_p] = (float(_b), _nb)
assert not [l for l, v in _lognew.items() if v < OLD_0113[l]], "0.1.14: a log dropped below its rarity price"
assert not [p for p in PRICE_0114 if tier_family(p) == "ore"], "0.1.14: the ores already follow their ladder"
assert not (set(PRICE_0114) & set(PRICE_015)), "0.1.14: Tree Sap is untiered"
PRODUCTS = [(_p, (PRICE_0114[_p][1] if _p in PRICE_0114 else _b), _n) for _p, _b, _n in PRODUCTS]
FUELS, CHARCOAL = fuel_list(MODEL, set(ids))
FIXED_BASE = dict((p[0], float(p[1])) for p in PRODUCTS if p[1] is not AUTO)


def all_prices(premium):
    d = dict(FIXED_BASE)
    d.update(auto_prices(FIXED_BASE, PROC, FUELS, CHARCOAL, premium))
    missing_auto = [i for i in PROC if i not in d]
    if missing_auto:
        raise SystemExit("processed goods without a price: %s" % missing_auto)
    return d


# ---- 0.1.15 C (Skyy 2026-10-16: "raise the sell price of everything to at least 2 coins, and scale everything else accordingly" +
#      "scale everything except the eternal seeds we set last night."): SCALE_X = the floor row's default / the cheapest 0.1.14 instant
#      sell at demand 1.0 (Eternal seeds left out; a raised product counted at its 0.1.13 value = the most a sell cap can hold it to),
#      rounded UP to the next 0.5. Every fixed default but the Eternal seeds x SCALE_X (PRICE_0115: id -> (0.1.14, 0.1.15) default, the
#      one-time update Catalog.migrate115 moves a line still at the old one); processed goods follow their inputs; OLD_0113 (what a sell
#      cap holds a product to) x SCALE_X - the inputs of every capped product scale, so its crafting value does; impactCoins x SCALE_X.
SCALE_FLOOR = 2       # = MINSELL_DEF (the Server Setup row market.minSell, defined with the floor below; asserted equal there)
SCALE_KEEP = sorted(_p for _p in FIXED_BASE if tier_family(_p) == "eternal")
assert len(SCALE_KEEP) == 14 and all(_p.endswith("_Eternal") for _p in SCALE_KEEP), "0.1.15: the 14 Eternal seed bags keep their price: %s" % SCALE_KEEP
ETERNAL_0114 = dict((_p, FIXED_BASE[_p]) for _p in SCALE_KEEP)
_px14 = all_prices(PREMIUM_DEF / 100.0)
_sell14 = {}
for _p, _b in _px14.items():
    if _p in SCALE_KEEP:
        continue
    _sell14[_p] = min(_b, OLD_0113[_p]) if (_p in PRICE_0114 and PRICE_0114[_p][1] > PRICE_0114[_p][0]) else _b
_cheap = sorted((_v * (1.0 - SPREAD), _p) for _p, _v in _sell14.items())
SCALE_MIN14 = _cheap[0]
SCALE_X = math.ceil(SCALE_FLOOR / SCALE_MIN14[0] * 2.0 - 1e-9) / 2.0
assert SCALE_X >= 1.0 and SCALE_MIN14[0] * SCALE_X >= SCALE_FLOOR - 1e-9
PRICE_0115 = {}
for _p, _b in sorted(FIXED_BASE.items()):
    if _p in SCALE_KEEP:
        continue
    _nb = _b * SCALE_X
    assert float("%g" % _nb) == _nb and float("%g" % _b) == _b and 0.01 <= _nb <= 1e9, ("0.1.15: %s %r x %r = %r does not print exactly" % (_p, _b, SCALE_X, _nb))
    PRICE_0115[_p] = (_b, _nb)
FIXED_BASE.update((_p, _n) for _p, (_o, _n) in PRICE_0115.items())
PRODUCTS = [(_p, (PRICE_0115[_p][1] if _p in PRICE_0115 else _b), _n) for _p, _b, _n in PRODUCTS]
OLD_0113 = dict((_p, _v * SCALE_X) for _p, _v in OLD_0113.items())
IMPACT_OLD = 10000.0                     # Market.IMPACT's 0.1.14 default (market.properties impactCoins)
IMPACT_DEF = IMPACT_OLD * SCALE_X
assert float("%g" % IMPACT_DEF) == IMPACT_DEF
print("0.1.15 scale: the cheapest 0.1.14 instant sell is %s %.4f -> x%g (floor %d / %.4f = %.4f, up to 0.5); %d fixed defaults scale, %d Eternal "
      "seed bags keep their price; impactCoins %g -> %g; the next cheapest 0.1.14 sells: %s"
      % (SCALE_MIN14[1], SCALE_MIN14[0], SCALE_X, SCALE_FLOOR, SCALE_MIN14[0], SCALE_FLOOR / SCALE_MIN14[0], len(PRICE_0115), len(SCALE_KEEP),
         IMPACT_OLD, IMPACT_DEF, ", ".join("%s %.3f" % (p, v) for v, p in _cheap[1:8])))


def unscaled(prices):
    """the same prices before the 0.1.15 scale (fixed ones; the caller re-derives the processed goods)"""
    return dict((_p, PRICE_0115[_p][0] if _p in PRICE_0115 else _v) for _p, _v in prices.items())


SEED_BASE = all_prices(PREMIUM_DEF / 100.0)
# ---- 3. the premium bound: (1 + max premium) x (1 - spread) <= 1 + spread, or buy inputs -> process -> sell pays at factor 1.0
assert (1.0 + PREMIUM_MAX / 100.0) * (1.0 - SPREAD) <= 1.0 + SPREAD, "PREMIUM_MAX %d%% makes processing pay at spread %s" % (PREMIUM_MAX, SPREAD)
assert 0 <= PREMIUM_MIN <= PREMIUM_DEF <= PREMIUM_MAX
# ---- 4. money loops: 0.1.2's check UNCHANGED (raises on a loop) at premium 0, 15, the default and the maximum + the 0.1.3 check
#         (fuel, charcoal, co-products, liquidation) at EVERY whole premium 0..22 - it runs in about a second
# 0.1.14: the loop checks of this step run after the SET recipe scan below (they need the sell caps + floor exemptions worked out over
# every SET jar's recipes too)


def set_jars():
    """[(mod, version, jar path)] of the tools/deploy_set.py SET (read as a literal, never imported); SkyyBazaar itself is skipped"""
    t = ast.parse(open(os.path.join(HERE, "..", "tools", "deploy_set.py"), encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets):
            out = []
            for mod, ver in ast.literal_eval(n.value):
                if mod == "SkyyBazaar":
                    continue
                jp = os.path.normpath(os.path.join(HERE, "..", mod, "%s-%s.jar" % (mod, ver)))
                if not os.path.exists(jp):
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not built (%s)" % (mod, ver, jp))
                out.append((mod, ver, jp))
            return out
    raise SystemExit("tools/deploy_set.py has no SET")


def set_model(M, data):
    """MODEL + every SET jar's Server/Item/Items (their Recipe, through Parent into vanilla too) and Server/Item/Recipes, and the jar
    items' resource types - added, never replacing a vanilla recipe or membership (the union can only make the check stricter)"""
    recipes = list(M["recipes"])
    rt_items = collections.defaultdict(list)
    for k, v in M["rt_items"].items():
        rt_items[k] = list(v)
    per_mod = []
    for mod, ver, jp in set_jars():
        z = zipfile.ZipFile(jp)
        items, recs = {}, []
        for n in z.namelist():
            if n.endswith(".json") and n.startswith("Server/Item/Items/"):
                try:
                    items[n.rsplit("/", 1)[1][:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
                except Exception:
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not JSON" % (mod, n))
            elif n.endswith(".json") and n.startswith("Server/Item/Recipes/"):
                try:
                    recs.append((n, json.loads(z.read(n).decode("utf-8-sig"))))
                except Exception:
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not JSON" % (mod, n))
        before = len(recipes)
        jm = None
        if items:
            merged = dict(data)
            merged.update(items)
            jm = asset_model(None, merged, None, [])
        for r in (jm["recipes"] if jm else []):
            if r[0] in items:
                recipes.append(("%s:%s" % (mod, r[0]), r[1], r[2], r[3], r[4]))
        for n, d in recs:
            outs = [(o["ItemId"], o.get("Quantity", 1) or 1) for o in (d.get("Output") or ([d["PrimaryOutput"]] if d.get("PrimaryOutput") else []))
                    if isinstance(o, dict) and o.get("ItemId")]
            ins = []
            for i in d.get("Input") or []:
                if isinstance(i, dict) and i.get("ItemId"):
                    ins.append(("I", i["ItemId"], i.get("Quantity", 1) or 1))
                elif isinstance(i, dict) and i.get("ResourceTypeId"):
                    ins.append(("R", i["ResourceTypeId"], i.get("Quantity", 1) or 1))
            br = d.get("BenchRequirement") or []
            br = [br] if isinstance(br, dict) else br
            if ins and outs:
                recipes.append(("%s:%s" % (mod, n), ins, outs, [(b.get("Type"), b.get("Id")) for b in br if isinstance(b, dict)], d.get("TimeSeconds")))
        for k in (items if jm else ()):
            for r in jm["rtypes"](k):
                if k not in rt_items[r]:
                    rt_items[r].append(k)
        per_mod.append((mod, len(items), len(recipes) - before))
    return {"inh": M["inh"], "rtypes": M["rtypes"], "rt_items": rt_items, "recipes": recipes, "benches": M["benches"],
            "fuels": M["fuels"]}, per_mod


SET_MODEL, SET_SCAN = set_model(MODEL, DATA)

# ================= 0.1.14: SELL CAPS + THE MINIMUM SELL PRICE, worked out over every recipe the checks know (vanilla + every SET jar:
# SkyyCollections' stone conversions and Enchanted compressing included), at every floor 0..MINSELL_MAX and premium min / default / max.
# A loop found -> (1) an output whose price 0.1.14 RAISED keeps its 0.1.13 value as its sell price (SELL_CAP); else (2) at floor 0 an
# input whose price 0.1.14 LOWERED keeps its 0.1.13 price; else, when the floor lifted an output: (3a) every input itself trades at the
# floor (junk -> junk: 1 cobble -> 2 rubble) -> those inputs' BUY side is raised just enough (BUY_X, x the floor value, at most
# BUY_X_MAX; their sell side keeps the floor), else (3b) the lifted outputs never take the floor (FLOOR_EXEMPT); else (2). Raising a buy
# price can never open a loop. Repeated until no recipe pays anywhere; a loop none of these closes stops the build.
MINSELL_DEF, MINSELL_MIN, MINSELL_MAX = 2, 0, 5      # Server Setup row market.minSell (coins per item)
assert SCALE_FLOOR == MINSELL_DEF, "0.1.15: the scale follows the floor row's default"
CONFIRM_DEF = 3000                                    # Server Setup row confirm.default (coins; Skyy "default like 3,000")
SELL_CAP, FLOOR_EXEMPT, HELD_0114, BUY_X = {}, set(), {}, {}
EFF["caps"], EFF["exempt"], EFF["bx"] = SELL_CAP, FLOOR_EXEMPT, BUY_X
BUY_X_MAX = 2.0       # a floor-taking input's buy side may be raised to at most 2 x the floor value; past that its outputs are exempt
_WHY = {}
_p0_ = all_prices(0.0)
_bc_ = math.floor(0.98 * (1 + SPREAD) * (_p0_[BRONZE_RECIPE[0]] + _p0_[BRONZE_RECIPE[1]]) / (1 - SPREAD) * 100.0) / 100.0
if _bc_ < _p0_[BRONZE_ID]:
    SELL_CAP[BRONZE_ID] = _bc_      # 0.1.20: Bronze sells for (just under) its two ingots' price: no buy ingots -> alloy -> sell profit at any premium 0-22
print("0.1.20: Bronze sell cap %g (buy stays %g; Copper + Iron Ingot at premium 0: %g + %g)" % (_bc_, _p0_[BRONZE_ID], _p0_[BRONZE_RECIPE[0]], _p0_[BRONZE_RECIPE[1]]))


def _cands(kd, key):
    return [key] if kd == "I" else list(SET_MODEL["rt_items"].get(key, []))


def _hold(pid, why):
    """(2): keep the 0.1.13 price of a product 0.1.14 lowered"""
    o, n = PRICE_0114.pop(pid)
    HELD_0114[pid] = (o, n, why)
    o0 = o                                               # 0.1.15: a held product's LIVE default is its 0.1.13 price (not the tier price n)
    o = o * (SCALE_X if pid in PRICE_0115 else 1.0)      # 0.1.15: the held 0.1.13 price, scaled like every other price
    FIXED_BASE[pid] = o
    if pid in PRICE_0115:
        PRICE_0115[pid] = (o0, o)                        # migrate115 expects the line to hold o0 (what 0.1.14 seeded), not n
    global PRODUCTS
    PRODUCTS = [(_p, (o if _p == pid else _b), _n) for _p, _b, _n in PRODUCTS]


import time as _time
_T0 = _time.time()


def _step_loops(model, px):
    """ONE-step loops (the admin guard's view, over every recipe of the model whose inputs are all products): inputs bought at the
    cheapest candidate's buy value + fuel, the product outputs sold at their sell value - under EFF. These are the ROOTS: a chain loop
    (the full check) is built on a cheap step; fixing the steps first keeps the fixes to the products that really cause a loop."""
    eb, es = eff_prices(px, SPREAD)
    benches = model["benches"]
    fb_ = benches.get("Furnace", {})
    ch_ = fb_["extra"][0][0] if fb_.get("extra") else None
    fs = None
    for f, fq in model["fuels"]:
        if f in eb and f not in fb_.get("ignored", set()) and fb_.get("per"):
            c = (eb[f] * (1 + SPREAD) - (es[ch_] * (1 - SPREAD) / fb_["per"] if ch_ in es else 0.0)) / fq
            fs = c if fs is None else min(fs, c)
    fs = max(0.0, fs or 0.0)
    out = []
    for name, ins, outs, bks, t in model["recipes"]:
        if not any(o in es for o, q in outs):
            continue
        tot, ok = 0.0, True
        for kd, key, q in ins:
            cs = [eb[c] for c in ([key] if kd == "I" else model["rt_items"].get(key, [])) if c in eb]
            if not cs:
                ok = False
                break
            tot += q * min(cs) * (1 + SPREAD)
        if not ok:
            continue
        for typ, bid in bks:
            b_ = benches.get(bid)
            if typ == "Processing" and b_ and b_["fuel"]:
                tot += fs * float(t or 0.0) * (1.0 - b_["reduction"])
                break
        val = sum(q * es[o] * (1 - SPREAD) for o, q in outs if o in es)
        if val > tot + 1e-9:
            out.append((val / tot if tot > 0 else float("inf"), name, ins, outs))
    return out


def _fixes(loops, fl, px, root):
    """apply the fixes the loops call for; returns (applied, unresolved). Pass A: sell caps, held prices and buy-side raises (none of
    them can open another loop); pass B, only when pass A found nothing: the floor-lifted outputs of ONE loop never take the floor."""
    fb = fl / (1.0 - SPREAD) if fl else 0.0
    eb, es = eff_prices(px, SPREAD)
    applied, unres, exempt_c = 0, [], []
    for lp in loops:
        ratio, name, ins, outs = lp[:4]
        if not root and ratio == float("inf"):
            continue                       # a chain cascading from a root (costs worked out to 0) - its root is fixed first
        cap = [o for o, q in outs if o in PRICE_0114 and PRICE_0114[o][1] > PRICE_0114[o][0] and o not in SELL_CAP]
        acap = [o for o, q in outs if o in ALLOY_FIXED and o in px]       # 0.1.20: a fixed-price alloy sells for its crafting value
        low = sorted(set(c for kd, key, q in ins for c in _cands(kd, key) if c in PRICE_0114 and PRICE_0114[c][1] < PRICE_0114[c][0]))
        flo = [o for o, q in outs if fl and o in px and o not in FLOOR_EXEMPT and min(px[o], SELL_CAP.get(o, px[o])) < fb - 1e-12]
        junk, allj = set(), bool(fl)
        for kd, key, q in ins:
            cs = [c for c in _cands(kd, key) if c in eb]
            if not cs:
                allj = False
                break
            m = min(eb[c] for c in cs)
            at = [c for c in cs if eb[c] <= m + 1e-12]
            if not all(c not in FLOOR_EXEMPT and eb[c] <= fb * BUY_X.get(c, 1.0) + 1e-12 for c in at):
                allj = False
                break
            junk.update(at)
        r = (ratio if ratio != float("inf") else 99.0) * 1.01
        if acap:
            for o in acap:
                _cur = min(px[o], SELL_CAP.get(o, px[o]))
                SELL_CAP[o] = math.floor(_cur / r * 100.0 - 1e-9) / 100.0
                _WHY[o] = name
        elif cap:
            for o in cap:
                SELL_CAP[o] = OLD_0113[o]
                _WHY[o] = name
        elif low and not fl:
            for c in low:
                if c in PRICE_0114:
                    _hold(c, name)
        elif allj and junk and all(BUY_X.get(c, 1.0) * r <= BUY_X_MAX for c in junk):
            for c in junk:
                BUY_X[c] = math.ceil(BUY_X.get(c, 1.0) * r * 100.0 - 1e-9) / 100.0
                _WHY[c] = "%s (floor %d: buy x%.2f)" % (name, fl, BUY_X[c])
        elif flo:
            exempt_c.append((name, flo))
            continue
        elif low:
            for c in low:
                if c in PRICE_0114:
                    _hold(c, name)
        else:
            unres.append((fl, ratio, name, ins, outs))
            continue
        applied += 1
    if not applied and exempt_c:
        name, flo = exempt_c[0]
        for o in flo:
            FLOOR_EXEMPT.add(o)
            _WHY[o] = "%s (floor %d)" % (name, fl)
        applied = 1
        unres = []
    return applied, unres


_unres, _nlc = [], 0
for _round in range(40):
    _changed, _unres = False, []
    for _fl in [MINSELL_MIN, MINSELL_DEF] + [f for f in range(MINSELL_MIN + 1, MINSELL_MAX + 1) if f != MINSELL_DEF]:
        EFF["floor"] = float(_fl)
        for _prem in (PREMIUM_MIN, PREMIUM_DEF, PREMIUM_MAX):
            for _guard in range(200):
                _px = all_prices(_prem / 100.0)
                _n, _u = _fixes(_step_loops(SET_MODEL, _px), _fl, _px, True)
                if _n:
                    _changed = True
                    continue
                if _u:
                    _unres += [(_prem,) + x for x in _u]
                    break
                _nlc += 1
                _n, _u = _fixes(loop_check(SET_MODEL, _px, SPREAD)[0], _fl, _px, False)
                if _n:
                    _changed = True
                    continue
                _unres += [(_prem,) + x for x in _u]
                break
    if not _changed:
        break
print("0.1.14 caps / floor worked out in %d sweeps, %d full loop checks, %.0f s" % (_round + 1, _nlc, _time.time() - _T0))
if _unres or _changed:
    for _prem, _fl, ratio, name, ins, outs in _unres[:30]:
        print("UNRESOLVED MONEY LOOP floor %d premium %d%% x%.3f %s in=%s -> out=%s" % (_fl, _prem, ratio, name, ins, outs))
    raise SystemExit("0.1.14: %d money loops neither a sell cap, a held price nor a floor exemption closes" % len(_unres))
EFF["floor"] = float(MINSELL_DEF)
print("0.1.14 sell caps (a recipe makes these for less - they sell at their 0.1.13 value): %s"
      % ", ".join("%s %g" % (i, SELL_CAP[i]) for i in sorted(SELL_CAP)))
for _i in HELD_0114:
    assert _i not in PRICE_0115 or PRICE_0115[_i][0] == HELD_0114[_i][0], "0.1.15: held %s - the update would expect %r, its line holds %r" % (_i, PRICE_0115[_i][0], HELD_0114[_i][0])
print("0.1.14 held at the 0.1.13 price (lowering it would let a recipe pay): %s"
      % (", ".join("%s %g (tier ladder %g; %s)" % (i, o, n, w.replace("Server/Item/Recipes/", "")) for i, (o, n, w) in sorted(HELD_0114.items())) or "none"))
print("0.1.14 minimum sell price %d (0-%d): %d products never take it (a recipe would turn it into coins): %s"
      % (MINSELL_DEF, MINSELL_MAX, len(FLOOR_EXEMPT), ", ".join("%s (%s)" % (i, _WHY.get(i, "?").replace("Server/Item/Recipes/", "")) for i in sorted(FLOOR_EXEMPT))))
print("0.1.14 buy side raised over the floor value (their sell side keeps the floor; a cheap conversion would pay otherwise): %s"
      % (", ".join("%s x%.2f" % (i, BUY_X[i]) for i in sorted(BUY_X)) or "none"))
# ---- the 0.1.3 checks (moved here from step 4): check_assets + the full loop check over the vanilla recipes, every premium at the
#      default floor, premium min / default / max at every other floor
_f0 = EFF["floor"]
EFF["floor"] = 0.0
_selftest = loop_check_selftest()
EFF["floor"] = _f0
print("loop check self-test: the craft -> salvage -> smelt chain is seen (%s), a chain that does not pay is not" % ", ".join(_selftest))
for _fl in range(MINSELL_MIN, MINSELL_MAX + 1):
    EFF["floor"] = float(_fl)
    for _prem in (range(PREMIUM_MIN, PREMIUM_MAX + 1) if _fl == MINSELL_DEF else (PREMIUM_MIN, PREMIUM_DEF, PREMIUM_MAX)):
        _px = all_prices(_prem / 100.0)
        if _prem in (PREMIUM_MIN, 15, PREMIUM_DEF, PREMIUM_MAX) and _fl in (0, MINSELL_DEF, MINSELL_MAX):
            check_assets(_px, SPREAD, dict(ENCH_DATA, **ZONE_DATA), [r for r in ZONE_RECS if r[0] != "SkyWynn:Alloy_Bronze"])   # 0.1.10: + the Enchanted items; 0.1.20: + the zone metals
        for _mn, _mdl in ((("vanilla", MODEL), ("SET jars", SET_MODEL)) if _fl == MINSELL_DEF else (("SET jars", SET_MODEL),)):
            _loops, _costable, _nrec, _passes = loop_check(_mdl, _px, SPREAD)
            if _loops:
                for ratio, name, ins, outs, fuel_s in sorted(_loops, reverse=True)[:30]:
                    print("MONEY LOOP (%s) x%.3f  %s  in=%s -> out=%s fuel=%.1fs" % (_mn, ratio, name, ins, outs, fuel_s))
                raise SystemExit("%d buy -> process / craft -> sell money loops (%s) at premium %d%%, minimum sell price %d"
                                 % (len(_loops), _mn, _prem, _fl))
            if _prem in (PREMIUM_MIN, PREMIUM_DEF, PREMIUM_MAX) and _fl == MINSELL_DEF and _mdl is MODEL:
                print("loop check at premium %d%%: %d recipes (+ fuel, + burn), %d fully buyable, fixed point in %d passes, no money loops"
                      % (_prem, _nrec, _costable, _passes))
EFF["floor"] = float(MINSELL_DEF)
print("0.1.14 full verification done at %.0f s" % (_time.time() - _T0))
# ---- 0.1.15: with the floor OFF, every product but the Eternal seeds already sells 1 for at least the floor row's default at demand 1.0
#      (the scale did it, not the floor); the Eternal seeds keep their 2026-10-15 prices; the sample table
EFF["floor"] = 0.0
_pb15, _ps15 = eff_prices(all_prices(PREMIUM_DEF / 100.0), SPREAD)
EFF["floor"] = float(MINSELL_DEF)
_low15 = sorted((round(_ps15[_p] * (1.0 - SPREAD), 4), _p) for _p in _ps15 if _p not in SCALE_KEEP and _ps15[_p] * (1.0 - SPREAD) < MINSELL_DEF - 1e-9)
assert not _low15, "0.1.15: products still selling under %d with the floor off: %s" % (MINSELL_DEF, _low15[:10])
assert all(FIXED_BASE[_p] == ETERNAL_0114[_p] for _p in SCALE_KEEP), "0.1.15: an Eternal seed price moved"
_sm = ["Rubble_Stone", "Rock_Stone_Cobble", "Ore_Copper", "Ingredient_Bar_Copper", "Ore_Iron", "Ingredient_Bar_Iron", "Ore_Adamantite",
       "Wood_Oak_Trunk", "Plant_Sapling_Oak", "Ingredient_Tree_Sap", "Plant_Crop_Wheat_Item", EN.PREFIX + "Wheat", "Plant_Seeds_Wheat",
       "Plant_Seeds_Wheat_Eternal", "Plant_Crop_Potato_Item", "Plant_Seeds_Potato_Eternal", "Ingredient_Fibre", "Ingredient_Leather_Light",
       "Ingredient_Life_Essence", "Food_Fish_Raw", "Ingredient_Crystal_Blue"]
_old15 = unscaled(FIXED_BASE)
_old15.update(auto_prices(_old15, PROC, FUELS, CHARCOAL, PREMIUM_DEF / 100.0))
_new15 = all_prices(PREMIUM_DEF / 100.0)
print("0.1.15 samples (base 0.1.14 -> 0.1.15; sell cap): %s" % "; ".join(
    "%s %g -> %g%s" % (_p, round(_old15[_p], 3), round(_new15[_p], 3), (" (cap %g)" % SELL_CAP[_p]) if _p in SELL_CAP else "")
    for _p in _sm if _p in _new15))
_rat = [(_p, _old15[_p], _new15[_p]) for _p in _new15 if _p not in SCALE_KEEP and (
    abs(_new15[_p] - _old15[_p] * SCALE_X) > (0.01 * SCALE_X + 1e-9 if _p in PROC else 1e-9 * _new15[_p]))]
assert not _rat, "0.1.15: products that did not move by x%g: %s" % (SCALE_X, _rat[:10])
_proc_r = [_new15[_p] / _old15[_p] for _p in PROC if _p in _new15 and _old15[_p] > 0]
print("0.1.15: all %d products but the %d Eternal seed bags moved by x%g (fixed ones exactly; %d processed goods within the 0.01 price step: "
      "x%.4f .. x%.4f); the cheapest sale with the floor "
      "off is now %s" % (len(_new15), len(SCALE_KEEP), SCALE_X, len(_proc_r), min(_proc_r), max(_proc_r), min((round(_ps15[_p] * (1.0 - SPREAD), 3), _p) for _p in _ps15 if _p not in SCALE_KEEP)))
print("loop check: no money loop at any premium %d-%d%% (minimum sell price %d), nor at premium %d / %d / %d with any minimum "
      "sell price %d-%d (vanilla + SET jar recipes)" % (PREMIUM_MIN, PREMIUM_MAX, MINSELL_DEF, PREMIUM_MIN, PREMIUM_DEF,
                                                        PREMIUM_MAX, MINSELL_MIN, MINSELL_MAX))
# ---- 0.1.14: the buy price is never at or below the sell price (any product, any demand 0.25-4, any floor), and no instant sale of a
#      product that takes the floor pays less than it - the Market.quote unit rule: max(base x demand, floor value) x (1 +- spread)
for _fl in range(MINSELL_MIN, MINSELL_MAX + 1):
    for _p, _b in all_prices(PREMIUM_DEF / 100.0).items():
        _fb = _fl / (1.0 - SPREAD) if (_fl and _p not in FLOOR_EXEMPT) else 0.0
        _sb = min(_b, SELL_CAP.get(_p, _b))
        for _d in (0.25, 0.5, 1.0, 2.0, 4.0):
            _bu, _se = max(_b * _d, _fb * BUY_X.get(_p, 1.0)) * (1 + SPREAD), max(_sb * _d, _fb) * (1 - SPREAD)
            assert _bu > _se, ("0.1.14: buy at or below sell", _p, _fl, _d)
            assert not _fb or _se >= _fl - 1e-9, ("0.1.14: a sale under the minimum", _p, _fl, _d)
# ---- 0.1.14: the step a buy pushes the demand must stay under (1 + s) / (1 - s) or ONE buy then ONE sell pays: step = exp(ln 1.1 x
#      base / impact) was only capped at 4, so every product over ~21,000 (Enchanted Cobalt / Adamantite, the top Eternal seeds) could
#      be bought and sold straight back at a profit (0.1.13: Enchanted Adamantite 57,600 -> step 1.73: +26,000 coins a round trip).
#      Market.step now also stops at 1 + 0.9 x ((1 + s) / (1 - s) - 1) = 1.2 at the 10 % spread.
_IMPACT = IMPACT_DEF      # 0.1.15: x SCALE_X with the prices
STEP_MAX = 1.0 + 0.9 * ((1.0 + SPREAD) / (1.0 - SPREAD) - 1.0)
for _p, _b in all_prices(PREMIUM_DEF / 100.0).items():
    _st = min(4.0, STEP_MAX, math.exp(math.log(1.10) * _b / _IMPACT))
    _sb = min(_b, SELL_CAP.get(_p, _b))
    assert _sb * _st * (1 - SPREAD) < _b * (1 + SPREAD), "0.1.14: %s base %g: one buy then one sell would pay (step %.3f)" % (_p, _b, _st)
# ---- 0.1.14: SkyyMerchants (the SET pin's stock tables): no merchant weapon liquidates (salvage -> smelt / tan -> Bazaar sale) for more
#      than its price - the merchants sell only weapons / mounts / pet eggs (no Bazaar product); the fallback weapons cost at least the
#      cheapest zone's median table price


def merchant_rows():
    mv = [v for m, v, jp in set_jars() if m == "SkyyMerchants"]
    if not mv:
        return None, []
    t = ast.parse(open(os.path.join(HERE, "..", "SkyyMerchants", "build_skyymerchants_%s.py" % mv[0]), encoding="utf8").read())
    rows = []
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") in ("WEAPONS", "MOUNTS", "PETS") for x in n.targets):
            rows += [tuple(r[:4]) for r in ast.literal_eval(n.value)]
    return mv[0], rows


MERCH_VER, MERCH_ROWS = merchant_rows()
_mz = {}
for _id, _z, _pr, _st in MERCH_ROWS:
    for _zz in str(_z).split(","):
        _mz.setdefault(_zz.strip(), []).append(_pr)
MERCH_FLOOR = min(sorted(v)[len(v) // 2] for v in _mz.values()) if _mz else 0
MERCH_BAD = {}
MERCH_LIQ = {}
for _tag, _fl, _old in (("0.1.13", 0.0, True), ("0.1.15", float(MINSELL_DEF), False), ("0.1.15 max floor", float(MINSELL_MAX), False)):
    if _old:
        EFF["caps"], EFF["exempt"], EFF["bx"] = {}, set(), {}
        _fbo = unscaled(FIXED_BASE)                      # 0.1.15: the real 0.1.13 prices
        _fbo.update((i, o) for i, (o, n) in PRICE_0114.items())
        _pxm = dict(_fbo)
        _pxm.update(auto_prices(_fbo, PROC, FUELS, CHARCOAL, PREMIUM_MAX / 100.0))
    else:
        _pxm = all_prices(PREMIUM_MAX / 100.0)
    EFF["floor"] = _fl
    _vals = {}
    loop_check(SET_MODEL, _pxm, SPREAD, None, _vals)
    EFF["caps"], EFF["exempt"], EFF["bx"] = SELL_CAP, FLOOR_EXEMPT, BUY_X
    _liq = _vals["liq"]
    _bad = [(i, round(_liq.get(i, 0.0)), pr) for i, z, pr, st in MERCH_ROWS if _liq.get(i, 0.0) >= pr]
    _bad += [(i, round(v), MERCH_FLOOR) for i, v in _liq.items() if i.startswith("Weapon_") and i not in FIXED_BASE and v >= MERCH_FLOOR]
    MERCH_BAD[_tag] = sorted(set((i, pr) for i, v, pr in _bad))
    MERCH_LIQ[_tag] = dict(_liq)                         # 0.1.15: for the precise zone check below
    _top = sorted(((v, i) for i, v in _liq.items() if i.startswith("Weapon_") or i in [r[0] for r in MERCH_ROWS]), reverse=True)[:3]
    print("0.1.14 SkyyMerchants %s check (%s prices, premium %d%%): %d stock rows, fallback weapons cost >= %d; best weapon liquidation %s; "
          "rows a player could buy and liquidate for more: %s" % (MERCH_VER, _tag, PREMIUM_MAX, len(MERCH_ROWS), MERCH_FLOOR,
                                                                   ", ".join("%s %.0f" % (i, v) for v, i in _top), MERCH_BAD[_tag] or "none"))
EFF["caps"], EFF["exempt"], EFF["floor"] = SELL_CAP, FLOOR_EXEMPT, float(MINSELL_DEF)
# ---- 0.1.15: the check above prices every fallback weapon at the CHEAPEST zone's median (2,500) - at x4.5 that flags every Adamantite /
#      Mithril / Doomed weapon. The PRECISE check: each stock row at its own price in its zones; each vanilla fallback weapon (SkyyMerchants
#      0.1.1's pool rule: a metal-ladder Weapon_* with an ItemLevel and Quality Common..Epic; no arrows / shields / Rusty / NPC / Test) only
#      in the zones whose level band holds its ItemLevel, at that zone's median table price (fallbackPrice). A row / weapon that liquidates
#      (salvage -> smelt / tan -> Bazaar sale, premium max) for more than that price at 0.1.15 but not at 0.1.13 = a NEW merchant -> Bazaar
#      loop: SkyyMerchants is another builder's mod, so it is reported here (MERCH_FOLLOWUP) and the build stops if the list changes.
def merch_precise():
    mv = [v for m, v, jp in set_jars() if m == "SkyyMerchants"]
    if not mv:
        return {}, {}
    t = ast.parse(open(os.path.join(HERE, "..", "SkyyMerchants", "build_skyymerchants_%s.py" % mv[0]), encoding="utf8").read())
    zl = []
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "ZONES" for x in n.targets):
            zl = ast.literal_eval(n.value)
    band = {}
    for k, _a, _e, lv in zl:
        lo, hi = [int(x) for x in str(lv).split("-")]
        band[str(k).replace("zone", "")] = (lo, hi)
    med = {}
    for _id, _z, _pr, _st in MERCH_ROWS:
        for _zz in str(_z).split(","):
            med.setdefault(_zz.strip(), []).append(_pr)
    med = dict((z, sorted(v)[len(v) // 2]) for z, v in med.items())
    z_ = zipfile.ZipFile(ASSETS)
    path = dict((n.rsplit("/", 1)[1][:-5], n) for n in z_.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))

    def get(i, key, depth=0):
        d = _load_json(z_, path[i]) or {}
        if key in d or depth > 8 or not d.get("Parent") or d.get("Parent") not in path:
            return d.get(key)
        return get(d["Parent"], key, depth + 1)
    metals = ("Copper", "Bronze", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
    fb = {}
    for i in sorted(path):
        w = i.split("_")
        if not i.startswith("Weapon_") or i.startswith(("Weapon_Arrow_", "Weapon_Shield_")):
            continue
        if not any(m in w for m in metals) or any(x in w for x in ("Rusty", "NPC", "Test")):
            continue
        lv, q = get(i, "ItemLevel"), get(i, "Quality")
        if isinstance(lv, int) and lv > 0 and q in ("Common", "Uncommon", "Rare", "Epic"):
            fb[i] = lv
    offers = {}        # id -> the cheapest price a merchant asks for it anywhere
    for _id, _z, _pr, _st in MERCH_ROWS:
        offers[_id] = min(offers.get(_id, _pr), _pr)
    for i, lv in fb.items():
        for zk, (lo, hi) in band.items():
            if lo <= lv <= hi and zk in med:
                offers[i] = min(offers.get(i, med[zk]), med[zk])
    return offers, fb


MERCH_OFFERS, MERCH_FB = merch_precise()
MERCH_PRECISE = {}
for _tag in ("0.1.13", "0.1.15", "0.1.15 max floor"):
    _lq = MERCH_LIQ.get(_tag, {})
    MERCH_PRECISE[_tag] = dict((i, (round(_lq[i]), pr)) for i, pr in MERCH_OFFERS.items() if _lq.get(i, 0.0) >= pr)
_tight = sorted(((MERCH_LIQ.get("0.1.15", {}).get(i, 0.0) / pr, i, pr) for i, pr in MERCH_OFFERS.items()), reverse=True)[:6]
print("0.1.15 SkyyMerchants tightest at x%g (liquidation / cheapest merchant price, 1.0 = a loop): %s" % (SCALE_X, ", ".join(
    "%s (Lv %s) %.0f / %d = %.2f" % (i, MERCH_FB.get(i, "table"), MERCH_LIQ["0.1.15"].get(i, 0.0), pr, r) for r, i, pr in _tight)))
MERCH_NEW = sorted(set(MERCH_PRECISE["0.1.15"]) | set(MERCH_PRECISE["0.1.15 max floor"]) - set(MERCH_PRECISE["0.1.13"]))
print("0.1.15 SkyyMerchants %s PRECISE check (%d stock rows + %d fallback weapons at their zone's median, premium %d%%): loops at 0.1.13 "
      "prices: %s; NEW at x%g: %s" % (MERCH_VER, len(MERCH_ROWS), len(MERCH_FB), PREMIUM_MAX,
                                      ", ".join("%s liquidates %d >= costs %d" % (i, v, pr) for i, (v, pr) in sorted(MERCH_PRECISE["0.1.13"].items())) or "none",
                                      SCALE_X, ", ".join("%s (Lv %s) liquidates %d >= costs %d" % (i, MERCH_FB.get(i, "table"), MERCH_PRECISE["0.1.15"].get(i, MERCH_PRECISE["0.1.15 max floor"].get(i))[0],
                                                                                 MERCH_OFFERS[i]) for i in MERCH_NEW) or "none"))
MERCH_FOLLOWUP = None
if MERCH_FOLLOWUP is not None:
    assert MERCH_NEW == MERCH_FOLLOWUP, "0.1.15: the merchant follow-up list changed: %s" % MERCH_NEW
else:
    assert not MERCH_NEW, "0.1.15 opens a merchant -> Bazaar loop (report it; SkyyMerchants is not this round's mod): %s" % MERCH_NEW
# ---- 0.1.14: the price table by tier (old -> new), per family
_px_new = all_prices(PREMIUM_DEF / 100.0)
_fbo = unscaled(FIXED_BASE)                              # 0.1.15: old = the real 0.1.13 prices
_fbo.update((i, o) for i, (o, n) in PRICE_0114.items())
_px_old = dict(_fbo)
_px_old.update(auto_prices(_fbo, PROC, FUELS, CHARCOAL, PREMIUM_DEF / 100.0))
for _sp, _lg in SAPLING_LOG.items():
    TIERED[_sp] = ("sapling", TIERED[_lg][1])
for _f in ("ore", "bar", "log", "sapling", "crop", "seed", "eternal", "enchanted"):
    _rows = sorted((t, p) for p, (f, t) in TIERED.items() if f == _f)
    _bt = {}
    for t, p in _rows:
        _bt.setdefault(t, []).append(p)
    print("0.1.14 %s by tier (base old -> new; sell cap): %s" % (_f, "; ".join(
        "T%d %s" % (t, ", ".join("%s %g->%g%s" % (p.replace("Plant_Seeds_", "").replace("Plant_Crop_", "").replace("Wood_", "").replace(
            "_Trunk", "").replace("Ingredient_Bar_", "").replace("Skyy_Ench_", "").replace("Ore_", "").replace("Plant_Sapling_", ""), round(_px_old[p], 2), round(_px_new[p], 2),
            (" (sells as %g)" % SELL_CAP[p]) if p in SELL_CAP else "") for p in ps)) for t, ps in sorted(_bt.items()))))
    _mins = dict((t, min(_px_new[p] for p in ps)) for t, ps in _bt.items())
    _maxs = dict((t, max(_px_new[p] for p in ps)) for t, ps in _bt.items())
    _ts = sorted(_bt)
    _bad = [(a, b) for a, b in zip(_ts, _ts[1:]) if not _mins[b] > _maxs[a]]
    if _bad:
        print("  NOTE %s: a higher tier is not above every product of the tier below at %s" % (_f, _bad))
print("0.1.14: %d default prices change (%d up, %d down), %d held at their 0.1.13 price"
      % (len(PRICE_0114), len([1 for o, n in PRICE_0114.values() if n > o]), len([1 for o, n in PRICE_0114.values() if n < o]), len(HELD_0114)))
_extra = [(m, i, r) for m, i, r in SET_SCAN if i or r]
for _prem in range(PREMIUM_MIN, PREMIUM_MAX + 1):
    _loops = loop_check(SET_MODEL, all_prices(_prem / 100.0), SPREAD)[0]
    if _loops:
        for ratio, name, ins, outs, fuel_s in sorted(_loops, reverse=True)[:30]:
            print("MONEY LOOP (SET jars) x%.3f  %s  in=%s -> out=%s fuel=%.1fs" % (ratio, name, ins, outs, fuel_s))
        raise SystemExit("%d money loops through the SET jars' recipes at premium %d%%" % (len(_loops), _prem))
print("0.1.4 SET recipe scan: %d jars, items / recipes added: %s; %d recipes in all - no money loop at any premium %d-%d%%"
      % (len(SET_SCAN), ", ".join("%s %d/%d" % e for e in _extra), len(SET_MODEL["recipes"]), PREMIUM_MIN, PREMIUM_MAX))
def tight(prem, n=10):
    """the n recipes closest to paying at this premium (liquidated outputs / cheapest inputs, 1.0 = a loop), processing recipes of the
    AUTO goods (and fuel burns) left out - those sit at (1 + premium) x 0.9 / 1.1 by construction"""
    got = []
    loop_check(SET_MODEL, all_prices(prem / 100.0), SPREAD, got)
    bound = (1 + prem / 100.0) * (1 - SPREAD) / (1 + SPREAD)
    seen, top, at = set(), [], set()
    for r, nm, ins, outs, fs in sorted(got, key=lambda x: -x[0]):
        if nm in seen or all(o in PROC for o, q in outs):
            continue
        seen.add(nm)
        if r >= bound - 1e-6:
            at.add(nm)          # liquidated through a processing step (burn to charcoal, smelt, tan, weave): the premium bound
            continue
        top.append((r, nm))
        if len(top) >= n:
            break
    return top, len(at)


MARGINS = dict((p, tight(p)) for p in (PREMIUM_DEF, PREMIUM_MAX))
for _p, (_top, _at) in sorted(MARGINS.items()):
    print("tightest recipes at premium %d%% (outputs liquidated / inputs at their cheapest; 1.0 = a loop; %d recipes sit at the processing "
          "bound %.4f): %s" % (_p, _at, (1 + _p / 100.0) * (1 - SPREAD) / (1 + SPREAD),
                               "; ".join("%s %.4f" % (n.replace("Server/Item/Recipes/", "").replace(".json", ""), r) for r, n in _top)))
# ---- 5. what the jar carries
SEED_LINES = []
for pid, base, name in PRODUCTS:
    SEED_LINES.append("%s=%s,%s,%s" % (pid, BAG_OF[pid], ("%g" % SEED_BASE[pid]) if base is AUTO else ("%g" % float(base)), name))
OLD_SEED_LINES = ["%s=%s,%s,%s" % (p, c, ("%g" % b), n) for p, c, b, n in PRODUCTS_012]
# 0.1.4: the 0.1.3 seed lines (0.1.3 fixed prices = PRICE_014's old values, its auto prices at the default premium from them)
_fb013 = dict(FIXED_BASE)
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_0114.items())   # 0.1.14: the 0.1.13 defaults first (PRICE_014's 0.1.3 ones win)
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_014.items())
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_015.items())   # 0.1.5: sap was 4 in 0.1.3 (and 0.1.4)
_auto013 = auto_prices(_fb013, PROC, FUELS, CHARCOAL, PREMIUM_DEF / 100.0)
SEED013_LINES = ["%s=%s,%s,%s" % (pid, OLD_BAG_OF.get(BAG_OF[pid], BAG_OF[pid]), "%g" % (_auto013[pid] if base is AUTO else _fb013[pid]), name) for pid, base, name in PRODUCTS]   # 0.1.9: the 0.1.3 category
# 0.1.9: ids whose bag moved (fish: Farming -> Fishing) -> their old bag; the NEW products of 0.1.9 (appended once by Catalog.migrate19)
OLDBAG_ID = [pid for pid, _b, _n in PRODUCTS if BAG_OF[pid] in OLD_BAG_OF]
OLDBAG_TAB = [OLD_BAG_OF[BAG_OF[pid]] for pid in OLDBAG_ID]
NEW019 = ["Ingredient_Crystal_Blue", "Ingredient_Crystal_Cyan", "Ingredient_Crystal_Green", "Ingredient_Crystal_Pink", "Ingredient_Crystal_Purple",
          "Ingredient_Crystal_Red", "Ingredient_Crystal_White", "Ingredient_Crystal_Yellow", "Ingredient_Crystal_Void"]
assert all(i in BAG_OF and BAG_OF[i] == "Mining" for i in NEW019), "0.1.9: the crystals must be Mining bag products"
# 0.1.10: appended once by Catalog.migrate110 - FROZEN at 0.1.16 to the original 19 ids (tools/skyyench.py grew a 20th row; migrate110 stays
# exactly what it was, the new row has its own one-time update migrate116)
NEW0110 = ["Skyy_Ench_Cobblestone", "Skyy_Ench_Rubble", "Skyy_Ench_Copper", "Skyy_Ench_Iron", "Skyy_Ench_Thorium", "Skyy_Ench_Cobalt",
           "Skyy_Ench_Adamantite", "Skyy_Ench_Oak", "Skyy_Ench_Maple", "Skyy_Ench_Gumboab", "Skyy_Ench_Redwood", "Skyy_Ench_Sallow",
           "Skyy_Ench_Wheat", "Skyy_Ench_Carrot", "Skyy_Ench_Cauliflower", "Skyy_Ench_Pumpkin", "Skyy_Ench_Tomato", "Skyy_Ench_Cotton",
           "Skyy_Ench_Potato"]
assert len(NEW0110) == 19 and NEW0110 == EN20_IDS[:19], "0.1.16: NEW0110 = the 19 Enchanted ids of 0.1.10 (frozen; 0.1.19: skyyench TABLE_20)"
# 0.1.16 (Skyy 2026-10-16 "make enchanted sticks too"): appended once by Catalog.migrate116 (migrate110's pattern)
NEW0116 = ["Skyy_Ench_Stick"]
assert NEW0116 == [i for i in EN20_IDS if i not in NEW0110], "0.1.16: NEW0116 = every Enchanted id after the frozen 19 (0.1.19: of TABLE_20)"
assert all(i in BAG_OF and BAG_OF[i] == EN.cat_of(i) == "Foraging" for i in NEW0116), [(i, BAG_OF.get(i)) for i in NEW0116]
assert all(i in BAG_OF and BAG_OF[i] == EN.cat_of(i) for i in NEW0110), [(i, BAG_OF.get(i), EN.cat_of(i)) for i in NEW0110]
assert all(i in PROC for i in NEW0110 + NEW0116), "0.1.10: every Enchanted product is a processed good"
for _i in NEW0110 + NEW0116:
    _e = PROC[_i]
    assert _e["outq"] == 1 and len(_e["inputs"]) == 1 and _e["inputs"][0][0] == EN.RATIO and _e["secs"] == 0.0, (_i, _e)
# 0.1.19 (round coll24, Skyy 2026-10-16 C1 follow-ups "Bazaar lists the new Enchanted items"): appended once by Catalog.migrate119
# (migrate116's pattern) = every listed Enchanted id after the frozen 20, in table order
NEW0120_ENCH = [i for i in EN.IDS if i not in EN102_IDS]      # 0.1.20: Enchanted rows the live table grew after migrate119's 102
NEW0119 = [i for i in EN.IDS if i in EN102_IDS and i not in NEW0110 and i not in NEW0116]
assert len(NEW0119) == len(EN.IDS) - 20 - len(NEW0120_ENCH) and len(NEW0119) >= 80 and not set(NEW0119) & set(EN20_IDS), len(NEW0119)
assert all(i in BAG_OF and BAG_OF[i] == EN.cat_of(i) for i in NEW0119), [(i, BAG_OF.get(i), EN.cat_of(i)) for i in NEW0119 if BAG_OF.get(i) != EN.cat_of(i)]
assert all(i in PROC for i in NEW0119), "0.1.19: every new Enchanted product is a processed good: %s" % [i for i in NEW0119 if i not in PROC]
for _i in NEW0119:
    _e = PROC[_i]
    assert _e["outq"] == 1 and len(_e["inputs"]) == 1 and _e["inputs"][0][0] == EN.RATIO and _e["secs"] == 0.0, (_i, _e)
_bycat = {}
for _i in NEW0119:
    _bycat[BAG_OF[_i]] = _bycat.get(BAG_OF[_i], 0) + 1
print("0.1.19: %d Enchanted products appended once (migrate119) - %s; seed prices at the default premium, e.g. %s"
      % (len(NEW0119), ", ".join("%s %d" % (_c, _bycat[_c]) for _c in BAG_TABS if _c in _bycat),
         ", ".join("%s %g" % (i[len(EN.PREFIX):], SEED_BASE[i]) for i in NEW0119 if i[len(EN.PREFIX):] in ("Corn", "Silver", "Gold", "Mithril", "Sand", "Crystal", "Bone", "HideHeavy", "Voidheart", "Ash"))))
# 0.1.20 (round ores01): appended once by Catalog.migrate120 (migrate119's pattern) = the zone metals (PRODUCTS order = by tier) + any new Enchanted id
NEW0120 = [i for i in ids if i in ZONE_PRODUCT_IDS] + NEW0120_ENCH
assert len(NEW0120) == len(ZONE_PRODUCT_IDS) + len(NEW0120_ENCH) and len(ZONE_PRODUCT_IDS) == 13, NEW0120
assert all(i in BAG_OF for i in NEW0120) and all(BAG_OF[i] == ("Mining" if i.startswith("Ore_") else "Smithing") for i in ZONE_PRODUCT_IDS), [(i, BAG_OF.get(i)) for i in ZONE_PRODUCT_IDS]
assert all(i in PROC for i in NEW0120 if not i.startswith("Ore_")), "0.1.20: every new ingot / alloy / Enchanted product is a processed good: %s" % [i for i in NEW0120 if not i.startswith("Ore_") and i not in PROC]
for _i in NEW0120_ENCH:
    _e = PROC[_i]
    assert _e["outq"] == 1 and len(_e["inputs"]) == 1 and _e["inputs"][0][0] == EN.RATIO and _e["secs"] == 0.0, (_i, _e)
for _k, _a, _b, _s in ZONE_ALLOYS:
    _e = PROC["Ingredient_Bar_%s_SkyWynn" % _k]
    assert _e["bench"] == "SkyyAlloy" and _e["outq"] == 1 and len(_e["inputs"]) == 2 and _e["secs"] > 0.0, (_k, _e)
print("0.1.20: %d zone metal products + %d new Enchanted products appended once (migrate120); seed prices at the default premium: %s"
      % (len(ZONE_PRODUCT_IDS), len(NEW0120_ENCH), ", ".join("%s %g" % (i, SEED_BASE[i]) for i in NEW0120)))
print("0.1.10: %d Enchanted products appended once (migrate110), seed prices at the default premium: %s"
      % (len(NEW0110), ", ".join("%s %s" % (i[len(EN.PREFIX):], "%g" % SEED_BASE[i]) for i in NEW0110)))
assert OLDBAG_ID and all(BAG_OF[i] == "Fishing" for i in OLDBAG_ID)
print("0.1.16: the Enchanted Stick (100 %s -> 1) appended once (migrate116), seed price %g at the default premium (%g%%; the Stick %g)"
      % (PROC[NEW0116[0]]["inputs"][0][1], SEED_BASE[NEW0116[0]], PREMIUM_DEF, FIXED_BASE["Ingredient_Stick"]))
print("0.1.9: %d fish products moved Farming -> Fishing (no file rewrite: OLDBAG), %d new Mining products appended once (migrate19): %s"
      % (len(OLDBAG_ID), len(NEW019), ", ".join(NEW019)))
assert sum(1 for a, b in zip(SEED013_LINES, SEED_LINES) if a != b) >= len(PRICE_014)
_order = proc_order(PROC, CHARCOAL)        # the Java reprices in this order (inputs first)
PROC_SPEC = "\n".join("%s/%g/%s/%s/%s" % (i, PROC[i]["outq"], repr(round(PROC[i]["secs"], 6)), PROC[i]["bench"],
                                          ";".join("%g:%s" % (q, ",".join(c)) for q, c in PROC[i]["inputs"])) for i in _order)
FUEL_SPEC = ";".join("%s:%s:%s" % (f, repr(q), repr(sh)) for f, q, sh in FUELS)
for _t in (PROC_SPEC, FUEL_SPEC):
    assert '"' not in _t and "\\" not in _t
EXTRA_ID = [i for i in EXTRA_TABS for t in EXTRA_TABS[i]]
EXTRA_TAB = [t for i in EXTRA_TABS for t in EXTRA_TABS[i]]
# ---- 0.1.15 (Skyy 2026-10-16: "put crops, enchanted crops seeds and eternal seeds per crop in that order sorted by tier. and place the
#      saplings in foraging not farming."): B. every sapling moves Farming -> Foraging (MV_ID / MV_SPEC, Catalog.tabsOf); A. each tab's
#      display order (DSP_KEY "<tab>|<id>", Catalog.inCat): Farming = one group per crop (crop, Enchanted crop, seeds, Eternal seeds) by
#      the crop's tier then name, the rest after by tier then name; Foraging = its 0.1.14 order with each sapling after its tree's log;
#      every other tab keeps its 0.1.14 (seed) order.
SAPLINGS = [p for p, _b, _n in PRODUCTS if p.startswith("Plant_Sapling_")]
assert SAPLINGS and all(BAG_OF[p] == "Farming" and p not in EXTRA_TABS for p in SAPLINGS), "0.1.15: saplings are Farming bag products"
MOVE_TAB = dict((p, ("Farming", "Foraging")) for p in SAPLINGS)
MV_ID = sorted(MOVE_TAB)
MV_SPEC = ["%s>%s" % MOVE_TAB[p] for p in MV_ID]
_NAME = dict((p, n) for p, _b, n in PRODUCTS)


def tabs_of(pid):
    """Catalog.tabsOf for a seed line (its file category = its bag): the bag, Skyy's adds, then the 0.1.15 move"""
    t = [BAG_OF[pid]] + [x for x in EXTRA_TABS.get(pid, ()) if x != BAG_OF[pid]]
    if pid in MOVE_TAB:
        f, to = MOVE_TAB[pid]
        t = [x for x in t if x != f] + ([to] if to not in t else [])
    return t


_TAB0 = dict((t, [p for p, _b, _n in PRODUCTS if t in tabs_of(p)]) for t in BAG_TABS)   # seed (0.1.14) order per tab
DISPLAY = dict(_TAB0)
_farm = set(_TAB0["Farming"])
_groups = []
for _c, _t in TT.CROPS:
    _crop = "Plant_Crop_%s_Item" % _c
    assert _crop in _farm, "0.1.15: the crop %s must be a Farming product (it leads its group)" % _crop
    _mem = [m for m in (_crop, EN.PREFIX + _c, "Plant_Seeds_" + _c, "Plant_Seeds_%s_Eternal" % _c) if m in _farm]
    _groups.append(((TT.tier(_crop), _NAME[_crop].lower(), _crop), _mem))
_groups.sort()
CROP_GROUPS = [m for _k, m in _groups]
_grouped = set(m for g in CROP_GROUPS for m in g)
_rest = sorted((p for p in _TAB0["Farming"] if p not in _grouped), key=lambda p: (TT.tier(p) or 0, _NAME[p].lower(), p))
DISPLAY["Farming"] = [m for g in CROP_GROUPS for m in g] + _rest
_for = [p for p in _TAB0["Foraging"] if p not in MOVE_TAB]
_logs = [p for p in _for if p.startswith("Wood_") and p.endswith("_Trunk")]
assert _logs, "0.1.15: Foraging has logs"
SAPLING_AFTER = {}
for _p in SAPLINGS:                       # PRODUCTS order: saplings of one tree stay in their seed order
    _lg = "Wood_%s_Trunk" % _p[len("Plant_Sapling_"):]
    _at = _lg if _lg in _for else None
    SAPLING_AFTER[_p] = _at
    _anchor_i = _for.index(_at) if _at else _for.index(_logs[-1])
    while _anchor_i + 1 < len(_for) and _for[_anchor_i + 1].startswith("Plant_Sapling_"):
        _anchor_i += 1                    # after the saplings already placed there
    _for.insert(_anchor_i + 1, _p)
# 0.1.16: the Enchanted Stick right after the Stick (not after the last Enchanted log, where the PRODUCTS order puts it)
assert "Ingredient_Stick" in _for and NEW0116[0] in _for, "0.1.16: the Stick and the Enchanted Stick are Foraging products"
_for.remove(NEW0116[0])
_for.insert(_for.index("Ingredient_Stick") + 1, NEW0116[0])
DISPLAY["Foraging"] = _for
# 0.1.19: in every tab but Farming a NEW0119 product sits right after its base (a resource type: after the last product of it), like the
# Enchanted Stick after the Stick; Farming keeps the 0.1.15 rule (the crop groups take the new Enchanted crops, the rest by tier then name)
ENCH_AFTER = {}
for _i in NEW0119 + NEW0120_ENCH:
    _tb = BAG_OF[_i]
    if _tb == "Farming":
        continue
    _bc = set(_c for _q, _cs in PROC[_i]["inputs"] for _c in _cs)
    _lst = DISPLAY[_tb]
    _at = [_p for _p in _lst if _p in _bc]
    if not _at:
        continue          # the base lives in another tab (the bars: Smithing) -> it stays with the tab's Enchanted ingots (PRODUCTS order)
    _lst.remove(_i)
    _lst.insert(_lst.index(_at[-1]) + 1, _i)
    ENCH_AFTER[_i] = _at[-1]
_ench_end = [i for i in NEW0119 + NEW0120_ENCH if BAG_OF[i] != "Farming" and i not in ENCH_AFTER]
print("0.1.19: %d new Enchanted products placed right after their base (%s ...); %d with their base in another tab stay after the tab's "
      "other Enchanted products (%s); %d in Farming by the 0.1.15 rule"
      % (len(ENCH_AFTER), ", ".join("%s after %s" % (k[len(EN.PREFIX):], v) for k, v in list(ENCH_AFTER.items())[:4]), len(_ench_end),
         ", ".join(i[len(EN.PREFIX):] for i in _ench_end), sum(1 for i in NEW0119 if BAG_OF[i] == "Farming")))
for _t in BAG_TABS:
    assert sorted(DISPLAY[_t]) == sorted(_TAB0[_t]) and len(set(DISPLAY[_t])) == len(DISPLAY[_t]), "0.1.15: tab %s lost / doubled a product" % _t
assert not [p for p in DISPLAY["Farming"] if p.startswith("Plant_Sapling_")] and set(SAPLINGS) <= set(DISPLAY["Foraging"])
DSP_KEY = ["%s|%s" % (t, p) for t in BAG_TABS for p in DISPLAY[t]]
assert DISPLAY["Foraging"][DISPLAY["Foraging"].index("Ingredient_Stick") + 1] == NEW0116[0]
print("0.1.16 Foraging order around the Stick: %s" % ", ".join(DISPLAY["Foraging"][max(0, DISPLAY["Foraging"].index("Ingredient_Stick") - 2):
                                                                               DISPLAY["Foraging"].index("Ingredient_Stick") + 3]))
print("0.1.15 Farming order (%d products, %d crop groups): %s" % (len(DISPLAY["Farming"]), len(CROP_GROUPS), ", ".join(DISPLAY["Farming"][:24])))
print("0.1.15: %d saplings moved Farming -> Foraging (%d after their log, %d after the last log: %s)"
      % (len(SAPLINGS), sum(1 for v in SAPLING_AFTER.values() if v), sum(1 for v in SAPLING_AFTER.values() if not v),
         ", ".join(p for p, v in SAPLING_AFTER.items() if not v) or "none"))


# ---- 6. fix round: the /bazaaradmin price GUARD's recipe table. Every recipe whose every input has a listed product and that makes at
#         least one listed product (+ burning fuel into charcoal) is one EDGE "fuel seconds|q:cand,cand;q:cand>q:out;q:out". The jar
#         refuses an admin price that makes a new edge pay in one step (inputs bought at their cheapest listed product, the listed
#         outputs sold), so an admin can no longer turn a fixed crafted good (planks, gravel, saplings, seeds, Greater Essence of Life
#         ...) into a money loop by moving its input - the review's point that only AUTO goods follow their inputs.
def edge_table(M, products, charcoal):
    out = []
    for name, ins, outs, bks, t in M["recipes"]:
        pouts = [(o, q) for o, q in outs if o in products]
        if not pouts:
            continue
        need = []
        for kd, key, q in ins:
            cand = [key] if kd == "I" else sorted(x for x in M["rt_items"].get(key, ()))
            cand = [c for c in cand if c in products]
            if not cand:
                need = None
                break
            need.append((q, cand))
        if not need:
            continue
        secs = 0.0
        for typ, bid in bks:
            b = M["benches"].get(bid)
            if typ == "Processing" and b and b["fuel"]:
                secs = max(secs, float(t or 0.0) * (1.0 - b["reduction"]))
        out.append((secs, need, pouts))
    fb = M["benches"].get("Furnace", {})
    if charcoal in products and fb.get("per"):
        for f, fq in M["fuels"]:
            if f in products and f not in fb.get("ignored", ()) and f != charcoal:
                out.append((0.0, [(fb["per"], [f])], [(charcoal, 1)]))
    return out


def edge_loops(edges, prices, spread, fuels, charcoal):
    """Catalog.loopingEdges in Python: the edges whose listed outputs sell (base x (1 - spread)) for more than their inputs cost (the
    cheapest listed candidate x (1 + spread) + fuel seconds x the cheapest fuel per second bought at (1 + spread), net of the charcoal
    it gives back sold at (1 - spread), never below 0)"""
    pb_, ps_ = eff_prices(prices, spread)        # 0.1.14: Catalog.buyVal / sellVal
    fs, ch = None, (ps_.get(charcoal) if charcoal else None)
    for f, fq, sh in fuels:
        pf = pb_.get(f)
        if pf is None:
            continue
        c = (pf * (1 + spread) - (sh * ch * (1 - spread) if (sh > 0 and ch is not None) else 0.0)) / fq
        fs = c if fs is None else min(fs, c)
    fs = max(0.0, fs or 0.0)
    out = []
    for k, (secs, ins, outs) in enumerate(edges):
        cost, ok = secs * fs, True
        for q, cand in ins:
            ps = [pb_[c] for c in cand if c in pb_]
            if not ps:
                ok = False
                break
            cost += q * min(ps) * (1 + spread)
        if not ok:
            continue
        val = sum(q * ps_[o] * (1 - spread) for o, q in outs if o in ps_)
        if val > cost + 1e-9:
            out.append(k)
    return out


EDGES = edge_table(MODEL, set(ids), CHARCOAL)
EDGE_LINES = ["%s|%s>%s" % (repr(round(secs, 6)), ";".join("%g:%s" % (q, ",".join(c)) for q, c in ins), ";".join("%g:%s" % (q, o) for o, q in outs))
              for secs, ins, outs in EDGES]
for _t in EDGE_LINES:
    assert '"' not in _t and "\\" not in _t and _t.count(">") == 1 and _t.count("|") == 1, _t
for _fl in range(MINSELL_MIN, MINSELL_MAX + 1):        # 0.1.14: + every minimum sell price
    EFF["floor"] = float(_fl)
    for _prem in range(PREMIUM_MIN, PREMIUM_MAX + 1):
        _el = edge_loops(EDGES, all_prices(_prem / 100.0), SPREAD, FUELS, CHARCOAL)
        if _el:
            raise SystemExit("the admin price guard would see %d paying recipe(s) at the default prices (premium %d%%, minimum sell %d): %s"
                             % (len(_el), _prem, _fl, [EDGE_LINES[k] for k in _el[:5]]))
EFF["floor"] = float(MINSELL_DEF)
print("admin price guard: %d one-step recipe edges among products (+ fuel burns), none pays at the default prices (premium %d-%d%%)"
      % (len(EDGES), PREMIUM_MIN, PREMIUM_MAX))
print("bags -> products: SkyySacks %s rule, %s listed; %d bag items skipped; %d processed goods (premium %d%% default, %d-%d), %d fuels"
      % (SACKS_VER, ", ".join("%s %d" % (b, len(BAGS[b])) for b in BAG_TABS), len(SKIPPED), len(PROC), PREMIUM_DEF, PREMIUM_MIN,
         PREMIUM_MAX, len(FUELS)))
for _r, _n in collections.Counter(r for _b, _i, r in SKIPPED).most_common():
    print("  skipped %4d: %s" % (_n, _r))
print("processed seed prices: " + ", ".join("%s %g" % (i.replace("Ingredient_", ""), SEED_BASE[i]) for i in _order))

# ================= javassist =================
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
DAM = "com.hypixel.hytale.assetstore.map.DefaultAssetMap"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"
ACM = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PLB = "com.hypixel.hytale.server.core.plugin.PluginBase"

for c, m in ((PLA, "getInventory"), (PLA, "getPageManager"), (PLA, "getComponentType"), (PGM, "openCustomPage"),
             (INV, "getStorage"), (INV, "getHotbar"), (INV, "getBackpack"),
             (IC, "getItemStack"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"), (IC, "getCapacity"),
             (IS, "getItemId"), (IS, "getQuantity"), (IS, "isEmpty"),
             (PR, "getUuid"), (PR, "getUsername"), (PR, "sendMessage"),
             (PAGE, "rebuild"), (PAGE, "build"), (PAGE, "handleDataEvent"), (UCB, "appendInline"), (UEB, "addEventBinding"),
             (EVD, "of"), (BT, "Activating"), (LIFE, "CanDismiss"), (ITM, "getAssetMap"), (DAM, "getAsset"), (OCU, "registerSimple"),
             (HSV, "SCHEDULED_EXECUTOR"), (ACM, "requirePermission"), (ACM, "addAliases"), (ACM, "withOptionalArg"),
             (ACM, "withRequiredArg"), (ACM, "setPermissionGroups"), (ACM, "addSubCommand"), (ACM, "addUsageVariant"),
             (CTX, "provided"), (CTX, "get"), (ATY, "STRING"), (MSG, "raw"),
             (PLB, "shutdown"), (PLB, "getDataDirectory"), (PLB, "getCommandRegistry"), (PLB, "getLogger")):
    B.probe(pool, c, m)
# 0.1.2: amount TextField (Validating + "@BzAmount" event data), set() for the field value / labels, max stack for inventory room
for c, m in ((BT, "Validating"), (EVD, "append"), (UCB, "set"), (ITM, "getMaxStack"), (DAM, "getAsset")):
    B.probe(pool, c, m)
# 0.1.3: the footer Close (CustomUIPage.close - protected, called on this from BzPage)
for c, m in ((PAGE, "close"), (PAGE, "rebuild")):
    B.probe(pool, c, m)
# 0.1.14: the confirm timeout - one delayed redraw on the player's world thread (BzRevert)
for c, m in ((WLD, "execute"), (PR, "getWorldUuid"), ("com.hypixel.hytale.server.core.universe.Universe", "getWorld"), (PR, "getReference")):
    B.probe(pool, c, m)

PKG = "com.skyy.bazaar"
utl  = pool.makeClass(PKG + ".BzUtil")
coin = pool.makeClass(PKG + ".Coins")
prod = pool.makeClass(PKG + ".Product")
cat_ = pool.makeClass(PKG + ".Catalog")
mkt  = pool.makeClass(PKG + ".Market")
inv_ = pool.makeClass(PKG + ".Inv")
res  = pool.makeClass(PKG + ".TradeResult")
trd  = pool.makeClass(PKG + ".Trader")
page = pool.makeClass(PKG + ".BzPage", pool.get(PAGE))
fac  = pool.makeClass(PKG + ".BzPageFactory")
cmd  = pool.makeClass(PKG + ".BzCmd", pool.get(APC))
adm  = pool.makeClass(PKG + ".BzAdminCmd", pool.get(APC))
aprc = pool.makeClass(PKG + ".BzAdmPriceCmd", pool.get(APC))
aprv = pool.makeClass(PKG + ".BzAdmPriceShowCmd", pool.get(APC))
arlc = pool.makeClass(PKG + ".BzAdmReloadCmd", pool.get(APC))
arsc = pool.makeClass(PKG + ".BzAdmResetCmd", pool.get(APC))
ainc = pool.makeClass(PKG + ".BzAdmInfoCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".BzTick")
pl   = pool.makeClass(PKG + ".SkyyBazaarPlugin", pool.get(JP))
rbf  = pool.makeClass(PKG + ".BzRebirthFn")    # 0.1.11: bazaar:fn:closeall (op 0) / bazaar:fn:wouldclose (op 1)
cfgc = pool.makeClass(PKG + ".BzCfg")          # 0.1.3: the processed goods premium (Server Setup row processed.premium)
bags = pool.makeClass(PKG + ".Bags")           # 0.1.5: SkyySacks' bag bridge (sell from the bags)
# 0.1.13 HUBS H3b: the kit's HubBar in THIS jar's package (cross-jar classes are not allowed, HUBS-CONTRACT 2.1) + the Bazaar tab's open
# Function (+ register)
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)   # 0.1.18: kit 1.7 (row 1, row 2, sub-tabs)
hopn = pool.makeClass(PKG + ".BzHubOpen")
# 0.1.17 MARKET MERGE: BzMarket (the SkyyAuctions bridge calls + the tier table), BzMkSort (tier, name, Bazaar first, id), BzOpenFn
# (bazaar:fn:open - SkyyAuctions 0.1.9's BAZAAR button)
mkb = pool.makeClass(PKG + ".BzMarket")
mks = pool.makeClass(PKG + ".BzMkSort")
mko = pool.makeClass(PKG + ".BzOpenFn")
cfm = pool.makeClass(PKG + ".BzConfirm")     # 0.1.14: the per-player confirm amount (confirm.properties) + the Settings switch
rvt = pool.makeClass(PKG + ".BzRevert")      # 0.1.14: the CONFIRM button's 10 s timeout (one delayed redraw, world thread)
# ================= 0.1.12 SOUND PASS ROUND 2: BzSnd (pasted by tools/bazaar_0_1_12_patch.py from tools/soundpass_gen.py - research/Sound-Pass-Plan.md) =================
# Vanilla sound event ids played BY ID, 2D to that player only (category UI); never throws; 0.5 s per player per sound; the per-player
# switch settings:sounds:<uuid> (Boolean FALSE on the bridge = silent; SkyyMenu 0.3.25 /settings); Skyy_SkyyBazaar/sounds.properties.
import zipfile as _sndzf, jpype as _sndjp
_SNDZ = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")   # read-only
SOUND_IDS = set(os.path.basename(_n)[:-5] for _n in _sndzf.ZipFile(_SNDZ).namelist() if _n.startswith("Server/Audio/SoundEvents/") and _n.endswith(".json"))
SND_SOUNDS = [["buy", "BUY", "Buy done", "SFX_Coins_Land"], ["sell", "SELL", "Sell done", "SFX_Coins_Land"]]
for _s in SND_SOUNDS:
    assert _s[3] in SOUND_IDS, "0.1.12: sound event %s is not in Assets.zip" % _s[3]
_SND_PKG = (PKG).rstrip(".")
_SND_FIELDS = [
    "public static volatile boolean ON = true;",
    "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong MUTED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong WARNS = new java.util.concurrent.atomic.AtomicLong();",
    "public static final long GAP_MS = 500L;",
    "public static final String MUTE_KEY = \"settings:sounds:\";",
    "public static java.nio.file.Path FILE;",
    "public static volatile boolean S_BUY = true;",
    "public static volatile String S_BUY_ID = \"SFX_Coins_Land\";",
    "public static volatile boolean S_SELL = true;",
    "public static volatile String S_SELL_ID = \"SFX_Coins_Land\";",
    "public static final String DEFAULT_TEXT = \"# SkyyBazaar sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Bazaar -> Sounds,\\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\\nsounds.enabled=true\\n# Buy done: A bazaar buy went through (items bought).\\nsound.buy=true\\nsound.buy.id=SFX_Coins_Land\\n# Sell done: A bazaar sale paid (one product or Sell inventory).\\nsound.sell=true\\nsound.sell.id=SFX_Coins_Land\\n\";",
]
_SND_METHODS = [
    r'''
public static void warn(String msg) {
  WARNS.incrementAndGet();
  try { com.hypixel.hytale.logger.HytaleLogger.get("SkyyBazaar").at(java.util.logging.Level.WARNING).log("[SkyyBazaar] " + msg); } catch (Throwable t) { }
}''',
    r'''
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}''',
    r'''
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Coins_Land).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}''',
    r'''
public static String check(String key, String value) {
  return err(value);
}''',
    r'''
public static boolean word(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return d;
}''',
    r'''
public static String id(int w) {
  if (!ON) return null;
  boolean on = false;
  String v = null;
  if (w == 0) { on = S_BUY; v = S_BUY_ID; }
  if (w == 1) { on = S_SELL; v = S_SELL_ID; }
  if (!on || v == null) return null;
  v = v.trim();
  return v.length() == 0 ? null : v;
}''',
    r'''
public static java.util.Map bridge() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    return o instanceof java.util.Map ? (java.util.Map) o : null;
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.Map b = bridge();
    if (b == null) return false;
    Object o = b.get(MUTE_KEY + u.toString());
    return (o instanceof Boolean) && !((Boolean) o).booleanValue();
  } catch (Throwable t) { return false; }
}''',
    r'''
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}''',
    r'''
public static com.hypixel.hytale.server.core.universe.PlayerRef ref(java.util.UUID u) {
  if (u == null) return null;
  try {
    com.hypixel.hytale.server.core.universe.Universe uni = com.hypixel.hytale.server.core.universe.Universe.get();
    return uni == null ? null : uni.getPlayer(u);
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean playTo(com.hypixel.hytale.server.core.universe.PlayerRef pr, int w) {
  if (pr == null) return false;
  String id = id(w);
  if (id == null) return false;
  try {
    if (!pr.isValid()) return false;
    java.util.UUID u = pr.getUuid();
    if (muted(u)) { MUTED.incrementAndGet(); return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(u) + "|" + w, System.currentTimeMillis())) return false;
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return true;
  } catch (Throwable t) {
    if (WARNED.putIfAbsent("!play", Boolean.TRUE) == null) warn("could not play a sound (logged once): " + t);
    return false;
  }
}''',
    r'''
public static boolean play(java.util.UUID u, int w) {
  if (u == null || id(w) == null) return false;
  return playTo(ref(u), w);
}''',
    r'''
public static boolean ok(java.util.UUID u, String res, int w) {
  if (res == null || !res.startsWith("+")) return false;
  return play(u, w);
}''',
    r'''
public static String text() {
  int n = 0;
  if (S_BUY && S_BUY_ID != null && S_BUY_ID.trim().length() > 0) n++;
  if (S_SELL && S_SELL_ID != null && S_SELL_ID.trim().length() > 0) n++;
  return "sounds " + (ON ? "on" : "off") + " (" + n + " of 2)";
}''',
    r'''
public static String load(java.nio.file.Path dir) {
  if (dir == null) return text();
  FILE = dir.resolve("sounds.properties");
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("sounds.properties.tmp");
      java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ON = word(p.getProperty("sounds.enabled"), true);
    S_BUY = word(p.getProperty("sound.buy"), true);
    S_BUY_ID = p.getProperty("sound.buy.id", "SFX_Coins_Land").trim();
    S_SELL = word(p.getProperty("sound.sell"), true);
    S_SELL_ID = p.getProperty("sound.sell.id", "SFX_Coins_Land").trim();
  } catch (Throwable t) { warn("could not read sounds.properties (the sounds keep their defaults): " + t); }
  return text();
}''',
]
_snd_cls = pool.makeClass(_SND_PKG + ".BzSnd")
for _src in _SND_FIELDS:
    _snd_cls.addField(_sndjp.JClass("javassist.CtField").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
for _src in _SND_METHODS:
    _snd_cls.addMethod(_sndjp.JClass("javassist.CtNewMethod").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
_snd_cls.writeFile(OUT)
print("BzSnd: 2 sound(s), every default id is in Assets.zip")


def jt(src, **kw):
    """0.1.3 Java blocks: @PKG@ / @PLA@ / ... tokens (kit output never holds '@'), plus the block's own @NAME@ values"""
    for k, v in list(_JT.items()) + list(kw.items()):
        src = src.replace("@" + k + "@", str(v))
    left = re.findall(r"@[A-Z][A-Z0-9]*@", src)
    assert not left, "unfilled tokens %s" % left
    return src


_JT = {"PKG": PKG, "PLA": PLA, "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT, "MSG": MSG, "ITM": ITM, "IC": IC, "IS": IS, "REF": REF,
       "ST": ST, "PR": PR, "LIFE": LIFE, "WLD": WLD, "CTX": CTX}


def jarr(vals):
    return "new String[] { " + ", ".join(SUI.java_lit(v) for v in vals) + " }"


# ================= 0.1.3 BzCfg fields + the config kit (Server Setup -> Bazaar, tools/skyycfg.py; tools/CONFIG-CONTRACT.md) =================
# The ONE row: processed.premium (int %, default 20, 0-22, live). BzCfg.load reads the file first in setup(); the kit (CfgPub.start, the
# last line of setup) publishes config:def:SkyyBazaar + config:fn:SkyyBazaar; an in-game change runs the after= hook BzCfg.changed
# (Catalog.reprice), a hand edit + the kit's next write / reload is caught by the 10 s tick (Catalog.tick: PREMIUM moved -> reprice).
cfgc.addField(CtField.make("public static volatile int PREMIUM = %d;" % PREMIUM_DEF, cfgc))
cfgc.addField(CtField.make("public static final int DEF = %d;" % PREMIUM_DEF, cfgc))
cfgc.addField(CtField.make("public static final int MIN = %d;" % PREMIUM_MIN, cfgc))
cfgc.addField(CtField.make("public static final int MAX = %d;" % PREMIUM_MAX, cfgc))
cfgc.addField(CtField.make("public static java.nio.file.Path FILE;", cfgc))
# 0.1.14: the minimum instant sell price (coins per item; read by Catalog.floorBase, clamped there) + new players' confirm amount
cfgc.addField(CtField.make("public static volatile int MINSELL = %d;" % MINSELL_DEF, cfgc))
cfgc.addField(CtField.make("public static final int MINSELL_MIN = %d;" % MINSELL_MIN, cfgc))
cfgc.addField(CtField.make("public static final int MINSELL_MAX = %d;" % MINSELL_MAX, cfgc))
cfgc.addField(CtField.make("public static volatile int CONFIRM = %d;" % CONFIRM_DEF, cfgc))
CFG_TEXT = ("# SkyyBazaar settings. Change them in game: SkyWynn Menu > Server Setup > Bazaar (or edit this file, then /bazaaradmin reload).\n"
            "# processed.premium = how much more (in %%) a processed good costs than the raw inputs of its vanilla recipe (recipe ratio +\n"
            "#   fuel): Furnace bars, stone and charcoal, Tannery leather, cloth bolts. %d-%d; above %d buying the inputs, processing\n"
            "#   and selling would pay.\n"
            "processed.premium=%d\n"
            "# market.minSell = the fewest coins an instant sale pays per item, at any demand (%d = off, at most %d). Buy prices stay above it.\n"
            "market.minSell=%d\n"
            "# confirm.default = new players' confirm amount: a buy of this many coins or more asks CONFIRM first (0 = every buy). Each\n"
            "#   player sets their own on the Bazaar page (bottom row).\n"
            "confirm.default=%d\n" % (PREMIUM_MIN, PREMIUM_MAX, PREMIUM_MAX, PREMIUM_DEF, MINSELL_MIN, MINSELL_MAX, MINSELL_DEF, CONFIRM_DEF))
cfgc.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % SUI.java_lit(CFG_TEXT), cfgc))
CFG_CATS = [("market", "Market"), ("sounds", "Sounds")]   # 0.1.12: + Sounds
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding)
    ("processed.premium", "Processed goods premium", "market", "int", str(PREMIUM_DEF), str(PREMIUM_MIN), str(PREMIUM_MAX), "step=1",
     "%", "live", "Bars, stone, charcoal, leather and cloth bolts cost this much more than their raw inputs. Max 22.",
     "field:BzCfg.PREMIUM@config.properties:processed.premium;after=BzCfg.changed"),
    # 0.1.14 (Skyy 2026-10-15): the minimum instant sell price + new players' confirm amount
    ("market.minSell", "Minimum instant sell price", "market", "int", str(MINSELL_DEF), str(MINSELL_MIN), str(MINSELL_MAX), "step=1",
     "coins", "live", "No instant sale pays less per item; buys stay above it. 0 = off, max %d. Never rescales prices." % MINSELL_MAX,
     "field:BzCfg.MINSELL@config.properties:market.minSell;after=BzCfg.floorChanged"),
    ("confirm.default", "Confirm purchases above", "market", "int", str(CONFIRM_DEF), "0", "1000000000", "step=100", "coins", "live",
     "Players who never set their own: buys of this many coins or more ask CONFIRM first. 0 = every buy.",
     "field:BzCfg.CONFIRM@config.properties:confirm.default"),
    # 0.1.12 sound pass round 2: Server Setup -> Bazaar -> Sounds
    ('sounds.enabled', 'Sounds', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'Off = SkyyBazaar plays no sound at all. Players can also mute every sound in /settings.', 'field:BzSnd.ON@Skyy_SkyyBazaar/sounds.properties:sounds.enabled'),
    ('sound.buy', 'Buy done sound', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'A bazaar buy went through (items bought). Off = silent.', 'field:BzSnd.S_BUY@Skyy_SkyyBazaar/sounds.properties:sound.buy'),
    ('sound.buy.id', 'Buy done sound id', 'sounds', 'text', 'SFX_Coins_Land', '', '120', '', '', 'live', 'A vanilla sound event id (try it with /soundtest). Empty = no sound.', 'field:BzSnd.S_BUY_ID@Skyy_SkyyBazaar/sounds.properties:sound.buy.id;check=BzSnd.check'),
    ('sound.sell', 'Sell done sound', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'A bazaar sale paid (one product or Sell inventory). Off = silent.', 'field:BzSnd.S_SELL@Skyy_SkyyBazaar/sounds.properties:sound.sell'),
    ('sound.sell.id', 'Sell done sound id', 'sounds', 'text', 'SFX_Coins_Land', '', '120', '', '', 'live', 'A vanilla sound event id (try it with /soundtest). Empty = no sound.', 'field:BzSnd.S_SELL_ID@Skyy_SkyyBazaar/sounds.properties:sound.sell.id;check=BzSnd.check'),
]
KIT = CFG.emit(pool, PKG, MOD="SkyyBazaar", TITLE="Bazaar", VERSION=VERSION, NODE="skyybazaar.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyBazaar/config.properties", "Skyy_SkyyBazaar/sounds.properties"], NOTE="Prices, demand and products stay in products / market.properties.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CFG_TEXT, "sounds.properties": '# SkyyBazaar sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Bazaar -> Sounds,\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\nsounds.enabled=true\n# Buy done: A bazaar buy went through (items bought).\nsound.buy=true\nsound.buy.id=SFX_Coins_Land\n# Sell done: A bazaar sale paid (one product or Sell inventory).\nsound.sell=true\nsound.sell.id=SFX_Coins_Land\n'})   # 0.1.12: + sounds.properties
assert KIT.info.get("kit", "1.0") == "1.1", "the emitted config kit is %s, SkyyBazaar 0.1.3 pins 1.1" % KIT.info.get("kit", "1.0")
print("config kit %s: %d rows, files %s, KEEP 10" % (KIT.info.get("kit", "1.0"), KIT.info["rows"], ", ".join(KIT.info["files"])))

# ================= BzUtil =================
utl.addField(CtField.make(f"public static {LOG} LOG;", utl))
utl.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyBazaar] " + msg); } catch (Throwable t) { }
}""", utl))
utl.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyBazaar] " + msg); } catch (Throwable t) { }
}""", utl))
# 0.1.8 A: lock-free bridge (research/Code-Structure-Audit.md): cached in BRIDGE after the first call; only that call takes the
# System.class monitor (creation exactly as before: get, create if absent, put)
utl.addField(CtField.make("public static volatile java.util.Map BRIDGE;", utl))
utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", utl))
utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""", utl))
# UI text: whitelist letters, digits, space . - /   (everything else -> space; no quotes/braces/semicolons/colons/commas)
utl.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == ' ' || c == '.' || c == '-' || c == '/') sb.append(c);
    else sb.append(' ');
  }
  return sb.toString();
}""", utl))
# item ids: letters, digits, underscore only
utl.addMethod(CtNewMethod.make("""
public static boolean isId(String t) {
  if (t == null || t.length() == 0 || t.length() > 96) return false;
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}""", utl))
utl.addMethod(CtNewMethod.make("""
public static String num(double v) {
  if (v >= 1000.0) return String.valueOf(Math.round(v));
  return String.valueOf(Math.round(v * 100.0) / 100.0);
}""", utl))
utl.addMethod(CtNewMethod.make("""
public static boolean has(String data, String key) {
  return data != null && data.indexOf("\\"" + key + "\\"") >= 0;
}""", utl))
# 0.1.2: one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr, verified in game with the search TextField;
# the same copy runs the SkyyGuilds 0.1 page). quote = char 34, backslash = char 92, so no escape sequences are needed here.
utl.addMethod(CtNewMethod.make("""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""", utl))
# 0.1.2: custom amount text -> units. -1 = empty or not an amount, -2 = max / all, else the whole number (0 allowed, callers range-check).
# 500, 2k, 1.5k, 1m; commas, spaces and underscores are ignored; a fraction without a suffix (1.5) is refused.
utl.addMethod(CtNewMethod.make("""
public static long parseAmt(String raw) {
  if (raw == null) return -1L;
  String t = raw.trim().toLowerCase();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c != ' ' && c != ',' && c != '_') sb.append(c);
  }
  String s = sb.toString();
  if (s.length() == 0) return -1L;
  if (s.equals("max") || s.equals("all")) return -2L;
  double mul = 1.0;
  char last = s.charAt(s.length() - 1);
  if (last == 'k') { mul = 1000.0; s = s.substring(0, s.length() - 1); }
  else if (last == 'm') { mul = 1000000.0; s = s.substring(0, s.length() - 1); }
  if (s.length() == 0 || s.length() > 12) return -1L;
  int dots = 0;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '.') { dots++; continue; }
    if (c < '0' || c > '9') return -1L;
  }
  if (dots > 1 || s.equals(".")) return -1L;
  double v;
  try { v = Double.parseDouble(s) * mul; } catch (Throwable x) { return -1L; }
  if (!(v >= 0.0) || v > 1.0E12) return -1L;
  double r = Math.floor(v + 1.0E-9);
  if (Math.abs(v - r) > 1.0E-6) return -1L;
  return (long) r;
}""", utl))

# ================= Coins (SkyyCoins bridge; copied from SkyyBank) =================
coin.addMethod(CtNewMethod.make(f"""
public static boolean ready() {{
  java.util.Map b = {PKG}.BzUtil.bridge();
  return b.get("coins:fn:get") instanceof java.util.function.Function
      && b.get("coins:fn:add") instanceof java.util.function.Function
      && b.get("coins:fn:take") instanceof java.util.function.Function;
}}""", coin))
# every bridge apply() is guarded: a SkyyCoins function that THROWS must never unwind out of a half-done trade.
# get: balance, or -1 = the bridge threw / answered garbage (callers refuse to trade on -1).
# take / add: 1 = done, 0 = refused or missing, -1 = threw (outcome unknown - the caller logs it for an admin).
coin.addMethod(CtNewMethod.make(f"""
public static long get(java.util.UUID u) {{
  Object f = {PKG}.BzUtil.bridge().get("coins:fn:get");
  if (!(f instanceof java.util.function.Function)) return 0L;
  Object r = null;
  try {{ r = ((java.util.function.Function) f).apply(u); }}
  catch (Throwable t) {{ {PKG}.BzUtil.warn("coins:fn:get threw for " + u + ": " + t); return -1L; }}
  return r instanceof Number ? ((Number) r).longValue() : -1L;
}}""", coin))
coin.addMethod(CtNewMethod.make(f"""
public static int take(java.util.UUID u, long n) {{
  if (n <= 0L) return 0;
  Object f = {PKG}.BzUtil.bridge().get("coins:fn:take");
  if (!(f instanceof java.util.function.Function)) return 0;
  Object r = null;
  try {{ r = ((java.util.function.Function) f).apply(new Object[] {{ u, Long.valueOf(n) }}); }}
  catch (Throwable t) {{ {PKG}.BzUtil.warn("coins:fn:take threw for " + u + " (" + n + " coins): " + t); return -1; }}
  return (r instanceof Boolean && ((Boolean) r).booleanValue()) ? 1 : 0;
}}""", coin))
coin.addMethod(CtNewMethod.make(f"""
public static int add(java.util.UUID u, long n) {{
  if (n <= 0L) return 0;
  Object f = {PKG}.BzUtil.bridge().get("coins:fn:add");
  if (!(f instanceof java.util.function.Function)) return 0;
  Object r = null;
  try {{ r = ((java.util.function.Function) f).apply(new Object[] {{ u, Long.valueOf(n) }}); }}
  catch (Throwable t) {{ {PKG}.BzUtil.warn("coins:fn:add threw for " + u + " (" + n + " coins): " + t); return -1; }}
  return r instanceof Number ? 1 : 0;
}}""", coin))

# ================= Product =================
prod.addField(CtField.make("public String id;", prod))
prod.addField(CtField.make("public String cat;", prod))
prod.addField(CtField.make("public volatile double base;", prod))
prod.addField(CtField.make("public String name;", prod))
prod.addConstructor(CtNewConstructor.make("""
public Product(String id, String cat, double base, String name) {
  this.id = id; this.cat = cat; this.base = base; this.name = name;
}""", prod))

# ================= Catalog (0.1.3: products.properties + the bag tabs, processed prices, the one-time update) =================
# File order is kept on disk (0.1.2 format, so a rollback still reads it); what a TAB shows comes from the jar: a product's tabs = its
# bag (SEED's category, from SkyySacks' rule at build time) + Skyy's adds (EXTRA) + its own file category; inside a tab products follow
# the seed order (admin-added ones after, in file order); tabs follow TAB_ORDER (admin categories after, first appearance).
cat_.addField(CtField.make("public static java.nio.file.Path FILE;", cat_))
cat_.addField(CtField.make("public static java.nio.file.Path PFILE;", cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList LIST = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final java.util.HashMap BY_ID = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final java.util.HashSet WARNED = new java.util.HashSet();", cat_))
cat_.addField(CtField.make("public static final String[] SEED = %s;" % jarr(SEED_LINES), cat_))
cat_.addField(CtField.make("public static final String[] OLD_SEED = %s;" % jarr(OLD_SEED_LINES), cat_))
cat_.addField(CtField.make("public static final String[] SEED013 = %s;" % jarr(SEED013_LINES), cat_))
cat_.addField(CtField.make("public static final String[] TAB_ORDER = %s;" % jarr(BAG_TABS), cat_))
cat_.addField(CtField.make("public static final String[] EXTRA_ID = %s;" % jarr(EXTRA_ID), cat_))
cat_.addField(CtField.make("public static final String[] EXTRA_TAB = %s;" % jarr(EXTRA_TAB), cat_))
# 0.1.15: the sapling move (id -> "from>to") and each tab's display order ("<tab>|<id>" -> its place)
cat_.addField(CtField.make("public static final String[] MV_ID = %s;" % jarr(MV_ID), cat_))
cat_.addField(CtField.make("public static final String[] MV_SPEC = %s;" % jarr(MV_SPEC), cat_))
cat_.addField(CtField.make("public static final String[] DSP_KEY = %s;" % jarr(DSP_KEY), cat_))
cat_.addField(CtField.make("public static final java.util.HashMap MOVE = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final java.util.HashMap DSP = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final String PROC_SPEC = %s;" % SUI.java_lit(PROC_SPEC), cat_))
cat_.addField(CtField.make("public static final String FUEL_SPEC = %s;" % SUI.java_lit(FUEL_SPEC), cat_))
cat_.addField(CtField.make("public static final String CHARCOAL = %s;" % SUI.java_lit(CHARCOAL or ""), cat_))
# fix round: the admin price guard's recipe edges (the build's EDGE_LINES; parsed by init() into EDGE)
cat_.addField(CtField.make("public static final String[] EDGES = %s;" % jarr(EDGE_LINES), cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList EDGE = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static int GUARD_MOVED = 0;", cat_))
cat_.addField(CtField.make("public static final String HEADER = %s;" % SUI.java_lit(
    "# SkyyBazaar products - one per line: <ItemId>=<Category>,<basePrice>,<Display Name>\n"
    "# Every Void material shows in its category's tab (Mining, Foraging, Farming, Fishing, Combat, Smithing - building shapes and decoration\n"
    "# blocks are not listed); the category here adds a tab. Processed goods (Furnace bars, stone and charcoal, Tannery leather, cloth\n"
    "# bolts) follow their raw inputs x (1 + the premium in Server Setup) unless pricing.properties marks them fixed.\n"
    "# Keep base(B) < 1.22 x base(A) for any recipe A -> B (no money loops).\n"
    "# After editing run /bazaaradmin reload. /bazaaradmin price <itemId> <base> rewrites this file.\n"), cat_))
cat_.addField(CtField.make("public static final String PHEADER = %s;" % SUI.java_lit(
    "# SkyyBazaar processed goods (0.1.3) - written by the mod. auto = the base price follows the raw inputs of the vanilla recipe\n"
    "# (ratio + fuel) x (1 + the processed goods premium, Server Setup > Bazaar); fixed = the price in products.properties is kept as it\n"
    "# is (/bazaaradmin price <itemId> <base>; /bazaaradmin price <itemId> auto makes it follow its inputs again).\n"), cat_))
for _f in ("ORDER_IX", "BAG", "EXTRA", "PROC_BY", "CACHE"):
    cat_.addField(CtField.make("public static final java.util.HashMap %s = new java.util.HashMap();" % _f, cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList PROC = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList FUEL = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final java.util.HashSet AUTO = new java.util.HashSet();", cat_))
cat_.addField(CtField.make("public static java.util.ArrayList CATS = null;", cat_))
cat_.addField(CtField.make("public static boolean READY = false;", cat_))
cat_.addField(CtField.make("public static volatile boolean DIRTY = false;", cat_))
cat_.addField(CtField.make("public static volatile boolean MODES_BAD = false;", cat_))
cat_.addField(CtField.make("public static volatile double PREM = -1.0;", cat_))
cat_.addField(CtField.make("public static volatile int PCT = -1;", cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED = "";', cat_))
# 0.1.4: the one-time progression price update (migrate14): ids, 0.1.3 defaults, 0.1.4 defaults (seed spelling) + its marker
_m14 = sorted(PRICE_014)
cat_.addField(CtField.make("public static final String[] M14_ID = %s;" % jarr(_m14), cat_))
cat_.addField(CtField.make("public static final double[] M14_OLD = new double[] { %s };" % ", ".join(repr(float(PRICE_014[i][0])) for i in _m14), cat_))
cat_.addField(CtField.make("public static final double[] M14_NEW = new double[] { %s };" % ", ".join(repr(float(PRICE_014[i][1])) for i in _m14), cat_))
cat_.addField(CtField.make("public static final String[] M14_TXT = %s;" % jarr(["%g" % PRICE_014[i][1] for i in _m14]), cat_))
cat_.addField(CtField.make("public static final String[] M14_OTXT = %s;" % jarr(["%g" % PRICE_014[i][0] for i in _m14]), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED14 = "";', cat_))
# 0.1.9: OLDBAG = id -> its 0.1.8 bag where it moved (fish: Farming); NEW019 = the products 0.1.9 appends once; MIGRATED19 = its marker
cat_.addField(CtField.make("public static final String[] OLDBAG_ID = %s;" % jarr(OLDBAG_ID), cat_))
cat_.addField(CtField.make("public static final String[] OLDBAG_TAB = %s;" % jarr(OLDBAG_TAB), cat_))
cat_.addField(CtField.make("public static final java.util.HashMap OLDBAG = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final String[] NEW019 = %s;" % jarr(NEW019), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED19 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M19_LOG = new java.util.ArrayList();", cat_))
# 0.1.10: NEW0110 = the 19 Enchanted products appended once; MIGRATED110 = its marker
cat_.addField(CtField.make("public static final String[] NEW0110 = %s;" % jarr(NEW0110), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED110 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M110_LOG = new java.util.ArrayList();", cat_))
# 0.1.16: NEW0116 = the Enchanted Stick appended once; MIGRATED116 = its marker
cat_.addField(CtField.make("public static final String[] NEW0116 = %s;" % jarr(NEW0116), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED116 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M116_LOG = new java.util.ArrayList();", cat_))
# 0.1.19: NEW0119 = the C1 Enchanted products appended once; MIGRATED119 = its marker
cat_.addField(CtField.make("public static final String[] NEW0119 = %s;" % jarr(NEW0119), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED119 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M119_LOG = new java.util.ArrayList();", cat_))
# 0.1.20: NEW0120 = the zone metals (+ new Enchanted products) appended once; MIGRATED120 = its marker
cat_.addField(CtField.make("public static final String[] NEW0120 = %s;" % jarr(NEW0120), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED120 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M120_LOG = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M14_LOG = new java.util.ArrayList();", cat_))
# 0.1.14: the sell caps (id -> the sell base), the products that never take the minimum sell price, the one-time tier price update
cat_.addField(CtField.make("public static final String[] SC_ID = %s;" % jarr(sorted(SELL_CAP)), cat_))
cat_.addField(CtField.make("public static final double[] SC_V = new double[] { %s };" % ", ".join(repr(float(SELL_CAP[i])) for i in sorted(SELL_CAP)), cat_))
cat_.addField(CtField.make("public static final String[] NF_ID = %s;" % jarr(sorted(FLOOR_EXEMPT)), cat_))
cat_.addField(CtField.make("public static final String[] BX_ID = %s;" % jarr(sorted(BUY_X)), cat_))
cat_.addField(CtField.make("public static final double[] BX_V = new double[] { %s };" % ", ".join(repr(float(BUY_X[i])) for i in sorted(BUY_X)), cat_))
cat_.addField(CtField.make("public static final java.util.HashMap BUYX = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final java.util.HashMap SCAP = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final java.util.HashSet NOFLOOR = new java.util.HashSet();", cat_))
cat_.addField(CtField.make("public static volatile int FLOORPUB = -1;", cat_))
_m114 = sorted(PRICE_0114)
cat_.addField(CtField.make("public static final String[] M114_ID = %s;" % jarr(_m114), cat_))
cat_.addField(CtField.make("public static final double[] M114_OLD = new double[] { %s };" % ", ".join(repr(float(PRICE_0114[i][0])) for i in _m114), cat_))
cat_.addField(CtField.make("public static final double[] M114_NEW = new double[] { %s };" % ", ".join(repr(float(PRICE_0114[i][1])) for i in _m114), cat_))
cat_.addField(CtField.make("public static final String[] M114_TXT = %s;" % jarr(["%g" % PRICE_0114[i][1] for i in _m114]), cat_))
cat_.addField(CtField.make("public static final String[] M114_OTXT = %s;" % jarr(["%g" % PRICE_0114[i][0] for i in _m114]), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED114 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M114_LOG = new java.util.ArrayList();", cat_))
# 0.1.15: the x SCALE_X update (id -> 0.1.14 default / 0.1.15 default) + the impactCoins default
_m115 = sorted(PRICE_0115)
assert all(float("%g" % PRICE_0115[i][1]) == PRICE_0115[i][1] and float("%g" % PRICE_0115[i][0]) == PRICE_0115[i][0] for i in _m115)
cat_.addField(CtField.make("public static final String[] M115_ID = %s;" % jarr(_m115), cat_))
cat_.addField(CtField.make("public static final double[] M115_OLD = new double[] { %s };" % ", ".join(repr(float(PRICE_0115[i][0])) for i in _m115), cat_))
cat_.addField(CtField.make("public static final double[] M115_NEW = new double[] { %s };" % ", ".join(repr(float(PRICE_0115[i][1])) for i in _m115), cat_))
cat_.addField(CtField.make("public static final String[] M115_TXT = %s;" % jarr(["%g" % PRICE_0115[i][1] for i in _m115]), cat_))
cat_.addField(CtField.make("public static final String[] M115_OTXT = %s;" % jarr(["%g" % PRICE_0115[i][0] for i in _m115]), cat_))
cat_.addField(CtField.make("public static final java.util.HashMap M115_IX = new java.util.HashMap();", cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED115 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M115_LOG = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final double SCALE = %r;" % float(SCALE_X), cat_))
cat_.addField(CtField.make("public static final double IMP_OLD = %r;" % float(IMPACT_OLD), cat_))
cat_.addField(CtField.make("public static final double IMP_NEW = %r;" % float(IMPACT_DEF), cat_))
cat_.addField(CtField.make('public static final String IMP_TXT = "%r";' % float(IMPACT_DEF), cat_))
assert all(float("%g" % PRICE_0114[i][1]) == PRICE_0114[i][1] and float("%g" % PRICE_0114[i][0]) == PRICE_0114[i][0] for i in _m114)
assert not [i for i in SELL_CAP if i not in OLD_0113] and all(SELL_CAP[i] >= 0.01 for i in SELL_CAP)
assert all(float(t) == PRICE_014[i][1] for i, t in zip(_m14, ["%g" % PRICE_014[i][1] for i in _m14]))
# the jar tables -> maps, once (SEED: id -> seed order + bag tab; EXTRA; PROC_SPEC "id/outq/secs/bench/q:c1,c2;q:c3"; FUEL_SPEC "id:sec:back")
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void init() {
  if (READY) return;
  for (int i = 0; i < SEED.length; i++) {
    String sl = SEED[i];
    int eq = sl.indexOf('=');
    int c1 = eq < 0 ? -1 : sl.indexOf(',', eq + 1);
    if (eq <= 0 || c1 <= eq) continue;
    String id = sl.substring(0, eq);
    ORDER_IX.put(id, Integer.valueOf(i));
    if (i == 0) { for (int o = 0; o < OLDBAG_ID.length; o++) OLDBAG.put(OLDBAG_ID[o], OLDBAG_TAB[o]); }   // 0.1.9
    BAG.put(id, sl.substring(eq + 1, c1));
  }
  for (int i = 0; i < EXTRA_ID.length; i++) {
    java.util.ArrayList l = (java.util.ArrayList) EXTRA.get(EXTRA_ID[i]);
    if (l == null) { l = new java.util.ArrayList(); EXTRA.put(EXTRA_ID[i], l); }
    if (!l.contains(EXTRA_TAB[i])) l.add(EXTRA_TAB[i]);
  }
  String[] lines = PROC_SPEC.length() == 0 ? new String[0] : PROC_SPEC.split("\n");
  for (int i = 0; i < lines.length; i++) {
    String[] f = lines[i].split("/");
    if (f.length != 5) { @PKG@.BzUtil.warn("bad processed-goods table line " + lines[i]); continue; }
    String[] ins = f[4].split(";");
    double[] q = new double[ins.length];
    Object[] cand = new Object[ins.length];
    for (int k = 0; k < ins.length; k++) {
      int c = ins[k].indexOf(':');
      q[k] = Double.parseDouble(ins[k].substring(0, c));
      cand[k] = ins[k].substring(c + 1).split(",");
    }
    Object[] e = new Object[] { f[0], Double.valueOf(Double.parseDouble(f[1])), Double.valueOf(Double.parseDouble(f[2])), f[3], q, cand };
    PROC.add(e);
    PROC_BY.put(f[0], e);
  }
  String[] fu = FUEL_SPEC.length() == 0 ? new String[0] : FUEL_SPEC.split(";");
  for (int i = 0; i < fu.length; i++) {
    String[] f = fu[i].split(":");
    if (f.length != 3) continue;
    FUEL.add(new Object[] { f[0], Double.valueOf(Double.parseDouble(f[1])), Double.valueOf(Double.parseDouble(f[2])) });
  }
  // fix round: EDGES "secs|q:c1,c2;q:c3>q:o1;q:o2" -> { Double secs, double[] qIn, Object[] cand (String[]), double[] qOut, String[] out }
  for (int i = 0; i < EDGES.length; i++) {
    String[] a = EDGES[i].split("\\|");
    String[] io = a.length == 2 ? a[1].split(">") : new String[0];
    if (io.length != 2) { @PKG@.BzUtil.warn("bad recipe edge " + EDGES[i]); continue; }
    String[] ins = io[0].split(";");
    String[] outs = io[1].split(";");
    double[] qi = new double[ins.length];
    Object[] ci = new Object[ins.length];
    for (int k = 0; k < ins.length; k++) {
      int c = ins[k].indexOf(':');
      qi[k] = Double.parseDouble(ins[k].substring(0, c));
      ci[k] = ins[k].substring(c + 1).split(",");
    }
    double[] qo = new double[outs.length];
    String[] os = new String[outs.length];
    for (int k = 0; k < outs.length; k++) {
      int c = outs[k].indexOf(':');
      qo[k] = Double.parseDouble(outs[k].substring(0, c));
      os[k] = outs[k].substring(c + 1);
    }
    EDGE.add(new Object[] { Double.valueOf(Double.parseDouble(a[0])), qi, ci, qo, os });
  }
  for (int i = 0; i < SC_ID.length; i++) SCAP.put(SC_ID[i], Double.valueOf(SC_V[i]));   // 0.1.14
  for (int i = 0; i < NF_ID.length; i++) NOFLOOR.add(NF_ID[i]);
  for (int i = 0; i < BX_ID.length; i++) BUYX.put(BX_ID[i], Double.valueOf(BX_V[i]));
  for (int i = 0; i < MV_ID.length; i++) MOVE.put(MV_ID[i], MV_SPEC[i]);   // 0.1.15
  for (int i = 0; i < M115_ID.length; i++) M115_IX.put(M115_ID[i], Integer.valueOf(i));
  for (int i = 0; i < DSP_KEY.length; i++) DSP.put(DSP_KEY[i], Integer.valueOf(i));
  READY = true;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.Product get(String id) {{
  if (id == null) return null;
  return ({PKG}.Product) BY_ID.get(id);
}}""", cat_))
# 0.1.14: what a product trades at, at demand 1.0 (the build's eff_prices): the sell base (its cap where it has one), the floor value
# (minimum sell price / (1 - spread); 0 = none for this product), and buy / sell values with the floor (Market.quote walks the same rule)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double sellBase(@PKG@.Product p) {
  init();
  if (p == null) return 0.0;
  Double c = (Double) SCAP.get(p.id);
  return (c != null && c.doubleValue() < p.base) ? c.doubleValue() : p.base;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double floorBase(String id, double sp) {
  init();
  int m = @PKG@.BzCfg.MINSELL;
  if (m > @PKG@.BzCfg.MINSELL_MAX) m = @PKG@.BzCfg.MINSELL_MAX;
  if (m <= 0 || id == null || NOFLOOR.contains(id) || !(sp < 1.0)) return 0.0;
  return (double) m / (1.0 - sp);
}"""), cat_))
# the buy side's floor value: the floor value x BUY_X (a cheap input of a conversion buys a little higher; its sell side keeps the floor)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double buyFloor(String id, double sp) {
  double fb = floorBase(id, sp);
  if (fb <= 0.0) return 0.0;
  Double x = (Double) BUYX.get(id);
  return x == null ? fb : fb * x.doubleValue();
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static double buyVal(@PKG@.Product p, double sp) {
  if (p == null) return 0.0;
  double fb = buyFloor(p.id, sp);
  return p.base < fb ? fb : p.base;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static double sellVal(@PKG@.Product p, double sp) {
  if (p == null) return 0.0;
  double s = sellBase(p);
  double fb = floorBase(p.id, sp);
  return s < fb ? fb : s;
}"""), cat_))
cat_.addMethod(CtNewMethod.make("""
public static synchronized java.util.ArrayList all() {
  return new java.util.ArrayList(LIST);
}""", cat_))

cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean isProc(String id) {
  init();
  return id != null && PROC_BY.containsKey(id);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean isAuto(String id) {
  init();
  return id != null && PROC_BY.containsKey(id) && AUTO.contains(id);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized Object[] procEntry(String id) {
  init();
  if (id == null) return null;
  return (Object[]) PROC_BY.get(id);
}"""), cat_))
# a product's tabs in TAB_ORDER-first order: its bag (from the jar), Skyy's adds, its own file category
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.ArrayList tabsOf(@PKG@.Product p) {
  init();
  java.util.ArrayList raw = new java.util.ArrayList();
  if (p == null) return raw;
  String bg = (String) BAG.get(p.id);
  if (bg != null) raw.add(bg);
  java.util.ArrayList ex = (java.util.ArrayList) EXTRA.get(p.id);
  for (int i = 0; ex != null && i < ex.size(); i++) if (!raw.contains(ex.get(i))) raw.add(ex.get(i));
  // 0.1.9: a file category that is exactly the item's OLD bag (a fish line still saying Farming) adds no tab - the fish show in Fishing only
  if (p.cat != null && p.cat.length() > 0 && !raw.contains(p.cat) && !p.cat.equals(OLDBAG.get(p.id))) raw.add(p.cat);
  // 0.1.15 (Skyy 2026-10-16 "place the saplings in foraging not farming"): a moved product leaves its old tab for the new one
  String mv = (String) MOVE.get(p.id);
  int mk = mv == null ? -1 : mv.indexOf('>');
  if (mk > 0) {
    String mfrom = mv.substring(0, mk);
    String mto = mv.substring(mk + 1);
    while (raw.contains(mfrom)) raw.remove((Object) mfrom);
    if (!raw.contains(mto)) raw.add(mto);
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < TAB_ORDER.length; i++) if (raw.contains(TAB_ORDER[i])) out.add(TAB_ORDER[i]);
  for (int i = 0; i < raw.size(); i++) if (!out.contains(raw.get(i))) out.add(raw.get(i));
  return out;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.ArrayList categories() {
  if (CATS != null) return new java.util.ArrayList(CATS);
  java.util.ArrayList seen = new java.util.ArrayList();
  for (int i = 0; i < LIST.size(); i++) {
    java.util.ArrayList t = tabsOf((@PKG@.Product) LIST.get(i));
    for (int k = 0; k < t.size(); k++) if (!seen.contains(t.get(k))) seen.add(t.get(k));
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < TAB_ORDER.length; i++) if (seen.contains(TAB_ORDER[i])) out.add(TAB_ORDER[i]);
  for (int i = 0; i < seen.size(); i++) if (!out.contains(seen.get(i))) out.add(seen.get(i));
  CATS = out;
  return new java.util.ArrayList(out);
}"""), cat_))
# a tab's products: the 0.1.15 display order (DSP), then seed order, then admin-added ones in file order (an insertion sort into a per-tab
# cache; the cache is dropped by load)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.ArrayList inCat(String cat) {
  if (cat == null) return new java.util.ArrayList();
  java.util.ArrayList c = (java.util.ArrayList) CACHE.get(cat);
  if (c != null) return new java.util.ArrayList(c);
  init();
  java.util.ArrayList ps = new java.util.ArrayList();
  java.util.ArrayList ks = new java.util.ArrayList();
  for (int i = 0; i < LIST.size(); i++) {
    @PKG@.Product p = (@PKG@.Product) LIST.get(i);
    if (!tabsOf(p).contains(cat)) continue;
    Integer dk = (Integer) DSP.get(cat + "|" + p.id);   // 0.1.15: the tab's display order first
    Integer ix = (Integer) ORDER_IX.get(p.id);
    int key = dk != null ? dk.intValue() : (ix == null ? 2000000 + i : 1000000 + ix.intValue());
    int at = ks.size();
    while (at > 0 && ((Integer) ks.get(at - 1)).intValue() > key) at--;
    ks.add(at, Integer.valueOf(key));
    ps.add(at, p);
  }
  CACHE.put(cat, ps);
  return new java.util.ArrayList(ps);
}"""), cat_))
# true when the live Item asset map knows the id (unknown ids are never shown or traded)
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized boolean usable(String id) {{
  if (id == null || !BY_ID.containsKey(id)) return false;
  boolean ok = false;
  try {{ ok = {ITM}.getAssetMap().getAsset(id) != null; }} catch (Throwable t) {{ ok = false; }}
  if (!ok && WARNED.add(id)) {PKG}.BzUtil.warn("product " + id + " is not a known item - hidden and not traded (fix products.properties)");
  return ok;
}}""", cat_))
# parse one line into a Product or null (+ warning)
cat_.addMethod(CtNewMethod.make(f"""
public static {PKG}.Product parse(String line) {{
  if (line == null) return null;
  String s = line.trim();
  if (s.length() == 0 || s.startsWith("#") || s.startsWith("!")) return null;
  int eq = s.indexOf('=');
  if (eq <= 0) {{ {PKG}.BzUtil.warn("products.properties: bad line (no =): " + s); return null; }}
  String id = s.substring(0, eq).trim();
  String[] parts = s.substring(eq + 1).split(",");
  if (!{PKG}.BzUtil.isId(id) || parts.length < 2) {{ {PKG}.BzUtil.warn("products.properties: bad line: " + s); return null; }}
  String cat = parts[0].trim();
  double base;
  try {{ base = Double.parseDouble(parts[1].trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("products.properties: bad price: " + s); return null; }}
  if (!(base >= 0.01 && base <= 1000000000.0)) {{ {PKG}.BzUtil.warn("products.properties: price must be 0.01 .. 1000000000: " + s); return null; }}
  if (cat.length() == 0 || cat.length() > 16) {{ {PKG}.BzUtil.warn("products.properties: category must be 1-16 chars: " + s); return null; }}
  String name = "";
  for (int i = 2; i < parts.length; i++) {{ if (i > 2) name = name + " "; name = name + parts[i].trim(); }}
  if (name.length() == 0) name = id.replace('_', ' ');
  return new {PKG}.Product(id, cat, base, name);
}}""", cat_))
cat_.addMethod(CtNewMethod.make("""
public static synchronized void writeLines(java.util.List lines) throws java.io.IOException {
  java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  StringBuilder sb = new StringBuilder(HEADER);
  for (int i = 0; i < lines.size(); i++) sb.append((String) lines.get(i)).append('\\n');
  java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
  java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}""", cat_))

# 0.1.3: a product line read without a warning (the one-time update and the line-keeping save read every line; load() warns about bad
# ones as 0.1.2 did). Fix round: EXACTLY parse()'s rules (id, at least 2 parts, a price 0.01 .. 1000000000, a category of 1-16
# characters) - a line load() refuses is no product here either, so the update appends that product's seed line instead of losing it
cat_.addMethod(CtNewMethod.make(jt(r"""
public static @PKG@.Product peek(String line) {
  if (line == null) return null;
  String s = line.trim();
  if (s.length() == 0 || s.startsWith("#") || s.startsWith("!")) return null;
  int eq = s.indexOf('=');
  if (eq <= 0) return null;
  String id = s.substring(0, eq).trim();
  String[] parts = s.substring(eq + 1).split(",");
  if (!@PKG@.BzUtil.isId(id) || parts.length < 2) return null;
  String cat = parts[0].trim();
  double base;
  try { base = Double.parseDouble(parts[1].trim()); } catch (Throwable t) { return null; }
  if (!(base >= 0.01 && base <= 1000000000.0)) return null;
  if (cat.length() == 0 || cat.length() > 16) return null;
  String name = "";
  for (int i = 2; i < parts.length; i++) { if (i > 2) name = name + " "; name = name + parts[i].trim(); }
  if (name.length() == 0) name = id.replace('_', ' ');
  return new @PKG@.Product(id, cat, base, name);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static boolean sameLine(@PKG@.Product a, @PKG@.Product b) {
  return a != null && b != null && a.id.equals(b.id) && a.cat.equals(b.cat) && Math.abs(a.base - b.base) < 1.0E-9 && a.name.equals(b.name);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String seedLine(String id) {
  init();
  if (id == null) return null;
  Integer ix = (Integer) ORDER_IX.get(id);
  if (ix == null) return null;
  return SEED[ix.intValue()];
}"""), cat_))
# a line still holding a default: the 0.1.2 seed line or the 0.1.3 seed line of that id (same category, price, name; "6" = "6.0")
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean isDefault(@PKG@.Product p) {
  if (p == null) return false;
  if (sameLine(p, peek(seedLine(p.id)))) return true;
  for (int i = 0; i < SEED013.length; i++) {
    @PKG@.Product q0 = peek(SEED013[i]);
    if (q0 != null && q0.id.equals(p.id) && sameLine(p, q0)) return true;
  }
  for (int i = 0; i < OLD_SEED.length; i++) {
    @PKG@.Product q = peek(OLD_SEED[i]);
    if (q != null && q.id.equals(p.id)) return sameLine(p, q);
  }
  return false;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
  java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}"""), cat_))
# pricing.properties: mode.<id>=auto|fixed per processed good + the one-time update marker (only when the update ran: stamp non-empty)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void writeModes(String stamp) throws java.io.IOException {
  init();
  if (PFILE == null) return;
  if (MODES_BAD) throw new java.io.IOException("pricing.properties could not be read at start - not overwritten");
  StringBuilder sb = new StringBuilder(PHEADER);
  for (int i = 0; i < PROC.size(); i++) {
    String id = (String) ((Object[]) PROC.get(i))[0];
    sb.append("mode.").append(id).append('=').append(AUTO.contains(id) ? "auto" : "fixed").append('\n');
  }
  if (stamp != null && stamp.length() > 0) {
    sb.append("# the one-time update to 0.1.3 is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.3=").append(stamp).append('\n');
  }
  if (MIGRATED14 != null && MIGRATED14.length() > 0) {
    sb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.4=").append(MIGRATED14).append('\n');
  }
  if (MIGRATED19 != null && MIGRATED19.length() > 0) {
    sb.append("# the one-time 0.1.9 new-products update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.9=").append(MIGRATED19).append('\n');
  }
  if (MIGRATED110 != null && MIGRATED110.length() > 0) {
    sb.append("# the one-time 0.1.10 Enchanted products update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.10=").append(MIGRATED110).append('\n');
  }
  if (MIGRATED114 != null && MIGRATED114.length() > 0) {
    sb.append("# the one-time 0.1.14 prices-by-tier update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.14=").append(MIGRATED114).append('\n');
  }
  if (MIGRATED115 != null && MIGRATED115.length() > 0) {
    sb.append("# the one-time 0.1.15 x" + @PKG@.BzUtil.num(SCALE) + " price update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.15=").append(MIGRATED115).append('\n');
  }
  if (MIGRATED116 != null && MIGRATED116.length() > 0) {
    sb.append("# the one-time 0.1.16 Enchanted Stick update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.16=").append(MIGRATED116).append('\n');
  }
  if (MIGRATED119 != null && MIGRATED119.length() > 0) {
    sb.append("# the one-time 0.1.19 Enchanted products update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.19=").append(MIGRATED119).append('\n');
  }
  if (MIGRATED120 != null && MIGRATED120.length() > 0) {
    sb.append("# the one-time 0.1.20 zone metals update is done (remove this line only to run it again)\n");
    sb.append("migrated.0.1.20=").append(MIGRATED120).append('\n');
  }
  atomicWrite(PFILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void loadModes() {
  init();
  java.util.Properties pp = new java.util.Properties();
  MODES_BAD = false;
  try {
    if (PFILE != null && java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(PFILE, new java.nio.file.OpenOption[0]);
      try { pp.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    MODES_BAD = true;
    @PKG@.BzUtil.warn("could not read pricing.properties (" + t + ") - processed goods keep their file prices until it can be read; it is not overwritten");
  }
  AUTO.clear();
  for (int i = 0; i < PROC.size(); i++) {
    String id = (String) ((Object[]) PROC.get(i))[0];
    if (MODES_BAD) continue;
    String m = pp.getProperty("mode." + id, "auto").trim();
    if (!m.equalsIgnoreCase("fixed")) AUTO.add(id);
  }
  String mg = pp.getProperty("migrated.0.1.3");
  if (mg != null && mg.trim().length() > 0) MIGRATED = mg.trim();
  String mg14 = pp.getProperty("migrated.0.1.4");
  if (mg14 != null && mg14.trim().length() > 0) MIGRATED14 = mg14.trim();
  String mg19 = pp.getProperty("migrated.0.1.9");
  if (mg19 != null && mg19.trim().length() > 0) MIGRATED19 = mg19.trim();
  String mg110 = pp.getProperty("migrated.0.1.10");
  if (mg110 != null && mg110.trim().length() > 0) MIGRATED110 = mg110.trim();
  String mg114 = pp.getProperty("migrated.0.1.14");
  if (mg114 != null && mg114.trim().length() > 0) MIGRATED114 = mg114.trim();
  String mg115 = pp.getProperty("migrated.0.1.15");
  if (mg115 != null && mg115.trim().length() > 0) MIGRATED115 = mg115.trim();
  String mg116 = pp.getProperty("migrated.0.1.16");
  if (mg116 != null && mg116.trim().length() > 0) MIGRATED116 = mg116.trim();
  String mg119 = pp.getProperty("migrated.0.1.19");
  if (mg119 != null && mg119.trim().length() > 0) MIGRATED119 = mg119.trim();
  String mg120 = pp.getProperty("migrated.0.1.20");
  if (mg120 != null && mg120.trim().length() > 0) MIGRATED120 = mg120.trim();
}"""), cat_))
# 0.1.2's load (same reading rules) + the tab caches dropped + the processed-goods modes read
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized int load() {
  init();
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.util.ArrayList seed = new java.util.ArrayList();
      for (int i = 0; i < SEED.length; i++) seed.add(SEED[i]);
      writeLines(seed);
      @PKG@.BzUtil.info("seeded " + FILE + " with " + SEED.length + " products");
    }
    java.util.List lines = java.nio.file.Files.readAllLines(FILE, java.nio.charset.StandardCharsets.UTF_8);
    java.util.ArrayList list = new java.util.ArrayList();
    java.util.HashMap map = new java.util.HashMap();
    for (int i = 0; i < lines.size(); i++) {
      @PKG@.Product p = parse((String) lines.get(i));
      if (p == null) continue;
      if (map.containsKey(p.id)) { @PKG@.BzUtil.warn("products.properties: duplicate " + p.id + " ignored"); continue; }
      list.add(p); map.put(p.id, p);
    }
    LIST.clear(); LIST.addAll(list);
    BY_ID.clear(); BY_ID.putAll(map);
    WARNED.clear();
  } catch (Throwable t) { @PKG@.BzUtil.warn("could not load products: " + t); }
  CACHE.clear();
  CATS = null;
  loadModes();
  return LIST.size();
}"""), cat_))
# THE ONE-TIME UPDATE (PROJECT-RULES one-time migrations): runs while pricing.properties has no migrated.0.1.3 marker. A fresh install is
# seeded with the seed lines. An existing file: a verified byte copy products.properties.v012bak first (never overwritten), then line by
# line: a line still holding a default (0.1.2 or 0.1.3 seed: same category, price, name) becomes its 0.1.3 seed line when that differs
# in category / price / name (a line that only spells a number differently, "6.0" for "6", keeps its bytes); a hand-edited line
# stays byte for byte (a processed good on it becomes FIXED, logged - reprice holds it at its no-loop limit); every 0.1.3 product the
# file lacks is appended in seed order - a line load() would refuse (peek = parse's rules) does not count as having it; comments,
# blank / unknown lines and each line's own line ending are kept. products.properties is written first, the marker last, so a failed
# step changes nothing it cannot redo: the next start runs the same, idempotent update again.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate() {
  init();
  try {
    java.util.Properties pp = new java.util.Properties();
    if (PFILE != null && java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(PFILE, new java.nio.file.OpenOption[0]);
      try { pp.load(in); } finally { in.close(); }
    }
    String done = pp.getProperty("migrated.0.1.3");
    if (done != null && done.trim().length() > 0) { MIGRATED = done.trim(); return null; }
    boolean fresh = !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]);
    java.util.HashSet fixedIds = new java.util.HashSet();
    java.util.ArrayList kept = new java.util.ArrayList();
    int added = 0;
    int rewrote = 0;
    StringBuilder sb = new StringBuilder();
    if (fresh) {
      sb.append(HEADER);
      for (int i = 0; i < SEED.length; i++) sb.append(SEED[i]).append('\n');
      added = SEED.length;
    } else {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      java.nio.file.Path bak = FILE.resolveSibling(FILE.getFileName().toString() + ".v012bak");
      if (!java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0])) {
        java.nio.file.Files.write(bak, raw, new java.nio.file.OpenOption[0]);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the copy " + bak + " does not match the file - nothing changed");
      }
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      boolean endNl = txt.endsWith("\n");
      String[] lines = txt.split("\n", -1);
      int n = lines.length;
      if (endNl) n = n - 1;
      java.util.HashSet have = new java.util.HashSet();
      for (int i = 0; i < n; i++) {
        String ln = lines[i];
        boolean cr = ln.endsWith("\r");
        String body = cr ? ln.substring(0, ln.length() - 1) : ln;
        String out = body;
        @PKG@.Product p = peek(body);
        if (p != null && !have.contains(p.id)) {
          have.add(p.id);
          String sl = seedLine(p.id);
          if (sl != null && isDefault(p)) {
            if (!sameLine(p, peek(sl))) { out = sl; rewrote++; }
          } else if (PROC_BY.containsKey(p.id)) {
            fixedIds.add(p.id);
            kept.add(p.id);
          }
        }
        sb.append(out);
        if (i < n - 1 || endNl) sb.append(cr ? "\r\n" : "\n");
      }
      if (n > 0 && !endNl) sb.append(nl);
      for (int i = 0; i < SEED.length; i++) {
        String id = SEED[i].substring(0, SEED[i].indexOf('='));
        if (have.contains(id)) continue;
        sb.append(SEED[i]).append(nl);
        added++;
      }
    }
    atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
    AUTO.clear();
    for (int i = 0; i < PROC.size(); i++) {
      String id = (String) ((Object[]) PROC.get(i))[0];
      if (!fixedIds.contains(id)) AUTO.add(id);
    }
    String stamp = java.time.Instant.now().toString();
    MODES_BAD = false;
    writeModes(stamp);
    MIGRATED = stamp;
    String msg = fresh ? ("first start: products.properties seeded with " + added + " products")
                       : ("one-time update to 0.1.3: " + added + " products added, " + rewrote + " default lines updated"
                          + (kept.isEmpty() ? "" : ", your own prices kept for " + kept + " (fixed - /bazaaradmin price <id> auto makes one follow its inputs)")
                          + "; the old file is products.properties.v012bak");
    @PKG@.BzUtil.info(msg);
    return "MIGRATE-0.1.3 " + (fresh ? "seeded " : "added ") + added + " rewrote " + rewrote + " fixed " + kept.size();
  } catch (Throwable t) {
    @PKG@.BzUtil.warn("the one-time 0.1.3 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.4: THE ONE-TIME PROGRESSION PRICE UPDATE (PROJECT-RULES one-time migrations). Runs after migrate() (0.1.3; it must have marked
# migrated.0.1.3) while pricing.properties has no migrated.0.1.4. A product line (first one of its id that load() would read; peek =
# parse's rules) whose price is EXACTLY its 0.1.3 default (M14_OLD, numerically) gets M14_TXT in place of the price text only; a price
# that is not the 0.1.3 default is kept and logged; everything else (other lines, comments, spacing, each line ending, a missing final
# newline) stays byte for byte. Before products.properties is written its bytes go to config-history/ (read back + compared - a
# mismatch throws, nothing changes). products.properties first, the marker last (appended to pricing.properties, its bytes kept), so a
# failed step changes nothing it cannot redo. The trades.log lines wait in M14_LOG (setup writes them after Market.load).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int m14(String id) {
  if (id == null) return -1;
  for (int i = 0; i < M14_ID.length; i++) if (M14_ID[i].equals(id)) return i;
  return -1;
}"""), cat_))
# 0.1.15: the x SCALE_X update's table lookup + "this line already holds its 0.1.15 default" (a fresh 0.1.15 install seeds the scaled
# prices: migrate14 / migrate114 / migrate115 count such a line as done, never as an admin's price)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int m115(String id) {
  if (id == null) return -1;
  init();
  Integer k = (Integer) M115_IX.get(id);
  return k == null ? -1 : k.intValue();
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static boolean m115now(@PKG@.Product p) {
  int k = p == null ? -1 : m115(p.id);
  return k >= 0 && Math.abs(p.base - M115_NEW[k]) < 1.0E-9;
}"""), cat_))
# 0.1.15: a verified byte copy of a data file in config-history/ (written, read back, compared - a mismatch throws); returns its name
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String histCopy(java.nio.file.Path f, byte[] raw) throws java.io.IOException {
  java.nio.file.Path hd = f.toAbsolutePath().getParent().resolve("config-history");
  java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
  java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
  java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
  String nm = "Skyy_SkyyBazaar~" + f.getFileName().toString() + ".";
  java.nio.file.Path bak = hd.resolve(nm + fm.format(t0) + ".bak");
  int g = 0;
  while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
    g++;
    bak = hd.resolve(nm + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
  }
  atomicWrite(bak, raw);
  byte[] back = java.nio.file.Files.readAllBytes(bak);
  if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match " + f.getFileName() + " - nothing changed");
  return "config-history/" + bak.getFileName().toString();
}"""), cat_))
# 0.1.14: the tier price update's table lookup + "this line already holds its 0.1.14 default" (a fresh 0.1.14 install seeds the new
# prices; migrate14 must count such a line as done, not as an admin's price)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int m114(String id) {
  if (id == null) return -1;
  for (int i = 0; i < M114_ID.length; i++) if (M114_ID[i].equals(id)) return i;
  return -1;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static boolean m114now(@PKG@.Product p) {
  int k = p == null ? -1 : m114(p.id);
  return (k >= 0 && Math.abs(p.base - M114_NEW[k]) < 1.0E-9) || m115now(p);   // 0.1.15: or its 0.1.15 default
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String withPrice(String body, String np) {
  int eq = body.indexOf('=');
  if (eq < 0) return null;
  int c1 = body.indexOf(',', eq + 1);
  if (c1 < 0) return null;
  int c2 = body.indexOf(',', c1 + 1);
  int end = c2 < 0 ? body.length() : c2;
  String tok = body.substring(c1 + 1, end);
  int a = 0;
  while (a < tok.length() && Character.isWhitespace(tok.charAt(a))) a++;
  int b = tok.length();
  while (b > a && Character.isWhitespace(tok.charAt(b - 1))) b--;
  return body.substring(0, c1 + 1) + tok.substring(0, a) + np + tok.substring(b) + body.substring(end);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate14() {
  init();
  M14_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m13 = pp.getProperty("migrated.0.1.3");
    if (m13 == null || m13.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.4");
    if (done != null && done.trim().length() > 0) { MIGRATED14 = done.trim(); return null; }
    int rewrote = 0;
    int already = 0;
    java.util.ArrayList kept = new java.util.ArrayList();
    java.util.ArrayList lines = new java.util.ArrayList();
    StringBuilder ex = new StringBuilder();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String[] ls = txt.split("\n", -1);
      StringBuilder sb = new StringBuilder(txt.length() + 64);
      java.util.HashSet have = new java.util.HashSet();
      for (int i = 0; i < ls.length; i++) {
        String ln = ls[i];
        boolean cr = ln.endsWith("\r");
        String body = cr ? ln.substring(0, ln.length() - 1) : ln;
        String out = body;
        @PKG@.Product p = peek(body);
        if (p != null && !have.contains(p.id)) {
          have.add(p.id);
          int k = m14(p.id);
          if (k >= 0) {
            if (Math.abs(p.base - M14_OLD[k]) < 1.0E-9 && !m115now(p)) {   // 0.1.15: a line at its 0.1.15 default is done
              String nb = withPrice(body, M14_TXT[k]);
              @PKG@.Product q = peek(nb);
              if (nb != null && q != null && q.id.equals(p.id) && q.cat.equals(p.cat) && q.name.equals(p.name) && Math.abs(q.base - M14_NEW[k]) < 1.0E-9) {
                out = nb;
                rewrote++;
                lines.add("MIGRATE-0.1.4 PRICE " + p.id + " " + M14_OTXT[k] + " -> " + M14_TXT[k] + " (undo: /bazaaradmin price " + p.id + " " + M14_OTXT[k] + ")");
                if (rewrote <= 4) { if (ex.length() > 0) ex.append(", "); ex.append(p.name).append(' ').append(M14_OTXT[k]).append(" -> ").append(M14_TXT[k]); }
              } else {
                kept.add(p.id);
                lines.add("MIGRATE-0.1.4 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (the line could not be rewritten safely; the 0.1.4 default is " + M14_TXT[k] + ")");
              }
            } else if (Math.abs(p.base - M14_NEW[k]) < 1.0E-9 || m114now(p)) {
              already++;
            } else {
              kept.add(p.id + " " + @PKG@.BzUtil.num(p.base));
              lines.add("MIGRATE-0.1.4 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (your price; the 0.1.3 default was " + M14_OTXT[k] + ", the 0.1.4 default is " + M14_TXT[k] + ")");
            }
          }
        }
        sb.append(out);
        if (i < ls.length - 1) sb.append(cr ? "\r\n" : "\n");
        else if (cr) sb.append('\r');
      }
      if (rewrote > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.4=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED14 = stamp;
    String head = "MIGRATE-0.1.4 rewrote " + rewrote + " kept " + kept.size() + " already " + already + (backup.length() > 0 ? " backup " + backup : "");
    M14_LOG.add(head);
    M14_LOG.addAll(lines);
    String msg = "one-time 0.1.4 progression price update (Skyy 2026-10-04: x2 per tier step): " + rewrote + " default prices updated"
               + (ex.length() > 0 ? " (" + ex + (rewrote > 4 ? ", ..." : "") + ")" : "")
               + (kept.isEmpty() ? "" : ", your own prices kept for " + kept)
               + (already > 0 ? ", " + already + " already at the 0.1.4 price" : "")
               + (backup.length() > 0 ? "; the old file is " + backup + ", every change + its undo command is in trades.log" : "");
    @PKG@.BzUtil.info(msg);
    return head;
  } catch (Throwable t) {
    M14_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.4 price update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.14: THE ONE-TIME PRICES-BY-TIER UPDATE (PROJECT-RULES one-time migrations; migrate14's pattern, run after migrate110). Runs while
# pricing.properties has migrated.0.1.4 and no migrated.0.1.14: a product line whose price is still EXACTLY its 0.1.13 default (M114_OLD;
# "16" = "16.0") gets its 0.1.14 default - the price text only (withPrice: id, category, name, spacing and the line ending stay byte for
# byte); a line already at the 0.1.14 default counts as done; any other price is KEPT (an admin's /bazaaradmin price or a hand edit) and
# logged. products.properties is written only when a line changed, after a byte copy in config-history/ was written, read back and
# compared (a mismatch changes nothing); the marker is appended to pricing.properties last (its other bytes stay). A failed step writes no
# marker and retries at the next start (idempotent). trades.log: one MIGRATE-0.1.14 summary + a line per change with its undo command.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate114() {
  init();
  M114_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.14");
    if (done != null && done.trim().length() > 0) { MIGRATED114 = done.trim(); return null; }
    int rewrote = 0;
    int already = 0;
    java.util.ArrayList kept = new java.util.ArrayList();
    java.util.ArrayList lines = new java.util.ArrayList();
    StringBuilder ex = new StringBuilder();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String[] ls = txt.split("\n", -1);
      StringBuilder sb = new StringBuilder(txt.length() + 64);
      java.util.HashSet have = new java.util.HashSet();
      for (int i = 0; i < ls.length; i++) {
        String ln = ls[i];
        boolean cr = ln.endsWith("\r");
        String body = cr ? ln.substring(0, ln.length() - 1) : ln;
        String out = body;
        @PKG@.Product p = peek(body);
        if (p != null && !have.contains(p.id)) {
          have.add(p.id);
          int k = m114(p.id);
          if (k >= 0) {
            if (Math.abs(p.base - M114_OLD[k]) < 1.0E-9 && !m115now(p)) {   // 0.1.15: a line at its 0.1.15 default is done
              String nb = withPrice(body, M114_TXT[k]);
              @PKG@.Product q = peek(nb);
              if (nb != null && q != null && q.id.equals(p.id) && q.cat.equals(p.cat) && q.name.equals(p.name) && Math.abs(q.base - M114_NEW[k]) < 1.0E-9) {
                out = nb;
                rewrote++;
                lines.add("MIGRATE-0.1.14 PRICE " + p.id + " " + M114_OTXT[k] + " -> " + M114_TXT[k] + " (undo: /bazaaradmin price " + p.id + " " + M114_OTXT[k] + ")");
                if (rewrote <= 4) { if (ex.length() > 0) ex.append(", "); ex.append(p.name).append(' ').append(M114_OTXT[k]).append(" -> ").append(M114_TXT[k]); }
              } else {
                kept.add(p.id);
                lines.add("MIGRATE-0.1.14 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (the line could not be rewritten safely; the 0.1.14 default is " + M114_TXT[k] + ")");
              }
            } else if (Math.abs(p.base - M114_NEW[k]) < 1.0E-9 || m115now(p)) {
              already++;
            } else {
              kept.add(p.id + " " + @PKG@.BzUtil.num(p.base));
              lines.add("MIGRATE-0.1.14 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (your price; the 0.1.13 default was " + M114_OTXT[k] + ", the 0.1.14 default is " + M114_TXT[k] + ")");
            }
          }
        }
        sb.append(out);
        if (i < ls.length - 1) sb.append(cr ? "\r\n" : "\n");
        else if (cr) sb.append('\r');
      }
      if (rewrote > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.14 prices-by-tier update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.14=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED114 = stamp;
    String head = "MIGRATE-0.1.14 rewrote " + rewrote + " kept " + kept.size() + " already " + already + (backup.length() > 0 ? " backup " + backup : "");
    M114_LOG.add(head);
    M114_LOG.addAll(lines);
    String msg = "one-time 0.1.14 price update (Skyy 2026-10-15: prices by tier, Eternal seeds from 800): " + rewrote + " default prices updated"
               + (ex.length() > 0 ? " (" + ex + (rewrote > 4 ? ", ..." : "") + ")" : "")
               + (kept.isEmpty() ? "" : ", your own prices kept for " + kept)
               + (already > 0 ? ", " + already + " already at the 0.1.14 price" : "")
               + (backup.length() > 0 ? "; the old file is " + backup + ", every change + its undo command is in trades.log" : "");
    @PKG@.BzUtil.info(msg);
    return head;
  } catch (Throwable t) {
    M114_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.14 price update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.15: THE ONE-TIME x SCALE UPDATE (PROJECT-RULES one-time migrations; migrate114's pattern, run after it). Runs while
# pricing.properties has migrated.0.1.14 and no migrated.0.1.15: a product line whose price is still EXACTLY its 0.1.14 default (M115_OLD)
# gets its 0.1.15 default (the price text only - withPrice); a line already at the 0.1.15 default counts as done; any other price is KEPT
# (an admin's /bazaaradmin price or a hand edit) and logged. market.properties: the LAST impactCoins line (Properties' rule) still at the
# 0.1.14 default 10000 gets IMP_TXT (the value text only); already IMP_NEW = done; any other value is KEPT and logged; no line = the jar's
# new default. Each
# changed file is written only after its verified byte copy in config-history/ (histCopy); every other byte and line ending stays; the
# marker is appended to pricing.properties LAST (its other bytes stay). A failed step writes no marker and the next start runs the same,
# idempotent update again. trades.log: one MIGRATE-0.1.15 summary + a line per change with its undo command (M115_LOG).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate115() {
  init();
  M115_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m114 = pp.getProperty("migrated.0.1.14");
    if (m114 == null || m114.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.15");
    if (done != null && done.trim().length() > 0) { MIGRATED115 = done.trim(); return null; }
    int rewrote = 0;
    int already = 0;
    java.util.ArrayList kept = new java.util.ArrayList();
    java.util.ArrayList lines = new java.util.ArrayList();
    StringBuilder ex = new StringBuilder();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String[] ls = txt.split("\n", -1);
      StringBuilder sb = new StringBuilder(txt.length() + 256);
      java.util.HashSet have = new java.util.HashSet();
      for (int i = 0; i < ls.length; i++) {
        String ln = ls[i];
        boolean cr = ln.endsWith("\r");
        String body = cr ? ln.substring(0, ln.length() - 1) : ln;
        String out = body;
        @PKG@.Product p = peek(body);
        if (p != null && !have.contains(p.id)) {
          have.add(p.id);
          int k = m115(p.id);
          if (k >= 0) {
            if (Math.abs(p.base - M115_OLD[k]) < 1.0E-9) {
              String nb = withPrice(body, M115_TXT[k]);
              @PKG@.Product q = peek(nb);
              if (nb != null && q != null && q.id.equals(p.id) && q.cat.equals(p.cat) && q.name.equals(p.name) && Math.abs(q.base - M115_NEW[k]) < 1.0E-9) {
                out = nb;
                rewrote++;
                lines.add("MIGRATE-0.1.15 PRICE " + p.id + " " + M115_OTXT[k] + " -> " + M115_TXT[k] + " (undo: /bazaaradmin price " + p.id + " " + M115_OTXT[k] + ")");
                if (rewrote <= 4) { if (ex.length() > 0) ex.append(", "); ex.append(p.name).append(' ').append(M115_OTXT[k]).append(" -> ").append(M115_TXT[k]); }
              } else {
                kept.add(p.id);
                lines.add("MIGRATE-0.1.15 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (the line could not be rewritten safely; the 0.1.15 default is " + M115_TXT[k] + ")");
              }
            } else if (Math.abs(p.base - M115_NEW[k]) < 1.0E-9) {
              already++;
            } else {
              kept.add(p.id + " " + @PKG@.BzUtil.num(p.base));
              lines.add("MIGRATE-0.1.15 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (your price; the 0.1.14 default was " + M115_OTXT[k] + ", the 0.1.15 default is " + M115_TXT[k] + ")");
            }
          }
        }
        sb.append(out);
        if (i < ls.length - 1) sb.append(cr ? "\r\n" : "\n");
        else if (cr) sb.append('\r');
      }
      if (rewrote > 0) {
        backup = histCopy(FILE, raw);
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    // market.properties impactCoins (Properties text: key, then '=' / ':' / blanks, then the value; the last line of a key wins)
    String impact = "default";
    String mbackup = "";
    java.nio.file.Path mf = FILE.toAbsolutePath().resolveSibling("market.properties");   // = Market.FILE (setup: the same folder)
    if (mf != null && java.nio.file.Files.exists(mf, new java.nio.file.LinkOption[0])) {
      byte[] mraw = java.nio.file.Files.readAllBytes(mf);
      String mt = new String(mraw, "ISO-8859-1");
      String[] ml = mt.split("\n", -1);
      int at = -1;
      int vs = -1;
      for (int i = 0; i < ml.length; i++) {
        String b = ml[i].endsWith("\r") ? ml[i].substring(0, ml[i].length() - 1) : ml[i];
        int a = 0;
        while (a < b.length() && (b.charAt(a) == ' ' || b.charAt(a) == '\t' || b.charAt(a) == '\f')) a++;
        if (a >= b.length() || b.charAt(a) == '#' || b.charAt(a) == '!') continue;
        int j = a;
        while (j < b.length() && "=: \t\f".indexOf(b.charAt(j)) < 0) j++;
        if (!b.substring(a, j).equals("impactCoins")) continue;
        int v = j;
        while (v < b.length() && (b.charAt(v) == ' ' || b.charAt(v) == '\t' || b.charAt(v) == '\f')) v++;
        if (v < b.length() && (b.charAt(v) == '=' || b.charAt(v) == ':')) {
          v++;
          while (v < b.length() && (b.charAt(v) == ' ' || b.charAt(v) == '\t' || b.charAt(v) == '\f')) v++;
        }
        at = i;
        vs = v;
      }
      if (at >= 0) {
        boolean cr = ml[at].endsWith("\r");
        String b = cr ? ml[at].substring(0, ml[at].length() - 1) : ml[at];
        String val = b.substring(vs).trim();
        double dv = -1.0;
        try { dv = Double.parseDouble(val); } catch (Throwable x) { dv = -1.0; }
        if (Math.abs(dv - IMP_OLD) < 1.0E-9) {
          ml[at] = b.substring(0, vs) + IMP_TXT + (cr ? "\r" : "");
          StringBuilder mb = new StringBuilder(mt.length() + 16);
          for (int i = 0; i < ml.length; i++) { if (i > 0) mb.append('\n'); mb.append(ml[i]); }
          mbackup = histCopy(mf, mraw);
          atomicWrite(mf, mb.toString().getBytes("ISO-8859-1"));
          impact = "moved";
          lines.add("MIGRATE-0.1.15 IMPACT impactCoins " + val + " -> " + IMP_TXT + " (undo: set impactCoins=" + val + " in market.properties, then /bazaaradmin reload)");
        } else if (Math.abs(dv - IMP_NEW) < 1.0E-9) {
          impact = "already";
        } else {
          impact = "kept";
          lines.add("MIGRATE-0.1.15 KEPT impactCoins " + val + " (your value; the 0.1.14 default was " + @PKG@.BzUtil.num(IMP_OLD) + ", the 0.1.15 default is " + IMP_TXT + ")");
        }
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.15 x" + @PKG@.BzUtil.num(SCALE) + " price update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.15=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED115 = stamp;
    String head = "MIGRATE-0.1.15 x" + @PKG@.BzUtil.num(SCALE) + " rewrote " + rewrote + " kept " + kept.size() + " already " + already + " impact " + impact
                + (backup.length() > 0 ? " backup " + backup : "") + (mbackup.length() > 0 ? " market backup " + mbackup : "");
    M115_LOG.add(head);
    M115_LOG.addAll(lines);
    String msg = "one-time 0.1.15 price update (Skyy 2026-10-16: every price x" + @PKG@.BzUtil.num(SCALE) + " so the cheapest sells for 2, the Eternal seeds unchanged): "
               + rewrote + " default prices updated"
               + (ex.length() > 0 ? " (" + ex + (rewrote > 4 ? ", ..." : "") + ")" : "")
               + (kept.isEmpty() ? "" : ", your own prices kept for " + kept)
               + (already > 0 ? ", " + already + " already at the 0.1.15 price" : "")
               + (impact.equals("moved") ? ", impactCoins " + @PKG@.BzUtil.num(IMP_OLD) + " -> " + IMP_TXT : (impact.equals("kept") ? ", your impactCoins kept" : ""))
               + (backup.length() > 0 || mbackup.length() > 0 ? "; the old files are in config-history/, every change + its undo command is in trades.log" : "");
    @PKG@.BzUtil.info(msg);
    return head;
  } catch (Throwable t) {
    M115_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.15 price update failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.9: THE ONE-TIME NEW-PRODUCTS UPDATE (PROJECT-RULES one-time migrations; the migrate14 pattern). Runs after migrate14 while
# pricing.properties has migrated.0.1.4 and no migrated.0.1.9. Each NEW019 product whose id is in no line load() would read gets its seed
# line APPENDED (nothing else changes: every existing byte and line ending stays; the file's own newline style; a missing final newline is
# added first). Before products.properties is written its bytes go to config-history/ (read back + compared - a mismatch throws, nothing
# changes). products.properties first, the marker last (appended to pricing.properties, its bytes kept): a failed step changes nothing it
# cannot redo. The trades.log lines wait in M19_LOG (setup writes them after Market.load).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate19() {
  init();
  M19_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.9");
    if (done != null && done.trim().length() > 0) { MIGRATED19 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW019.length; i++) {
        if (have.contains(NEW019[i])) { already++; continue; }
        String sl = seedLine(NEW019[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.9 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.9 new-products update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.9=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED19 = stamp;
    String head = "MIGRATE-0.1.9 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M19_LOG.add(head);
    M19_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.9 update (SkyyVoid puts crystal shards in Mining): " + added + " new Mining product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M19_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.9 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.10: THE ONE-TIME ENCHANTED PRODUCTS UPDATE = migrate19's code with its own names (NEW0110, marker migrated.0.1.10, M110_LOG); it
# runs after migrate19 while pricing.properties has migrated.0.1.4 and no migrated.0.1.10, and appends each NEW0110 product not in the file.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate110() {
  init();
  M110_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.10");
    if (done != null && done.trim().length() > 0) { MIGRATED110 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW0110.length; i++) {
        if (have.contains(NEW0110[i])) { already++; continue; }
        String sl = seedLine(NEW0110[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.10 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.10 Enchanted products update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.10=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED110 = stamp;
    String head = "MIGRATE-0.1.10 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M110_LOG.add(head);
    M110_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.10 update (the Enchanted materials): " + added + " new product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M110_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.10 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.16: THE ONE-TIME ENCHANTED STICK UPDATE = migrate110's code with its own names (NEW0116, marker migrated.0.1.16, M116_LOG; built
# from migrate110's text by tools/bazaar_0_1_16_patch.py); it runs after migrate115 while pricing.properties has migrated.0.1.4 and no
# migrated.0.1.16, and appends the NEW0116 product when no line holds it.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate116() {
  init();
  M116_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.16");
    if (done != null && done.trim().length() > 0) { MIGRATED116 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW0116.length; i++) {
        if (have.contains(NEW0116[i])) { already++; continue; }
        String sl = seedLine(NEW0116[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.16 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.16 Enchanted Stick update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.16=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED116 = stamp;
    String head = "MIGRATE-0.1.16 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M116_LOG.add(head);
    M116_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.16 update (the Enchanted Stick): " + added + " new product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M116_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.16 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.19: THE ONE-TIME C1 ENCHANTED PRODUCTS UPDATE = migrate116's code with its own names (NEW0119, marker migrated.0.1.19, M119_LOG;
# built from migrate116's text by tools/bazaar_0_1_19_patch.py); it runs after migrate116 while pricing.properties has migrated.0.1.4 and no
# migrated.0.1.19, and appends each NEW0119 product no line holds.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate119() {
  init();
  M119_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.19");
    if (done != null && done.trim().length() > 0) { MIGRATED119 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW0119.length; i++) {
        if (have.contains(NEW0119[i])) { already++; continue; }
        String sl = seedLine(NEW0119[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.19 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.19 Enchanted products update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.19=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED119 = stamp;
    String head = "MIGRATE-0.1.19 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M119_LOG.add(head);
    M119_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.19 update (the C1 Enchanted products): " + added + " new product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M119_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.19 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# ---- 0.1.20: THE ONE-TIME ZONE METALS UPDATE = migrate119's code with its own names (NEW0120, marker migrated.0.1.20, M120_LOG;
# built from migrate119's text by tools/bazaar_0_1_19_patch.py); it runs after migrate119 while pricing.properties has migrated.0.1.4 and no
# migrated.0.1.20, and appends each NEW0120 product no line holds.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate120() {
  init();
  M120_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m14 = pp.getProperty("migrated.0.1.4");
    if (m14 == null || m14.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.20");
    if (done != null && done.trim().length() > 0) { MIGRATED120 = done.trim(); return null; }
    int added = 0;
    int already = 0;
    java.util.ArrayList lines = new java.util.ArrayList();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
      java.util.HashSet have = new java.util.HashSet();
      String[] ls = txt.split("\n", -1);
      for (int i = 0; i < ls.length; i++) {
        @PKG@.Product p = peek(ls[i].endsWith("\r") ? ls[i].substring(0, ls[i].length() - 1) : ls[i]);
        if (p != null) have.add(p.id);
      }
      StringBuilder sb = new StringBuilder(txt);
      boolean nlDone = txt.length() == 0 || txt.endsWith("\n");
      for (int i = 0; i < NEW0120.length; i++) {
        if (have.contains(NEW0120[i])) { already++; continue; }
        String sl = seedLine(NEW0120[i]);
        if (sl == null) continue;
        if (!nlDone) { sb.append(nl); nlDone = true; }
        sb.append(sl).append(nl);
        added++;
        lines.add("MIGRATE-0.1.20 ADDED " + sl + " (undo: delete that line from products.properties, then /bazaaradmin reload)");
      }
      if (added > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.20 zone metals update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.20=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED120 = stamp;
    String head = "MIGRATE-0.1.20 added " + added + " already " + already + (backup.length() > 0 ? " backup " + backup : "") + " (undo all: put the backup back as products.properties)";
    M120_LOG.add(head);
    M120_LOG.addAll(lines);
    @PKG@.BzUtil.info("one-time 0.1.20 update (the zone metals): " + added + " new product(s) added" + (already > 0 ? ", " + already + " were already listed" : "") + (backup.length() > 0 ? "; the old file is " + backup + ", every line + its undo is in trades.log" : ""));
    return head;
  } catch (Throwable t) {
    M120_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.20 update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
# the raw-input value of a processed good: inputs (qty x the cheapest listed product of each input) + fuel (seconds x the cheapest
# listed fuel per second net of the charcoal it gives back, never below 0), per output item. -1 = an input has no listed product.
# Fix round: an input that is itself a processed good counts at min(its price, its own raw value) (rv: the raw values of the goods
# before it in PROC order) - the premium is never stacked (Dawnstone = 4 cobble x (1 + premium), not (1 + premium)^2).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double value0(Object[] e, java.util.HashMap rv) {
  double[] q = (double[]) e[4];
  Object[] cand = (Object[]) e[5];
  double tot = 0.0;
  for (int k = 0; k < q.length; k++) {
    String[] cs = (String[]) cand[k];
    double best = -1.0;
    for (int j = 0; j < cs.length; j++) {
      @PKG@.Product p = (@PKG@.Product) BY_ID.get(cs[j]);
      if (p == null) continue;
      double b = p.base;
      Double r = rv == null ? null : (Double) rv.get(cs[j]);
      if (r != null && r.doubleValue() >= 0.0 && r.doubleValue() < b) b = r.doubleValue();
      if (best < 0.0 || b < best) best = b;
    }
    if (best < 0.0) return -1.0;
    tot += q[k] * best;
  }
  double secs = ((Double) e[2]).doubleValue();
  if (secs > 0.0) {
    double per = 0.0;
    boolean any = false;
    @PKG@.Product ch = (@PKG@.Product) BY_ID.get(CHARCOAL);
    for (int i = 0; i < FUEL.size(); i++) {
      Object[] f = (Object[]) FUEL.get(i);
      @PKG@.Product fp = (@PKG@.Product) BY_ID.get((String) f[0]);
      if (fp == null) continue;
      double sh = ((Double) f[2]).doubleValue();
      double back = (sh > 0.0 && ch != null) ? sh * ch.base : 0.0;
      double c = (fp.base - back) / ((Double) f[1]).doubleValue();
      if (!any || c < per) { per = c; any = true; }
    }
    if (any && per > 0.0) tot += per * secs;
  }
  return tot / ((Double) e[1]).doubleValue();
}"""), cat_))
# every processed good's raw value, in PROC order (inputs first), on the current prices
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.HashMap rawValues() {
  init();
  java.util.HashMap rv = new java.util.HashMap();
  for (int k = 0; k < PROC.size(); k++) {
    Object[] e = (Object[]) PROC.get(k);
    rv.put((String) e[0], Double.valueOf(value0(e, rv)));
  }
  return rv;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double valueOf(Object[] e) {
  if (e == null) return -1.0;
  Double r = (Double) rawValues().get((String) e[0]);
  return r == null ? -1.0 : r.doubleValue();
}"""), cat_))
# every processed good on auto: base = floor(value x (1 + prem), 0.01) - never above the exact value, so (1 + prem) x (1 - spread) <=
# 1 + spread (BzCfg.effective) keeps buy inputs -> process -> sell from paying. PROC is in the build's proc_order: charcoal first (bars
# use its new price), every processed input before what is made from it (Dawnstone after Quartzite), so one pass is enough.
# Fix round: a FIXED processed good above its no-loop limit (value x (1 + spread) / (1 - spread), the price /bazaaradmin price refuses
# above - reached by a hand edit of products.properties or an input an admin made cheaper) is held at that limit, with one warning.
# sp = Market.SPREAD, passed in by repriceLocked (Catalog is compiled before Market exists).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized int reprice0(double prem, int pct, double sp) {
  init();
  int moved = 0;
  java.util.HashMap rv = new java.util.HashMap();
  for (int k = 0; k < PROC.size(); k++) {
    Object[] e = (Object[]) PROC.get(k);
    String id = (String) e[0];
    @PKG@.Product p = (@PKG@.Product) BY_ID.get(id);
    double v = value0(e, rv);
    rv.put(id, Double.valueOf(v));
    if (p == null) continue;
    if (!AUTO.contains(id)) {
      if (!(sp > 0.0) || sp >= 1.0 || v <= 0.0) continue;
      double cap = Math.floor(v * (1.0 + sp) / (1.0 - sp) * 100.0) / 100.0;
      if (cap >= 0.01 && p.base > cap + 1.0E-9) {
        if (WARNED.add("cap:" + id + ":" + @PKG@.BzUtil.num(cap))) @PKG@.BzUtil.warn(id + " has the fixed price " + @PKG@.BzUtil.num(p.base) + " - above " + @PKG@.BzUtil.num(cap) + " buying its inputs, processing and selling makes coins, so it is held at " + @PKG@.BzUtil.num(cap) + " (/bazaaradmin price " + id + " auto makes it follow its inputs)");
        p.base = cap;
        moved++;
      }
      continue;
    }
    if (v < 0.0) {
      if (WARNED.add("proc:" + id)) @PKG@.BzUtil.warn(id + " follows its inputs, but none of them is a product any more - it keeps " + @PKG@.BzUtil.num(p.base));
      continue;
    }
    double nb = Math.floor(v * (1.0 + prem) * 100.0 + 1.0E-9) / 100.0;
    if (nb < 0.01) nb = 0.01;
    if (nb > 1.0E9) nb = 1.0E9;
    if (Math.abs(nb - p.base) > 1.0E-9) { p.base = nb; moved++; }
  }
  if (moved > 0) DIRTY = true;
  PREM = prem;
  PCT = pct;
  return moved;
}"""), cat_))
# fix round: a line-keeping save (0.1.2 rewrote the whole file from memory, dropping comments, CRLF and the number spelling): every
# product line whose category / price / name differs from memory is rewritten in place, every other line (comments, blank and unknown
# lines, lines load() refuses, a duplicate, a product line equal to memory - "6" stays "6") keeps its bytes and its own line ending;
# products the file lacks are appended (the file's line ending). No file yet: the 0.1.2 way (header + every product).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void saveProducts() throws java.io.IOException {
  if (FILE == null) return;
  if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
    java.util.ArrayList all = new java.util.ArrayList();
    for (int i = 0; i < LIST.size(); i++) {
      @PKG@.Product q = (@PKG@.Product) LIST.get(i);
      all.add(q.id + "=" + q.cat + "," + @PKG@.BzUtil.num(q.base) + "," + q.name);
    }
    writeLines(all);
    return;
  }
  String txt = new String(java.nio.file.Files.readAllBytes(FILE), java.nio.charset.StandardCharsets.UTF_8);
  String nl = txt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  boolean endNl = txt.endsWith("\n");
  String[] lines = txt.split("\n", -1);
  int n = lines.length;
  if (endNl) n = n - 1;
  java.util.HashSet done = new java.util.HashSet();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < n; i++) {
    String ln = lines[i];
    boolean cr = ln.endsWith("\r");
    String body = cr ? ln.substring(0, ln.length() - 1) : ln;
    String out = body;
    @PKG@.Product p = peek(body);
    if (p != null && !done.contains(p.id)) {
      @PKG@.Product q = (@PKG@.Product) BY_ID.get(p.id);
      if (q != null) {
        done.add(p.id);
        if (!sameLine(p, q)) out = q.id + "=" + q.cat + "," + @PKG@.BzUtil.num(q.base) + "," + q.name;
      }
    }
    sb.append(out);
    if (i < n - 1 || endNl) sb.append(cr ? "\r\n" : "\n");
  }
  if (n > 0 && !endNl) sb.append(nl);
  for (int i = 0; i < LIST.size(); i++) {
    @PKG@.Product q = (@PKG@.Product) LIST.get(i);
    if (done.contains(q.id)) continue;
    sb.append(q.id + "=" + q.cat + "," + @PKG@.BzUtil.num(q.base) + "," + q.name).append(nl);
  }
  atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void flushIfDirty() {
  if (!DIRTY) return;
  DIRTY = false;
  try { saveProducts(); } catch (Throwable t) { DIRTY = true; @PKG@.BzUtil.warn("could not save products.properties: " + t); }
}"""), cat_))
# /bazaaradmin price: memory first (a processed good becomes FIXED); the command then reprices (goods made from it follow) and save()s
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean setBase(String id, double base) {
  @PKG@.Product p = get(id);
  if (p == null || !(base >= 0.01 && base <= 1000000000.0)) return false;
  p.base = base;
  init();
  if (PROC_BY.containsKey(id)) AUTO.remove(id);
  DIRTY = true;
  return true;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean setAuto(String id) {
  init();
  if (get(id) == null || !PROC_BY.containsKey(id)) return false;
  AUTO.add(id);
  DIRTY = true;
  return true;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String save() {
  try {
    DIRTY = false;
    saveProducts();
    writeModes(MIGRATED);
    return null;
  } catch (Throwable t) { DIRTY = true; return String.valueOf(t); }
}"""), cat_))
# ================= Market (factors, pricing, decay, persistence, trade log queue) =================
mkt.addField(CtField.make("public static java.nio.file.Path FILE;", mkt))
mkt.addField(CtField.make("public static java.nio.file.Path LOGFILE;", mkt))
mkt.addField(CtField.make("public static volatile double SPREAD = %s;" % SPREAD, mkt))
mkt.addField(CtField.make("public static volatile double IMPACT = %r;" % IMPACT_DEF, mkt))   # 0.1.15: 10000 x SCALE_X
mkt.addField(CtField.make("public static volatile double HALFLIFE = 120.0;", mkt))
mkt.addField(CtField.make("public static final double MINF = 0.25;", mkt))
mkt.addField(CtField.make("public static final double MAXF = 4.0;", mkt))
mkt.addField(CtField.make("public static long LAST = 0L;", mkt))
mkt.addField(CtField.make("public static boolean DIRTY = false;", mkt))
# 0.1.8 B: PEND = decay moved a factor or lastDecayMillis since the last write (persisted at most every 5 min: decay is reproducible from
# the saved factors + lastDecayMillis); SAVED = when the last snapshot was taken (millis); CSV = the bazaar:products text last put;
# MOVED = how many ids the last decay published (harness / status)
mkt.addField(CtField.make("public static boolean PEND = false;", mkt))
mkt.addField(CtField.make("public static long SAVED = 0L;", mkt))
mkt.addField(CtField.make("public static final long PEND_MS = 300000L;", mkt))
mkt.addField(CtField.make("public static String CSV = null;", mkt))
mkt.addField(CtField.make("public static int MOVED = 0;", mkt))
mkt.addField(CtField.make("public static final java.util.HashMap F = new java.util.HashMap();", mkt))
mkt.addField(CtField.make("public static final java.util.HashMap BOUGHT = new java.util.HashMap();", mkt))
mkt.addField(CtField.make("public static final java.util.HashMap SOLD = new java.util.HashMap();", mkt))
mkt.addField(CtField.make("public static final java.util.concurrent.ConcurrentLinkedQueue LOGQ = new java.util.concurrent.ConcurrentLinkedQueue();", mkt))
mkt.addMethod(CtNewMethod.make("""
public static double clampF(double f) {
  if (!(f == f)) return 1.0;
  if (f < MINF) return MINF;
  if (f > MAXF) return MAXF;
  return f;
}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static synchronized double factor(String id) {
  Double d = (Double) F.get(id);
  return d == null ? 1.0 : d.doubleValue();
}""", mkt))
# lifetime counters - F / BOUGHT / SOLD are plain HashMaps, so every read goes through the Market.class lock like the writes
mkt.addMethod(CtNewMethod.make("""
public static synchronized long getBought(String id) {
  Long v = (Long) BOUGHT.get(id);
  return v == null ? 0L : v.longValue();
}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static synchronized long getSold(String id) {
  Long v = (Long) SOLD.get(id);
  return v == null ? 0L : v.longValue();
}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static double step({PKG}.Product p) {{
  double s = Math.exp(Math.log(1.10) * p.base / IMPACT);
  if (!(s >= 1.0)) s = 1.0;
  if (s > 4.0) s = 4.0;
  // 0.1.14: never a step one buy + one sell back can profit from: under (1 + spread) / (1 - spread) (1.2 at the 10 % spread)
  double mx = 1.0 + 0.9 * ((1.0 + SPREAD) / (1.0 - SPREAD) - 1.0);
  if (s > mx) s = mx;
  return s;
}}""", mkt))
# total whole-coin price of qty units walked unit by unit from the current factor; -1 = cannot price
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized long quote(String id, int qty, boolean buy) {{
  {PKG}.Product p = {PKG}.Catalog.get(id);
  if (p == null || qty <= 0 || qty > 1000000) return -1L;
  double f = factor(id);
  double st = step(p);
  double mult = buy ? 1.0 + SPREAD : 1.0 - SPREAD;
  double pb = buy ? p.base : {PKG}.Catalog.sellBase(p);     // 0.1.14: the sell cap (Eternal seeds: their crafting value)
  double fb = buy ? {PKG}.Catalog.buyFloor(id, SPREAD) : {PKG}.Catalog.floorBase(id, SPREAD);   // 0.1.14: the minimum sell price (0 = none)
  double total = 0.0;
  for (int i = 0; i < qty; i++) {{
    double v = pb * f;
    if (v < fb) v = fb;
    total += v * mult;
    f = clampF(buy ? f * st : f / st);
  }}
  if (!(total >= 0.0) || total > 1.0E15) return -1L;
  return buy ? (long) Math.ceil(total - 1.0E-7) : (long) Math.floor(total + 1.0E-7);
}}""", mkt))
# 0.1.2: the most units a purse can pay for right now (cap = room / per-trade limit). Display + validation only - quote() is untouched.
# ONE walk with quote()'s exact arithmetic (same factor, step, spread, the same additions in the same order, the same rounding and
# 1e15 limit), so the running total after k units is bit-identical to quote(id, k, true); the total only ever rises (every unit adds
# base * factor * (1 + spread) > 0), so the first unit the purse cannot cover ends the walk. Work = min(answer + 1, cap) steps on the
# world thread (a binary search over quote() was about 2-3x cap per render, up to ~300k steps at the 100000 per-trade limit).
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized int maxBuyable(String id, long purse, int cap) {{
  {PKG}.Product p = {PKG}.Catalog.get(id);
  if (p == null || purse <= 0L || cap <= 0) return 0;
  if (cap > 1000000) cap = 1000000;
  double f = factor(id);
  double st = step(p);
  double mult = 1.0 + SPREAD;
  double fb = {PKG}.Catalog.buyFloor(id, SPREAD);            // 0.1.14: quote()'s exact arithmetic (+ the floor)
  double total = 0.0;
  int best = 0;
  for (int i = 0; i < cap; i++) {{
    double v = p.base * f;
    if (v < fb) v = fb;
    total += v * mult;
    f = clampF(f * st);
    if (!(total >= 0.0) || total > 1.0E15) break;
    long c = (long) Math.ceil(total - 1.0E-7);
    if (c > purse) break;
    best = i + 1;
  }}
  return best;
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized double unit(String id, boolean buy) {{
  {PKG}.Product p = {PKG}.Catalog.get(id);
  if (p == null) return 0.0;
  double v = (buy ? p.base : {PKG}.Catalog.sellBase(p)) * factor(id);   // 0.1.14: cap + floor, as quote()
  double fb = buy ? {PKG}.Catalog.buyFloor(id, SPREAD) : {PKG}.Catalog.floorBase(id, SPREAD);
  if (v < fb) v = fb;
  return v * (buy ? 1.0 + SPREAD : 1.0 - SPREAD);
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void publish(String id) {{
  java.util.Map b = {PKG}.BzUtil.bridge();
  long s = quote(id, 1, false);
  long bu = quote(id, 1, true);
  if (s >= 0L) b.put("bazaar:sell:" + id, Long.valueOf(s)); else b.remove("bazaar:sell:" + id);
  if (bu >= 0L) b.put("bazaar:buy:" + id, Long.valueOf(bu)); else b.remove("bazaar:buy:" + id);
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void publishAll() {{
  java.util.ArrayList all = {PKG}.Catalog.all();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < all.size(); i++) {{
    String id = (({PKG}.Product) all.get(i)).id;
    publish(id);
    if (sb.length() > 0) sb.append(',');
    sb.append(id);
  }}
  String csv = sb.toString();
  java.util.Map b = {PKG}.BzUtil.bridge();
  if (!csv.equals(CSV) || !csv.equals(b.get("bazaar:products"))) {{ b.put("bazaar:products", csv); CSV = csv; }}
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void unpublishAll() {{
  java.util.Map b = {PKG}.BzUtil.bridge();
  java.util.ArrayList all = {PKG}.Catalog.all();
  for (int i = 0; i < all.size(); i++) {{
    String id = (({PKG}.Product) all.get(i)).id;
    b.remove("bazaar:sell:" + id); b.remove("bazaar:buy:" + id);
  }}
  b.remove("bazaar:products");
  CSV = null;
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void apply(String id, int qty, boolean buy) {{
  {PKG}.Product p = {PKG}.Catalog.get(id);
  if (p == null || qty <= 0) return;
  double f = factor(id);
  double st = step(p);
  for (int i = 0; i < qty; i++) f = clampF(buy ? f * st : f / st);
  F.put(id, Double.valueOf(f));
  java.util.HashMap m = buy ? BOUGHT : SOLD;
  Long old = (Long) m.get(id);
  m.put(id, Long.valueOf((old == null ? 0L : old.longValue()) + (long) qty));
  DIRTY = true;
  publish(id);
}}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static synchronized void reset(String id) {
  if (id == null) F.clear(); else F.remove(id);
  DIRTY = true;
  publishAll();
}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static synchronized void decay(long now) {
  if (LAST <= 0L) { LAST = now; DIRTY = true; return; }
  long dt = now - LAST;
  if (dt < 1000L) return;
  if (dt > 604800000L) dt = 604800000L;
  double k = Math.pow(0.5, (double) dt / (HALFLIFE * 60000.0));
  java.util.ArrayList moved = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(F.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    double f = ((Double) F.get(id)).doubleValue();
    double nf = clampF(Math.exp(Math.log(f) * k));
    if (Math.abs(nf - 1.0) < 0.0001) { F.remove(id); moved.add(id); }
    else if (nf != f) { F.put(id, Double.valueOf(nf)); moved.add(id); }
  }
  LAST = now;
  PEND = true;
  if (now - SAVED >= PEND_MS) DIRTY = true;
  for (int i = 0; i < moved.size(); i++) publish((String) moved.get(i));
  MOVED = moved.size();
}
""", mkt))
# 0.1.8 B: shutdown writes a pending decay too (the next start would recompute it anyway - this keeps the file current)
mkt.addMethod(CtNewMethod.make("""
public static synchronized void forcePending() {
  if (PEND) DIRTY = true;
}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  try {{
    java.util.Properties p = new java.util.Properties();
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
    }}
    double sp = 0.10, im = {IMPACT_DEF!r}, hl = 120.0;   // 0.1.15: the impactCoins default x SCALE
    try {{ sp = Double.parseDouble(p.getProperty("spread", "0.10").trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad spread"); }}
    try {{ im = Double.parseDouble(p.getProperty("impactCoins", "{IMPACT_DEF!r}").trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad impactCoins"); }}
    try {{ hl = Double.parseDouble(p.getProperty("halfLifeMinutes", "120").trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad halfLifeMinutes"); }}
    if (!(sp >= 0.01)) sp = 0.01;
    if (sp > 0.45) sp = 0.45;
    if (!(im >= 100.0)) im = 100.0;
    if (im > 1.0E12) im = 1.0E12;
    if (!(hl >= 1.0)) hl = 1.0;
    if (hl > 1000000.0) hl = 1000000.0;
    SPREAD = sp; IMPACT = im; HALFLIFE = hl;
    long last = 0L;
    try {{ last = Long.parseLong(p.getProperty("lastDecayMillis", "0").trim()); }} catch (Throwable t) {{ last = 0L; }}
    LAST = last;
    PEND = false;
    F.clear(); BOUGHT.clear(); SOLD.clear();
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = (String) en.nextElement();
      try {{
        if (k.startsWith("f.")) F.put(k.substring(2), Double.valueOf(clampF(Double.parseDouble(p.getProperty(k).trim()))));
        else if (k.startsWith("bought.")) BOUGHT.put(k.substring(7), Long.valueOf(Long.parseLong(p.getProperty(k).trim())));
        else if (k.startsWith("sold.")) SOLD.put(k.substring(5), Long.valueOf(Long.parseLong(p.getProperty(k).trim())));
      }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad value for " + k); }}
    }}
    DIRTY = true;
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("could not load market: " + t); }}
}}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties snapshot() {
  if (!DIRTY) return null;
  DIRTY = false;
  PEND = false;
  SAVED = System.currentTimeMillis();
  java.util.Properties p = new java.util.Properties();
  p.setProperty("spread", String.valueOf(SPREAD));
  p.setProperty("impactCoins", String.valueOf(IMPACT));
  p.setProperty("halfLifeMinutes", String.valueOf(HALFLIFE));
  p.setProperty("lastDecayMillis", String.valueOf(LAST));
  java.util.Iterator it = F.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty("f." + e.getKey(), String.valueOf(((Double) e.getValue()).doubleValue())); }
  it = BOUGHT.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty("bought." + e.getKey(), String.valueOf(((Long) e.getValue()).longValue())); }
  it = SOLD.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty("sold." + e.getKey(), String.valueOf(((Long) e.getValue()).longValue())); }
  return p;
}""", mkt))
mkt.addMethod(CtNewMethod.make("""
public static void log(String line) {
  LOGQ.add(java.time.Instant.now().toString() + " " + line);
}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static void flushLog() {{
  synchronized (LOGQ) {{
    if (LOGQ.isEmpty()) return;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 1000000; i++) {{
      Object o = LOGQ.poll();
      if (o == null) break;
      sb.append((String) o).append('\\n');
    }}
    try {{
      java.nio.file.Files.createDirectories(LOGFILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(LOGFILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8),
        new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND }});
    }} catch (Throwable t) {{ {PKG}.BzUtil.warn("could not append trades.log (" + sb.length() + " chars lost): " + t); }}
  }}
}}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static void flush() {{
  synchronized (LOGQ) {{
    java.util.Properties p = snapshot();
    if (p != null) {{
      try {{
        java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
        java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
        java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
        try {{ p.store(out, "SkyyBazaar market - spread, impactCoins (coins of base value per 10 pct move), halfLifeMinutes; f.<id> demand factor"); }} finally {{ out.close(); }}
        java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
      }} catch (Throwable t) {{ {PKG}.BzUtil.warn("could not save market: " + t); synchronized ({PKG}.Market.class) {{ DIRTY = true; }} }}
    }}
    flushLog();
  }}
}}""", mkt))

# ================= 0.1.3 BzCfg (the premium) + Catalog.reprice under the Market lock (after Market: they read SPREAD / publish) =================
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static int clampPct(int v) {
  if (v < MIN) return MIN;
  if (v > MAX) return MAX;
  return v;
}"""), cfgc))
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static void load(java.nio.file.Path dir) {
  FILE = dir.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      String txt = DEFAULT_TEXT.replace("\n", System.lineSeparator());
      java.nio.file.Files.write(FILE, txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    String v = p.getProperty("processed.premium");
    if (v != null) {
      String t = v.trim();
      if (t.endsWith("%")) t = t.substring(0, t.length() - 1).trim();
      try { PREMIUM = clampPct(Integer.parseInt(t)); }
      catch (Throwable x) { @PKG@.BzUtil.warn("config.properties: processed.premium must be a whole number " + MIN + "-" + MAX + " - using " + PREMIUM); }
    }
    // 0.1.14: the minimum instant sell price + new players' confirm amount (a missing line keeps the default)
    String ms = p.getProperty("market.minSell");
    if (ms != null) {
      try { int v2 = Integer.parseInt(ms.trim()); MINSELL = v2 < MINSELL_MIN ? MINSELL_MIN : (v2 > MINSELL_MAX ? MINSELL_MAX : v2); }
      catch (Throwable x) { @PKG@.BzUtil.warn("config.properties: market.minSell must be a whole number " + MINSELL_MIN + "-" + MINSELL_MAX + " - using " + MINSELL); }
    }
    String cd = p.getProperty("confirm.default");
    if (cd != null) {
      try { int v3 = Integer.parseInt(cd.trim()); CONFIRM = v3 < 0 ? 0 : (v3 > 1000000000 ? 1000000000 : v3); }
      catch (Throwable x) { @PKG@.BzUtil.warn("config.properties: confirm.default must be a whole number of coins - using " + CONFIRM); }
    }
  } catch (Throwable t) { @PKG@.BzUtil.warn("could not read config.properties (" + t + ") - processed goods premium " + PREMIUM + "%"); }
}"""), cfgc))
# the highest premium that can never let buy inputs -> process -> sell pay at factor 1.0 with the spread in force: (1 + p)(1 - s) <= 1 + s
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static double maxSafe() {
  double s = @PKG@.Market.SPREAD;
  if (!(s > 0.0) || s >= 1.0) return 0.0;
  return (1.0 + s) / (1.0 - s) - 1.0 - 1.0E-6;
}"""), cfgc))
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static double effective() {
  double p = (double) clampPct(PREMIUM) / 100.0;
  double m = maxSafe();
  if (p > m) p = m;
  if (p < 0.0) p = 0.0;
  return p;
}"""), cfgc))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int repriceLocked(double pe, int pct) {
  synchronized (@PKG@.Market.class) { return reprice0(pe, pct, @PKG@.Market.SPREAD); }
}"""), cat_))
# lock order Market -> Catalog everywhere (trades: Market.quote -> Catalog.get); publishAll only when a price moved
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int reprice() {
  int moved = repriceLocked(@PKG@.BzCfg.effective(), @PKG@.BzCfg.PREMIUM);
  if (moved > 0) @PKG@.Market.publishAll();
  return moved;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static void tick() {
  if (@PKG@.BzCfg.PREMIUM != PCT || Math.abs(@PKG@.BzCfg.effective() - PREM) > 1.0E-12) reprice();
  // 0.1.14: a minimum sell price changed by a hand edit + reload (the in-game change runs BzCfg.floorChanged) republishes every price
  if (@PKG@.BzCfg.MINSELL != FLOORPUB) { FLOORPUB = @PKG@.BzCfg.MINSELL; @PKG@.Market.publishAll(); }
  flushIfDirty();
}"""), cat_))
# the highest FIXED price of a processed good that cannot let buy inputs -> process -> sell pay at factor 1.0 (-1 = unknown)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static double loopCap(String id) {
  Object[] e = procEntry(id);
  if (e == null) return -1.0;
  double v = valueOf(e);
  if (v <= 0.0) return -1.0;
  double s = @PKG@.Market.SPREAD;
  if (!(s > 0.0) || s >= 1.0) return -1.0;
  return Math.floor(v * (1.0 + s) / (1.0 - s) * 100.0) / 100.0;
}"""), cat_))
# the detail panel's processed-goods line (+ the other tabs a two-tab product is listed in)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String procLine(@PKG@.Product p) {
  if (p == null) return "";
  String out = "";
  Object[] e = procEntry(p.id);
  if (e != null) {
    if (!isAuto(p.id)) out = "Processed - a fixed price set by the server";
    else {
      String bench = (String) e[3];
      String what = bench.equals("Tannery") ? "tanning it yourself" : (bench.equals("Furnace fuel") ? "burning fuel for it yourself"
                    : (bench.equals("Furnace") ? "smelting it yourself" : (bench.equals("SkyyAlloy") ? "alloying it yourself" : bench + " it yourself")));
      String ins = "its raw inputs";
      double[] q = (double[]) e[4];
      Object[] cand = (Object[]) e[5];
      double oq = ((Double) e[1]).doubleValue();
      if (q.length == 1 && ((String[]) cand[0]).length == 1) {
        @PKG@.Product ip = get(((String[]) cand[0])[0]);
        // an input that is itself processed (Dawnstone from Quartzite): the premium is over ITS raw inputs, so say that
        if (ip != null && !isProc(ip.id)) ins = (q[0] == 1.0 ? "the " : ((long) q[0]) + " ") + ip.name + (oq > 1.0 ? " (" + ((long) q[0]) + " makes " + ((long) oq) + ")" : "");
      } else if (bench.equals("Furnace fuel")) ins = ((long) q[0]) + " fuel items";
      long pct = Math.round(@PKG@.BzCfg.effective() * 100.0);
      out = "Processed - costs " + pct + "% more than buying " + ins + " and " + what;
    }
  }
  init();
  Double sc = (Double) SCAP.get(p.id);   // 0.1.14: the sell cap
  if (sc != null && sc.doubleValue() < p.base) out = out + (out.length() > 0 ? "   -   " : "") + "Sells for its crafting value (" + @PKG@.BzUtil.num(sc.doubleValue()) + " each at demand 1.0) - a recipe makes it for less";
  java.util.ArrayList t = tabsOf(p);
  if (t.size() > 1) {
    String also = "";
    for (int i = 1; i < t.size(); i++) also = also + (also.length() > 0 ? " and " : "") + t.get(i);
    out = out + (out.length() > 0 ? "   -   " : "") + "listed in the " + t.get(0) + " and " + also + " tabs";
  }
  return out;
}"""), cat_))
# ---- fix round: the /bazaaradmin price GUARD (the build's edge_loops in Java). An edge pays when its listed outputs sell for more than
# its inputs cost: inputs at the cheapest listed candidate x (1 + spread), + fuel seconds x the cheapest fuel per second bought at
# (1 + spread) net of the charcoal it gives back sold at (1 - spread) (never below 0); outputs at base x (1 - spread). One step, at
# demand 1.0 (the build's full check covers chains at the default prices; demand drift is market arbitrage that corrects itself).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized double edgeFuel(double sp) {
  double best = 0.0;
  boolean any = false;
  @PKG@.Product ch = (@PKG@.Product) BY_ID.get(CHARCOAL);
  for (int i = 0; i < FUEL.size(); i++) {
    Object[] f = (Object[]) FUEL.get(i);
    @PKG@.Product fp = (@PKG@.Product) BY_ID.get((String) f[0]);
    if (fp == null) continue;
    double sh = ((Double) f[2]).doubleValue();
    double back = (sh > 0.0 && ch != null) ? sh * sellVal(ch, sp) * (1.0 - sp) : 0.0;   // 0.1.14: caps + floor
    double c = (buyVal(fp, sp) * (1.0 + sp) - back) / ((Double) f[1]).doubleValue();
    if (!any || c < best) { best = c; any = true; }
  }
  return (any && best > 0.0) ? best : 0.0;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized java.util.HashSet loopingEdges(double sp) {
  init();
  java.util.HashSet out = new java.util.HashSet();
  double fs = edgeFuel(sp);
  for (int k = 0; k < EDGE.size(); k++) {
    Object[] e = (Object[]) EDGE.get(k);
    double cost = ((Double) e[0]).doubleValue() * fs;
    double[] qi = (double[]) e[1];
    Object[] ci = (Object[]) e[2];
    boolean ok = true;
    for (int i = 0; i < qi.length && ok; i++) {
      String[] cs = (String[]) ci[i];
      double best = -1.0;
      for (int j = 0; j < cs.length; j++) {
        @PKG@.Product p = (@PKG@.Product) BY_ID.get(cs[j]);
        if (p == null) continue;
        double bv = buyVal(p, sp);   // 0.1.14: + the floor
        if (best < 0.0 || bv < best) best = bv;
      }
      if (best < 0.0) ok = false;
      else cost += qi[i] * best * (1.0 + sp);
    }
    if (!ok) continue;
    double[] qo = (double[]) e[3];
    String[] os = (String[]) e[4];
    double val = 0.0;
    for (int i = 0; i < qo.length; i++) {
      @PKG@.Product p = (@PKG@.Product) BY_ID.get(os[i]);
      if (p != null) val += qo[i] * sellVal(p, sp) * (1.0 - sp);   // 0.1.14: caps + floor
    }
    if (val > cost + 1.0E-9) out.add(Integer.valueOf(k));
  }
  return out;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String qty(double q) {
  if (q == Math.floor(q) && Math.abs(q) < 1.0E15) return String.valueOf((long) q);
  return @PKG@.BzUtil.num(q);
}"""), cat_))
# "2 Quartzite Cobble -> 1 Quartzite" (an input shows its cheapest listed candidate)
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String edgeText(int k) {
  if (k < 0 || k >= EDGE.size()) return "a recipe";
  Object[] e = (Object[]) EDGE.get(k);
  double[] qi = (double[]) e[1];
  Object[] ci = (Object[]) e[2];
  double[] qo = (double[]) e[3];
  String[] os = (String[]) e[4];
  String s = "";
  for (int i = 0; i < qi.length; i++) {
    String[] cs = (String[]) ci[i];
    String nm = cs.length > 0 ? cs[0] : "?";
    double best = -1.0;
    for (int j = 0; j < cs.length; j++) {
      @PKG@.Product p = (@PKG@.Product) BY_ID.get(cs[j]);
      if (p != null && (best < 0.0 || p.base < best)) { best = p.base; nm = p.name; }
    }
    s = s + (i > 0 ? " + " : "") + qty(qi[i]) + " " + nm;
  }
  s = s + " -> ";
  for (int i = 0; i < qo.length; i++) {
    @PKG@.Product p = (@PKG@.Product) BY_ID.get(os[i]);
    s = s + (i > 0 ? " + " : "") + qty(qo[i]) + " " + (p == null ? os[i] : p.name);
  }
  return s;
}"""), cat_))
# start + /bazaaradmin reload: one warning per recipe that pays at the prices on disk (a hand edit) - nothing is changed
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized int warnLoops(double sp) {
  java.util.HashSet l = loopingEdges(sp);
  int n = 0;
  for (int k = 0; k < EDGE.size(); k++) {
    if (!l.contains(Integer.valueOf(k))) continue;
    n++;
    if (WARNED.add("edge:" + k)) @PKG@.BzUtil.warn("at the prices in products.properties " + edgeText(k) + " makes coins (buy the inputs, craft or process, sell) - change those prices together");
  }
  return n;
}"""), cat_))
# set one price (or auto) and reprice; when that makes a recipe edge pay that did not pay before, put the old price + mode back,
# reprice again and return why (null = done). Called under the Market lock (setGuarded), so no trade sees the refused price.
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String setGuarded0(String id, double v, boolean auto, double sp, double pe, int pct) {
  @PKG@.Product p = get(id);
  if (p == null) return id + " is not a bazaar product";
  java.util.HashSet before = loopingEdges(sp);
  double old = p.base;
  boolean wasAuto = AUTO.contains(id);
  boolean ok = auto ? setAuto(id) : setBase(id, v);
  if (!ok) return auto ? ("only processed goods can follow their inputs") : ("base must be 0.01 .. 1000000000");
  GUARD_MOVED = reprice0(pe, pct, sp);
  java.util.HashSet after = loopingEdges(sp);
  int bad = -1;
  for (int k = 0; k < EDGE.size() && bad < 0; k++) {
    Integer key = Integer.valueOf(k);
    if (after.contains(key) && !before.contains(key)) bad = k;
  }
  if (bad < 0) return null;
  p.base = old;
  if (wasAuto) AUTO.add(id); else AUTO.remove(id);
  reprice0(pe, pct, sp);
  GUARD_MOVED = 0;
  return "at that price " + edgeText(bad) + " would make coins (buy the inputs, craft or process, sell) - change the prices of that recipe's inputs and outputs together";
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String setGuarded(String id, double v, boolean auto) {
  synchronized (@PKG@.Market.class) { return setGuarded0(id, v, auto, @PKG@.Market.SPREAD, @PKG@.BzCfg.effective(), @PKG@.BzCfg.PREMIUM); }
}"""), cat_))
# 0.1.14: the minimum sell price moved (in game): every published price follows now; recipes that would pay are warned about
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static void floorChanged(String key) {
  try { @PKG@.Catalog.FLOORPUB = MINSELL; @PKG@.Market.publishAll(); @PKG@.Catalog.warnLoops(@PKG@.Market.SPREAD); }
  catch (Throwable t) { @PKG@.BzUtil.warn("republishing prices after " + key + " failed: " + t); }
}"""), cfgc))
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static void changed(String key) {
  try { @PKG@.Catalog.reprice(); } catch (Throwable t) { @PKG@.BzUtil.warn("processed goods reprice after " + key + " failed: " + t); }
}"""), cfgc))

# ================= Inv (count-verified inventory moves; world thread only) =================
# 0.1.7 THE MARKET WALL (tools/bazaar_0_1_7_patch.py): market:veto = owner -> Function(ItemStack) -> null or a reason (the Auction House's
# contract; SkyyGear 0.2.14 walls Mythic / Untiered / Set gear). The first reason wins; a veto that throws refuses; no map = nothing walled.
inv_.addMethod(CtNewMethod.make(f"""
public static String veto({IS} s) {{
  if (s == null || s.isEmpty()) return null;
  Object o = null;
  try {{ o = {PKG}.BzUtil.bridge().get("market:veto"); }} catch (Throwable t) {{ o = null; }}
  if (!(o instanceof java.util.Map)) return null;
  java.util.Iterator it = new java.util.ArrayList(((java.util.Map) o).values()).iterator();
  while (it.hasNext()) {{
    Object f = it.next();
    if (!(f instanceof java.util.function.Function)) continue;
    try {{
      Object r = ((java.util.function.Function) f).apply(s);
      if (r != null) return String.valueOf(r);
    }} catch (Throwable t) {{ return "could not check this item"; }}
  }}
  return null;
}}""", inv_))
# a stack WITH metadata that a veto refuses (plain stacks are never asked: ordinary materials cost nothing)
inv_.addMethod(CtNewMethod.make(f"""
public static boolean walled({IS} it) {{
  return it != null && !it.isEmpty() && it.getMetadata() != null && veto(it) != null;
}}""", inv_))
# a product whose PLAIN stack is walled (an Untiered-table id) - null = fine
inv_.addMethod(CtNewMethod.make(f"""
public static String wallId(String id) {{
  if (id == null) return null;
  try {{ return veto(new {IS}(id, 1)); }} catch (Throwable t) {{ return null; }}
}}""", inv_))
inv_.addMethod(CtNewMethod.make(f"""
public static int countIn({IC} c, String id) {{
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || walled(it)) continue;
    n += it.getQuantity();
  }}
  return n;
}}""", inv_))
inv_.addMethod(CtNewMethod.make(f"""
public static {IC}[] conts({PLA} p) {{
  {INV} inv = p == null ? null : p.getInventory();
  if (inv == null) return new {IC}[0];
  return new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
}}""", inv_))
inv_.addMethod(CtNewMethod.make(f"""
public static int count({PLA} p, String id) {{
  {IC}[] cs = conts(p);
  int n = 0;
  for (int i = 0; i < cs.length; i++) n += countIn(cs[i], id);
  return n;
}}""", inv_))
# adds up to qty; every add is measured by re-counting the container, so it can never hand out more than qty
inv_.addMethod(CtNewMethod.make(f"""
public static int give({PLA} p, String id, int qty) {{
  if (qty <= 0) return 0;
  {IC}[] cs = conts(p);
  int given = 0;
  for (int c = 0; c < cs.length && given < qty; c++) {{
    {IC} cont = cs[c];
    if (cont == null) continue;
    for (int guard = 0; guard < 64 && given < qty; guard++) {{
      int want = qty - given;
      int before = countIn(cont, id);
      try {{ cont.addItemStack(new {IS}(id, want)); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("addItemStack " + id + " failed: " + t); break; }}
      int got = countIn(cont, id) - before;
      if (got <= 0) break;
      if (got > want) {{ {PKG}.BzUtil.warn("container took more " + id + " than asked (" + got + " > " + want + ")"); got = want; }}
      given += got;
    }}
  }}
  return given;
}}""", inv_))
# removes up to n slot by slot; each slot re-read after the removal; returns what was removed
inv_.addMethod(CtNewMethod.make(f"""
public static int take({PLA} p, String id, int n) {{
  if (n <= 0) return 0;
  {IC}[] cs = conts(p);
  int taken = 0;
  for (int c = 0; c < cs.length && taken < n; c++) {{
    {IC} cont = cs[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap && taken < n; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || walled(it)) continue;
      int q = it.getQuantity();
      int want = q < n - taken ? q : n - taken;
      if (want <= 0) continue;
      try {{ cont.removeItemStackFromSlot(s, want); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("removeItemStackFromSlot failed: " + t); continue; }}
      {IS} after = cont.getItemStack(s);
      int left = (after == null || after.isEmpty() || !id.equals(after.getItemId())) ? 0 : after.getQuantity();
      if (q - left > 0) taken += q - left;
    }}
  }}
  return taken;
}}""", inv_))

# ================= Bags (0.1.5): SkyySacks 0.7.13's bag bridge - sell from the Magic Bags the player carries =================
# sacks:fn:count {UUID, id} -> Long (-1 paused), sacks:fn:all UUID -> Map id -> Long (null paused), sacks:fn:take {UUID, id, Long} -> Long
# removed, sacks:fn:put {UUID, id, Long} -> Long returned (only what a take removed). World thread only (the page click thread). No SkyySacks /
# one older than 0.7.13 (no sacks:fn:take) = no bags: every count 0, every take 0 - 0.1.4 behaviour.
bags.addField(CtField.make("public static final int CAP = 1000000000;", bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static boolean on() {
  try {
    java.util.Map b = @PKG@.BzUtil.bridge();
    return (b.get("sacks:fn:take") instanceof java.util.function.Function) && (b.get("sacks:fn:count") instanceof java.util.function.Function);
  } catch (Throwable t) { return false; }
}"""), bags))
# one bridge call -> its Long answer; -2 = absent / failed / not a number
bags.addMethod(CtNewMethod.make(jt(r"""
public static long call(String key, Object arg) {
  try {
    Object f = @PKG@.BzUtil.bridge().get(key);
    if (!(f instanceof java.util.function.Function)) return -2L;
    Object r = ((java.util.function.Function) f).apply(arg);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.BzUtil.warn("bag bridge " + key + " failed: " + t); }
  return -2L;
}"""), bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static int count(java.util.UUID u, String id) {
  if (u == null || id == null || !on()) return 0;
  long r = call("sacks:fn:count", new Object[] { u, id });
  if (r <= 0L) return 0;
  return r > (long) CAP ? CAP : (int) r;
}"""), bags))
# every item the player can take from the bags now: an empty map when there are no bags (or they are paused); null only when SkyySacks
# has count + take but no sacks:fn:all - then held() asks count per item
bags.addMethod(CtNewMethod.make(jt(r"""
public static java.util.HashMap all(java.util.UUID u) {
  java.util.HashMap out = new java.util.HashMap();
  if (u == null || !on()) return out;
  try {
    Object f = @PKG@.BzUtil.bridge().get("sacks:fn:all");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof java.util.Map)) return out;
    java.util.Iterator it = ((java.util.Map) r).entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getKey() instanceof String) || !(e.getValue() instanceof Number)) continue;
      long v = ((Number) e.getValue()).longValue();
      if (v > 0L) out.put(e.getKey(), Long.valueOf(v > (long) CAP ? (long) CAP : v));
    }
  } catch (Throwable t) { @PKG@.BzUtil.warn("bag bridge sacks:fn:all failed: " + t); }
  return out;
}"""), bags))
bags.addMethod(CtNewMethod.make(jt(r"""
public static int held(java.util.HashMap m, java.util.UUID u, String id) {
  if (m == null) return count(u, id);
  Long v = (Long) m.get(id);
  return v == null ? 0 : (int) v.longValue();
}"""), bags))
# take up to n out of the bags; the answer is what really left the pool (only that may be paid for)
bags.addMethod(CtNewMethod.make(jt(r"""
public static int take(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0 || !on()) return 0;
  long r = call("sacks:fn:take", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  if (r > (long) n) @PKG@.BzUtil.warn("SkyySacks removed " + r + " " + id + " when " + n + " were asked - paying for what left the bags");
  return r > (long) CAP ? CAP : (int) r;
}"""), bags))
# review fix: the sale PAID for n of its take - they leave SkyySacks' refund ledger (a later put can never return them); 0 when absent
bags.addMethod(CtNewMethod.make(jt(r"""
public static int commit(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = call("sacks:fn:commit", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}"""), bags))
# the refund path: put back up to n (SkyySacks only returns what a take removed); the caller gives the rest to the inventory
bags.addMethod(CtNewMethod.make(jt(r"""
public static int put(java.util.UUID u, String id, int n) {
  if (u == null || id == null || n <= 0) return 0;
  long r = call("sacks:fn:put", new Object[] { u, id, Long.valueOf((long) n) });
  if (r <= 0L) return 0;
  return r > (long) n ? n : (int) r;
}"""), bags))

# ================= TradeResult =================
res.addField(CtField.make("public boolean ok;", res))
res.addField(CtField.make("public int qty;", res))
res.addField(CtField.make("public long coins;", res))
res.addField(CtField.make("public String msg;", res))
# alert = the player may be owed coins or items (refund / pay / give-back failed): the page also sends msg to chat
res.addField(CtField.make("public boolean alert;", res))
# 0.1.2: moved = a custom trade was refused because the price changed since the player saw it; price = the new total (re-armed)
res.addField(CtField.make("public boolean moved;", res))
res.addField(CtField.make("public long price;", res))
# 0.1.5: how many of the sold items came out of the bags (Sell inventory sums it for its line)
res.addField(CtField.make("public int fromBags;", res))
res.addConstructor(CtNewConstructor.make("""
public TradeResult(boolean ok, int qty, long coins, String msg) {
  this.ok = ok; this.qty = qty; this.coins = coins; this.msg = msg;
}""", res))

# ================= Trader (atomic trades) =================
TR = PKG + ".TradeResult"
trd.addField(CtField.make("public static final int MAXQ = 100000;", trd))
# 0.1.2: SkyyProfiles crash recovery (tools/PROFILES-CONTRACT.md rule 5) - while profile:busy:<uuid> is present the live inventory may
# be replaced by a snapshot a moment later, so no trade may move items (a sale would pay coins AND get the items back).
trd.addMethod(CtNewMethod.make(f"""
public static boolean busy(java.util.UUID u) {{
  if (u == null) return false;
  try {{ return {PKG}.BzUtil.bridge().get("profile:busy:" + u) != null; }} catch (Throwable t) {{ return false; }}
}}""", trd))
# 0.1.2: how many units of id fit in storage + hotbar + backpack (the containers Inv.give fills): empty slot = max stack, partial stack
# of the same item = the rest of it. Max stack unknown -> MAXQ (no room limit; buy0 still refunds whatever does not fit).
trd.addMethod(CtNewMethod.make(f"""
public static int room({PLA} p, String id) {{
  if (p == null || id == null) return 0;
  int max = 0;
  try {{
    {ITM} it = ({ITM}) {ITM}.getAssetMap().getAsset(id);
    if (it != null) max = it.getMaxStack();
  }} catch (Throwable t) {{ max = 0; }}
  if (max <= 0) return MAXQ;
  {IC}[] cs = {PKG}.Inv.conts(p);
  long room = 0L;
  for (int c = 0; c < cs.length; c++) {{
    {IC} cont = cs[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short sl = 0; sl < cap; sl++) {{
      {IS} st = cont.getItemStack(sl);
      if (st == null || st.isEmpty()) room += (long) max;
      else if (id.equals(st.getItemId()) && st.getQuantity() < max) room += (long) (max - st.getQuantity());
    }}
  }}
  return room > (long) MAXQ ? MAXQ : (int) room;
}}""", trd))
# 0.1.5: Magic Bags are never traded (Skyy's lock: /trade + the AH block them; the Bazaar never lists them - this holds even if an admin
# adds a Skyy_Sack_* line to products.properties)
trd.addMethod(CtNewMethod.make("""
public static boolean locked(String id) {
  return id != null && id.startsWith("Skyy_Sack_");
}""", trd))
# 0.1.5 (Skyy: "use hytale stack numbers"): the item's real max stack - Item.getMaxStack after the engine's Parent inheritance and
# Item.processConfig (no MaxStack: tool / weapon / armor / builder tool 1, else 100); 0 / unknown -> 100 (the plain-item default)
trd.addField(CtField.make("public static final int DEF_STACK = 100;", trd))
trd.addMethod(CtNewMethod.make(f"""
public static int stack(String id) {{
  int max = 0;
  try {{
    {ITM} it = id == null ? null : ({ITM}) {ITM}.getAssetMap().getAsset(id);
    if (it != null) max = it.getMaxStack();
  }} catch (Throwable t) {{ max = 0; }}
  if (max <= 0) max = DEF_STACK;
  if (max > MAXQ) max = MAXQ;
  return max;
}}""", trd))
# 0.1.5: a cancelled sale returns its items: the bag part through sacks:fn:put first, whatever it does not take into the inventory
trd.addMethod(CtNewMethod.make(f"""
public static int giveBack({PLA} p, java.util.UUID u, String id, int inv, int bag) {{
  int back = 0;
  if (bag > 0) back = {PKG}.Bags.put(u, id, bag);
  if (bag - back > 0) {PKG}.Bags.commit(u, id, bag - back);   // review fix: the part the bags did not take back leaves the refund ledger
  int rest = inv + (bag - back);
  if (rest > 0) back += {PKG}.Inv.give(p, id, rest);
  return back;
}}""", trd))
# 0.1.19 (round coll24, Skyy 2026-10-16 "lets lock the eternal seeds with the collection"): SkyyCollections 0.2.24's coll:fn:eternal (KEY
# CONTRACT: apply(Object[]{ UUID, String itemId }) -> "" allowed / a non-empty reason = LOCKED / null = Collections still loading). Asked only
# for Plant_Seeds_<Crop>_Eternal, on every call (nothing cached across profiles). null here = allowed (no Function = no lock anywhere);
# else the player-facing reason the buy is refused for. A throwing Function refuses, with one WARN a minute.
trd.addField(CtField.make("public static volatile long ETER_WARN = 0L;", trd))
trd.addMethod(CtNewMethod.make(jt(r"""
public static String eterWhy(java.util.UUID u, String id) {
  if (id == null || !id.startsWith("Plant_Seeds_") || !id.endsWith("_Eternal")) return null;
  Object f = null;
  try { f = @PKG@.BzUtil.bridge().get("coll:fn:eternal"); } catch (Throwable t) { f = null; }
  if (f == null || !(f instanceof java.util.function.Function)) return null;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, id }); }
  catch (Throwable t) {
    long now = System.currentTimeMillis();
    if (now - ETER_WARN >= 60000L) { ETER_WARN = now; @PKG@.BzUtil.warn("coll:fn:eternal failed for " + id + " (" + t + ") - Eternal seed buys are refused while it fails (this warning at most once a minute)"); }
    return "the Collections unlock check failed - nothing bought, try again in a moment";
  }
  if (r == null) return "Collections are still loading - try again in a moment";
  if (!(r instanceof String)) return "the Collections unlock check gave no answer - nothing bought, try again in a moment";
  String s = (String) r;
  return s.length() == 0 ? null : s;
}"""), trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buy0({PLA} p, java.util.UUID u, String who, String id, int qty) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot take coins");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
  if (p == null || qty <= 0 || qty > MAXQ) return new {TR}(false, 0, 0L, "bad amount");
  if (locked(id)) return new {TR}(false, 0, 0L, "Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold");
  String wv = {PKG}.Inv.wallId(id);      // 0.1.7 the market wall
  if (wv != null) return new {TR}(false, 0, 0L, wv);
  String ew = eterWhy(u, id);            // 0.1.19: an Eternal seed bag its crop's collection has not unlocked (coll:fn:eternal)
  if (ew != null) return new {TR}(false, 0, 0L, ew);
  long cost = {PKG}.Market.quote(id, qty, true);
  if (cost <= 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  long purse = {PKG}.Coins.get(u);
  if (purse < 0L) return new {TR}(false, 0, 0L, "the coin bank did not answer - nothing bought, try again");
  if (purse < cost) return new {TR}(false, 0, 0L, "you need " + cost + " coins - you have " + purse);
  int before = {PKG}.Inv.count(p, id);
  int tk = {PKG}.Coins.take(u, cost);
  if (tk < 0) {{
    {PKG}.BzUtil.warn("TAKE ERROR: " + who + " " + u + " " + id + " x" + qty + " - coins:fn:take threw while taking " + cost + " coins, purse state unknown, nothing given");
    {PKG}.Market.log("TAKE-ERROR " + who + " " + u + " " + id + " " + qty + " " + cost);
    {TR} te = new {TR}(false, 0, 0L, "the coin bank failed while taking " + cost + " coins - nothing was bought. If your purse went down tell an admin - it is logged");
    te.alert = true;
    return te;
  }}
  if (tk == 0) return new {TR}(false, 0, 0L, "not enough coins");
  int reported = {PKG}.Inv.give(p, id, qty);
  int real = {PKG}.Inv.count(p, id) - before;
  if (real < 0) real = 0;
  if (real > qty) {{ {PKG}.BzUtil.warn("buy count mismatch for " + u + " " + id + ": got " + real + " asked " + qty); real = qty; }}
  if (real != reported) {PKG}.BzUtil.warn("buy " + id + ": give() said " + reported + " but the inventory shows " + real + " (using " + real + ")");
  long charged = cost;
  if (real < qty) {{
    charged = real == 0 ? 0L : {PKG}.Market.quote(id, real, true);
    if (charged < 0L) charged = cost * (long) real / (long) qty;
    if (charged > cost) charged = cost;
  }}
  long refund = cost - charged;
  if (real > 0) {PKG}.Market.apply(id, real, true);
  boolean refundOk = true;
  if (refund > 0L) {{
    int ad = {PKG}.Coins.add(u, refund);
    if (ad != 1) {{
      refundOk = false;
      {PKG}.BzUtil.warn("REFUND FAILED: " + who + " " + u + " is owed " + refund + " coins (" + id + ", coins:fn:add " + (ad < 0 ? "threw - it may or may not have paid" : "refused or missing") + ")");
      {PKG}.Market.log((ad < 0 ? "REFUND-ERROR " : "REFUND-FAILED ") + who + " " + u + " " + id + " owed " + refund);
    }}
  }}
  if (real > 0) {PKG}.Market.log("BUY " + who + " " + u + " " + id + " " + real + " " + charged + " f=" + {PKG}.BzUtil.num({PKG}.Market.factor(id)));
  String owed = "the refund of " + refund + " coins FAILED - tell an admin - it is logged";
  if (real == 0) {{
    {TR} r0 = new {TR}(false, 0, 0L, refundOk ? "your inventory is full - nothing bought and your coins were refunded" : "your inventory is full - nothing bought and " + owed);
    r0.alert = !refundOk;
    return r0;
  }}
  String m = "bought " + real + " " + pr.name + " for " + charged + " coins";
  if (real < qty) m = m + (refundOk ? " - inventory full so " + refund + " coins were refunded" : " - inventory full and " + owed);
  {TR} r1 = new {TR}(true, real, charged, m);
  r1.alert = !refundOk;
  {PKG}.BzSnd.play(u, 0);   // 0.1.12 sound pass: buy done (the buyer only)
  return r1;
}}""", trd))
# 0.1.5: the inventory first (count-verified, 0.1.4's rule), then the bags (sacks:fn:take - what it reports is what left); coins only for
# what really left; a failed payment returns the bag part to the bags (sacks:fn:put) and the rest to the inventory
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell0({PLA} p, java.util.UUID u, String who, String id, int want) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (locked(id)) return new {TR}(false, 0, 0L, "Void bags (the Pocket Dimension, old Magic Bags) can never be bought or sold");
  String wv = {PKG}.Inv.wallId(id);      // 0.1.7 the market wall
  if (wv != null) return new {TR}(false, 0, 0L, wv);
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
  int inv = {PKG}.Inv.count(p, id);
  int bag = {PKG}.Bags.count(u, id);
  long hl = (long) inv + (long) bag;
  int held = hl > 2000000000L ? 2000000000 : (int) hl;
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  int n = (want <= 0 || want > held) ? held : want;
  if (n > MAXQ) n = MAXQ;
  long quote = {PKG}.Market.quote(id, n, false);
  if (quote < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  if (quote == 0L) return new {TR}(false, 0, 0L, n + " " + pr.name + " is worth 0 coins right now - sell more at once");
  long purse = {PKG}.Coins.get(u);
  if (purse < 0L) return new {TR}(false, 0, 0L, "the coin bank did not answer - nothing sold, try again");
  if (purse > Long.MAX_VALUE - 2L * quote) return new {TR}(false, 0, 0L, "your purse is full");
  int fromInv = n < inv ? n : inv;
  int invTaken = 0;
  if (fromInv > 0) {{
    {PKG}.Inv.take(p, id, fromInv);
    invTaken = inv - {PKG}.Inv.count(p, id);
    if (invTaken < 0) invTaken = 0;
  }}
  int bagTaken = 0;
  if (n - invTaken > 0 && bag > 0) bagTaken = {PKG}.Bags.take(u, id, n - invTaken);
  int removed = invTaken + bagTaken;
  if (removed <= 0) return new {TR}(false, 0, 0L, "could not remove the items - nothing sold");
  long pay = removed == n ? quote : {PKG}.Market.quote(id, removed, false);
  if (pay <= 0L || purse > Long.MAX_VALUE - pay) {{
    int back1 = giveBack(p, u, id, invTaken, bagTaken);
    {PKG}.BzUtil.warn("sell cancelled for " + u + " " + id + " removed " + removed + " (bags " + bagTaken + ") returned " + back1);
    {PKG}.Market.log("SELL-CANCELLED " + who + " " + u + " " + id + " removed " + removed + " returned " + back1 + " bags=" + bagTaken);
    if (back1 >= removed) return new {TR}(false, 0, 0L, "sale cancelled - your items were returned");
    {TR} rc = new {TR}(false, 0, 0L, "sale cancelled but only " + back1 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rc.alert = true;
    return rc;
  }}
  int ad = {PKG}.Coins.add(u, pay);
  if (ad != 1) {{
    int back2 = giveBack(p, u, id, invTaken, bagTaken);
    {PKG}.BzUtil.warn("PAY FAILED for " + who + " " + u + " " + id + " x" + removed + " (" + pay + " coins, coins:fn:add " + (ad < 0 ? "threw - it may or may not have paid" : "refused or missing") + ") - returned " + back2 + " items (bags " + bagTaken + ")");
    {PKG}.Market.log((ad < 0 ? "PAY-ERROR " : "PAY-FAILED ") + who + " " + u + " " + id + " " + removed + " " + pay + " returned " + back2 + " bags=" + bagTaken);
    if (back2 >= removed) return new {TR}(false, 0, 0L, "could not pay - your items were returned");
    {TR} rp = new {TR}(false, 0, 0L, "could not pay and only " + back2 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rp.alert = true;
    return rp;
  }}
  if (bagTaken > 0) {PKG}.Bags.commit(u, id, bagTaken);   // review fix: paid - those can never be put back
  {PKG}.Market.apply(id, removed, false);
  {PKG}.Market.log("SELL " + who + " " + u + " " + id + " " + removed + " " + pay + " f=" + {PKG}.BzUtil.num({PKG}.Market.factor(id)) + (bagTaken > 0 ? " bags=" + bagTaken : ""));
  {TR} ok = new {TR}(true, removed, pay, "sold " + removed + " " + pr.name + " for " + pay + " coins" + (bagTaken > 0 ? " (" + bagTaken + " from the Void)" : ""));
  ok.fromBags = bagTaken;
  {PKG}.BzSnd.play(u, 1);   // 0.1.12 sound pass: sell done (the seller only; Sell inventory = one sting through the 0.5 s gate)
  return ok;
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buy({PLA} p, java.util.UUID u, String who, String id, int qty) {{
  synchronized ({PKG}.Market.class) {{ return buy0(p, u, who, id, qty); }}
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell({PLA} p, java.util.UUID u, String who, String id, int want) {{
  synchronized ({PKG}.Market.class) {{ return sell0(p, u, who, id, want); }}
}}""", trd))
# 0.1.2 custom amount BUY: exact qty (1 .. room, 1 .. MAXQ; the purse is checked by buy0), refused when the total now costs more than
# the maxCost the player was shown (moved + price = the new total so the page can re-arm), then the unchanged buy0.
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyN0({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (qty < 1 || qty > MAXQ) return new {TR}(false, 0, 0L, "type an amount from 1 to " + MAXQ);
  if ({PKG}.Catalog.get(id) == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  int rm = room(p, id);
  if (qty > rm) return new {TR}(false, 0, 0L, rm <= 0 ? "your inventory is full - nothing bought" : "only " + rm + " fit in your inventory - nothing bought");
  long cost = {PKG}.Market.quote(id, qty, true);
  if (cost <= 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  if (maxCost > 0L && cost > maxCost) {{
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now cost " + cost + " coins (you saw " + maxCost + ") - click CONFIRM to buy at the new price");
    mv.moved = true;
    mv.price = cost;
    return mv;
  }}
  return buy0(p, u, who, id, qty);
}}""", trd))
# 0.1.2 custom amount SELL: exact qty (1 .. held; sell0 alone would quietly sell less), refused when it now pays less than minPay.
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellN0({PLA} p, java.util.UUID u, String who, String id, int qty, long minPay) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (qty < 1 || qty > MAXQ) return new {TR}(false, 0, 0L, "type an amount from 1 to " + MAXQ);
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  long hl0 = (long) {PKG}.Inv.count(p, id) + (long) {PKG}.Bags.count(u, id);   // 0.1.5: + the bags
  int held = hl0 > 2000000000L ? 2000000000 : (int) hl0;
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  if (qty > held) return new {TR}(false, 0, 0L, "you only hold " + held + " " + pr.name + " - nothing sold");
  long pay = {PKG}.Market.quote(id, qty, false);
  if (pay < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  // a sale now worth 0 is refused outright (sell0 refuses it too) - never a "price moved, click again" that nothing re-arms
  if (pay == 0L) return new {TR}(false, 0, 0L, qty + " " + pr.name + " is worth 0 coins right now - sell more at once");
  if (minPay > 0L && pay < minPay) {{
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now pay " + pay + " coins (you saw " + minPay + ") - click CONFIRM to sell at the new price");
    mv.moved = true;
    mv.price = pay;
    return mv;
  }}
  return sell0(p, u, who, id, qty);
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyN({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  synchronized ({PKG}.Market.class) {{ return buyN0(p, u, who, id, qty, maxCost); }}
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellN({PLA} p, java.util.UUID u, String who, String id, int qty, long minPay) {{
  synchronized ({PKG}.Market.class) {{ return sellN0(p, u, who, id, qty, minPay); }}
}}""", trd))
# 0.1.14 Buy 1 / Buy <stack>: buy0 exactly as before (it may still buy fewer when the inventory fills and refund the rest), but refused -
# moved + price = the new total, so the page asks again - when the total now costs more than maxCost (the total the player saw or the one
# the page just checked against their confirm amount). maxCost <= 0 = no cap. Under the Market lock: quote + buy0 are one step.
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyC0({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  if (id != null && maxCost > 0L && qty > 0 && qty <= MAXQ && {PKG}.Catalog.get(id) != null) {{
    long cost = {PKG}.Market.quote(id, qty, true);
    if (cost > maxCost) {{
      {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now cost " + cost + " coins (you saw " + maxCost + ") - click CONFIRM to buy at the new price");
      mv.moved = true;
      mv.price = cost;
      return mv;
    }}
  }}
  return buy0(p, u, who, id, qty);
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buyC({PLA} p, java.util.UUID u, String who, String id, int qty, long maxCost) {{
  synchronized ({PKG}.Market.class) {{ return buyC0(p, u, who, id, qty, maxCost); }}
}}""", trd))
# {{items, coins}} that Sell inventory would move right now
# {{items, coins, from the bags}} that Sell inventory would move right now (0.1.5: inventory + bags, each capped at the per-trade limit)
# 0.1.15 E (Skyy 2026-10-16 "make the sell inventory button per category. so its (sell farming.) and it sells all your farming stuff. then
# add a sell all button above that."): the products a sell button walks - one tab (Catalog.inCat), or null = every product
trd.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList pick(String cat) {{
  return cat == null ? {PKG}.Catalog.all() : {PKG}.Catalog.inCat(cat);
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static long[] preview0({PLA} p, java.util.UUID u, String cat) {{
  java.util.ArrayList all = pick(cat);
  java.util.HashMap bm = {PKG}.Bags.all(u);
  long items = 0L, coins = 0L, fromBags = 0L;
  for (int i = 0; i < all.size(); i++) {{
    String id = (({PKG}.Product) all.get(i)).id;
    if (locked(id) || !{PKG}.Catalog.usable(id)) continue;
    int inv = {PKG}.Inv.count(p, id);
    int bg = {PKG}.Bags.held(bm, u, id);
    long h = (long) inv + (long) bg;
    if (h <= 0L) continue;
    int q = h > (long) MAXQ ? MAXQ : (int) h;
    long c = {PKG}.Market.quote(id, q, false);
    if (c <= 0L) continue;
    items += (long) q; coins += c;
    if (q > inv) fromBags += (long) (q - inv);
  }}
  return new long[] {{ items, coins, fromBags }};
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static long[] preview({PLA} p, java.util.UUID u, String cat) {{
  synchronized ({PKG}.Market.class) {{ return preview0(p, u, cat); }}
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellInventory({PLA} p, java.util.UUID u, String who, String cat) {{
  synchronized ({PKG}.Market.class) {{
    if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
    java.util.ArrayList all = pick(cat);
    String what = cat == null ? "bazaar" : cat;
    java.util.HashMap bm = {PKG}.Bags.all(u);
    int items = 0, kinds = 0, fromBags = 0; long coins = 0L;
    String warnMsg = null, lastFail = null;
    for (int i = 0; i < all.size(); i++) {{
      String id = (({PKG}.Product) all.get(i)).id;
      if (locked(id)) continue;
      if ({PKG}.Inv.count(p, id) <= 0 && {PKG}.Bags.held(bm, u, id) <= 0) continue;
      {TR} r = sell0(p, u, who, id, 0);
      if (r.ok) {{ items += r.qty; coins += r.coins; kinds++; fromBags += r.fromBags; }} else lastFail = r.msg;
      if (r.alert) warnMsg = r.msg;
    }}
    if (items == 0) {{
      {TR} rn = new {TR}(false, 0, 0L, warnMsg != null ? warnMsg : (lastFail != null ? lastFail : "nothing to sell - no " + what + " items in your inventory or the Void"));
      rn.alert = warnMsg != null;
      return rn;
    }}
    {TR} rs = new {TR}(true, items, coins, "sold " + items + (cat == null ? "" : " " + cat) + " items of " + kinds + " kinds for " + coins + " coins" + (fromBags > 0 ? " (" + fromBags + " from the Void)" : "") + (warnMsg != null ? " - but " + warnMsg : ""));
    rs.fromBags = fromBags;
    rs.alert = warnMsg != null;
    return rs;
  }}
}}""", trd))

# ================= 0.1.14 BzConfirm: the per-player confirm amount (Skyy 2026-10-15 "in settings set a confirm threshold ... default like
# 3,000") - Skyy_SkyyBazaar/confirm.properties (uuid=coins; written only when a player presses Set; an unreadable value is skipped), a
# player without a line gets BzCfg.CONFIRM (Server Setup > Bazaar > confirm.default). needs(u, total): the Settings switch bazaar.confirm
# is ON (settings:fn:get; no SkyyMenu = ON) and total >= the amount (0 = every buy). The switch registers like every adopter (settings:def
# + settings:fn:register, SkyyTrees' regSetting) - SkyyMenu's registry holds ON / OFF switches only, so the number lives on the page.
CONFIRM_KEY, CONFIRM_LABEL = "bazaar.confirm", "Bazaar: confirm big buys"
CONFIRM_HELP = "Buys at or above your amount ask CONFIRM first - set the amount on the Bazaar page"
assert len(CONFIRM_LABEL) <= 40 and len(CONFIRM_HELP) <= 90 and re.fullmatch(r"[a-z]+\.[A-Za-z]+", CONFIRM_KEY)
cfm.addField(CtField.make("public static java.nio.file.Path FILE;", cfm))
cfm.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MAP = new java.util.concurrent.ConcurrentHashMap();", cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static synchronized void load(java.nio.file.Path dir) {
  FILE = dir.resolve("confirm.properties");
  MAP.clear();
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Enumeration en = p.propertyNames();
    int bad = 0;
    while (en.hasMoreElements()) {
      String k = (String) en.nextElement();
      try {
        java.util.UUID.fromString(k.trim());
        long v = Long.parseLong(p.getProperty(k).trim());
        if (v < 0L || v > 1000000000000L) { bad++; continue; }
        MAP.put(k.trim(), Long.valueOf(v));
      } catch (Throwable t) { bad++; }
    }
    if (bad > 0) @PKG@.BzUtil.warn("confirm.properties: " + bad + " line(s) skipped (not uuid=coins) - those players get the server default");
  } catch (Throwable t) { @PKG@.BzUtil.warn("could not read confirm.properties (" + t + ") - every player gets the server default until it can be read"); }
}"""), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static long get(java.util.UUID u) {
  Object v = u == null ? null : MAP.get(u.toString());
  if (v instanceof Long) return ((Long) v).longValue();
  long d = (long) @PKG@.BzCfg.CONFIRM;
  return d < 0L ? 0L : d;
}"""), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static boolean switchOn(java.util.UUID u) {
  if (u == null) return true;
  try {
    Object f = @PKG@.BzUtil.bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, "@KEY@" });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""", KEY=CONFIRM_KEY), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static boolean needs(java.util.UUID u, long total) {
  if (!switchOn(u)) return false;
  return total >= get(u);
}"""), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean save() {
  if (FILE == null) return false;
  try {
    java.util.ArrayList ks = new java.util.ArrayList(MAP.keySet());
    java.util.Collections.sort(ks);
    StringBuilder sb = new StringBuilder("# SkyyBazaar - each player's confirm amount (player uuid=coins): a buy of this many coins or more asks CONFIRM first;\n# 0 = every buy. Players set it on the Bazaar page (bottom row); no line = Server Setup > Bazaar > Confirm purchases above.\n");
    for (int i = 0; i < ks.size(); i++) sb.append((String) ks.get(i)).append('=').append(String.valueOf(MAP.get(ks.get(i)))).append('\n');
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return true;
  } catch (Throwable t) { @PKG@.BzUtil.warn("could not save confirm.properties: " + t); return false; }
}"""), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static synchronized boolean set(java.util.UUID u, long v) {
  if (u == null || v < 0L || v > 1000000000000L) return false;
  Object old = MAP.put(u.toString(), Long.valueOf(v));
  if (save()) return true;
  if (old == null) MAP.remove(u.toString()); else MAP.put(u.toString(), old);
  return false;
}"""), cfm))
cfm.addMethod(CtNewMethod.make(jt(r"""
public static void register() {
  try {
    Object[] a = new Object[] { "SkyyBazaar", "@KEY@", "@LABEL@", "coins", Boolean.TRUE, "@HELP@" };
    java.util.Map br = @PKG@.BzUtil.bridge();
    br.put("settings:def:@KEY@", a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""", KEY=CONFIRM_KEY, LABEL=CONFIRM_LABEL, HELP=CONFIRM_HELP), cfm))
# BzRevert: fields + constructor here (BzPage.schedRevert makes one); run() after the page methods it calls
rvt.addInterface(pool.get("java.lang.Runnable"))
rvt.addField(CtField.make("public %s.BzPage page;" % PKG, rvt))
rvt.addField(CtField.make("public int seq;", rvt))
rvt.addField(CtField.make("public boolean onWorld;", rvt))
rvt.addConstructor(CtNewConstructor.make("public BzRevert(%s.BzPage page, int seq, boolean onWorld) { this.page = page; this.seq = seq; this.onWorld = onWorld; }" % PKG, rvt))

# ================= 0.1.17 MARKET MERGE: BzMarket + BzMkSort (defined before BzPage, which calls them) =================
# THE tier table (tools/tier_tags.py ROWS: id -> display tier 1-8) as one "id:tier|..." constant, parsed once; an id without a row but with
# a SkyyGear level (an AH gear listing) takes the level band TT.tier_for_level (proved equal below); everything else sorts last (99).
import tier_tags as _TT17
_T17 = sorted(_TT17.ROWS)
assert _T17 and all(re.fullmatch(r"[A-Za-z0-9_]+", _i) for _i in _T17) and all(1 <= _TT17.tier(_i) <= 8 for _i in _T17)
BZ_TIER_SPEC = "|".join("%s:%d" % (_i, _TT17.tier(_i)) for _i in _T17)
BZ_LV_BANDS = ((40, 7), (35, 6), (25, 5), (20, 4), (15, 3), (10, 2))


def _bz_lv(lv, iid):
    if "Onyxium" in iid:
        return 8
    for _lo, _t in BZ_LV_BANDS:
        if lv >= _lo:
            return _t
    return 1


assert all(_bz_lv(_l, _x) == _TT17.tier_for_level(_l, _x) for _l in range(0, 120) for _x in ("Weapon_Sword_Iron", "Armor_Onyxium_Chest")), \
    "0.1.17: the Java level bands = tools/tier_tags.py tier_for_level"
print("0.1.17 MARKET MERGE: %d tier rows from tools/tier_tags.py (%d chars), level bands %s" % (len(_T17), len(BZ_TIER_SPEC), BZ_LV_BANDS))
mkb.addField(CtField.make("public static final String TIER_SPEC = %s;" % SUI.java_lit(BZ_TIER_SPEC), mkb))
mkb.addField(CtField.make("public static volatile java.util.HashMap TIERS = null;", mkb))
mkb.addMethod(CtNewMethod.make(jt(r"""
public static java.util.HashMap tiers() {
  java.util.HashMap m = TIERS;
  if (m != null) return m;
  m = new java.util.HashMap();
  String[] parts = TIER_SPEC.split("\\|");
  for (int i = 0; i < parts.length; i++) {
    int c = parts[i].indexOf(':');
    if (c > 0) m.put(parts[i].substring(0, c), Integer.valueOf(Integer.parseInt(parts[i].substring(c + 1))));
  }
  TIERS = m;
  return m;
}"""), mkb))
mkb.addMethod(CtNewMethod.make(jt(r"""
public static int lvTier(String id, int lv) {
  if (id != null && id.indexOf("Onyxium") >= 0) return 8;
@BANDS@
  return 1;
}""", BANDS="\n".join("  if (lv >= %d) return %d;" % b_ for b_ in BZ_LV_BANDS)), mkb))
# the sort tier of an item: the table, else (level >= 0) the level band, else 99 (untiered: after every tiered item)
mkb.addMethod(CtNewMethod.make(jt(r"""
public static int tier(String id, int level) {
  if (id == null) return 99;
  Object o = tiers().get(id);
  if (o instanceof Integer) return ((Integer) o).intValue();
  if (level >= 0) return lvTier(id, level);
  return 99;
}"""), mkb))
# an item id that may go into the inline markup (ItemIcon ItemId) - letters, digits, '_' only
mkb.addMethod(CtNewMethod.make(jt(r"""
public static boolean okId(String s) {
  if (s == null || s.length() == 0 || s.length() > 96) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}"""), mkb))
mkb.addMethod(CtNewMethod.make(jt(r"""
public static java.util.function.Function fn(String key) {
  Object f = null;
  try { f = @PKG@.BzUtil.bridge().get(key); } catch (Throwable t) { f = null; }
  if (f instanceof java.util.function.Function) return (java.util.function.Function) f;
  return null;
}"""), mkb))
# SkyyAuctions 0.1.9+ is loaded: it publishes both ah:fn:find and ah:fn:open
mkb.addMethod(CtNewMethod.make(jt(r"""
public static boolean ahOn() {
  return fn("ah:fn:find") != null && fn("ah:fn:open") != null;
}"""), mkb))
# ah:fn:find (KEY CONTRACT, tools/auctions_0_1_9_patch.py): apply(String query) -> java.util.List of Object[]{ String itemId, String name,
# Integer listings, Long lowestEach, Long cheapestPrice, Long cheapestQty, String endsIn, Integer level (-1 none), String color }.
# Every row is type-checked here (a bad row is skipped), the item id must be markup-safe; at most 300 rows.
mkb.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList ahFind(String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (q == null || q.trim().length() == 0) return out;
  java.util.function.Function f = fn("ah:fn:find");
  if (f == null) return out;
  Object r = null;
  try { r = f.apply(q); } catch (Throwable t) { @PKG@.BzUtil.warn("ah:fn:find failed: " + t); return out; }
  if (!(r instanceof java.util.List)) return out;
  java.util.List l = (java.util.List) r;
  for (int i = 0; i < l.size() && out.size() < 300; i++) {
    Object o = l.get(i);
    if (!(o instanceof Object[])) continue;
    Object[] e = (Object[]) o;
    if (e.length < 9 || !(e[0] instanceof String) || !(e[1] instanceof String) || !(e[2] instanceof Integer) || !(e[3] instanceof Long)
        || !(e[4] instanceof Long) || !(e[5] instanceof Long) || !(e[6] instanceof String) || !(e[7] instanceof Integer)) continue;
    if (((Integer) e[2]).intValue() < 1 || !okId((String) e[0])) continue;
    out.add(e);
  }
  return out;
}"""), mkb))
# ah:fn:open: apply(Object[]{ UUID, String query }) opens the Auction House page (browse, that search) for the player -> TRUE
mkb.addMethod(CtNewMethod.make(jt(r"""
public static boolean ahOpen(java.util.UUID u, String q) {
  java.util.function.Function f = fn("ah:fn:open");
  if (f == null || u == null) return false;
  try { return Boolean.TRUE.equals(f.apply(new Object[] { u, q == null ? "" : q })); }
  catch (Throwable t) { @PKG@.BzUtil.warn("ah:fn:open failed: " + t); return false; }
}"""), mkb))
# 0.1.18: ah:fn:view (SkyyAuctions 0.1.10+, KEY CONTRACT in tools/auctions_0_1_10_patch.py): apply(Object[]{ UUID, String view }) opens the
# Auction House on that view ("browse" / "create" / "manage") -> Boolean; apply(UUID) -> Long = the claims waiting for that player's profile
mkb.addMethod(CtNewMethod.make(jt(r"""
public static boolean ahViewOn() {
  return fn("ah:fn:view") != null;
}"""), mkb))
mkb.addMethod(CtNewMethod.make(jt(r"""
public static boolean ahView(java.util.UUID u, String view) {
  java.util.function.Function f = fn("ah:fn:view");
  if (f == null || u == null || view == null) return false;
  try { return Boolean.TRUE.equals(f.apply(new Object[] { u, view })); }
  catch (Throwable t) { @PKG@.BzUtil.warn("ah:fn:view failed: " + t); return false; }
}"""), mkb))
mkb.addMethod(CtNewMethod.make(jt(r"""
public static long ahOwed(java.util.UUID u) {
  java.util.function.Function f = fn("ah:fn:view");
  if (f == null || u == null) return 0L;
  try {
    Object r = f.apply(u);
    if (r instanceof Long) { long v = ((Long) r).longValue(); return v < 0L ? 0L : v; }
  } catch (Throwable t) { @PKG@.BzUtil.warn("ah:fn:view (count) failed: " + t); }
  return 0L;
}"""), mkb))
mks.addInterface(pool.get("java.util.Comparator"))
mks.addConstructor(CtNewConstructor.make("public BzMkSort() { }", mks))
# entries Object[]{ Integer tier, String lower-case name, Integer kind (0 Bazaar, 1 AH), String id, payload }
mks.addMethod(CtNewMethod.make(jt(r"""
public int compare(Object a, Object b) {
  Object[] x = (Object[]) a;
  Object[] y = (Object[]) b;
  int c = Integer.compare(((Integer) x[0]).intValue(), ((Integer) y[0]).intValue());
  if (c != 0) return c;
  c = ((String) x[1]).compareTo((String) y[1]);
  if (c != 0) return c;
  c = Integer.compare(((Integer) x[2]).intValue(), ((Integer) y[2]).intValue());
  if (c != 0) return c;
  return ((String) x[3]).compareTo((String) y[3]);
}"""), mks))

# ================= BzPage 0.1.18 = the MENU PATTERN page (research/Menu-Pattern.md 3; kit skyyui 1.7 hub_page; notes: tools/bazaar_0_1_18_patch.py) =================
# Skyy 2026-10-16 (docs/answered/ui.md): "I never want to have to use a back button. The menus at the top should always be there for easy
# navigation." + "keep this top bar at this size consistent at the top across every menu." + "i dont mind scrolling, but if there are only a
# few items try to scale them to all fit." The 1600 x 980 hub page: title bar | row 1 | row 2 (Market selected) | the ONE sub-tab row
# (BAZAAR | AUCTION HOUSE | CREATE BIN | MANAGE + the purse) | three columns: LEFT the bag tabs (an in-page list), SELL <tab> / SELL ALL
# TABS, the confirm amount | MIDDLE the search row, the header + count, ONE scroll list of cells (no pages; few cells grow) | RIGHT the
# detail well (456) | the footer: the result line + Close. Every 0.1.17 id, binding payload and click path is kept (only prev / next went).
# Static labels only use the kit's proven inline charset; run-time texts are b.set. SUI.assert_proven + assert_menu_page on every state.
BZ_HUB, BZ_TAB = "market", "bazaar"
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_THEME == "sky" and SUI.THEME_PAD["sky"] == 24, "0.1.18: kit skyyui 1.7 hub_page"
BZ_HUB_ROW = [r for r in SUI.HUB_TABS if r[0] == BZ_HUB and r[1] == BZ_TAB]
assert len(BZ_HUB_ROW) == 1 and BZ_HUB_ROW[0][3] == "SkyyBazaar", "0.1.13: Market > Bazaar is SkyyBazaar's contract tab"
_, _, BZ_HUB_ORDER, _, BZ_HUB_LABEL, BZ_HUB_CMD = BZ_HUB_ROW[0]
assert (BZ_HUB_ORDER, BZ_HUB_LABEL, BZ_HUB_CMD) == (10, "Bazaar", "bazaar"), BZ_HUB_ROW
BZ_HUB_LABEL = "Market"         # 0.1.17 MARKET MERGE: the merged tab's label (id bazaar, order 10, /bazaar stay the contract's)
SUI.check_text(BZ_HUB_LABEL)
BZ_SH = SUI.hub_page("SkyyBzF", BZ_HUB, sub=True, footer=True, body_id="SkyyBzFB", content_id="SkyyBz", content_layout="Left")
BZ_IW, BZ_CH = SUI.HUB_PAGE_IW, BZ_SH.content_h
BZ_W, BZ_H = BZ_SH.w, BZ_SH.h
assert (BZ_W, BZ_H, BZ_IW, BZ_CH) == (1600, 980, 1552, 676), ("0.1.18: the hub page", BZ_W, BZ_H, BZ_IW, BZ_CH)
BZ_GAP, BZ_LW, BZ_RW = 12, 300, SUI.DETAIL_W
BZ_MW = BZ_IW - BZ_LW - BZ_RW - 2 * BZ_GAP                        # 772: the middle column
assert BZ_MW == 772, BZ_MW
BZ_MAXT = 6                     # the bag tabs listed (0.1.17's limit; more tabs = the "tell an admin" header line)
BZ_PER = 39                     # 0.1.17's cells a page: only the constructor's first arrays now (render sizes them to what it shows)
BZ_SHOW = 180                   # cells before the Show more row (20 rows of 9; Menu-Pattern 3.3: a very long list shows the rest on a click)
BZ_SENT, BZ_SISENT, BZ_STK, BZ_CFS = "QzTabQz", "QzSiQz", "QzStkQz", "QzCfQz"
_bi = lambda base, expr: base + SUI.J(expr, "0")
BZM = {}


def bz_gold(mk):
    """0.1.14: an armed button's label turns gold (the kit's @ColorGoldHighlight) - the CONFIRM look"""
    a, b = "TextColor: %s" % SUI.color("buttonText"), "TextColor: %s" % SUI.color("gold")
    assert mk.count(a) == 3, "0.1.14: a Primary / Destructive label has 3 coloured states: %s" % mk[:120]
    return mk.replace(a, b)


# ---- the ONE sub-tab row (#SkyyBzFSub): BAZAAR | AUCTION HOUSE | CREATE BIN | MANAGE (HubBar.subTab, 150 x 32) + a 5 px gap + the purse
BZ_SUBS = ["Bazaar", "Auction House", "Create BIN", "Manage"]
BZ_SUB_W = SUI.SUB_TAB_W
assert SUI.assert_sub_tabs_fit(BZ_SUBS, BZ_SUB_W) == 4 * 150 + 3 * 5, "0.1.18: the four sub-tabs fit"
assert SUI.text_width("Manage (999)", SUI.BUTTON_SIZES["small"][0], bold=True, upper=True) <= BZ_SUB_W - 2 * SUI.SUB_TAB_PAD, "MANAGE (999)"
BZ_PURSE_MIN = BZ_IW - 4 * BZ_SUB_W - 4 * SUI.SUB_TAB_GAP        # 932: the purse with all four sub-tabs
BZM["SUBGAP"] = SUI.spacer(w=SUI.SUB_TAB_GAP, h=SUI.SUB_TAB_H)
BZM["PURSE"] = SUI.label("SkyyBzPurse", "", "bold", w=SUI.J("pw", str(BZ_PURSE_MIN)), h=SUI.SUB_TAB_H, align="End",
                         col=SUI.color_by([("purseOk", "gold")], "error"))
for _t in ("Purse  99999999999 coins", "Purse unavailable - coin bank error", "SkyyCoins is not loaded - trading is off"):
    assert SUI.text_width(_t, 16, bold=True) <= BZ_PURSE_MIN, _t
# ---- LEFT column (#SkyyBzL): the bag tabs (in-page selection, the open one Primary), SELL <tab> / SELL ALL TABS, the confirm amount
BZM["LEFT"] = SUI.group("SkyyBzL", "Top", w=BZ_LW, h=BZ_CH)
BZ_TAB_GAP = 6
BZ_TABS_H = BZ_MAXT * (SUI.BTN_H + BZ_TAB_GAP)                   # 300
BZM["TABCOL"] = SUI.group("SkyyBzTabs", "Top", h=BZ_TABS_H)
BZM["TABON"] = SUI.button(_bi("SkyyBzTab", "i"), BZ_SENT, "primary", w=BZ_LW, anchor={"bottom": BZ_TAB_GAP})
BZM["TABOFF"] = SUI.button(_bi("SkyyBzTab", "i"), BZ_SENT, "secondary", w=BZ_LW, anchor={"bottom": BZ_TAB_GAP})
for _t in ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"):
    assert SUI.text_width(_t, 17, bold=True, upper=True) <= BZ_LW - 2 * SUI.BTN_PAD, _t
assert SUI.text_width("W" * 16, 12, bold=True, upper=True) <= BZ_LW - 2 * SUI.BTN_PAD, "a 16-letter admin tab name fits at the shrink floor"
# 0.1.15 E: SELL <open tab> (the tab name drawn inline after tabText) and SELL ALL TABS; each turns into the gold Confirm sell on its own
BZM["SELLINV"] = SUI.choose(SUI.J("siOn"), bz_gold(SUI.button("SkyyBzSellInv", "Confirm sell", "destructive", w=BZ_LW, anchor={"bottom": BZ_TAB_GAP})),
                            SUI.button("SkyyBzSellInv", "Sell " + BZ_SISENT, "destructive", w=BZ_LW, fit=False, anchor={"bottom": BZ_TAB_GAP}))
BZM["SELLALL"] = SUI.choose(SUI.J("saOn"), bz_gold(SUI.button("SkyyBzSellAllTabs", "Confirm sell", "destructive", w=BZ_LW)),
                            SUI.button("SkyyBzSellAllTabs", "Sell all tabs", "destructive", w=BZ_LW))
BZ_SELL_H = 2 * SUI.BTN_H + BZ_TAB_GAP
for _t in ("Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"):   # the bag tabs fit without shrinking
    assert SUI.text_width("Sell " + _t, 17, bold=True, upper=True) <= BZ_LW - 2 * SUI.BTN_PAD, _t
# 0.1.14: the player's confirm amount: 'Confirm buys from' [amount] Set + the note (run-time text)
BZ_CF_TOP, BZ_CFL_H, BZ_CFN_H, BZ_CFF_W, BZ_CFB_W = 12, 24, 62, 180, 110
BZM["CFLAB"] = SUI.label(None, "Confirm buys from", "fieldLabel", w=BZ_LW, h=BZ_CFL_H, anchor={"top": BZ_CF_TOP})
BZM["CFROW"] = SUI.group("SkyyBzCfRow", "Left", h=SUI.BTN_H)
BZ_CFROW = [SUI.text_field("SkyyBzCfBox", "SkyyBzCf", w=BZ_CFF_W, h=SUI.BTN_H, placeholder="3000", max_length=12),
            SUI.button("SkyyBzCfSet", "Set", "secondary", w=BZ_CFB_W, anchor={"left": 10})]
BZM["CFNOTE"] = SUI.label("SkyyBzCfNote", "", "caption", w=BZ_LW, h=BZ_CFN_H, size=13, wrap=True)
BZ_CF_NOTES = ["coins or more ask CONFIRM (0 = every buy) - totals: buys round up, sells down",
               "coins - asking is OFF in your Settings (Coins & Bank)"]
for _t in BZ_CF_NOTES:
    assert SUI.text_width(_t, 13) <= 3 * (BZ_LW - 30), ("0.1.18 the confirm note fits 3 lines", _t)
BZ_LSP = BZ_CH - BZ_TABS_H - BZ_SELL_H - BZ_CF_TOP - BZ_CFL_H - SUI.BTN_H - BZ_CFN_H
assert BZ_LSP >= 40, BZ_LSP
BZM["LSP"] = SUI.spacer(h=BZ_LSP)
BZM["CGAP"] = SUI.spacer(w=BZ_GAP, h=BZ_CH)
# ---- MIDDLE column (#SkyyBzM): the one search, the header + count, ONE scroll list of cells
BZM["MID"] = SUI.group("SkyyBzM", "Top", w=BZ_MW, h=BZ_CH)
BZ_FIND_BW = 120
BZ_FIND_W = BZ_MW - 2 * (10 + BZ_FIND_BW)                        # 512
BZM["FINDROW"] = SUI.group("SkyyBzFindRow", "Left", h=SUI.BTN_H)
# 0.1.6: search_field is gated UNVERIFIED in the kit, but Skyy saw its probe page (11) work on 2026-09-30 -> trial=True + allow below
BZ_FIND = [SUI.search_field("SkyyBzFindBox", "SkyyBzFind", w=BZ_FIND_W, placeholder="Search both markets - name or item id", max_length=40,
                            trial=True, anchor={"top": (SUI.BTN_H - SUI.SEARCH_H) // 2}),
           SUI.button("SkyyBzFindGo", "Search", "secondary", w=BZ_FIND_BW, anchor={"left": 10}),
           SUI.button("SkyyBzFindClr", "Clear", "secondary", w=BZ_FIND_BW, sound="cancel", anchor={"left": 10})]
assert SUI.text_width("Search both markets - name or item id", 16) <= BZ_FIND_W - 40, BZ_FIND_W
BZ_HEAD_TOP, BZ_HEAD_H, BZ_CNT_W = 6, 30, 150
BZM["HEAD"] = SUI.group("SkyyBzHead", "Left", h=BZ_HEAD_H, anchor={"top": BZ_HEAD_TOP})
BZM["SUB"] = SUI.label("SkyyBzSub", "", "default", w=BZ_MW - BZ_CNT_W, h=BZ_HEAD_H, size=14)
BZM["COUNT"] = SUI.label("SkyyBzCount", "", "caption", w=BZ_CNT_W, h=BZ_HEAD_H, size=14, align="End")
BZ_GRID_TOP = 6
BZ_GRID_H = BZ_CH - SUI.BTN_H - BZ_HEAD_TOP - BZ_HEAD_H - BZ_GRID_TOP   # 590
BZM["GRID"] = SUI.scroll_list("SkyyBzGrid", h=BZ_GRID_H, well=True, anchor={"top": BZ_GRID_TOP})
BZ_CGAP = 4
BZ_GRID_IW = BZ_MW - 2 * SUI.WELL_LIST_PAD - SUI.SCROLL_SIZE - SUI.SCROLL_SPACING      # 752: room for the cells beside the scrollbar
BZ_GRID_IH = BZ_GRID_H - 2 * SUI.WELL_LIST_PAD                                        # 582
BZ_CELLS = SUI.grow_row_sizes(BZ_GRID_IH, 74, gap=BZ_CGAP)       # Skyy rule 7: 74 / 107 / 148 px cells
BZ_GCOLS = [(BZ_GRID_IW + BZ_CGAP) // (c + BZ_CGAP) for c in BZ_CELLS]
BZ_GLEAD = [max(0, (BZ_GRID_IW - n_ * (c + BZ_CGAP)) // 2) for c, n_ in zip(BZ_CELLS, BZ_GCOLS)]
assert BZ_CELLS == [74, 107, 148] and BZ_GCOLS == [9, 6, 4], (BZ_CELLS, BZ_GCOLS)
assert all(n_ * (c + BZ_CGAP) + l_ <= BZ_GRID_IW for c, n_, l_ in zip(BZ_CELLS, BZ_GCOLS, BZ_GLEAD))
BZM["ROWS"], BZM["CELLS"] = [], []
for _k, _c in enumerate(BZ_CELLS):
    BZM["ROWS"].append(SUI.group(_bi("SkyyBzRow", "r"), "Left", h=_c, anchor={"bottom": BZ_CGAP}, pad={"left": BZ_GLEAD[_k]}))
    _bzcell = lambda st, c=_c: SUI.icon_cell(_bi("SkyyBzCell", "idx"), SUI.J("p.id", "Ore_Copper"), c, st, qty=True, anchor={"right": BZ_CGAP})
    BZM["CELLS"].append(SUI.choose(SUI.J("con"), _bzcell("selected"), _bzcell("normal")))
BZM["EMPTYL"] = SUI.empty_state("SkyyBzEmpty", h=80)
BZM["MOREROW"] = SUI.group("SkyyBzMoreRow", "Left", h=SUI.BTN_H, anchor={"top": 4}, pad={"left": BZ_GLEAD[0]})
BZM["MORE"] = SUI.button("SkyyBzMore", "Show more", "secondary", w=300)
# ---- RIGHT column: the detail well (#SkyyBzDetail, 456 = SUI.DETAIL_W)
BZ_DIN_W, BZ_DIN_H = BZ_RW - 2 * SUI.WELL_PAD, BZ_CH - 2 * SUI.WELL_PAD     # 440 x 660
BZM["DET"] = SUI.panel("SkyyBzDetail", "well", w=BZ_RW, h=BZ_CH, layout="Top")
BZ_DICON = 96
BZM["DTOP"] = SUI.group("SkyyBzDTop", "Left", h=BZ_DICON, anchor={"bottom": 8})
BZM["DICON"] = SUI.icon_cell("SkyyBzDIcon", SUI.J("id", "Ore_Copper"), state="static", w=BZ_DICON, h=BZ_DICON, icon=BZ_DICON - 16)
BZM["DNAME"] = SUI.label("SkyyBzDName", "", "rowName", w=BZ_DIN_W - BZ_DICON - 12, h=BZ_DICON, size=20, bold=True, wrap=True, anchor={"left": 12})
BZ_DLINE_H = 44
BZ_DLINES = [("DBUY", SUI.label("SkyyBzDBuy", "", "default", h=BZ_DLINE_H, size=15, col="success", wrap=True)),
             ("DSELL", SUI.label("SkyyBzDSell", "", "default", h=BZ_DLINE_H, size=15, col="error", wrap=True)),
             ("DHOLD", SUI.label("SkyyBzDHold", "", "default", h=BZ_DLINE_H, size=15, wrap=True)),
             ("DDEM", SUI.label("SkyyBzDDem", "", "caption", h=BZ_DLINE_H, size=14, wrap=True)),
             ("DPROC", SUI.label("SkyyBzDProc", "", "caption", h=BZ_DLINE_H, size=14, col="info", wrap=True))]
# 0.1.5: Buy / Sell <stack> = the item's real Hytale max stack; the number is drawn inline (BZ_STK replaced in Java, like the tab names)
BZ_ACT_BW = (BZ_DIN_W - 8) // 2                                  # 216
BZ_ACT_SW = (BZ_DIN_W - 16) // 3                                 # 141
BZM["ACTS"] = SUI.group("SkyyBzActs", "Left", h=SUI.BTN_H, anchor={"top": 8})
BZ_ACTS = [SUI.button("SkyyBzBuy1", "Buy 1", "primary", w=BZ_ACT_BW),
           SUI.button("SkyyBzBuyStk", "Buy " + BZ_STK, "primary", w=BZ_ACT_BW, anchor={"left": 8}, fit=False)]
BZM["SELLS"] = SUI.group("SkyyBzSells", "Left", h=SUI.BTN_H, anchor={"top": 6})
BZ_SELLS = [SUI.button("SkyyBzSell1", "Sell 1", "destructive", w=BZ_ACT_SW),
            SUI.button("SkyyBzSellStk", "Sell " + BZ_STK, "destructive", w=BZ_ACT_SW, anchor={"left": 8}, fit=False),
            SUI.button("SkyyBzSellAll", "Sell all", "destructive", w=BZ_DIN_W - 2 * BZ_ACT_SW - 16, anchor={"left": 8})]
assert SUI.text_width("Sell 100", 17, bold=True, upper=True) <= BZ_ACT_SW - 2 * SUI.BTN_PAD and 2 * BZ_ACT_BW + 8 == BZ_DIN_W
BZM["AMTLAB"] = SUI.label(None, "Custom amount", "fieldLabel", h=24, anchor={"top": 10})
BZM["AMTROW"] = SUI.group("SkyyBzAmtRow", "Left", h=SUI.BTN_H)
BZ_AMTF = SUI.text_field("SkyyBzAmtBox", "SkyyBzAmt", w=BZ_DIN_W, h=SUI.BTN_H, placeholder="Amount", max_length=12)
BZM["ABROW"] = SUI.group("SkyyBzABRow", "Left", h=SUI.BTN_H, anchor={"top": 6})
BZ_AB = [SUI.button("SkyyBzABuy", "Buy", "primary", w=BZ_ACT_BW), SUI.button("SkyyBzASell", "Sell", "destructive", w=BZ_ACT_BW, anchor={"left": 8})]
BZM["AMTHINT"] = SUI.label("SkyyBzAmtHint", "", "caption", h=24)
BZM["LIM"] = SUI.label("SkyyBzLimits", "", "default", h=66, size=15, col="value", wrap=True)
# 0.1.14: the CONFIRM variants (same id, width and place as the button they replace; the label is put in at run time - BzPage.cfText)
BZ_CF = {"SkyyBzBuy1": bz_gold(SUI.button("SkyyBzBuy1", BZ_CFS, "primary", w=BZ_ACT_BW, fit=False)),
         "SkyyBzBuyStk": bz_gold(SUI.button("SkyyBzBuyStk", BZ_CFS, "primary", w=BZ_ACT_BW, anchor={"left": 8}, fit=False)),
         "SkyyBzABuy": bz_gold(SUI.button("SkyyBzABuy", BZ_CFS, "primary", w=BZ_ACT_BW, fit=False)),
         "SkyyBzASell": bz_gold(SUI.button("SkyyBzASell", BZ_CFS, "destructive", w=BZ_ACT_BW, anchor={"left": 8}, fit=False))}
BZ_CF_WORST = ["CONFIRM - 9999999 coins", "CONFIRM - 9999M coins", "CONFIRM - 9999B coins", "CONFIRM - 1000T coins"]
for _t in BZ_CF_WORST + ["CONFIRM - 205 coins"]:
    SUI.check_text(_t)
    assert SUI.text_width(_t, 12, bold=True, upper=True) <= BZ_ACT_BW - 2 * SUI.BTN_PAD, _t
# 0.1.17: an Auction House cell's detail: OPEN IN AUCTION HOUSE + a note where the Buy buttons sit
BZM["AHACTS"] = SUI.group("SkyyBzActs", "Left", h=SUI.BTN_H, anchor={"top": 8})
BZM["AHOPEN"] = SUI.button("SkyyBzAhOpen", "Open in Auction House", "primary", w=BZ_DIN_W)
BZM["AHNOTE"] = SUI.label("SkyyBzAhNote", "", "caption", h=BZ_DLINE_H, size=14, wrap=True, anchor={"top": 6})
BZ_AH_NOTE = "Shows every listing of this item, cheapest first - buying happens there"
assert SUI.text_width("Open in Auction House", 17, bold=True, upper=True) <= BZ_DIN_W - 2 * SUI.BTN_PAD
BZM["NODETTX"] = SUI.label(None, "Click a product to see its prices and trade it", "default", h=BZ_DIN_H, align="Center", wrap=True)
# ---- the footer (#SkyyBzFFoot): the result line (coloured by its words) + Close
BZ_CLOSE_W = SUI.BTN_MIN_W
BZ_INFO_W = BZ_IW - SUI.FOOT_GAP - BZ_CLOSE_W                    # 1370
BZM["INFO"] = SUI.label("SkyyBzInfo", "", "default", h=SUI.FOOT_BTN_H, w=BZ_INFO_W, size=16, bold=True, align="Center",
                        col=SUI.J("infoColor(this.info)", SUI.COLOR["success"]), wrap=True)
BZM["FSP"] = SUI.spacer(w=SUI.FOOT_GAP, h=SUI.FOOT_BTN_H)
BZM["CLOSE"] = SUI.foot_button("SkyyBzClose", "Close", BZ_CLOSE_W, sound="cancel")
BZ_DET_HS = {"product": 2 * SUI.WELL_PAD + BZ_DICON + 8 + 5 * BZ_DLINE_H + (8 + SUI.BTN_H) + (6 + SUI.BTN_H) + (10 + 24) + SUI.BTN_H
                        + (6 + SUI.BTN_H) + 24 + 66,
             "ah": 2 * SUI.WELL_PAD + BZ_DICON + 8 + 5 * BZ_DLINE_H + (8 + SUI.BTN_H) + (6 + BZ_DLINE_H) + 66}
assert max(BZ_DET_HS.values()) <= BZ_CH, ("0.1.18: the detail well holds every line", BZ_DET_HS)
BZ_TAB_ROWS = [(t, SUI.hub_tab_label(BZ_HUB, t) if t != BZ_TAB else BZ_HUB_LABEL) for t, *_r in SUI.hub_page_tabs(BZ_HUB)]
assert [t for t, _l in BZ_TAB_ROWS] == ["bazaar", "merchants"], BZ_TAB_ROWS


def bz_sample(state="product", cf=False, nsub=4, ncells=20, gk=None, more=False, empty=False):
    # one static page state (J() samples) = what render() draws, for the proven-property, width, height and menu-pattern proofs.
    # state product / ah (an Auction House cell selected) / none; cf = every button armed (CONFIRM); nsub = the sub-tabs drawn (1 no AH,
    # 2 AH 0.1.9, 4 AH 0.1.10); ncells / gk = the grid (gk None = the tier render() picks); more = the Show more row; empty = no cells
    _cfm = lambda mk: SUI.render(mk).replace(BZ_CFS, BZ_CF_WORST[0])
    ap = SUI.hub_page_preview(BZ_SH, tabs=BZ_TAB_ROWS, my_tab=BZ_TAB)
    ap.extend(SUI.sub_tabs_preview("SkyyBzF", BZ_SUBS[:nsub], 0, BZ_SUB_W))
    ap.append(("SkyyBzFSub", BZM["SUBGAP"]))
    pw = BZ_IW - nsub * BZ_SUB_W - nsub * SUI.SUB_TAB_GAP
    ap.append(("SkyyBzFSub", SUI.render(BZM["PURSE"]).replace("Width: %d," % BZ_PURSE_MIN, "Width: %d," % pw)))
    ap.append(("SkyyBz", BZM["LEFT"]))
    ap.append(("SkyyBzL", BZM["TABCOL"]))
    for t in range(BZ_MAXT):
        ap.append(("SkyyBzTabs", SUI.render(BZM["TABON" if t == 0 else "TABOFF"]).replace("SkyyBzTab0", "SkyyBzTab%d" % t)))
    ap.append(("SkyyBzL", BZM["LSP"]))
    ap.append(("SkyyBzL", BZM["SELLINV"].a if cf else BZM["SELLINV"].b))
    ap.append(("SkyyBzL", BZM["SELLALL"].a if cf else BZM["SELLALL"].b))
    ap.append(("SkyyBzL", BZM["CFLAB"]))
    ap.append(("SkyyBzL", BZM["CFROW"]))
    for mk in BZ_CFROW:
        ap.append(("SkyyBzCfRow", mk))
    ap.append(("SkyyBzL", BZM["CFNOTE"]))
    ap.append(("SkyyBz", BZM["CGAP"]))
    ap.append(("SkyyBz", BZM["MID"]))
    ap.append(("SkyyBzM", BZM["FINDROW"]))
    for mk in BZ_FIND:
        ap.append(("SkyyBzFindRow", mk))
    ap.append(("SkyyBzM", BZM["HEAD"]))
    ap.append(("SkyyBzHead", BZM["SUB"]))
    ap.append(("SkyyBzHead", BZM["COUNT"]))
    ap.append(("SkyyBzM", BZM["GRID"]))
    n = 0 if empty else ncells
    k = gk if gk is not None else bz_pick(n)
    cols = BZ_GCOLS[k]
    for r in range((n + cols - 1) // cols):
        ap.append(("SkyyBzGrid", SUI.render(BZM["ROWS"][k]).replace("SkyyBzRow0", "SkyyBzRow%d" % r)))
        for c in range(cols):
            idx = r * cols + c
            if idx >= n:
                break
            mk = BZM["CELLS"][k].a if idx == 0 else BZM["CELLS"][k].b
            ap.append(("SkyyBzRow%d" % r, SUI.render(mk).replace("SkyyBzCell0", "SkyyBzCell%d" % idx)))
    if n == 0:
        ap.append(("SkyyBzGrid", BZM["EMPTYL"]))
    if more:
        ap.append(("SkyyBzGrid", BZM["MOREROW"]))
        ap.append(("SkyyBzMoreRow", BZM["MORE"]))
    ap.append(("SkyyBz", BZM["CGAP"]))
    ap.append(("SkyyBz", BZM["DET"]))
    if state in ("product", "ah"):
        ap.append(("SkyyBzDetail", BZM["DTOP"]))
        ap.append(("SkyyBzDTop", BZM["DICON"]))
        ap.append(("SkyyBzDTop", BZM["DNAME"]))
        for _k, mk in BZ_DLINES:
            ap.append(("SkyyBzDetail", mk))
    if state == "ah":
        ap.append(("SkyyBzDetail", BZM["AHACTS"]))
        ap.append(("SkyyBzActs", BZM["AHOPEN"]))
        ap.append(("SkyyBzDetail", BZM["AHNOTE"]))
        ap.append(("SkyyBzDetail", BZM["LIM"]))
    elif state == "product":
        ap.append(("SkyyBzDetail", BZM["ACTS"]))
        for i, mk in enumerate(BZ_ACTS):
            ap.append(("SkyyBzActs", _cfm(BZ_CF[("SkyyBzBuy1", "SkyyBzBuyStk")[i]]) if cf else mk))
        ap.append(("SkyyBzDetail", BZM["SELLS"]))
        for mk in BZ_SELLS:
            ap.append(("SkyyBzSells", mk))
        ap.append(("SkyyBzDetail", BZM["AMTLAB"]))
        ap.append(("SkyyBzDetail", BZM["AMTROW"]))
        ap.append(("SkyyBzAmtRow", BZ_AMTF))
        ap.append(("SkyyBzDetail", BZM["ABROW"]))
        for i, mk in enumerate(BZ_AB):
            ap.append(("SkyyBzABRow", _cfm(BZ_CF[("SkyyBzABuy", "SkyyBzASell")[i]]) if cf else mk))
        ap.append(("SkyyBzDetail", BZM["AMTHINT"]))
        ap.append(("SkyyBzDetail", BZM["LIM"]))
    else:
        ap.append(("SkyyBzDetail", BZM["NODETTX"]))
    ap.append(("SkyyBzFFoot", BZM["INFO"]))
    ap.append(("SkyyBzFFoot", BZM["FSP"]))
    ap.append(("SkyyBzFFoot", BZM["CLOSE"]))
    return ap


def bz_pick(n):
    # = render()'s tier pick: the biggest cell size whose rows all fit the list (else the normal 74 px cells, the list scrolls)
    for k in (2, 1):
        rows = (n + BZ_GCOLS[k] - 1) // BZ_GCOLS[k]
        if n > 0 and rows * (BZ_CELLS[k] + BZ_CGAP) <= BZ_GRID_IH:
            return k
    return 0


assert [bz_pick(n) for n in (0, 1, 12, 13, 24, 25, 30, 31, 200)] == [0, 2, 2, 1, 1, 1, 1, 0, 0], [bz_pick(n) for n in (0, 1, 12, 13, 24, 25, 30, 31, 200)]
_bz_states = [dict(state=s, cf=c, nsub=ns, ncells=nc, more=mo, empty=em)
              for s, c in (("product", False), ("product", True), ("ah", False), ("none", False))
              for ns in (1, 2, 4) for nc, mo, em in ((5, False, False), (20, False, False), (180, True, False), (0, False, True))]
for _kw in _bz_states:
    _ap = bz_sample(**_kw)
    SUI.check_page(_ap, "SkyyBz")
    SUI.assert_proven(_ap, allow=("search-field",), what="bazaar page 0.1.18 %s (0.1.6 search field: probe page 11 seen by Skyy 2026-09-30)" % _kw)
    SUI.check_sky_paths(_ap, tab_icons=True)
    SUI.assert_menu_page(_ap, BZ_SH, what="bazaar page 0.1.18 %s" % _kw)
    assert SUI.used_width(_ap, "SkyyBzFSub") == BZ_IW, ("0.1.18 the sub-tab row", _kw, SUI.used_width(_ap, "SkyyBzFSub"))
    assert SUI.used_width(_ap, "SkyyBz") == BZ_IW, ("0.1.18 the three columns", SUI.used_width(_ap, "SkyyBz"))
    assert SUI.used_height(_ap, "SkyyBzL") == BZ_CH, ("0.1.18 the left column", SUI.used_height(_ap, "SkyyBzL"))
    assert SUI.used_height(_ap, "SkyyBzM") == BZ_CH, ("0.1.18 the middle column", SUI.used_height(_ap, "SkyyBzM"))
    assert SUI.used_height(_ap, "SkyyBzDetail") <= BZ_DIN_H, ("0.1.18 the detail well", _kw, SUI.used_height(_ap, "SkyyBzDetail"))
    assert SUI.used_width(_ap, "SkyyBzFindRow") == BZ_MW and SUI.used_width(_ap, "SkyyBzHead") == BZ_MW
    assert SUI.used_width(_ap, "SkyyBzFFoot") == BZ_IW and SUI.used_width(_ap, "SkyyBzCfRow") <= BZ_LW
    for _r in ("SkyyBzActs", "SkyyBzSells", "SkyyBzAmtRow", "SkyyBzABRow"):
        assert SUI.used_width(_ap, _r) <= BZ_DIN_W, (_r, SUI.used_width(_ap, _r))
    for _r in range(25):
        if any(p == "SkyyBzRow%d" % _r for p, _mk in _ap):
            assert SUI.used_width(_ap, "SkyyBzRow%d" % _r) <= BZ_GRID_IW, ("0.1.18 a grid row", _r, SUI.used_width(_ap, "SkyyBzRow%d" % _r))
for _gk in (0, 1, 2):
    SUI.assert_menu_page(bz_sample(ncells=BZ_GCOLS[_gk] * 2, gk=_gk), BZ_SH, what="bazaar page 0.1.18 cells tier %d" % _gk)
for _mk in (BZM["TABON"], BZM["TABOFF"]):
    SUI.check_markup(_mk)
    assert SUI.render(_mk).count(BZ_SENT) == 1
_zels = SUI.check_sky_paths(BZ_SH.appends)
assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[BZ_HUB], "Close"} <= set(_zels), "0.1.18: the sky hub page: %s" % _zels
BZ_HUB_JAVA = SUI.java_hub_page(BZ_SH, BZ_TAB, cls=PKG + ".HubBar")
assert BZ_HUB_JAVA == 'com.skyy.bazaar.HubBar.page17(b, ev, "SkyyBzF", "market", "bazaar", 1552, this.playerRef.getUuid(), 2);', BZ_HUB_JAVA


def bz_jcf(parent, normal, cid, var):
    """0.1.14: Java - the gold CONFIRM variant with its run-time label when var is set, else the normal button"""
    cf = BZ_CF[cid]
    line = SUI.java_append(parent, cf)
    lit = SUI.java_value(cf)
    assert line.count(lit) == 1 and BZ_CFS in lit
    line = line.replace(lit, "(%s).replace(%s, %s)" % (lit, SUI.java_value(BZ_CFS), var))
    return "if (%s != null) { %s } else { %s }" % (var, line, SUI.java_append(parent, normal))


_ja = SUI.java_append
BZ_J = {
    "SHELL": BZ_SH.java("b") + "\n" + BZ_HUB_JAVA,      # 0.1.18: the kit 1.7 page + rows 1 / 2 + the X
    "PURSE": "\n".join([_ja("SkyyBzFSub", BZM["SUBGAP"]), _ja("SkyyBzFSub", BZM["PURSE"])]),
    "LEFT": "\n".join([_ja("SkyyBz", BZM["LEFT"]), _ja("SkyyBzL", BZM["TABCOL"])]),
    "TABON": SUI.java_value(BZM["TABON"]),
    "TABOFF": SUI.java_value(BZM["TABOFF"]),
    "LSP": _ja("SkyyBzL", BZM["LSP"]),
    "SELLINV": _ja("SkyyBzL", BZM["SELLINV"]),
    "SELLALL": _ja("SkyyBzL", BZM["SELLALL"]),
    "CF": "\n".join([_ja("SkyyBzL", BZM["CFLAB"]), _ja("SkyyBzL", BZM["CFROW"])] + [_ja("SkyyBzCfRow", mk) for mk in BZ_CFROW]
                    + [_ja("SkyyBzL", BZM["CFNOTE"])]),
    "CGAP": _ja("SkyyBz", BZM["CGAP"]),
    "MID": _ja("SkyyBz", BZM["MID"]),
    "FIND": "\n".join([_ja("SkyyBzM", BZM["FINDROW"])] + [_ja("SkyyBzFindRow", mk) for mk in BZ_FIND]),
    "HEAD": "\n".join([_ja("SkyyBzM", BZM["HEAD"]), _ja("SkyyBzHead", BZM["SUB"]), _ja("SkyyBzHead", BZM["COUNT"])]),
    "GRID": _ja("SkyyBzM", BZM["GRID"]),
    "EMPTYL": _ja("SkyyBzGrid", BZM["EMPTYL"]),
    "MORE": "\n".join([_ja("SkyyBzGrid", BZM["MOREROW"]), _ja("SkyyBzMoreRow", BZM["MORE"])]),
    "DETW": _ja("SkyyBz", BZM["DET"]),
    "NODET": _ja("SkyyBzDetail", BZM["NODETTX"]),
    "DET": "\n".join([_ja("SkyyBzDetail", BZM["DTOP"]), _ja("SkyyBzDTop", BZM["DICON"]), _ja("SkyyBzDTop", BZM["DNAME"])]
                     + [_ja("SkyyBzDetail", mk) for _k, mk in BZ_DLINES]),
    # 0.1.14: an armed button (cfB1 / cfBS / cfAB / cfAS = its 'CONFIRM - <total> coins' label, null = not armed) is drawn as its gold
    # CONFIRM variant (same id, width and place)
    "ACTS": "\n".join([_ja("SkyyBzDetail", BZM["ACTS"]), bz_jcf("SkyyBzActs", BZ_ACTS[0], "SkyyBzBuy1", "cfB1"),
                       bz_jcf("SkyyBzActs", BZ_ACTS[1], "SkyyBzBuyStk", "cfBS"), _ja("SkyyBzDetail", BZM["SELLS"])]
                      + [_ja("SkyyBzSells", mk) for mk in BZ_SELLS]),
    "AMT": "\n".join([_ja("SkyyBzDetail", BZM["AMTLAB"]), _ja("SkyyBzDetail", BZM["AMTROW"]), _ja("SkyyBzAmtRow", BZ_AMTF),
                      _ja("SkyyBzDetail", BZM["ABROW"]), bz_jcf("SkyyBzABRow", BZ_AB[0], "SkyyBzABuy", "cfAB"),
                      bz_jcf("SkyyBzABRow", BZ_AB[1], "SkyyBzASell", "cfAS"), _ja("SkyyBzDetail", BZM["AMTHINT"])]),
    "LIM": _ja("SkyyBzDetail", BZM["LIM"]),
    "AHACTS": "\n".join([_ja("SkyyBzDetail", BZM["AHACTS"]), _ja("SkyyBzActs", BZM["AHOPEN"]), _ja("SkyyBzDetail", BZM["AHNOTE"])]),
    "FOOT": "\n".join([_ja("SkyyBzFFoot", BZM["INFO"]), _ja("SkyyBzFFoot", BZM["FSP"]), _ja("SkyyBzFFoot", BZM["CLOSE"])]),
}
for _k in range(3):
    BZ_J["ROW%d" % _k] = _ja("SkyyBzGrid", BZM["ROWS"][_k])
    _cl = _ja("SkyyBzRow" + SUI.J("r", "0"), BZM["CELLS"][_k])
    assert _cl.count("(p.id)") == 2, _cl                          # the icon item of both cell looks (selected / normal)
    BZ_J["CELL%d" % _k] = _cl.replace("(p.id)", "(cid)")
assert not any("@" in v for v in BZ_J.values())
# 0.1.5: the stack number on the two stack buttons - the sentinel inside the Java string literal becomes " + stk + " (int stk in render)
assert BZ_J["ACTS"].count(BZ_STK) == 2 and sum(v.count(BZ_STK) for v in BZ_J.values()) == 2
BZ_J["ACTS"] = BZ_J["ACTS"].replace(BZ_STK, '" + stk + "')
# 0.1.15 E: SELL <open tab> - the sentinel inside the Java string literal becomes " + tabText(this.cat) + " (letters, digits, spaces)
assert sum(v.count(BZ_SISENT) for v in BZ_J.values()) == 1 and BZ_J["SELLINV"].count(BZ_SISENT) == 1
BZ_J["SELLINV"] = BZ_J["SELLINV"].replace(BZ_SISENT, '" + tabText(this.cat) + "')
# the result line's colour by its words (the 0.1.2 texts carry no + / - / = mark): green done, red refused / failed, yellow asks
BZ_INFO_COLOR = SUI.java_color_by_text("infoColor", [
    ("startsWith", "bought ", "+"), ("startsWith", "sold ", "+"),
    ("contains", "FAILED", "-"), ("contains", "tell an admin", "-"), ("contains", "could not", "-"), ("contains", "not loaded", "-"),
    ("contains", "did not answer", "-"), ("contains", "failed", "-"), ("startsWith", "you need ", "-"), ("startsWith", "not enough", "-"),
    ("contains", "inventory is full", "-"), ("startsWith", "you have no", "-"), ("startsWith", "you only hold", "-"),
    ("startsWith", "Void bags", "-"),
    ("contains", "worth 0 coins", "-"), ("startsWith", "that is not", "-"), ("contains", "price moved", "warning"),
    ("contains", "again within", "warning"), ("contains", "click Confirm", "warning"), ("contains", "click Buy or Sell", "warning"),
    ("contains", "click CONFIRM", "warning"), ("contains", "timed out", "warning")],       # 0.1.14
    empty="=", default="=")
# 0.1.6 fix (review): the runtime header texts measured at their worst case against their labels (the kit only checks static text)
_WC = max((chr(c) for c in range(32, 127)), key=lambda c: SUI.text_width(c, 14))
BZ_TXT_WORST = {
    "header (20 widest characters + ...)": (SUI.text_width("Search: " + _WC * 20 + "...   -   9999 products in all tabs", 14), BZ_MW - BZ_CNT_W),
    "0.1.17 header (both markets)": (SUI.text_width("Search: " + _WC * 20 + "...   -   999 Bazaar + 999 Auction House", 14), BZ_MW - BZ_CNT_W),
    "count (showing)": (SUI.text_width("showing 9999 of 9999", 14), BZ_CNT_W),
    "count (results)": (SUI.text_width("9999 results", 14), BZ_CNT_W),
    "the header line": (SUI.text_width("Instant buy and sell with the market - prices move with every trade and drift back over time", 14), BZ_MW - BZ_CNT_W)}
for _k, (_tw, _lw) in BZ_TXT_WORST.items():
    assert _tw <= _lw, ("0.1.6 text wider than its label", _k, _tw, _lw)
print("0.1.6 text widths (px / label): " + ", ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in BZ_TXT_WORST.items()))
print("page: %d x %d kit 1.7 hub page (content %d x %d: %d | %d | %d), cells %s px (%s a row), %d before Show more, kit %s" % (
    BZ_W, BZ_H, BZ_IW, BZ_CH, BZ_LW, BZ_MW, BZ_RW, BZ_CELLS, BZ_GCOLS, BZ_SHOW, KIT_ID))

page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String sel;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String[] tabs;", page))
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public long confirmUntil;", page))
page.addField(CtField.make("public String confirmWhat;", page))   # 0.1.15 E: "sellinv" (SELL <tab>) or "sellalltabs" (SELL ALL TABS)
page.addField(CtField.make("public String confirmCat;", page))    # 0.1.15 E: the tab SELL <tab> priced
# 0.1.2 custom amount: the last submitted field text (put back on every rebuild) and the totals the player was shown (armBuy / armSell
# = the price for armBQ / armSQ units of armId, -1 = that side is not armed) until armUntil.
page.addField(CtField.make("public String amount;", page))
page.addField(CtField.make("public String armId;", page))
page.addField(CtField.make("public int armBQ;", page))
page.addField(CtField.make("public long armBuy;", page))
page.addField(CtField.make("public int armSQ;", page))
page.addField(CtField.make("public long armSell;", page))
page.addField(CtField.make("public long armUntil;", page))
# 0.1.3: the grid page of the open tab (52 products a page)
page.addField(CtField.make("public int pageNo;", page))
# 0.1.6 search: query = the applied search ("" = the normal tab view), findDraft = the field text (every binding carries it; put back on
# every rebuild), catPage = the tab's grid page when the search started (Clear goes back to it)
page.addField(CtField.make("public String query;", page))
page.addField(CtField.make("public String findDraft;", page))
page.addField(CtField.make("public int catPage;", page))
# 0.1.14: the armed Buy 1 / Buy <stack> (cfAct = "buy1" | "buystk", for cfQ units of cfId at the total cfCost until cfUntil), armForce =
# the custom side was armed by a Buy / Sell click (its button shows CONFIRM whatever the amount), cfSeq = the newest timeout's number,
# cfDraft = the confirm amount field's text (every binding carries it)
page.addField(CtField.make("public String cfAct;", page))
page.addField(CtField.make("public String cfId;", page))
page.addField(CtField.make("public int cfQ;", page))
page.addField(CtField.make("public long cfCost;", page))
page.addField(CtField.make("public long cfUntil;", page))
page.addField(CtField.make("public int cfSeq;", page))
page.addField(CtField.make("public boolean armForce;", page))
page.addField(CtField.make("public String cfDraft;", page))
page.addField(CtField.make("public long cfShown;", page))     # review: when the newest CONFIRM was drawn (0.3 s before a click counts)
# 0.1.17 MARKET MERGE: ahCells = the AH item id of each grid cell (null = a product / empty), ahSel = the selected AH item (never a product:
# sel stays null meanwhile), ahRows = the newest search's AH rows by item id (memory only)
page.addField(CtField.make("public String[] ahCells;", page))
page.addField(CtField.make("public String ahSel;", page))
page.addField(CtField.make("public java.util.HashMap ahRows;", page))
# 0.1.18: showN = the cells the scroll list shows (0 = BZ_SHOW; "more" adds BZ_SHOW; a tab / search starts again)
page.addField(CtField.make("public int showN;", page))
page.addConstructor(CtNewConstructor.make(jt(r"""
public BzPage(@PR@ pr, String sel) {
  super(pr, @LIFE@.CanDismiss);
  this.sel = sel;
  this.info = "";
  this.confirmUntil = 0L;
  this.amount = "";
  this.armId = null;
  this.armBQ = 0;
  this.armBuy = -1L;
  this.armSQ = 0;
  this.armSell = -1L;
  this.armUntil = 0L;
  this.pageNo = 0;
  this.query = "";
  this.findDraft = "";
  this.catPage = 0;
  this.cfAct = null;
  this.cfId = null;
  this.cfQ = 0;
  this.cfCost = -1L;
  this.cfUntil = 0L;
  this.cfSeq = 0;
  this.armForce = false;
  this.cfDraft = "";
  this.cfShown = 0L;
  this.ahCells = new String[@PER@];
  this.ahSel = null;
  this.ahRows = new java.util.HashMap();
  @PKG@.Product p = @PKG@.Catalog.get(sel);
  this.cat = p == null ? null : p.cat;
}""", PER=BZ_PER), page))
page.addMethod(CtNewMethod.make("""
public void disarm() {
  this.armId = null;
  this.armBQ = 0;
  this.armBuy = -1L;
  this.armSQ = 0;
  this.armSell = -1L;
  this.armUntil = 0L;
  this.armForce = false;
  this.cfAct = null;
  this.cfId = null;
  this.cfQ = 0;
  this.cfCost = -1L;
  this.cfUntil = 0L;
}""", page))
# event data for a binding; while the amount field is on the page every binding also carries its current text (@BzAmount)
page.addMethod(CtNewMethod.make(f"""
public {EVD} evd(String a, boolean amt) {{
  {EVD} d = {EVD}.of("a", a);
  if (amt) d = d.append("@BzAmount", "#SkyyBzAmt.Value");
  // 0.1.6: the search field is on every page state - every binding carries its text (kept as the draft; only find applies it)
  d = d.append("@BzFind", "#SkyyBzFind.Value");
  d = d.append("@BzCf", "#SkyyBzCf.Value");   // 0.1.14: the confirm amount field is on every page state too
  return d;
}}""", page))
# 0.1.6 search helpers (static: the harness calls them directly). findNorm: trimmed, inner whitespace runs -> one space, at most 40 chars.
page.addMethod(CtNewMethod.make(r"""
public static String findNorm(String q) {
  if (q == null) return "";
  StringBuilder sb = new StringBuilder();
  boolean sp = false;
  for (int i = 0; i < q.length(); i++) {
    char c = q.charAt(i);
    if (Character.isWhitespace(c) || Character.isISOControl(c)) { sp = sb.length() > 0; continue; }
    if (sp) { if (sb.length() >= 40) break; sb.append(' '); sp = false; }
    if (sb.length() >= 40) break;
    sb.append(c);
  }
  return sb.toString().trim();
}""", page))
# the lower-case words of a normalized search ("" -> none)
page.addMethod(CtNewMethod.make(r"""
public static String[] findWords(String q) {
  String n = findNorm(q).toLowerCase(java.util.Locale.ROOT);
  if (n.length() == 0) return new String[0];
  java.util.ArrayList out = new java.util.ArrayList();
  int i = 0;
  while (i < n.length()) {
    int j = n.indexOf(' ', i);
    if (j < 0) j = n.length();
    if (j > i) out.add(n.substring(i, j));
    i = j + 1;
  }
  String[] w = new String[out.size()];
  for (int k = 0; k < w.length; k++) w[k] = (String) out.get(k);
  return w;
}""", page))
# true when EVERY word is part of the display name or the item id (the id also with '_' as spaces); case-insensitive
page.addMethod(CtNewMethod.make(jt(r"""
public static boolean findMatch(@PKG@.Product p, String[] w) {
  if (p == null || w == null || w.length == 0) return false;
  String id = p.id == null ? "" : p.id;
  String hay = ((p.name == null ? "" : p.name) + " " + id + " " + id.replace('_', ' ')).toLowerCase(java.util.Locale.ROOT);
  for (int i = 0; i < w.length; i++) if (hay.indexOf(w[i]) < 0) return false;
  return true;
}"""), page))
# every usable product of every tab that matches, each once: tab order, then the tab's own order
page.addMethod(CtNewMethod.make(jt(r"""
public static java.util.ArrayList findAll(String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] w = findWords(q);
  if (w.length == 0) return out;
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayList cats = @PKG@.Catalog.categories();
  for (int c = 0; c < cats.size(); c++) {
    java.util.ArrayList raw = @PKG@.Catalog.inCat((String) cats.get(c));
    for (int i = 0; i < raw.size(); i++) {
      @PKG@.Product p = (@PKG@.Product) raw.get(i);
      if (p == null || seen.contains(p.id) || !findMatch(p, w)) continue;
      seen.add(p.id);
      if (@PKG@.Catalog.usable(p.id)) out.add(p);
    }
  }
  return out;
}"""), page))
# 0.1.17 MARKET MERGE - the ONE search: every matching product (findAll) + every matching Auction House item (BzMarket.ahFind = SkyyAuctions'
# ah:fn:find; empty without it), sorted by tier, then name, then Bazaar before AH, then id (BzMkSort; Skyy 2026-10-16 "sort everything by
# tier"). Returns Product / Object[] (an AH row) entries; ahRows = the AH rows by item id.
page.addMethod(CtNewMethod.make(jt(r"""
public java.util.ArrayList marketFind(String q) {
  java.util.ArrayList bz = findAll(q);
  java.util.ArrayList ah = @PKG@.BzMarket.ahFind(q);
  java.util.HashMap rows = new java.util.HashMap();
  java.util.ArrayList keys = new java.util.ArrayList();
  for (int i = 0; i < bz.size(); i++) {
    @PKG@.Product p = (@PKG@.Product) bz.get(i);
    String nm = p.name == null ? p.id : p.name;
    keys.add(new Object[] { Integer.valueOf(@PKG@.BzMarket.tier(p.id, -1)), nm.toLowerCase(java.util.Locale.ROOT), Integer.valueOf(0), p.id, p });
  }
  for (int i = 0; i < ah.size(); i++) {
    Object[] r = (Object[]) ah.get(i);
    String id = (String) r[0];
    if (rows.containsKey(id)) continue;
    rows.put(id, r);
    keys.add(new Object[] { Integer.valueOf(@PKG@.BzMarket.tier(id, ((Integer) r[7]).intValue())), ((String) r[1]).toLowerCase(java.util.Locale.ROOT), Integer.valueOf(1), id, r });
  }
  java.util.Collections.sort(keys, new @PKG@.BzMkSort());
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < keys.size(); i++) out.add(((Object[]) keys.get(i))[4]);
  this.ahRows = rows;
  return out;
}"""), page))
# lim = {{afford (-1 = coin bank error; already capped by room and MAXQ), room, held}}. null = OK, else why the amount is refused.
page.addMethod(CtNewMethod.make(f"""
public static String buyWhy(int q, int[] lim) {{
  int afford = lim[0];
  int room = lim[1];
  if (afford < 0) return "the coin bank did not answer - try again";
  if (q < 1) return room <= 0 ? "your inventory is full" : (afford <= 0 ? "you cannot afford even 1" : "type 1 or more");
  if (q > {PKG}.Trader.MAXQ) return "at most " + {PKG}.Trader.MAXQ + " per trade";
  if (q > room) return room <= 0 ? "your inventory is full" : "only " + room + " fit in your inventory";
  if (q > afford) return afford <= 0 ? "you cannot afford even 1" : "your purse covers " + afford + " at most";
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static String sellWhy(int q, int held) {{
  if (held <= 0) return "you have none to sell";
  if (q < 1) return "type 1 or more";
  if (q > {PKG}.Trader.MAXQ) return "at most " + {PKG}.Trader.MAXQ + " per trade";
  if (q > held) return "you only hold " + held;
  return null;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public int[] limits({PLA} p, java.util.UUID u, String id) {{
  int bagH = {PKG}.Bags.count(u, id);
  long hl = (long) {PKG}.Inv.count(p, id) + (long) bagH;
  int held = hl > 2000000000L ? 2000000000 : (int) hl;
  int room = {PKG}.Trader.room(p, id);
  int afford = -1;
  if ({PKG}.Coins.ready()) {{
    long purse = {PKG}.Coins.get(u);
    if (purse >= 0L) afford = {PKG}.Market.maxBuyable(id, purse, room < {PKG}.Trader.MAXQ ? room : {PKG}.Trader.MAXQ);
  }}
  return new int[] {{ afford, room, held, bagH }};
}}""", page))
# 0.1.3: a tab name drawn inline: letters, digits and spaces only (the kit's proven inline charset), at most 16
page.addMethod(CtNewMethod.make(r"""
public static String tabText(String c) {
  if (c == null) return "Tab";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < c.length() && sb.length() < 16; i++) {
    char ch = c.charAt(i);
    if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == ' ') sb.append(ch);
  }
  String t = sb.toString().trim();
  return t.length() == 0 ? "Tab" : t;
}""", page))
page.addMethod(CtNewMethod.make(BZ_INFO_COLOR, page))
page.addMethod(CtNewMethod.make(r"""
public static String cfText(long c) {
  String n;
  if (c < 10000000L) n = String.valueOf(c < 0L ? 0L : c);
  else if (c < 10000000000L) n = ((c + 999999L) / 1000000L) + "M";
  else if (c < 10000000000000L) n = ((c + 999999999L) / 1000000000L) + "B";
  else n = ((c + 999999999999L) / 1000000000000L) + "T";
  return "CONFIRM - " + n + " coins";
}""", page))
# the whole page (build() only resolves the player; render() is also what the offline markup check calls). 0.1.18: the kit 1.7 hub page -
# the sub-tab row (+ the purse), LEFT (bag tabs, sells, the confirm amount), MIDDLE (search, header, the cell scroll list), RIGHT (detail),
# the footer (result line + Close). Every id, payload and text of 0.1.17 is kept; the cells are one scroll list (no pager).
page.addMethod(CtNewMethod.make(jt(r"""
public void render(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ player) {
  java.util.ArrayList cats = @PKG@.Catalog.categories();
  if (this.cat == null || !cats.contains(this.cat)) { this.cat = cats.isEmpty() ? null : (String) cats.get(0); this.pageNo = 0; }
  if (this.sel != null && !@PKG@.Catalog.usable(this.sel)) this.sel = null;
  boolean ahOn = @PKG@.BzMarket.ahOn();   // 0.1.17: SkyyAuctions 0.1.9+ is there (the AUCTION HOUSE sub-tab + AH search results)
  boolean ahView = ahOn && @PKG@.BzMarket.ahViewOn();   // 0.1.18: SkyyAuctions 0.1.10+ (CREATE BIN + MANAGE sub-tabs)
  boolean coinsOk = @PKG@.Coins.ready();
  boolean confirming = System.currentTimeMillis() <= this.confirmUntil;
  boolean saOn = confirming && "sellalltabs".equals(this.confirmWhat);   // 0.1.15 E: which sell button shows Confirm sell
  boolean siOn = confirming && !saOn;
  @PKG@.Product sp = @PKG@.Catalog.get(this.sel);
  boolean amtOn = sp != null && player != null;
  java.util.ArrayList list = new java.util.ArrayList();
  // 0.1.6: a search lists the matches of EVERY tab instead of the open tab
  boolean searching = this.query != null && this.query.length() > 0;
  if (searching) list = marketFind(this.query);   // 0.1.17: both markets, sorted by tier
  else {
    this.ahRows = new java.util.HashMap();
    java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : @PKG@.Catalog.inCat(this.cat);
    for (int i = 0; i < raw.size(); i++) { @PKG@.Product q = (@PKG@.Product) raw.get(i); if (@PKG@.Catalog.usable(q.id)) list.add(q); }
  }
  // 0.1.17: an AH selection lives only while its item is in the current search results
  if (this.ahSel != null && (!searching || this.ahRows == null || !this.ahRows.containsKey(this.ahSel))) this.ahSel = null;
  int total = list.size();
  int nAh = 0;
  for (int i = 0; i < total; i++) { if (!(list.get(i) instanceof @PKG@.Product)) nAh++; }
  // 0.1.18: ONE scroll list - the first showN cells (Show more adds @SHOW@), never pages
  int showN = this.showN > 0 ? this.showN : @SHOW@;
  int n = total < showN ? total : showN;
  long pv = coinsOk ? @PKG@.Coins.get(u) : 0L;
  boolean purseOk = coinsOk && pv >= 0L;
  String purse = coinsOk ? (pv >= 0L ? ("Purse  " + pv + " coins") : "Purse unavailable - coin bank error") : "SkyyCoins is not loaded - trading is off";
  int nt = cats.size() < @MAXT@ ? cats.size() : @MAXT@;
  int hidC = cats.size() - nt;
  String sub = "Instant buy and sell with the market - prices move with every trade and drift back over time";
  if (hidC > 0) sub = hidC + " more tabs do not fit the page (" + @MAXT@ + " tabs) - tell an admin";
  // 0.1.6 fix: the header shows at most 20 characters of the search (the field keeps the full text) so a 40-character search fits
  String qs = this.query == null ? "" : this.query;
  if (qs.length() > 20) qs = qs.substring(0, 20) + "...";
  if (searching) sub = "Search: " + qs + "   -   " + total + (total == 1 ? " product" : " products") + " in all tabs";
  if (searching && ahOn) sub = "Search: " + qs + "   -   " + (total - nAh) + " Bazaar + " + nAh + " Auction House";   // 0.1.17
@SHELL@
  // the ONE sub-tab row: BAZAAR (this sub-view) | AUCTION HOUSE | CREATE BIN | MANAGE (SkyyAuctions) + the purse at its right end
  @PKG@.HubBar.subTab(b, ev, "SkyyBzF", 0, "Bazaar", true, (String) null, @SUBW@);
  ev.addEventBinding(@BT@.Activating, "#SkyyBzFSub0", evd("mk:bz", amtOn));
  int ns = 1;
  if (ahOn) {
    @PKG@.HubBar.subTab(b, ev, "SkyyBzF", 1, "Auction House", false, (String) null, @SUBW@);
    ev.addEventBinding(@BT@.Activating, "#SkyyBzFSub1", evd("mk:ah", amtOn));
    ns = 2;
  }
  if (ahView) {
    @PKG@.HubBar.subTab(b, ev, "SkyyBzF", 2, "Create BIN", false, (String) null, @SUBW@);
    ev.addEventBinding(@BT@.Activating, "#SkyyBzFSub2", evd("mk:create", amtOn));
    @PKG@.HubBar.subTab(b, ev, "SkyyBzF", 3, "Manage", false, (String) null, @SUBW@);
    long owed = @PKG@.BzMarket.ahOwed(u);
    if (owed > 0L) b.set("#SkyyBzFSub3.Text", "Manage (" + owed + ")");
    ev.addEventBinding(@BT@.Activating, "#SkyyBzFSub3", evd("mk:manage", amtOn));
    ns = 4;
  }
  int pw = @IW@ - ns * @SUBW@ - ns * @SUBGAP@;
@PURSE@
  b.set("#SkyyBzPurse.Text", purse);
  // LEFT: the bag tabs (an in-page list; a search shows none selected), SELL <tab> / SELL ALL TABS, the confirm amount
@LEFT@
  this.tabs = new String[nt];
  for (int i = 0; i < nt; i++) {
    String c = (String) cats.get(i);
    this.tabs[i] = c;
    boolean ton = !searching && c.equals(this.cat);
    b.appendInline("#SkyyBzTabs", (ton ? (@TABON@) : (@TABOFF@)).replace("@SENT@", tabText(c)));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzTab" + i, evd("tab:" + i, amtOn));
  }
@LSP@
@SELLINV@
  ev.addEventBinding(@BT@.Activating, "#SkyyBzSellInv", evd("sellinv", amtOn));
@SELLALL@
  ev.addEventBinding(@BT@.Activating, "#SkyyBzSellAllTabs", evd("sellalltabs", amtOn));   // 0.1.15 E
@CF@
  // 0.1.14: the player's confirm amount (their draft while they type, else what is saved / the server default) + Set / Enter
  String cfv = (this.cfDraft != null && this.cfDraft.length() > 0) ? this.cfDraft : String.valueOf(@PKG@.BzConfirm.get(u));
  b.set("#SkyyBzCf.Value", cfv);
  b.set("#SkyyBzCfNote.Text", @PKG@.BzConfirm.switchOn(u) ? "@CFN0@" : "@CFN1@");
  ev.addEventBinding(@BT@.Validating, "#SkyyBzCf", evd("cfset", amtOn), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyBzCfSet", evd("cfset", amtOn));
@CGAP@
  // MIDDLE: the one search, the header + count, the cells
@MID@
@FIND@
  String fd = this.findDraft == null ? "" : this.findDraft;
  if (fd.length() > 0) b.set("#SkyyBzFind.Value", fd);
  ev.addEventBinding(@BT@.Validating, "#SkyyBzFind", evd("find", amtOn), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyBzFindGo", evd("find", amtOn));
  ev.addEventBinding(@BT@.Activating, "#SkyyBzFindClr", evd("fclear", amtOn));
@HEAD@
  b.set("#SkyyBzSub.Text", sub);
  String cnt = total <= 0 ? "" : (n < total ? ("showing " + n + " of " + total) : (total + (searching ? (total == 1 ? " result" : " results") : (total == 1 ? " product" : " products"))));
  b.set("#SkyyBzCount.Text", cnt);
@GRID@
  // Skyy rule 7: the biggest cell size whose rows all fit the list (else the normal cells and the list scrolls)
  int[] gc = new int[] { @GC0@, @GC1@, @GC2@ };
  int[] gh = new int[] { @GH0@, @GH1@, @GH2@ };
  int gk = 0;
  for (int k = 2; k >= 1; k--) {
    int rws = (n + gc[k] - 1) / gc[k];
    if (gk == 0 && n > 0 && rws * (gh[k] + @CELLGAP@) <= @GIH@) gk = k;
  }
  int cols = gc[gk];
  this.cells = new String[n];
  this.ahCells = new String[n];
  java.util.HashMap bagm = player == null ? new java.util.HashMap() : @PKG@.Bags.all(u);
  int nr = (n + cols - 1) / cols;
  for (int r = 0; r < nr; r++) {
    if (gk == 2) { @ROW2@ } else if (gk == 1) { @ROW1@ } else { @ROW0@ }
    for (int k = 0; k < cols; k++) {
      int idx = r * cols + k;
      if (idx >= n) break;
      // 0.1.17: a cell is a Bazaar product or (in a search) an Auction House item (Object[] row; its corner says "AH <listings>")
      Object lo = list.get(idx);
      @PKG@.Product p = null;
      Object[] ar = null;
      if (lo instanceof @PKG@.Product) p = (@PKG@.Product) lo;
      else ar = (Object[]) lo;
      String cid;
      boolean con;
      if (p != null) { cid = p.id; this.cells[idx] = p.id; this.ahCells[idx] = null; con = p.id.equals(this.sel); }
      else { cid = (String) ar[0]; this.cells[idx] = null; this.ahCells[idx] = cid; con = cid.equals(this.ahSel); }
      if (gk == 2) { @CELL2@ } else if (gk == 1) { @CELL1@ } else { @CELL0@ }
      if (p != null) {
        int held = player == null ? 0 : @PKG@.Inv.count(player, p.id) + @PKG@.Bags.held(bagm, u, p.id);
        // review fix: the cell label fits 7 digits - 10,000,000+ (a raised bag cap) shows as 12.3M; "You hold" keeps the exact number
        if (held > 0) b.set("#SkyyBzCell" + idx + "Qty.Text", held >= 10000000 ? (held / 1000000) + "." + ((held / 100000) % 10) + "M" : String.valueOf(held));
      } else b.set("#SkyyBzCell" + idx + "Qty.Text", "AH " + ((Integer) ar[2]).intValue());
      ev.addEventBinding(@BT@.Activating, "#SkyyBzCell" + idx, evd("cell:" + idx, amtOn));
    }
  }
  if (n == 0) {
@EMPTYL@
    b.set("#SkyyBzEmpty.Text", searching ? "No matches - try fewer letters or Clear" : "No products in this tab");
  }
  if (n < total) {
@MORE@
    ev.addEventBinding(@BT@.Activating, "#SkyyBzMore", evd("more", amtOn));
  }
@CGAP@
  // RIGHT: the detail well - an Auction House cell's detail, a product's trade panel, or the hint
@DETW@
  Object[] ahd = null;
  if (!amtOn && this.ahSel != null && this.ahRows != null) ahd = (Object[]) this.ahRows.get(this.ahSel);
  if (ahd != null) {
    String id = (String) ahd[0];
    int an = ((Integer) ahd[2]).intValue();
    long aEach = ((Long) ahd[3]).longValue();
    long aPrice = ((Long) ahd[4]).longValue();
    long aQty = ((Long) ahd[5]).longValue();
    int aHeld = player == null ? 0 : @PKG@.Inv.count(player, id);
@DET@
    b.set("#SkyyBzDName.Text", "Auction House - " + (String) ahd[1]);
    b.set("#SkyyBzDBuy.Text", "Buy It Now from " + aEach + " coins each   -   the cheapest listing: " + aPrice + " coins for " + aQty);
    b.set("#SkyyBzDSell.Text", "To sell yours, list it there with Create BIN   -   you hold " + aHeld + " in your inventory");
    b.set("#SkyyBzDHold.Text", an + (an == 1 ? " listing" : " listings") + "   -   the next one ends in " + (String) ahd[6]);
    b.set("#SkyyBzDDem.Text", "Player listings: the sellers set these prices - market demand does not move them");
    b.set("#SkyyBzDProc.Text", "This is the Auction House, not the Bazaar - the Bazaar never trades listings");
@AHACTS@
    b.set("#SkyyBzAhNote.Text", "@AHNOTE@");
    ev.addEventBinding(@BT@.Activating, "#SkyyBzAhOpen", evd("ahopen", false));
@LIM@
    b.set("#SkyyBzLimits.Text", "Open in Auction House to buy - every listing of this item, cheapest first");
  } else if (!amtOn) {
@NODET@
  } else {
    String id = sp.id;
    int stk = @PKG@.Trader.stack(id);
    long b1 = @PKG@.Market.quote(id, 1, true), bS = @PKG@.Market.quote(id, stk, true);
    long s1 = @PKG@.Market.quote(id, 1, false), sS = @PKG@.Market.quote(id, stk, false);
    int[] lim = limits(player, u, id);
    int held = lim[2];
    // 0.1.14: which buttons are armed right now (their CONFIRM label; null = the normal button)
    long nowR = System.currentTimeMillis();
    String cfB1 = null;
    String cfBS = null;
    String cfAB = null;
    String cfAS = null;
    if (this.cfAct != null && nowR <= this.cfUntil && id.equals(this.cfId)) {
      if (this.cfAct.equals("buy1")) cfB1 = cfText(this.cfCost);
      else if (this.cfAct.equals("buystk")) cfBS = cfText(this.cfCost);
    }
    if (nowR <= this.armUntil && id.equals(this.armId)) {
      if (this.armBuy > 0L && (this.armForce || @PKG@.BzConfirm.needs(u, this.armBuy))) cfAB = cfText(this.armBuy);
      if (this.armSell > 0L) cfAS = cfText(this.armSell);
    }
    long sAll = held > 0 ? @PKG@.Market.quote(id, held > @PKG@.Trader.MAXQ ? @PKG@.Trader.MAXQ : held, false) : 0L;
    double f = @PKG@.Market.factor(id);
@DET@
    b.set("#SkyyBzDName.Text", sp.name);
    b.set("#SkyyBzDBuy.Text", "Instant buy   " + b1 + " coins for 1   -   " + bS + " for " + stk + "   -   about " + @PKG@.BzUtil.num(@PKG@.Market.unit(id, true)) + " each");
    b.set("#SkyyBzDSell.Text", "Instant sell   " + s1 + " coins for 1   -   " + sS + " for " + stk + "   -   about " + @PKG@.BzUtil.num(@PKG@.Market.unit(id, false)) + " each");
    b.set("#SkyyBzDHold.Text", "You hold " + held + (lim[3] > 0 ? " (" + lim[3] + " in the Void)" : "") + (held > 0 ? "   -   selling all pays " + sAll + " coins" : ""));
    b.set("#SkyyBzDDem.Text", "Demand " + @PKG@.BzUtil.num(f) + "x   -   buying pushes it up and selling pushes it down - it drifts back to 1.0x");
    b.set("#SkyyBzDProc.Text", @PKG@.Catalog.procLine(sp));
@ACTS@
    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuy1", evd("buy1", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuyStk", evd("buystk", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzSell1", evd("sell1", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzSellStk", evd("sellstk", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzSellAll", evd("sellall", true));
@AMT@
    if (this.amount != null && this.amount.length() > 0) b.set("#SkyyBzAmt.Value", this.amount);
    b.set("#SkyyBzAmtHint.Text", "Enter shows the price");
    ev.addEventBinding(@BT@.Validating, "#SkyyBzAmt", evd("amt", true), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyBzABuy", evd("abuy", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzASell", evd("asell", true));
    int mq = @PKG@.Trader.MAXQ;
    String lt;
    if (!coinsOk) lt = "SkyyCoins is not loaded - trading is off.";
    else if (@PKG@.Trader.busy(u)) lt = "Your profile is still loading - trading is paused. Click again in a moment.";
    else if (lim[0] < 0) lt = "The coin bank did not answer - buy limit unknown. You can sell up to " + (held > mq ? mq : held) + ".";
    else {
      int mb = lim[0];
      String why = mb >= mq ? "the per-trade limit" : (mb >= lim[1] ? (lim[1] <= 0 ? "your inventory is full" : "inventory room") : "your purse");
      lt = "You can buy up to " + mb + " (" + why + ") and sell up to " + (held > mq ? mq : held) + ".   Amounts like 500, 2k or max.";
    }
@LIM@
    b.set("#SkyyBzLimits.Text", lt);
  }
  // FOOTER: the result line + Close
@FOOT@
  b.set("#SkyyBzInfo.Text", this.info == null ? "" : this.info);
  ev.addEventBinding(@BT@.Activating, "#SkyyBzClose", evd("close", amtOn));
}""", SHOW=BZ_SHOW, MAXT=BZ_MAXT, SENT=BZ_SENT, SUBW=BZ_SUB_W, SUBGAP=SUI.SUB_TAB_GAP, IW=BZ_IW, CELLGAP=BZ_CGAP, GIH=BZ_GRID_IH,
   GC0=BZ_GCOLS[0], GC1=BZ_GCOLS[1], GC2=BZ_GCOLS[2], GH0=BZ_CELLS[0], GH1=BZ_CELLS[1], GH2=BZ_CELLS[2],
   CFN0=BZ_CF_NOTES[0], CFN1=BZ_CF_NOTES[1], AHNOTE=BZ_AH_NOTE, **BZ_J), page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  render(b, ev, u, player);
}}""", page))
# ---- 0.1.14 the CONFIRM flow. schedRevert: a confirm shown now turns back by itself when its time runs out - ONE delayed task (the
# server scheduler -> the player's world thread, BzRevert), never a periodic update; a newer confirm or any click makes it a no-op (cfSeq).
page.addMethod(CtNewMethod.make(jt(r"""
public java.util.UUID worldUuid() {
  return this.playerRef.getWorldUuid();
}"""), page))
page.addMethod(CtNewMethod.make(jt(r"""
public void schedRevert(long ms) {
  this.cfSeq = this.cfSeq + 1;
  this.cfShown = System.currentTimeMillis();   // every CONFIRM drawn by a click schedules its timeout here
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.BzRevert(this, this.cfSeq, false), ms + 250L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.BzUtil.warn("could not schedule the confirm timeout: " + t); }
}""", HSV=HSV), page))
# world thread: nothing armed any more (a click answered it) or a newer confirm -> nothing; still the open page and the time ran out ->
# the confirm is cancelled and ONLY the result line is updated (review: a redraw would wipe text typed since the last click); the stale
# CONFIRM button only asks again when clicked
page.addMethod(CtNewMethod.make(jt(r"""
public void revert(int seq) {
  try {
    if (seq != this.cfSeq) return;
    long now = System.currentTimeMillis();
    boolean cf = this.cfAct != null;
    boolean am = this.armId != null && (this.armBuy > 0L || this.armSell > 0L);
    boolean si = this.confirmUntil > 0L;
    if (!cf && !am && !si) return;
    if ((cf && now <= this.cfUntil) || (am && now <= this.armUntil) || (si && now <= this.confirmUntil)) return;
    com.hypixel.hytale.component.Ref hr = this.playerRef.getReference();
    if (hr == null || !hr.isValid()) return;
    com.hypixel.hytale.component.Store hs = hr.getStore();
    if (hs == null) return;
    @PLA@ hp = (@PLA@) hs.getComponent(hr, @PLA@.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    disarm();
    this.confirmUntil = 0L;
    this.info = "the confirm timed out - nothing was bought or sold (a click asks again)";
    com.hypixel.hytale.server.core.ui.builder.UICommandBuilder hb = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();
    hb.set("#SkyyBzInfo.Text", this.info);
    sendUpdate(hb, false);
  } catch (Throwable t) { @PKG@.BzUtil.warn("bazaar confirm timeout failed: " + t); }
}"""), page))
page.addMethod(CtNewMethod.make(jt(r"""
public void arm(String act, String id, int q, long cost, long now) {
  this.cfAct = act;
  this.cfId = id;
  this.cfQ = q;
  this.cfCost = cost;
  this.cfUntil = now + 10000L;
  schedRevert(10000L);
}"""), page))
# Buy 1 / Buy <stack>: the armed button clicked again (same product, same amount, in time) buys with the shown total as the cap; else a
# total below the player's confirm amount buys at once (capped at that total - a price that rose in between asks again); else - or when
# buy0 would refuse anyway (no coins, purse short, inventory full, profile loading: buyC answers why) - arm. null = armed (info set).
page.addMethod(CtNewMethod.make(jt(r"""
public @TR@ buyClick(@PLA@ p, java.util.UUID u, String who, String a, int q, boolean hit, long seen, int seenQ, long now) {
  String id = this.sel;
  if (hit && seenQ == q && seen > 0L) {
    @TR@ r = @PKG@.Trader.buyC(p, u, who, id, q, seen);
    if (r != null && r.moved && r.price > 0L) arm(a, id, q, r.price, now);
    return r;
  }
  @PKG@.Product sp = @PKG@.Catalog.get(id);
  if (id == null || sp == null || q < 1 || !@PKG@.Catalog.usable(id) || !@PKG@.Coins.ready() || @PKG@.Trader.busy(u) || @PKG@.Trader.eterWhy(u, id) != null) return @PKG@.Trader.buyC(p, u, who, id, q, 0L);   // 0.1.19: + a locked Eternal seed (never armed)
  long c = @PKG@.Market.quote(id, q, true);
  if (c <= 0L) return @PKG@.Trader.buyC(p, u, who, id, q, 0L);
  if (!@PKG@.BzConfirm.needs(u, c) || @PKG@.Coins.get(u) < c || @PKG@.Trader.room(p, id) <= 0) {
    @TR@ r0 = @PKG@.Trader.buyC(p, u, who, id, q, c);
    if (r0 != null && r0.moved && r0.price > 0L) arm(a, id, q, r0.price, now);
    return r0;
  }
  arm(a, id, q, c, now);
  long t = @PKG@.BzConfirm.get(u);
  this.info = "Buy " + q + " " + sp.name + " for " + c + " coins - click CONFIRM within 10 s" + (t > 0L ? " (buys of " + t + " coins or more ask first)" : " (every buy asks first)");
  return null;
}""", TR=TR), page))
# the confirm amount field: Set / Enter saves the typed amount (500, 2k, 1m; 0 = every buy asks)
page.addMethod(CtNewMethod.make(jt(r"""
public void cfSet(java.util.UUID u) {
  String t = this.cfDraft == null ? "" : this.cfDraft.trim();
  long v = @PKG@.BzUtil.parseAmt(t);
  if (v < 0L) {
    this.info = t.length() == 0 ? "type an amount of coins first - for example 3000 or 5k (0 = every buy asks)" : "that is not an amount - type a whole number of coins like 3000 or 5k";
    return;
  }
  if (!@PKG@.BzConfirm.set(u, v)) { this.info = "could not save your confirm amount - try again"; return; }
  this.cfDraft = "";
  this.info = v <= 0L ? "saved - every buy now asks you to CONFIRM first" : "saved - buys of " + v + " coins or more ask you to CONFIRM first, smaller ones go through on the first click";
}"""), page))
rvt.addMethod(CtNewMethod.make(jt(r"""
public void run() {
  try {
    if (this.page == null) return;
    if (this.onWorld) { this.page.revert(this.seq); return; }
    if (this.seq != this.page.cfSeq) return;
    java.util.UUID wu = this.page.worldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w != null) w.execute(new @PKG@.BzRevert(this.page, this.seq, true));
  } catch (Throwable t) { }
}""", UNI="com.hypixel.hytale.server.core.universe.Universe"), rvt))
# 0.1.2 custom amount click: a = amt (Enter: price both sides, never trades) | abuy | asell. The price is always shown before a trade:
# an unpriced Buy / Sell click only arms that side; the armed click trades with the shown total as a cap (Trader.buyN / sellN).
page.addMethod(CtNewMethod.make(f"""
public void amountAction({PLA} p, java.util.UUID u, String who, String a, long now) {{
  {PKG}.Product sp = {PKG}.Catalog.get(this.sel);
  if (sp == null || !{PKG}.Catalog.usable(sp.id)) {{ this.info = "click a product first"; disarm(); return; }}
  if (!{PKG}.Coins.ready()) {{ this.info = "SkyyCoins is not loaded - trading is off"; disarm(); return; }}
  // never price or arm a trade that buy0 / sell0 would refuse anyway (profile crash recovery at join)
  if ({PKG}.Trader.busy(u)) {{ this.info = "your profile is still loading - try again in a moment"; disarm(); return; }}
  String id = sp.id;
  String nm = sp.name;
  long v = {PKG}.BzUtil.parseAmt(this.amount);
  if (v == -1L) {{
    boolean empty = this.amount == null || this.amount.trim().length() == 0;
    this.info = empty ? "type an amount first - for example 500 or 2k - or max" : "that is not an amount - type a whole number like 500 or 2k - or max";
    disarm();
    return;
  }}
  int[] lim = limits(p, u, id);
  int mq = {PKG}.Trader.MAXQ;
  int qb = 0;
  int qs = 0;
  if (v == -2L) {{ qb = lim[0] < 0 ? 0 : lim[0]; qs = lim[2] > mq ? mq : lim[2]; }}
  else {{ qb = v > (long) mq ? mq + 1 : (int) v; qs = qb; }}
  if (a.equals("amt")) {{
    String wb = buyWhy(qb, lim);
    if (wb == null) wb = {PKG}.Trader.eterWhy(u, id);   // 0.1.19: a locked Eternal seed is never priced to buy
    String ws = sellWhy(qs, lim[2]);
    long cb = wb == null ? {PKG}.Market.quote(id, qb, true) : -1L;
    long cs = ws == null ? {PKG}.Market.quote(id, qs, false) : -1L;
    if (wb == null && cb <= 0L) wb = "no price right now";
    if (ws == null && cs <= 0L) ws = cs == 0L ? "worth 0 coins - sell more at once" : "no price right now";
    disarm();
    this.armId = id;
    if (wb == null) {{ this.armBQ = qb; this.armBuy = cb; }}
    if (ws == null) {{ this.armSQ = qs; this.armSell = cs; }}
    if (wb == null || ws == null) {{ this.armUntil = now + 15000L; schedRevert(15000L); }}   // 0.1.14: the timeout turns it back
    if (wb == null && ws == null && qb == qs) this.info = qb + " " + nm + " - buy for " + cb + " coins - sell for " + cs + " coins - click Buy or Sell";
    else {{
      String tb = wb == null ? "Buy " + qb + " for " + cb + " coins" : "Buy - " + wb;
      String ts = ws == null ? "Sell " + qs + " for " + cs + " coins" : "Sell - " + ws;
      this.info = nm + "   " + tb + "   /   " + ts;
    }}
    return;
  }}
  boolean buy = a.equals("abuy");
  int q = buy ? qb : qs;
  String why = buy ? buyWhy(qb, lim) : sellWhy(qs, lim[2]);
  if (why == null && buy) why = {PKG}.Trader.eterWhy(u, id);   // 0.1.19: a locked Eternal seed is never armed (buy0 refuses it too)
  if (why != null) {{ this.info = (buy ? "Buy " : "Sell ") + nm + " - " + why; disarm(); return; }}
  boolean armed = now <= this.armUntil && id.equals(this.armId) && (buy ? (this.armBuy > 0L && this.armBQ == q) : (this.armSell > 0L && this.armSQ == q));
  long seenD = -1L;
  if (!armed) {{
    // max / all is worked out again on every click; if this side was priced for a different max a moment ago (prices, the purse or
    // the inventory changed), say so instead of a plain re-quote (a fixed number that moved is reported by Trader.buyN0 / sellN0)
    int was = 0;
    if (v == -2L && now <= this.armUntil && id.equals(this.armId)) was = buy ? (this.armBuy > 0L ? this.armBQ : 0) : (this.armSell > 0L ? this.armSQ : 0);
    long c = {PKG}.Market.quote(id, q, buy);
    disarm();
    if (c <= 0L) {{ this.info = c == 0L ? q + " " + nm + " is worth 0 coins right now - sell more at once" : "price error - tell an admin"; return; }}
    // 0.1.14: a buy below the player's confirm amount goes through on this first click, capped at the total just worked out (a price
    // that rose in between is refused by buyN and asked again); a sell, a changed max or a total at / above the amount asks CONFIRM
    boolean direct = buy && was <= 0 && !{PKG}.BzConfirm.needs(u, c);
    if (!direct) {{
      this.armId = id;
      if (buy) {{ this.armBQ = q; this.armBuy = c; }} else {{ this.armSQ = q; this.armSell = c; }}
      this.armUntil = now + 10000L;
      this.armForce = true;
      String pre = was > 0 && was != q ? "your max changed from " + was + " to " + q + " - " : "";
      this.info = pre + (buy ? "Buy " : "Sell ") + q + " " + nm + " for " + c + " coins - click CONFIRM within 10 s";
      schedRevert(10000L);
      return;
    }}
    seenD = c;
  }}
  long seen = seenD > 0L ? seenD : (buy ? this.armBuy : this.armSell);
  {TR} r = null;
  if (buy) r = {PKG}.Trader.buyN(p, u, who, id, q, seen);
  else r = {PKG}.Trader.sellN(p, u, who, id, q, seen);
  disarm();
  if (r == null) return;
  if (r.moved && r.price > 0L) {{
    this.armId = id;
    if (buy) {{ this.armBQ = q; this.armBuy = r.price; }} else {{ this.armSQ = q; this.armSell = r.price; }}
    this.armUntil = now + 10000L;
    this.armForce = true;      // 0.1.14: the moved price asks CONFIRM
    schedRevert(10000L);
  }}
  if (r.alert) this.playerRef.sendMessage({MSG}.raw("[Bazaar] " + r.msg));
  this.info = r.msg;
}}""", page))
# 0.1.18: rows 1 + 2 (kit 1.7 HubBar.route: row 1 hub:h:<id> - Home, another hub, this hub = self; row 2 hub:<tab>; the X hub:close)
# 0.1.13: a hub bar click (HubBar.handle FIRST, HUBS-CONTRACT 2.6): the X closes; "< Menu" (/skymenu), another tab (its open Function or
# its command) and the Bazaar tab itself are done (no redraw: a typed amount / search stays); a tab that could not open (hidden / missing
# / failed) answers on the result line. false = not a hub click (the page goes on as 0.1.12).
# review fix (2026-10-15): a handled hub click that leaves this page open (its own tab, "< Menu" / a command still on its way, a
# Function that answered TRUE without a page) is ANSWERED - a no-op update (the hub title set to itself): the client's "Loading..."
# ends and typed text stays. Never to a page that is no longer the open page (another tab replaced it).
page.addMethod(CtNewMethod.make(jt(r"""
public void hubAck() {
  try {
    com.hypixel.hytale.component.Ref hr = this.playerRef.getReference();
    if (hr == null || !hr.isValid()) return;
    com.hypixel.hytale.component.Store hs = hr.getStore();
    if (hs == null) return;
    com.hypixel.hytale.server.core.entity.entities.Player hp = (com.hypixel.hytale.server.core.entity.entities.Player) hs.getComponent(hr, com.hypixel.hytale.server.core.entity.entities.Player.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    com.hypixel.hytale.server.core.ui.builder.UICommandBuilder hb = new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder();
    hb.set("#SkyyBzFTitle.Text", "Market");
    sendUpdate(hb, false);
  } catch (Throwable t) { }
}"""), page))
page.addMethod(CtNewMethod.make(jt(r"""
public boolean hubClick(String data) {
  String r = null;
  try { r = @PKG@.HubBar.route(this.playerRef, data, "market", "bazaar"); } catch (Throwable t) { r = null; }   // 0.1.18: rows 1 + 2
  if (r == null) return false;
  if (r.equals("close")) { try { close(); } catch (Throwable tc) { @PKG@.BzUtil.warn("bazaar page hub close failed: " + tc); } return true; }
  if (r.equals("self") || r.equals("back") || r.equals("bridge") || r.equals("command")) { hubAck(); return true; }
  this.info = "That tab could not open right now - try again.";
  try { rebuild(); } catch (Throwable tr) { }
  return true;
}"""), page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  if (hubClick(data)) return;   // 0.1.13: the hub bar
  try {{
    if (data == null) return;
    // 0.1.2: the action is matched exactly (SkyyGuilds pattern) - text typed into the amount field can never look like a payload
    String a = {PKG}.BzUtil.jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    long now = System.currentTimeMillis();
    // while the amount field is on the page every binding carries its text - keep what was typed across clicks and rebuilds
    if (data.indexOf("\\"@BzAmount\\"") >= 0) {{
      String v = {PKG}.BzUtil.jsonStr(data, "@BzAmount").trim();
      if (v.length() > 12) v = v.substring(0, 12);
      this.amount = v;
    }}
    // 0.1.6: every binding carries the search field text - keep it as the draft (only Enter / Search apply it)
    if (data.indexOf("\\"@BzFind\\"") >= 0) this.findDraft = findNorm({PKG}.BzUtil.jsonStr(data, "@BzFind"));
    // 0.1.14: the confirm amount field's text (only Set / Enter saves it)
    if (data.indexOf("\\"@BzCf\\"") >= 0) {{
      String cv = {PKG}.BzUtil.jsonStr(data, "@BzCf").trim();
      if (cv.length() > 12) cv = cv.substring(0, 12);
      this.cfDraft = cv;
    }}
    // 0.1.14 review: a click on a CONFIRM sooner than 0.3 s after it was drawn (a double-click) is answered but does not count
    boolean soonCf = (a.equals("buy1") || a.equals("buystk")) && a.equals(this.cfAct) && this.cfId != null && this.cfId.equals(this.sel) && now <= this.cfUntil;
    boolean soonAm = (a.equals("abuy") || a.equals("asell")) && this.armForce && now <= this.armUntil;
    boolean soonSi = (a.equals("sellinv") || a.equals("sellalltabs")) && a.equals(this.confirmWhat) && now <= this.confirmUntil;
    if ((soonCf || soonAm || soonSi) && now - this.cfShown < 300L) {{ rebuild(); return; }}
    // 0.1.14: an armed Buy 1 / Buy <stack> clicked again in time (read before the disarm below - any other click turns it back)
    boolean cfHit = (a.equals("buy1") || a.equals("buystk")) && a.equals(this.cfAct) && now <= this.cfUntil && this.cfId != null && this.cfId.equals(this.sel);
    long cfSeen = this.cfCost;
    int cfSeenQ = this.cfQ;
    // any click other than the Sell inventory button itself cancels a pending "Confirm sell"
    // (selecting another item or trading must never leave the full-inventory sell armed)
    // 0.1.15 E: SELL <tab> / SELL ALL TABS - a click on the OTHER sell button cancels too
    boolean sellInvClick = a.equals("sellinv") || a.equals("sellalltabs");
    if (!sellInvClick || !a.equals(this.confirmWhat)) this.confirmUntil = 0L;
    // the same for a priced custom amount: only the amount field / its Buy and Sell buttons keep it armed
    boolean amtAct = a.equals("amt") || a.equals("abuy") || a.equals("asell");
    if (!amtAct) disarm();
    // 0.1.3: the footer Close (the vanilla way out next to Esc)
    if (a.equals("close")) {{ close(); return; }}
    // 0.1.17 MARKET MERGE: AUCTION HOUSE (the sub-view switch; the search text comes along) / OPEN IN AUCTION HOUSE (that item's listings)
    // -> SkyyAuctions' ah:fn:open replaces this page; without it /ah runs as the player (permission checks as typed); else one line
    // 0.1.18: BAZAAR (this sub-view) answers in place; CREATE BIN / MANAGE open the Auction House on that view (ah:fn:view, SkyyAuctions
    // 0.1.10+); MANAGE without it runs /ah manage as the player (permission checks as typed); else one line
    if (a.equals("mk:bz")) {{ this.info = ""; rebuild(); return; }}
    if (a.equals("mk:create") || a.equals("mk:manage")) {{
      String vw = a.equals("mk:create") ? "create" : "manage";
      if ({PKG}.BzMarket.ahView(u, vw)) {{ hubAck(); return; }}
      if (vw.equals("manage") && {PKG}.HubBar.run(this.playerRef, "ah manage") == 0) {{ hubAck(); return; }}
      this.info = "the Auction House is not on this server right now";
      rebuild();
      return;
    }}
    if (a.equals("mk:ah") || a.equals("ahopen")) {{
      String aq = a.equals("ahopen") ? this.ahSel : ((this.query != null && this.query.length() > 0) ? this.query : this.findDraft);
      if (aq == null) aq = "";
      if ({PKG}.BzMarket.ahOpen(u, aq)) {{ hubAck(); return; }}   // answered (a no-op once the AH page replaced this one)
      if ({PKG}.HubBar.run(this.playerRef, "ah") == 0) {{ hubAck(); return; }}
      this.info = "the Auction House is not on this server right now";
      rebuild();
      return;
    }}
    // 0.1.6 search: find applies the draft (empty = the normal view; the same text again keeps the results page - a double Enter / click);
    // fclear (or an empty find, or a tab) goes back to the tab and grid page the search started from
    if (a.equals("find")) {{
      String q = this.findDraft == null ? "" : this.findDraft;
      boolean was = this.query != null && this.query.length() > 0;
      if (q.length() == 0) {{ if (was) this.pageNo = this.catPage; this.query = ""; }}
      else if (!q.equals(this.query)) {{ if (!was) this.catPage = this.pageNo; this.query = q; this.pageNo = 0; }}
      this.showN = 0;
      this.info = "";
      rebuild();
      return;
    }}
    if (a.equals("fclear")) {{
      if (this.query != null && this.query.length() > 0) this.pageNo = this.catPage;
      this.query = "";
      this.findDraft = "";
      this.showN = 0;
      this.info = "";
      rebuild();
      return;
    }}
    if (a.equals("cfset")) {{ cfSet(u); rebuild(); return; }}   // 0.1.14: the confirm amount
    // 0.1.18: the cells are ONE scroll list (the 0.1.17 pager's prev / next are gone); Show more = the next BZ_SHOW cells
    if (a.equals("more")) {{ this.showN = (this.showN > 0 ? this.showN : {BZ_SHOW}) + {BZ_SHOW}; this.info = ""; rebuild(); return; }}
    for (int i = 0; this.tabs != null && i < this.tabs.length; i++) {{
      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.pageNo = 0; this.query = ""; this.findDraft = ""; this.showN = 0; this.info = ""; rebuild(); return; }}
    }}
    for (int i = 0; this.cells != null && i < this.cells.length; i++) {{
      if (this.cells[i] != null && a.equals("cell:" + i)) {{ this.sel = this.cells[i]; this.ahSel = null; this.info = ""; rebuild(); return; }}
    }}
    // 0.1.17: an Auction House cell selects that AH item (never a product: sel = null, so no Bazaar trade button can act on it)
    for (int i = 0; this.ahCells != null && i < this.ahCells.length; i++) {{
      if (this.ahCells[i] != null && a.equals("cell:" + i)) {{ this.ahSel = this.ahCells[i]; this.sel = null; this.info = ""; rebuild(); return; }}
    }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    String who = {PKG}.BzUtil.safe(this.playerRef.getUsername()).replace(' ', '_');
    if (amtAct) {{ amountAction(p, u, who, a, now); rebuild(); return; }}
    {TR} r = null;
    if (a.equals("buy1") || a.equals("buystk")) {{
      // 0.1.14: below the player's confirm amount the first click buys; at / above it the button turns into CONFIRM
      r = buyClick(p, u, who, a, a.equals("buy1") ? 1 : {PKG}.Trader.stack(this.sel), cfHit, cfSeen, cfSeenQ, now);
      if (r == null) {{ rebuild(); return; }}
    }}
    else if (a.equals("sell1")) r = {PKG}.Trader.sell(p, u, who, this.sel, 1);
    else if (a.equals("sellstk")) r = {PKG}.Trader.sell(p, u, who, this.sel, {PKG}.Trader.stack(this.sel));
    else if (a.equals("sellall")) r = {PKG}.Trader.sell(p, u, who, this.sel, 0);
    else if (sellInvClick) {{
      // no "sell N items - click Confirm sell" preview that every sell0 would then refuse (profile crash recovery at join)
      if ({PKG}.Trader.busy(u)) {{ this.info = "your profile is still loading - try again in a moment"; this.confirmUntil = 0L; rebuild(); return; }}
      // 0.1.15 E: SELL <tab> = the open tab's products only, SELL ALL TABS = every product (null)
      boolean every = a.equals("sellalltabs");
      if (now > this.confirmUntil) {{
        String sc = every ? null : this.cat;
        if (!every && sc == null) {{ this.info = "open a tab first"; this.confirmUntil = 0L; rebuild(); return; }}
        String what = every ? "bazaar" : sc;
        long[] pv = {PKG}.Trader.preview(p, u, sc);
        if (pv[0] <= 0L) {{ this.info = "nothing to sell - no " + what + " items in your inventory or the Void"; this.confirmUntil = 0L; }}
        else {{ this.info = "sell " + pv[0] + " " + what + " items" + (pv[2] > 0L ? " (" + pv[2] + " from the Void)" : "") + " for about " + pv[1] + " coins - click Confirm sell within 10 seconds"; this.confirmUntil = now + 10000L; this.confirmWhat = a; this.confirmCat = sc; schedRevert(10000L); }}
        rebuild();
        return;
      }}
      this.confirmUntil = 0L;
      String cc = every ? null : this.confirmCat;
      if (!every && cc == null) {{ this.info = "open a tab first"; rebuild(); return; }}
      r = {PKG}.Trader.sellInventory(p, u, who, cc);
    }}
    if (r == null) return;
    // chat copy for a finished Sell inventory and for anything where the player may be owed coins or items
    // (the info label is replaced by the next click; chat stays)
    if (r.alert || (sellInvClick && r.ok)) this.playerRef.sendMessage({MSG}.raw("[Bazaar] " + r.msg));
    this.info = r.msg;
    rebuild();
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("bazaar page event failed: " + t); }}
}}""", page))

fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public BzPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.BzPage(({PR}) o, (String) null);
}}""", fac))

# ================= 0.1.13 HUBS H3b: the Market > Bazaar tab's open Function (java.util.function.Function) =================
# the player's world thread (the bar's caller is always a page event, HUBS-CONTRACT 1): the bazaar page for the UUID as /bazaar opens it
# (never close-then-open: openCustomPage replaces the page on screen); FALSE = the bar runs /bazaar instead
hopn.addInterface(pool.get("java.util.function.Function"))
hopn.addConstructor(CtNewConstructor.make("public BzHubOpen() { }", hopn))
hopn.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null) return Boolean.FALSE;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return Boolean.FALSE;
    if (!@PKG@.Coins.ready()) pr.sendMessage(@MSG@.raw("[Bazaar] SkyyCoins is not loaded - you can look but not trade."));
    pm.openCustomPage(r, st, new @PKG@.BzPage(pr, (String) null));
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.BzUtil.warn("the Market > Bazaar tab could not open the bazaar page: " + t);
    return Boolean.FALSE;
  }
}""", UNI="com.hypixel.hytale.server.core.universe.Universe", PGM=PGM), hopn))
# setup(): hub:tab:market:bazaar = Object[]{ "SkyyBazaar", "Bazaar", Integer 10, "bazaar", open, null } (SUI.HUB_TABS). 1 = put.
hopn.addMethod(CtNewMethod.make(jt(r"""
public static int register() {
  Object[] e = @PKG@.HubBar.put("market", "bazaar", "SkyyBazaar", "@LABEL@", @ORDER@, "@CMD@", new @PKG@.BzHubOpen(), (Object) null);
  return e == null ? 0 : 1;
}""", LABEL=BZ_HUB_LABEL, ORDER=BZ_HUB_ORDER, CMD=BZ_HUB_CMD), hopn))

# ================= 0.1.17 MARKET MERGE: bazaar:fn:open (java.util.function.Function) =================
# apply(Object[]{ UUID, String query }): the player's world thread (the caller is a page event - SkyyAuctions 0.1.9's BAZAAR button);
# opens this page as /bazaar does, with that search applied when it is not empty (the text normalized like the search field) -> TRUE;
# FALSE for junk or an offline player (the caller then tries the hub tab / says so)
mko.addInterface(pool.get("java.util.function.Function"))
mko.addConstructor(CtNewConstructor.make("public BzOpenFn() { }", mko))
mko.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  if (!(o instanceof Object[])) return Boolean.FALSE;
  Object[] a = (Object[]) o;
  if (a.length < 1 || !(a[0] instanceof java.util.UUID)) return Boolean.FALSE;
  String q = (a.length > 1 && a[1] instanceof String) ? @PKG@.BzPage.findNorm((String) a[1]) : "";
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) a[0]);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null) return Boolean.FALSE;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return Boolean.FALSE;
    @PKG@.BzPage pg = new @PKG@.BzPage(pr, (String) null);
    if (q.length() > 0) { pg.query = q; pg.findDraft = q; pg.pageNo = 0; pg.catPage = 0; }
    pm.openCustomPage(r, st, pg);
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.BzUtil.warn("bazaar:fn:open could not open the bazaar page: " + t);
    return Boolean.FALSE;
  }
}""", UNI="com.hypixel.hytale.server.core.universe.Universe", PGM=PGM), mko))

# ================= /bazaar (/bz) =================
cmd.addConstructor(CtNewConstructor.make("""
public BzCmd() {
  super("bazaar", "Open the Bazaar - instant buy and sell of commodities");
  addAliases(new String[] { "bz" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    if (!{PKG}.Coins.ready()) pr.sendMessage({MSG}.raw("[Bazaar] SkyyCoins is not loaded - you can look but not trade."));
    player.getPageManager().openCustomPage(ref, store, new {PKG}.BzPage(pr, (String) null));
  }} catch (Throwable t) {{
    {PKG}.BzUtil.warn("/bazaar failed: " + t);
    pr.sendMessage({MSG}.raw("[Bazaar] could not open the bazaar"));
  }}
}}""", cmd))

# ================= /bazaaradmin =================
# 0.1.1: positional forms are real subcommands (price / reload / reset / info + a "price <itemId>" usage variant). The engine
# dispatches a subcommand BEFORE it checks the root permission, so each one requires skyybazaar.admin itself. The root keeps
# its optional --action/--item/--value args (0.1 forms) and every form runs the same static run() = the 0.1 execute body.
adm.addField(CtField.make(f"public {OA} actionArg;", adm))
adm.addField(CtField.make(f"public {OA} itemArg;", adm))
adm.addField(CtField.make(f"public {OA} valueArg;", adm))
# 0.1.3: status shows the premium; reload also re-reads config.properties through the config kit (hand edits logged via=file) and reprices;
# price <id> <base> on a processed good makes it FIXED (refused above the price that would let buy -> process -> sell pay) and every
# processed good made from a re-priced product follows it; price <id> auto puts a processed good back on its inputs; info says which.
# Fix round: every price change goes through Catalog.setGuarded (under the Market lock): a price that makes a recipe among products pay
# in one step that did not pay before is refused and changes nothing; reload warns about recipes that pay at the prices on disk.
adm.addMethod(CtNewMethod.make(jt(r"""
public static void run(@PR@ pr, String action, String itemRaw, String valueRaw) {
  try {
    if (action == null) {
      pr.sendMessage(@MSG@.raw("[Bazaar] " + @PKG@.Catalog.all().size() + " products in " + @PKG@.Catalog.categories().size() + " tabs, spread " + @PKG@.Market.SPREAD + ", impactCoins " + @PKG@.Market.IMPACT + ", halfLifeMinutes " + @PKG@.Market.HALFLIFE + ", processed goods premium " + @PKG@.BzCfg.PREMIUM + "% (applied " + @PKG@.BzUtil.num(@PKG@.BzCfg.effective() * 100.0) + "%), coins bridge " + (@PKG@.Coins.ready() ? "found" : "MISSING")));
      pr.sendMessage(@MSG@.raw("[Bazaar] /bazaaradmin price <itemId> <base|auto> | reload | reset <itemId|all> | info <itemId>"));
      return;
    }
    String a = action.trim().toLowerCase();
    String item = itemRaw != null ? itemRaw.trim() : null;
    if (a.equals("reload")) {
      @PKG@.Market.flushLog();
      String kit = "";
      try {
        Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
        if (o instanceof Object[] && ((Object[]) o).length > 2) kit = " Config: " + ((Object[]) o)[2];
      } catch (Throwable t) { @PKG@.BzUtil.warn("config kit reload failed: " + t); }
      int n = @PKG@.Catalog.load();
      @PKG@.Market.load();
      @PKG@.Catalog.reprice();
      @PKG@.Market.publishAll();
      @PKG@.Catalog.flushIfDirty();
      int paying = @PKG@.Catalog.warnLoops(@PKG@.Market.SPREAD);
      pr.sendMessage(@MSG@.raw("[Bazaar] reloaded " + n + " products in " + @PKG@.Catalog.categories().size() + " tabs; spread " + @PKG@.Market.SPREAD + ", impactCoins " + @PKG@.Market.IMPACT + ", halfLifeMinutes " + @PKG@.Market.HALFLIFE + ", processed goods premium " + @PKG@.BzCfg.PREMIUM + "%." + kit + (paying > 0 ? " WARNING: " + paying + " recipe(s) make coins at these prices - see the server log." : "")));
      return;
    }
    if (item == null) { pr.sendMessage(@MSG@.raw("[Bazaar] which item? /bazaaradmin " + a + " <itemId>")); return; }
    if (a.equals("reset")) {
      if (item.equalsIgnoreCase("all")) { @PKG@.Market.reset((String) null); pr.sendMessage(@MSG@.raw("[Bazaar] every demand factor reset to 1.0")); return; }
      if (@PKG@.Catalog.get(item) == null) { pr.sendMessage(@MSG@.raw("[Bazaar] " + item + " is not a bazaar product")); return; }
      @PKG@.Market.reset(item);
      pr.sendMessage(@MSG@.raw("[Bazaar] " + item + " demand reset to 1.0"));
      return;
    }
    @PKG@.Product p = @PKG@.Catalog.get(item);
    if (p == null) { pr.sendMessage(@MSG@.raw("[Bazaar] " + item + " is not a bazaar product - add it to products.properties and /bazaaradmin reload")); return; }
    boolean proc = @PKG@.Catalog.isProc(item);
    String mode = proc ? (@PKG@.Catalog.isAuto(item) ? "auto (follows its inputs)" : "fixed") : "fixed";
    if (a.equals("info")) {
      long bo = @PKG@.Market.getBought(item); long so = @PKG@.Market.getSold(item);
      pr.sendMessage(@MSG@.raw("[Bazaar] " + p.id + " (" + p.name + ", tabs " + @PKG@.Catalog.tabsOf(p) + "): base " + @PKG@.BzUtil.num(p.base) + " " + mode + ", demand " + @PKG@.BzUtil.num(@PKG@.Market.factor(item)) + "x, buy 1 = " + @PKG@.Market.quote(item, 1, true) + ", sell 1 = " + @PKG@.Market.quote(item, 1, false) + ", lifetime bought " + bo + " sold " + so + ", known item " + @PKG@.Catalog.usable(item)));
      return;
    }
    if (a.equals("price")) {
      if (valueRaw == null) { pr.sendMessage(@MSG@.raw("[Bazaar] /bazaaradmin price " + item + " <base" + (proc ? "|auto" : "") + ">  (now " + @PKG@.BzUtil.num(p.base) + ", " + mode + ")")); return; }
      String vr = valueRaw.trim();
      String who = @PKG@.BzUtil.safe(pr.getUsername()).replace(' ', '_');
      double old = p.base;
      if (vr.equalsIgnoreCase("auto")) {
        if (!proc) { pr.sendMessage(@MSG@.raw("[Bazaar] only processed goods (Furnace bars, stone and charcoal, Tannery leather, cloth bolts) can follow their inputs - " + item + " keeps a set price")); return; }
        String why = @PKG@.Catalog.setGuarded(item, 0.0, true);
        if (why != null) { pr.sendMessage(@MSG@.raw("[Bazaar] refused - " + why)); return; }
        @PKG@.Market.publishAll();
        String err = @PKG@.Catalog.save();
        @PKG@.Market.publish(item);
        @PKG@.Market.log("ADMIN-PRICE " + who + " " + pr.getUuid() + " " + item + " " + @PKG@.BzUtil.num(old) + " -> auto " + @PKG@.BzUtil.num(p.base));
        pr.sendMessage(@MSG@.raw("[Bazaar] " + item + " follows its inputs again: base " + @PKG@.BzUtil.num(old) + " -> " + @PKG@.BzUtil.num(p.base) + " (buy 1 = " + @PKG@.Market.quote(item, 1, true) + ", sell 1 = " + @PKG@.Market.quote(item, 1, false) + ")" + (err == null ? "" : " - could not save the files: " + err)));
        return;
      }
      double v;
      try { v = Double.parseDouble(vr); } catch (Throwable t) { pr.sendMessage(@MSG@.raw("[Bazaar] that is not a number" + (proc ? " (or auto)" : ""))); return; }
      if (proc) {
        double cap = @PKG@.Catalog.loopCap(item);
        if (cap > 0.0 && v > cap) { pr.sendMessage(@MSG@.raw("[Bazaar] at most " + @PKG@.BzUtil.num(cap) + " for " + item + " - above it buying its inputs, processing and selling makes coins")); return; }
      }
      if (!(v >= 0.01 && v <= 1000000000.0)) { pr.sendMessage(@MSG@.raw("[Bazaar] base must be 0.01 .. 1000000000")); return; }
      // fix round: the price guard - a price that makes a recipe among products pay in one step is refused (nothing changes)
      String why = @PKG@.Catalog.setGuarded(item, v, false);
      if (why != null) { pr.sendMessage(@MSG@.raw("[Bazaar] refused - " + why)); return; }
      int moved = @PKG@.Catalog.GUARD_MOVED;
      @PKG@.Market.publishAll();
      String err = @PKG@.Catalog.save();
      @PKG@.Market.publish(item);
      @PKG@.Market.log("ADMIN-PRICE " + who + " " + pr.getUuid() + " " + item + " " + @PKG@.BzUtil.num(old) + " -> " + @PKG@.BzUtil.num(v));
      pr.sendMessage(@MSG@.raw("[Bazaar] " + item + " base " + @PKG@.BzUtil.num(old) + " -> " + @PKG@.BzUtil.num(v) + (proc ? " (fixed - /bazaaradmin price " + item + " auto to follow its inputs)" : "") + " (buy 1 = " + @PKG@.Market.quote(item, 1, true) + ", sell 1 = " + @PKG@.Market.quote(item, 1, false) + ")" + (moved > 0 ? ", " + moved + " processed goods follow it" : "") + ". Keep recipe outputs under 1.22x their inputs." + (err == null ? "" : " Could not save the files: " + err)));
      return;
    }
    pr.sendMessage(@MSG@.raw("[Bazaar] unknown action " + a + " - price | reload | reset | info"));
  } catch (Throwable t) {
    @PKG@.BzUtil.warn("/bazaaradmin failed: " + t);
    pr.sendMessage(@MSG@.raw("[Bazaar] Usage: /bazaaradmin price <itemId> <base|auto> | reload | reset <itemId|all> | info <itemId>"));
  }
}"""), adm))

# --- subcommands / variant (javassist: each class gets its constructor + execute BEFORE the class that constructs it) ---
EXEC_SIG = f"protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world)"
def adm_exec(cls, call, what):
    cls.addMethod(CtNewMethod.make(f"""
{EXEC_SIG} {{
  try {{
    {call}
  }} catch (Throwable t) {{
    {PKG}.BzUtil.warn("/bazaaradmin {what} failed: " + t);
    pr.sendMessage({MSG}.raw("[Bazaar] Usage: /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>"));
  }}
}}""", cls))

# /bazaaradmin price <itemId>  (usage variant of price: 1 required arg -> shows the current base, like 0.1 without --value)
aprv.addField(CtField.make(f"public {RA} itemArg;", aprv))
aprv.addConstructor(CtNewConstructor.make(f"""
public BzAdmPriceShowCmd() {{
  super("(admin) show the current base price of a bazaar product");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
}}""", aprv))
adm_exec(aprv, f'{PKG}.BzAdminCmd.run(pr, "price", String.valueOf(ctx.get(this.itemArg)), (String) null);', "price")

# /bazaaradmin price <itemId> <base>
aprc.addField(CtField.make(f"public {RA} itemArg;", aprc))
aprc.addField(CtField.make(f"public {RA} valueArg;", aprc))
aprc.addConstructor(CtNewConstructor.make(f"""
public BzAdmPriceCmd() {{
  super("price", "(admin) set a product's base price: /bazaaradmin price <itemId> <base>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
  this.valueArg = withRequiredArg("base", "new base price (0.01 .. 1000000000)", {ATY}.STRING);
  addUsageVariant(new {PKG}.BzAdmPriceShowCmd());
}}""", aprc))
adm_exec(aprc, f'{PKG}.BzAdminCmd.run(pr, "price", String.valueOf(ctx.get(this.itemArg)), String.valueOf(ctx.get(this.valueArg)));', "price")

# /bazaaradmin reload
arlc.addConstructor(CtNewConstructor.make("""
public BzAdmReloadCmd() {
  super("reload", "(admin) re-read products.properties and market.properties from disk");
  requirePermission("skyybazaar.admin");
}""", arlc))
adm_exec(arlc, f'{PKG}.BzAdminCmd.run(pr, "reload", (String) null, (String) null);', "reload")

# /bazaaradmin reset <itemId|all>
arsc.addField(CtField.make(f"public {RA} itemArg;", arsc))
arsc.addConstructor(CtNewConstructor.make(f"""
public BzAdmResetCmd() {{
  super("reset", "(admin) reset a product's demand factor to 1.0: /bazaaradmin reset <itemId|all>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id, or all", {ATY}.STRING);
}}""", arsc))
adm_exec(arsc, f'{PKG}.BzAdminCmd.run(pr, "reset", String.valueOf(ctx.get(this.itemArg)), (String) null);', "reset")

# /bazaaradmin info <itemId>
ainc.addField(CtField.make(f"public {RA} itemArg;", ainc))
ainc.addConstructor(CtNewConstructor.make(f"""
public BzAdmInfoCmd() {{
  super("info", "(admin) prices, demand and lifetime volume of a product: /bazaaradmin info <itemId>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
}}""", ainc))
adm_exec(ainc, f'{PKG}.BzAdminCmd.run(pr, "info", String.valueOf(ctx.get(this.itemArg)), (String) null);', "info")

adm.addConstructor(CtNewConstructor.make(f"""
public BzAdminCmd() {{
  super("bazaaradmin", "(admin) /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>");
  requirePermission("skyybazaar.admin");
  this.actionArg = withOptionalArg("action", "price | reload | reset | info", {ATY}.STRING);
  this.itemArg = withOptionalArg("item", "item id (or all for reset)", {ATY}.STRING);
  this.valueArg = withOptionalArg("value", "new base price (0.01 .. 1000000000)", {ATY}.STRING);
  addSubCommand(new {PKG}.BzAdmPriceCmd());
  addSubCommand(new {PKG}.BzAdmReloadCmd());
  addSubCommand(new {PKG}.BzAdmResetCmd());
  addSubCommand(new {PKG}.BzAdmInfoCmd());
}}""", adm))
adm.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  // plain /bazaaradmin (status) and the 0.1 flag forms --action/--item/--value; positional forms are the subcommands above
  String a = ctx.provided(this.actionArg) ? String.valueOf(ctx.get(this.actionArg)) : (String) null;
  String item = ctx.provided(this.itemArg) ? String.valueOf(ctx.get(this.itemArg)) : (String) null;
  String v = ctx.provided(this.valueArg) ? String.valueOf(ctx.get(this.valueArg)) : (String) null;
  {PKG}.BzAdminCmd.run(pr, a, item, v);
}}""", adm))

# ================= BzTick (scheduler thread: decay + saves; never touches inventories) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public BzTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PKG}.Market.decay(System.currentTimeMillis());
    {PKG}.Market.flush();
    // 0.1.3: a premium changed by a hand edit (the kit's after= hook only runs for in-game changes) reprices; moved auto prices are
    // written to products.properties here, never on a caller's thread
    {PKG}.Catalog.tick();
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("tick failed: " + t); }}
}}""", tick))

# ================= 0.1.11 BzRebirthFn: rebirth R4 (KEY CONTRACT in tools/bazaar_0_1_11_patch.py). 0.1.x has no orders, no escrow and no
# claim stash (instant trades only), so nothing is ever open: closeall = "ok:0" (+ one trades.log line), wouldclose = "ok:0:0:0:0".
rbf.addInterface(pool.get("java.util.function.Function"))
rbf.addField(CtField.make("public int op;", rbf))
rbf.addConstructor(CtNewConstructor.make("public BzRebirthFn(int op) { this.op = op; }", rbf))
rbf.addMethod(CtNewMethod.make(jt(r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof String) || ((String) o).trim().length() == 0) return "err:bad-key";
    if (this.op == 1) return "ok:0:0:0:0";
    @PKG@.Market.log("CLOSEALL key=" + ((String) o).trim().replace(' ', '_') + " closed=0 (instant trades only - no open orders, nothing held)");
    return "ok:0";
  } catch (Throwable t) {
    @PKG@.BzUtil.warn("bazaar:fn:" + (this.op == 1 ? "wouldclose" : "closeall") + " failed: " + t);
    return "err:exception";
  }
}"""), rbf))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyBazaarPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(jt(r"""
public void setup() {
  @PKG@.BzUtil.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyBazaar");
  @PKG@.Catalog.FILE = dir.resolve("products.properties");
  @PKG@.Catalog.PFILE = dir.resolve("pricing.properties");
  @PKG@.Market.FILE = dir.resolve("market.properties");
  @PKG@.Market.LOGFILE = dir.resolve("trades.log");
  @PKG@.BzCfg.load(dir);
  @PKG@.BzSnd.load(dir);   // 0.1.12 sound pass: Skyy_SkyyBazaar/sounds.properties (before the kit)
  @PKG@.BzConfirm.load(dir);   // 0.1.14: each player's confirm amount (confirm.properties)
  String mig = @PKG@.Catalog.migrate();
  String mig14 = @PKG@.Catalog.migrate14();
  String mig19 = @PKG@.Catalog.migrate19();   // 0.1.9: the crystal shards appended once
  String mig110 = @PKG@.Catalog.migrate110();   // 0.1.10: the Enchanted materials appended once
  String mig114 = @PKG@.Catalog.migrate114();   // 0.1.14: prices by tier + the Eternal seeds, once
  String mig115 = @PKG@.Catalog.migrate115();   // 0.1.15: every price but the Eternal seeds x SCALE (+ impactCoins), once
  String mig116 = @PKG@.Catalog.migrate116();   // 0.1.16: the Enchanted Stick appended once
  String mig119 = @PKG@.Catalog.migrate119();   // 0.1.19: the C1 Enchanted products appended once
  String mig120 = @PKG@.Catalog.migrate120();   // 0.1.20: the zone metals appended once
  int n = @PKG@.Catalog.load();
  @PKG@.Market.load();
  if (@PKG@.Market.SPREAD < 0.10) @PKG@.BzUtil.warn("market.properties spread " + @PKG@.Market.SPREAD + " is below 0.10 - the build's no-money-loop proof assumes 0.10 (processed goods cap their premium at " + @PKG@.BzUtil.num(@PKG@.BzCfg.maxSafe() * 100.0) + "%)");
  @PKG@.Catalog.reprice();
  @PKG@.Market.publishAll();
  @PKG@.BzUtil.bridge().put("bazaar:fn:closeall", new @PKG@.BzRebirthFn(0));     // 0.1.11 rebirth R4 (tools/bazaar_0_1_11_patch.py)
  @PKG@.BzUtil.bridge().put("bazaar:fn:wouldclose", new @PKG@.BzRebirthFn(1));
  @PKG@.BzUtil.bridge().put("bazaar:fn:open", new @PKG@.BzOpenFn());     // 0.1.17 MARKET MERGE (SkyyAuctions 0.1.9's BAZAAR button)
  @PKG@.Catalog.flushIfDirty();
  @PKG@.Catalog.warnLoops(@PKG@.Market.SPREAD);
  if (mig != null) @PKG@.Market.log(mig);
  if (mig14 != null) { for (int i = 0; i < @PKG@.Catalog.M14_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M14_LOG.get(i)); }
  @PKG@.Catalog.M14_LOG.clear();
  if (mig19 != null) { for (int i = 0; i < @PKG@.Catalog.M19_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M19_LOG.get(i)); }
  @PKG@.Catalog.M19_LOG.clear();
  if (mig110 != null) { for (int i = 0; i < @PKG@.Catalog.M110_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M110_LOG.get(i)); }
  @PKG@.Catalog.M110_LOG.clear();
  if (mig114 != null) { for (int i = 0; i < @PKG@.Catalog.M114_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M114_LOG.get(i)); }
  @PKG@.Catalog.M114_LOG.clear();
  if (mig115 != null) { for (int i = 0; i < @PKG@.Catalog.M115_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M115_LOG.get(i)); }
  @PKG@.Catalog.M115_LOG.clear();
  if (mig116 != null) { for (int i = 0; i < @PKG@.Catalog.M116_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M116_LOG.get(i)); }
  @PKG@.Catalog.M116_LOG.clear();
  if (mig119 != null) { for (int i = 0; i < @PKG@.Catalog.M119_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M119_LOG.get(i)); }
  @PKG@.Catalog.M119_LOG.clear();
  if (mig120 != null) { for (int i = 0; i < @PKG@.Catalog.M120_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M120_LOG.get(i)); }
  @PKG@.Catalog.M120_LOG.clear();
  @PKG@.Catalog.FLOORPUB = @PKG@.BzCfg.MINSELL;
  @PKG@.BzConfirm.register();   // 0.1.14: the Settings switch bazaar.confirm (SkyWynn Menu > Settings > Coins & Bank)
  getCommandRegistry().registerCommand(new @PKG@.BzCmd());
  getCommandRegistry().registerCommand(new @PKG@.BzAdminCmd());
  @OCU@.registerSimple(this, @PKG@.SkyyBazaarPlugin.class, "SkyyBazaar", new @PKG@.BzPageFactory());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.BzTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  int hubTabs = 0;
  try { hubTabs = @PKG@.BzHubOpen.register(); } catch (Throwable t) { @PKG@.BzUtil.warn("could not put the Market > Bazaar hub tab: " + t); }   // 0.1.13
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBazaar] @VER@ ready - /bazaar (/bz; hub tab market:bazaar " + (hubTabs == 1 ? "put" : "NOT put") + "), " + n + " products in " + @PKG@.Catalog.categories().size() + " tabs, spread " + @PKG@.Market.SPREAD + ", processed goods premium " + @PKG@.BzCfg.PREMIUM + "%, minimum sell " + @PKG@.BzCfg.MINSELL + ", confirm from " + @PKG@.BzCfg.CONFIRM + " (coins bridge " + (@PKG@.Coins.ready() ? "found" : "NOT found yet") + ", @KIT@)");
  // LAST: the admin config kit reads config.properties after BzCfg.load and publishes config:def:SkyyBazaar + config:fn:SkyyBazaar
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""", OCU=OCU, HSV=HSV, VER=VERSION, KIT=KIT_ID), pl))
pl.addMethod(CtNewMethod.make(jt(r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.Market.decay(System.currentTimeMillis()); @PKG@.Market.forcePending(); @PKG@.Market.flush(); } catch (Throwable t) { }
  try { @PKG@.Catalog.flushIfDirty(); } catch (Throwable t) { }
  try { @PKG@.Market.unpublishAll(); } catch (Throwable t) { }
  try { @PKG@.BzUtil.bridge().remove("bazaar:fn:closeall"); @PKG@.BzUtil.bridge().remove("bazaar:fn:wouldclose"); } catch (Throwable t) { }
  try { @PKG@.BzUtil.bridge().remove("bazaar:fn:open"); } catch (Throwable t) { }   // 0.1.17
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.BzUtil.warn("config kit flush at shutdown failed: " + t); }
  try { @PKG@.HubBar.removeAll(); } catch (Throwable t) { }   // 0.1.13: the hub tab (only while it still holds OUR array)
  super.shutdown();
}"""), pl))

ALL = (utl, coin, prod, cat_, mkt, inv_, bags, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, rbf, pl, cfgc, hubb, hopn,
       cfm, rvt, mkb, mks, mko)   # 0.1.13: + hub; 0.1.14: + the confirm amount / timeout; 0.1.17: + the market merge
for c in ALL:
    c.writeFile(OUT)
KIT.write(OUT)   # deferred kit checks (the BzCfg.changed after= hook exists with the right signature), then the 7 Cfg* classes
print("classes written:", len(ALL) + 7)

# ================= 0.1.3: ACCESS AUDIT - what the JVM would refuse at RUN time with IllegalAccessError (the SkyyUiProbe 0.3.1 guard) =======
# javassist compiles a call to a protected / package-private member from any class, and -Xverify:all does not catch it either: the JVM
# checks member access when the instruction first runs (JVMS 5.4.4). So every class / member reference in the final class bytes is
# resolved here with the JVM's rules: a class must be public (or in our package); a member public, protected only from a subclass of its
# declaring class, package-private only in its own package, private only in its own class (copied from tools/trees_0_3_patch.py).
_JMod, _JCP = J["Modifier"], _jp.JClass("javassist.bytecode.ConstPool")
_JCF, _JDI, _JBI = (_jp.JClass("javassist.bytecode.ClassFile"), _jp.JClass("java.io.DataInputStream"), _jp.JClass("java.io.ByteArrayInputStream"))
_AOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
         0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
         0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def _apkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def _aelem(name):
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items):
    """items: [(the referencing CtClass, the javassist ClassFile of its final bytes)] -> (refused, used non-public members, refs)"""
    refused, used, seen = [], set(), 0
    for D, cf in items:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in _AOPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, _AOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != _JCP.CONST_Class:
                    continue
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                elif tag == _JCP.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = _aelem(cname)
                    if en is not None and _apkg(en) != _apkg(dn) and not _JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    Cc = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = Cc.getField(name, desc)
                    elif name == "<init>":
                        x = Cc.getConstructor(desc)
                    else:
                        x = Cc.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if _JMod.isPublic(md) or (_apkg(dcn) == _apkg(dn) and not _JMod.isPrivate(md)):
                        continue
                    if _JMod.isPrivate(md):
                        ok = dcn == dn
                    elif _JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False
                    use = "%s %s.%s%s" % (_JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


# self-test first: a class that is no page calling the page's protected close (the SkyyUiProbe 0.3 bug class) must be refused
_ast = pool.makeClass(PKG + ".AccessAuditSelfTest")
_ast.addMethod(CtNewMethod.make("public static void bad(%s p) { p.close(); }" % PAGE, _ast))
_ast_r, _ast_u, _ast_n = access_audit([(_ast, _JCF(_JDI(_JBI(_ast.toBytecode()))))])
_ast.detach()
assert len(_ast_r) == 1 and "CustomUIPage.close" in _ast_r[0] and "IllegalAccessError" in _ast_r[0], \
    "access audit self-test: the close call from a non-page class must be refused: %s" % _ast_r
_aitems = []
for _root, _dirs, _files in os.walk(OUT):
    for _fn in sorted(_files):
        if _fn.endswith(".class"):
            _cn = os.path.relpath(os.path.join(_root, _fn), OUT)[:-6].replace(os.sep, ".")
            with open(os.path.join(_root, _fn), "rb") as _f:
                _aitems.append((pool.get(_cn), _JCF(_JDI(_JBI(_f.read())))))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_aitems)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError) - call protected engine "
                     "members only from their subclass, on this:\n  %s" % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
assert len(_aitems) == len(ALL) + 8 and AUDIT_N > 2000, (len(_aitems), AUDIT_N)   # 0.1.12: + BzSnd
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used from their "
      "own subclass: %s" % (AUDIT_N, len(_aitems), ", ".join(AUDIT_USED) or "none"))

jar = os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)
m = B.manifest("SkyyBazaar", VERSION, "SkyWynn bazaar: /bazaar instant buy and sell of the Void materials (Mining, Foraging, Farming, Fishing, Combat, Smithing tabs) against a demand-driven market maker; processed goods cost a premium over their raw inputs. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBazaarPlugin")
# 0.1.13: the Sky Window kit art - all 59 files, byte-identical in every hub jar (sha256-pinned by the kit; HUBS-CONTRACT 2.7), under
# Common/UI/Custom/SkyyKit/ only (a texture outside Common/UI/Custom disconnects the client - probe k1b) -> the jar is an asset pack now
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit), "0.1.13: the kit art"
m["IncludesAssetPack"] = True
B.assemble(jar, m, OUT, extra_files=_kit)
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", SUI.HUB_FRAME[BZ_HUB], "Tertiary")) == 59, "0.1.13: the jar's kit art"
if "--deploy" in sys.argv:
    raise SystemExit("0.1.3: no --deploy from a build script - deploys go through python tools/deploy_set.py --yes (the SET)")
