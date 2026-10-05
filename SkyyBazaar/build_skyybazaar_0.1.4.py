"""SkyyBazaar 0.1.4 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.4.py            -> SkyyBazaar/SkyyBazaar-0.1.4.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.4 is GENERATED from build_skyybazaar_0.1.3.py by tools/bazaar_0_1_4_patch.py - edit the patch, not this file; 0.1.3 came
       from 0.1.2 by tools/bazaar_0_1_3_patch.py, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

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
SUI.verify()
KIT_ID = SUI.kit_id()

VERSION = "0.1.4"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SPREAD = 0.10

# ================= 0.1.3 products: EVERY item a Magic Bag holds, in the matching tab (Skyy 2026-10-03, LOCKED) =================
# "if it goes in the bag, it goes in a matching section in the bizzar." The tab of a product is not written here: the build runs
# SkyySacks' own compiled rule (SackDefs.catOf of the SET jar) over Assets.zip and checks this table against it (see the pipeline below).
BAG_TABS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")          # tab order = SkyySacks' bag order
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
]
NOSRC = "never obtainable in survival: no drop list, block or recipe gives it, so it never goes in a bag"
PREMIUM_BENCHES = ("Furnace", "Tannery")     # Skyy: "smelted bars and tanned leather" (+ the Furnace's charcoal and smelted stones)
# fix round: crafted processed goods (Skyy's "processed materials") whatever bench makes them: (regex on the id, what the player does).
# Their recipe = the one non-salvage recipe whose every input is a product (the build stops on two)
PREMIUM_ITEMS = ((r"^Ingredient_Bolt_", "weaving"),)
PREMIUM_DEF, PREMIUM_MIN, PREMIUM_MAX = 20, 0, 22   # Server Setup row processed.premium (%); 22: see the pipeline's premium bound
AUTO = None                                  # a processed good: priced from its raw inputs at run time
PRODUCTS = [  # (item id, base price or AUTO, official en-US name) - display order; the tab comes from the bag (build time)
    # ---- Mining bag
    ("Ore_Copper", 5, "Copper Ore"),
    ("Ore_Iron", 16, "Iron Ore"),
    ("Ore_Thorium", 48, "Thorium Ore"),
    ("Ore_Silver", 14, "Silver Ore"),
    ("Ore_Cobalt", 144, "Cobalt Ore"),
    ("Ore_Gold", 20, "Gold Ore"),
    ("Ore_Adamantite", 480, "Adamantite Ore"),
    ("Ore_Mithril", 1440, "Mithril Ore"),
    ("Ore_Onyxium", 3712, "Onyxium Ore"),            # fix round: only salvage gives it in vanilla; its ingot follows it (AUTO)
    ("Ore_Prisma", 75, "Prisma Ore"),
    ("Rock_Gem_Ruby", 40, "Ruby"),
    ("Rock_Gem_Sapphire", 40, "Sapphire"),
    ("Rock_Gem_Emerald", 40, "Emerald"),           # fix round: the gems no recipe uses (golem drops, gem blocks)
    ("Rock_Gem_Topaz", 40, "Topaz"),
    ("Rock_Gem_Zephyr", 40, "Zephyr"),
    ("Rock_Gem_Diamond", 120, "Diamond"),
    ("Rock_Gem_Voidstone", 120, "Voidstone"),
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
    ("Ingredient_Tree_Sap", 4, "Tree Sap"),
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
    ("Ingredient_Bar_Silver", AUTO, "Silver Ingot"),
    ("Ingredient_Bar_Cobalt", AUTO, "Cobalt Ingot"),
    ("Ingredient_Bar_Gold", AUTO, "Gold Ingot"),
    ("Ingredient_Bar_Adamantite", AUTO, "Adamantite Ingot"),
    ("Ingredient_Bar_Mithril", AUTO, "Mithril Ingot"),
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
]

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

def check_assets(products, spread):
    z = zipfile.ZipFile(ASSETS)
    items = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[n.rsplit("/", 1)[1][:-5]] = n
    missing = [p for p in products if p not in items]
    if missing:
        raise SystemExit("unknown item ids (not in Assets.zip Server/Item/Items): %s" % missing)
    data = {k: _load_json(z, v) for k, v in items.items()}
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
    INF = float("inf")
    cost = {p: b * (1 + spread) for p, b in products.items()}
    sell = {p: b * (1 - spread) for p, b in products.items()}
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


SACKS_VER = sacks_pin()
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
        if not pb or len(outs) != 1 or outs[0][0] not in products:
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


def loop_check(M, prices, spread, margins=None):
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
    cost = dict((p, b * (1 + spread)) for p, b in prices.items())
    liq = dict((p, b * (1 - spread)) for p, b in prices.items())
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
MODEL = asset_model(JS, DATA, DROPS, RECFILES)
BAGS, WHY, SKIPPED, BAG_NAMES = bag_items(JS, DATA, DROPS, MODEL, LANG)
ids = [p[0] for p in PRODUCTS]
if len(set(ids)) != len(ids):
    raise SystemExit("duplicate product rows: %s" % sorted(set(i for i in ids if ids.count(i) > 1)))
BAG_OF = {}
for _b, _l in BAGS.items():
    for _i in _l:
        BAG_OF[_i] = _b
missing = [(BAG_OF[i], i, BAG_NAMES[i]) for b in BAG_TABS for i in BAGS[b] if i not in set(ids)]
if missing:
    raise SystemExit("%d bag item(s) have no product row - add each to PRODUCTS (price + official name) or a SKIP rule with a reason:\n  %s"
                     % (len(missing), "\n  ".join("%s  %s  (%s)" % m for m in missing)))
_skip_of = dict((i, (b, r)) for b, i, r in SKIPPED)
_both = [(i, _skip_of[i][1]) for i in ids if i in _skip_of]
if _both:
    raise SystemExit("product row(s) for bag items a SKIP rule takes out - remove the row or narrow the rule: %s" % _both)
nobag = [i for i in ids if i not in BAG_OF]
if nobag:
    raise SystemExit("product row(s) for items no Magic Bag holds (SkyySacks %s) - remove them or fix the bag rule: %s" % (SACKS_VER, nobag))
# the guard is total: every item SackDefs.catOf puts in a bag is listed or skipped (a bag item can never fall through)
_catof_all = [i for i in sorted(DATA) if bag_of(i) is not None]
_unaccounted = [i for i in _catof_all if i not in BAG_OF and i not in _skip_of]
if _unaccounted:
    raise SystemExit("bag items neither listed nor skipped: %s" % _unaccounted[:40])
assert len(_catof_all) == len(BAG_OF) + len(_skip_of), (len(_catof_all), len(BAG_OF), len(_skip_of))
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
    if p not in PROC and p not in PRICE_014 and abs(float(_new[p][1]) - b) > 1e-9:
        raise SystemExit("0.1.2 product %s changed its raw price %s -> %s: keep it (existing markets)" % (p, b, _new[p][1]))
    if _new[p][2] != n:
        raise SystemExit("0.1.2 product %s changed its name %r -> %r" % (p, n, _new[p][2]))
# ---- 0.1.4: the PRODUCTS rows carry the 0.1.4 defaults, and the crops follow the vanilla farming path
for _i, (_o, _n) in PRICE_014.items():
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9, "PRICE_014 %s: row %s" % (_i, _new.get(_i))
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
FUELS, CHARCOAL = fuel_list(MODEL, set(ids))
FIXED_BASE = dict((p[0], float(p[1])) for p in PRODUCTS if p[1] is not AUTO)


def all_prices(premium):
    d = dict(FIXED_BASE)
    d.update(auto_prices(FIXED_BASE, PROC, FUELS, CHARCOAL, premium))
    missing_auto = [i for i in PROC if i not in d]
    if missing_auto:
        raise SystemExit("processed goods without a price: %s" % missing_auto)
    return d


SEED_BASE = all_prices(PREMIUM_DEF / 100.0)
# ---- 3. the premium bound: (1 + max premium) x (1 - spread) <= 1 + spread, or buy inputs -> process -> sell pays at factor 1.0
assert (1.0 + PREMIUM_MAX / 100.0) * (1.0 - SPREAD) <= 1.0 + SPREAD, "PREMIUM_MAX %d%% makes processing pay at spread %s" % (PREMIUM_MAX, SPREAD)
assert 0 <= PREMIUM_MIN <= PREMIUM_DEF <= PREMIUM_MAX
# ---- 4. money loops: 0.1.2's check UNCHANGED (raises on a loop) at premium 0, 15, the default and the maximum + the 0.1.3 check
#         (fuel, charcoal, co-products, liquidation) at EVERY whole premium 0..22 - it runs in about a second
_selftest = loop_check_selftest()
print("loop check self-test: the craft -> salvage -> smelt chain is seen (%s), a chain that does not pay is not" % ", ".join(_selftest))
for _prem in range(PREMIUM_MIN, PREMIUM_MAX + 1):
    _px = all_prices(_prem / 100.0)
    if _prem in (PREMIUM_MIN, 15, PREMIUM_DEF, PREMIUM_MAX):
        check_assets(_px, SPREAD)
    _loops, _costable, _nrec, _passes = loop_check(MODEL, _px, SPREAD)
    if _loops:
        for ratio, name, ins, outs, fuel_s in sorted(_loops, reverse=True)[:30]:
            print("MONEY LOOP x%.3f  %s  in=%s -> out=%s fuel=%.1fs" % (ratio, name, ins, outs, fuel_s))
        raise SystemExit("%d buy -> process / craft -> sell money loops at premium %d%% (fuel + charcoal + co-product + liquidation aware)"
                         % (len(_loops), _prem))
    if _prem in (PREMIUM_MIN, PREMIUM_DEF, PREMIUM_MAX):
        print("loop check at premium %d%%: %d recipes (+ fuel, + burn), %d fully buyable, fixed point in %d passes, no money loops"
              % (_prem, _nrec, _costable, _passes))
print("loop check: no money loop at any premium %d-%d%%" % (PREMIUM_MIN, PREMIUM_MAX))


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
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_014.items())
_auto013 = auto_prices(_fb013, PROC, FUELS, CHARCOAL, PREMIUM_DEF / 100.0)
SEED013_LINES = ["%s=%s,%s,%s" % (pid, BAG_OF[pid], "%g" % (_auto013[pid] if base is AUTO else _fb013[pid]), name) for pid, base, name in PRODUCTS]
assert sum(1 for a, b in zip(SEED013_LINES, SEED_LINES) if a != b) >= len(PRICE_014)
_order = proc_order(PROC, CHARCOAL)        # the Java reprices in this order (inputs first)
PROC_SPEC = "\n".join("%s/%g/%s/%s/%s" % (i, PROC[i]["outq"], repr(round(PROC[i]["secs"], 6)), PROC[i]["bench"],
                                          ";".join("%g:%s" % (q, ",".join(c)) for q, c in PROC[i]["inputs"])) for i in _order)
FUEL_SPEC = ";".join("%s:%s:%s" % (f, repr(q), repr(sh)) for f, q, sh in FUELS)
for _t in (PROC_SPEC, FUEL_SPEC):
    assert '"' not in _t and "\\" not in _t
EXTRA_ID = [i for i in EXTRA_TABS for t in EXTRA_TABS[i]]
EXTRA_TAB = [t for i in EXTRA_TABS for t in EXTRA_TABS[i]]


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
    fs, ch = None, (prices.get(charcoal) if charcoal else None)
    for f, fq, sh in fuels:
        pf = prices.get(f)
        if pf is None:
            continue
        c = (pf * (1 + spread) - (sh * ch * (1 - spread) if (sh > 0 and ch is not None) else 0.0)) / fq
        fs = c if fs is None else min(fs, c)
    fs = max(0.0, fs or 0.0)
    out = []
    for k, (secs, ins, outs) in enumerate(edges):
        cost, ok = secs * fs, True
        for q, cand in ins:
            ps = [prices[c] for c in cand if c in prices]
            if not ps:
                ok = False
                break
            cost += q * min(ps) * (1 + spread)
        if not ok:
            continue
        val = sum(q * prices[o] * (1 - spread) for o, q in outs if o in prices)
        if val > cost + 1e-9:
            out.append(k)
    return out


EDGES = edge_table(MODEL, set(ids), CHARCOAL)
EDGE_LINES = ["%s|%s>%s" % (repr(round(secs, 6)), ";".join("%g:%s" % (q, ",".join(c)) for q, c in ins), ";".join("%g:%s" % (q, o) for o, q in outs))
              for secs, ins, outs in EDGES]
for _t in EDGE_LINES:
    assert '"' not in _t and "\\" not in _t and _t.count(">") == 1 and _t.count("|") == 1, _t
for _prem in range(PREMIUM_MIN, PREMIUM_MAX + 1):
    _el = edge_loops(EDGES, all_prices(_prem / 100.0), SPREAD, FUELS, CHARCOAL)
    if _el:
        raise SystemExit("the admin price guard would see %d paying recipe(s) at the default prices (premium %d%%): %s"
                         % (len(_el), _prem, [EDGE_LINES[k] for k in _el[:5]]))
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
cfgc = pool.makeClass(PKG + ".BzCfg")          # 0.1.3: the processed goods premium (Server Setup row processed.premium)


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
CFG_TEXT = ("# SkyyBazaar settings. Change them in game: SkyWynn Menu > Server Setup > Bazaar (or edit this file, then /bazaaradmin reload).\n"
            "# processed.premium = how much more (in %%) a processed good costs than the raw inputs of its vanilla recipe (recipe ratio +\n"
            "#   fuel): Furnace bars, stone and charcoal, Tannery leather, cloth bolts. %d-%d; above %d buying the inputs, processing\n"
            "#   and selling would pay.\n"
            "processed.premium=%d\n" % (PREMIUM_MIN, PREMIUM_MAX, PREMIUM_MAX, PREMIUM_DEF))
cfgc.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % SUI.java_lit(CFG_TEXT), cfgc))
CFG_CATS = [("market", "Market")]
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding)
    ("processed.premium", "Processed goods premium", "market", "int", str(PREMIUM_DEF), str(PREMIUM_MIN), str(PREMIUM_MAX), "step=1",
     "%", "live", "Bars, stone, charcoal, leather and cloth bolts cost this much more than their raw inputs. Max 22.",
     "field:BzCfg.PREMIUM@config.properties:processed.premium;after=BzCfg.changed"),
]
KIT = CFG.emit(pool, PKG, MOD="SkyyBazaar", TITLE="Bazaar", VERSION=VERSION, NODE="skyybazaar.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyBazaar/config.properties"], NOTE="Prices, demand and products stay in products / market.properties.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CFG_TEXT})
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
utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
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
cat_.addField(CtField.make("public static final String PROC_SPEC = %s;" % SUI.java_lit(PROC_SPEC), cat_))
cat_.addField(CtField.make("public static final String FUEL_SPEC = %s;" % SUI.java_lit(FUEL_SPEC), cat_))
cat_.addField(CtField.make("public static final String CHARCOAL = %s;" % SUI.java_lit(CHARCOAL or ""), cat_))
# fix round: the admin price guard's recipe edges (the build's EDGE_LINES; parsed by init() into EDGE)
cat_.addField(CtField.make("public static final String[] EDGES = %s;" % jarr(EDGE_LINES), cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList EDGE = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static int GUARD_MOVED = 0;", cat_))
cat_.addField(CtField.make("public static final String HEADER = %s;" % SUI.java_lit(
    "# SkyyBazaar products - one per line: <ItemId>=<Category>,<basePrice>,<Display Name>\n"
    "# Every Magic Bag material shows in its bag's tab (Mining, Foraging, Farming, Combat, Smithing - building shapes and decoration\n"
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
cat_.addField(CtField.make("public static final java.util.ArrayList M14_LOG = new java.util.ArrayList();", cat_))
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
  READY = true;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.Product get(String id) {{
  if (id == null) return null;
  return ({PKG}.Product) BY_ID.get(id);
}}""", cat_))
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
  if (p.cat != null && p.cat.length() > 0 && !raw.contains(p.cat)) raw.add(p.cat);
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
# a tab's products: seed order, then admin-added ones in file order (an insertion sort into a per-tab cache; the cache is dropped by load)
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
    Integer ix = (Integer) ORDER_IX.get(p.id);
    int key = ix == null ? 1000000 + i : ix.intValue();
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
            if (Math.abs(p.base - M14_OLD[k]) < 1.0E-9) {
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
            } else if (Math.abs(p.base - M14_NEW[k]) < 1.0E-9) {
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
mkt.addField(CtField.make("public static volatile double IMPACT = 10000.0;", mkt))
mkt.addField(CtField.make("public static volatile double HALFLIFE = 120.0;", mkt))
mkt.addField(CtField.make("public static final double MINF = 0.25;", mkt))
mkt.addField(CtField.make("public static final double MAXF = 4.0;", mkt))
mkt.addField(CtField.make("public static long LAST = 0L;", mkt))
mkt.addField(CtField.make("public static boolean DIRTY = false;", mkt))
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
  double total = 0.0;
  for (int i = 0; i < qty; i++) {{
    total += p.base * f * mult;
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
  double total = 0.0;
  int best = 0;
  for (int i = 0; i < cap; i++) {{
    total += p.base * f * mult;
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
  return p.base * factor(id) * (buy ? 1.0 + SPREAD : 1.0 - SPREAD);
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
  {PKG}.BzUtil.bridge().put("bazaar:products", sb.toString());
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
  java.util.Iterator it = new java.util.ArrayList(F.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    double f = ((Double) F.get(id)).doubleValue();
    double nf = clampF(Math.exp(Math.log(f) * k));
    if (Math.abs(nf - 1.0) < 0.0001) F.remove(id); else F.put(id, Double.valueOf(nf));
  }
  LAST = now;
  DIRTY = true;
  publishAll();
}""", mkt))
mkt.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  try {{
    java.util.Properties p = new java.util.Properties();
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
    }}
    double sp = 0.10, im = 10000.0, hl = 120.0;
    try {{ sp = Double.parseDouble(p.getProperty("spread", "0.10").trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad spread"); }}
    try {{ im = Double.parseDouble(p.getProperty("impactCoins", "10000").trim()); }} catch (Throwable t) {{ {PKG}.BzUtil.warn("market.properties: bad impactCoins"); }}
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
                    : (bench.equals("Furnace") ? "smelting it yourself" : bench + " it yourself"));
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
    double back = (sh > 0.0 && ch != null) ? sh * ch.base * (1.0 - sp) : 0.0;
    double c = (fp.base * (1.0 + sp) - back) / ((Double) f[1]).doubleValue();
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
        if (best < 0.0 || p.base < best) best = p.base;
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
      if (p != null) val += qo[i] * p.base * (1.0 - sp);
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
cfgc.addMethod(CtNewMethod.make(jt(r"""
public static void changed(String key) {
  try { @PKG@.Catalog.reprice(); } catch (Throwable t) { @PKG@.BzUtil.warn("processed goods reprice after " + key + " failed: " + t); }
}"""), cfgc))

# ================= Inv (count-verified inventory moves; world thread only) =================
inv_.addMethod(CtNewMethod.make(f"""
public static int countIn({IC} c, String id) {{
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {{
    {IS} it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
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
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
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
trd.addMethod(CtNewMethod.make(f"""
public static {TR} buy0({PLA} p, java.util.UUID u, String who, String id, int qty) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot take coins");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
  if (p == null || qty <= 0 || qty > MAXQ) return new {TR}(false, 0, 0L, "bad amount");
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
  return r1;
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sell0({PLA} p, java.util.UUID u, String who, String id, int want) {{
  if (id == null) return new {TR}(false, 0, 0L, "click a product first");
  {PKG}.Product pr = {PKG}.Catalog.get(id);
  if (pr == null || !{PKG}.Catalog.usable(id)) return new {TR}(false, 0, 0L, "that item is not on the bazaar");
  if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
  if (p == null) return new {TR}(false, 0, 0L, "player not found");
  if (busy(u)) return new {TR}(false, 0, 0L, "your profile is still loading - try again in a moment");
  int held = {PKG}.Inv.count(p, id);
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  int n = (want <= 0 || want > held) ? held : want;
  if (n > MAXQ) n = MAXQ;
  long quote = {PKG}.Market.quote(id, n, false);
  if (quote < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  if (quote == 0L) return new {TR}(false, 0, 0L, n + " " + pr.name + " is worth 0 coins right now - sell more at once");
  long purse = {PKG}.Coins.get(u);
  if (purse < 0L) return new {TR}(false, 0, 0L, "the coin bank did not answer - nothing sold, try again");
  if (purse > Long.MAX_VALUE - 2L * quote) return new {TR}(false, 0, 0L, "your purse is full");
  {PKG}.Inv.take(p, id, n);
  int removed = held - {PKG}.Inv.count(p, id);
  if (removed <= 0) return new {TR}(false, 0, 0L, "could not remove the items - nothing sold");
  long pay = removed == n ? quote : {PKG}.Market.quote(id, removed, false);
  if (pay <= 0L || purse > Long.MAX_VALUE - pay) {{
    int back1 = {PKG}.Inv.give(p, id, removed);
    {PKG}.BzUtil.warn("sell cancelled for " + u + " " + id + " removed " + removed + " returned " + back1);
    {PKG}.Market.log("SELL-CANCELLED " + who + " " + u + " " + id + " removed " + removed + " returned " + back1);
    if (back1 >= removed) return new {TR}(false, 0, 0L, "sale cancelled - your items were returned");
    {TR} rc = new {TR}(false, 0, 0L, "sale cancelled but only " + back1 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rc.alert = true;
    return rc;
  }}
  int ad = {PKG}.Coins.add(u, pay);
  if (ad != 1) {{
    int back2 = {PKG}.Inv.give(p, id, removed);
    {PKG}.BzUtil.warn("PAY FAILED for " + who + " " + u + " " + id + " x" + removed + " (" + pay + " coins, coins:fn:add " + (ad < 0 ? "threw - it may or may not have paid" : "refused or missing") + ") - returned " + back2 + " items");
    {PKG}.Market.log((ad < 0 ? "PAY-ERROR " : "PAY-FAILED ") + who + " " + u + " " + id + " " + removed + " " + pay + " returned " + back2);
    if (back2 >= removed) return new {TR}(false, 0, 0L, "could not pay - your items were returned");
    {TR} rp = new {TR}(false, 0, 0L, "could not pay and only " + back2 + " of " + removed + " " + pr.name + " fit back - tell an admin - it is logged");
    rp.alert = true;
    return rp;
  }}
  {PKG}.Market.apply(id, removed, false);
  {PKG}.Market.log("SELL " + who + " " + u + " " + id + " " + removed + " " + pay + " f=" + {PKG}.BzUtil.num({PKG}.Market.factor(id)));
  return new {TR}(true, removed, pay, "sold " + removed + " " + pr.name + " for " + pay + " coins");
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
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now cost " + cost + " coins (you saw " + maxCost + ") - click Buy again to buy at the new price");
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
  int held = {PKG}.Inv.count(p, id);
  if (held <= 0) return new {TR}(false, 0, 0L, "you have no " + pr.name);
  if (qty > held) return new {TR}(false, 0, 0L, "you only hold " + held + " " + pr.name + " - nothing sold");
  long pay = {PKG}.Market.quote(id, qty, false);
  if (pay < 0L) return new {TR}(false, 0, 0L, "price error - tell an admin");
  // a sale now worth 0 is refused outright (sell0 refuses it too) - never a "price moved, click again" that nothing re-arms
  if (pay == 0L) return new {TR}(false, 0, 0L, qty + " " + pr.name + " is worth 0 coins right now - sell more at once");
  if (minPay > 0L && pay < minPay) {{
    {TR} mv = new {TR}(false, 0, 0L, "the price moved - " + qty + " now pay " + pay + " coins (you saw " + minPay + ") - click Sell again to sell at the new price");
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
# {{items, coins}} that Sell inventory would move right now
trd.addMethod(CtNewMethod.make(f"""
public static long[] preview({PLA} p) {{
  synchronized ({PKG}.Market.class) {{
    java.util.ArrayList all = {PKG}.Catalog.all();
    long items = 0L, coins = 0L;
    for (int i = 0; i < all.size(); i++) {{
      String id = (({PKG}.Product) all.get(i)).id;
      int held = {PKG}.Inv.count(p, id);
      if (held <= 0 || !{PKG}.Catalog.usable(id)) continue;
      long q = {PKG}.Market.quote(id, held > MAXQ ? MAXQ : held, false);
      if (q <= 0L) continue;
      items += (long) held; coins += q;
    }}
    return new long[] {{ items, coins }};
  }}
}}""", trd))
trd.addMethod(CtNewMethod.make(f"""
public static {TR} sellInventory({PLA} p, java.util.UUID u, String who) {{
  synchronized ({PKG}.Market.class) {{
    if (!{PKG}.Coins.ready()) return new {TR}(false, 0, 0L, "SkyyCoins is not loaded - the bazaar cannot pay coins");
    java.util.ArrayList all = {PKG}.Catalog.all();
    int items = 0, kinds = 0; long coins = 0L;
    String warnMsg = null, lastFail = null;
    for (int i = 0; i < all.size(); i++) {{
      String id = (({PKG}.Product) all.get(i)).id;
      if ({PKG}.Inv.count(p, id) <= 0) continue;
      {TR} r = sell0(p, u, who, id, 0);
      if (r.ok) {{ items += r.qty; coins += r.coins; kinds++; }} else lastFail = r.msg;
      if (r.alert) warnMsg = r.msg;
    }}
    if (items == 0) {{
      {TR} rn = new {TR}(false, 0, 0L, warnMsg != null ? warnMsg : (lastFail != null ? lastFail : "nothing to sell - no bazaar items in your inventory"));
      rn.alert = warnMsg != null;
      return rn;
    }}
    {TR} rs = new {TR}(true, items, coins, "sold " + items + " items of " + kinds + " kinds for " + coins + " coins" + (warnMsg != null ? " - but " + warnMsg : ""));
    rs.alert = warnMsg != null;
    return rs;
  }}
}}""", trd))

# ================= BzPage (0.1.3: the vanilla kit look - tools/skyyui.py, research/Vanilla-UI-Style-Guide.md section 7) =================
# Restyled element by element, keeping every 0.1.2 id, binding payload and the click logic (the old root #SkyyBz is the window body, so
# every 0.1.2 append target stays). The plain window (vanilla list pages: ShopPage / WarpListPage), 1080 wide, height = the sum of
# its parts (asserted): purse line | tab row (up to 6 tabs, the open one Primary, the rest Secondary; Sell inventory = Destructive) |
# a 13 x 4 grid of kit icon cells (52 a page, the WorldEventListRow palette, the held count bottom right) | the kit pager | the
# detail well (icon, name, buy / sell / hold / demand, processed-goods line) or a hint | Buy 1 / Buy 64 (Primary), Sell 1 / Sell 64 /
# Sell all (Destructive) | the amount field (the vanilla InputBox) with Buy / Sell | the limits line | a result line coloured by its
# words | content separator | footer note + Close (Secondary + the cancel sound). Only properties the deployed pages use (no FlexWeight,
# no LayoutMode Right / Center / Full): SUI.assert_proven on both page states. Tab names (data, not static text) are drawn inline after
# BzPage.tabText keeps letters, digits and spaces only (the kit's proven inline charset); button labels stay static.
BZ_W, BZ_COLS, BZ_ROWS, BZ_CELL, BZ_CGAP = 1080, 13, 4, 74, 4
BZ_PER = BZ_COLS * BZ_ROWS
BZ_MAXT, BZ_TW5, BZ_TW6, BZ_SIW = 6, 150, 135, 200
BZ_HEAD_H, BZ_TABS_M, BZ_DET_H, BZ_LIM_H, BZ_INFO_H, BZ_TOP = 30, 8, 150, 26, 44, 8
BZ_ACT_W, BZ_ACT_GAP = 190, 10
BZ_SEP = SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})
BZ_SEP_H = SUI.outer_size(BZ_SEP)[1]
BZ_PARTS = [BZ_HEAD_H, 2 * BZ_TABS_M + SUI.BTN_H, BZ_ROWS * (BZ_CELL + BZ_CGAP), 8 + SUI.BTN_SMALL_H, BZ_TOP + BZ_DET_H,
            BZ_TOP + SUI.BTN_H, BZ_TOP + SUI.BTN_H, BZ_LIM_H, BZ_INFO_H, BZ_SEP_H, SUI.BTN_H]
BZ_H = sum(BZ_PARTS) + SUI.TITLE_H + 2 * SUI.CONTENT_PAD
BZ_SH = SUI.page_shell("SkyyBzF", BZ_W, BZ_H, "Bazaar", kind="plain", body_id="SkyyBz")
BZ_IW = BZ_SH.inner_w
assert SUI.fit(BZ_PARTS, BZ_SH.inner_h, "bazaar page") == 0
BZ_GRID_L = (BZ_IW - BZ_COLS * (BZ_CELL + BZ_CGAP)) // 2
assert BZ_GRID_L >= 0
BZ_TABROOM = BZ_IW - BZ_SIW
assert BZ_MAXT * BZ_TW6 + (BZ_MAXT - 1) * SUI.TAB_GAP <= BZ_TABROOM and 5 * BZ_TW5 + 4 * SUI.TAB_GAP <= BZ_TABROOM
BZ_SENT = "QzTabQz"
_bi = lambda base, expr: base + SUI.J(expr, "0")
BZM = {}
BZM["HEAD"] = SUI.group("SkyyBzHead", "Left", h=BZ_HEAD_H)
BZM["SUB"] = SUI.label("SkyyBzSub", "", "default", w=BZ_IW - 350, h=BZ_HEAD_H)
BZM["PURSE"] = SUI.label("SkyyBzPurse", "", "bold", w=350, h=BZ_HEAD_H, align="End", col=SUI.color_by([("purseOk", "gold")], "error"))
BZM["TABROW"] = SUI.group("SkyyBzTabs", "Left", h=SUI.BTN_H, anchor={"top": BZ_TABS_M, "bottom": BZ_TABS_M})
BZM["TABON"] = SUI.button(_bi("SkyyBzTab", "i"), BZ_SENT, "primary", w=SUI.J("tw", str(BZ_TW5)))
BZM["TABOFF"] = SUI.button(_bi("SkyyBzTab", "i"), BZ_SENT, "secondary", w=SUI.J("tw", str(BZ_TW5)))
BZM["TABGAP"] = SUI.spacer(w=SUI.TAB_GAP, h=SUI.BTN_H)
BZM["TABFILL"] = SUI.spacer(w=SUI.J("gap", str(BZ_TABROOM - 5 * BZ_TW5 - 4 * SUI.TAB_GAP)), h=SUI.BTN_H)
BZM["SELLINV"] = SUI.choose(SUI.J("confirming"), SUI.button("SkyyBzSellInv", "Confirm sell", "destructive", w=BZ_SIW),
                            SUI.button("SkyyBzSellInv", "Sell inventory", "destructive", w=BZ_SIW))
BZM["ROW"] = SUI.group(_bi("SkyyBzRow", "r"), "Left", h=BZ_CELL, anchor={"bottom": BZ_CGAP}, pad={"left": BZ_GRID_L})
_bzcell = lambda st: SUI.icon_cell(_bi("SkyyBzCell", "idx"), SUI.J("p.id", "Ore_Copper"), BZ_CELL, st, qty=True, anchor={"right": BZ_CGAP})
BZM["CELL"] = SUI.choose(SUI.J("con"), _bzcell("selected"), _bzcell("normal"))
BZM["EMPTY"] = SUI.group(None, None, w=BZ_CELL, h=BZ_CELL, anchor={"right": BZ_CGAP}, bg="row")
BZ_PAGER = SUI.pager("SkyyBz", "SkyyBzPg", BZ_IW, prev_on=SUI.J("this.pageNo > 0"), next_on=SUI.J("this.pageNo < pages - 1"))
assert BZ_PAGER.h == 8 + SUI.BTN_SMALL_H and (BZ_PAGER.prev, BZ_PAGER.page, BZ_PAGER.next) == ("SkyyBzPgPrev", "SkyyBzPgPage", "SkyyBzPgNext")
BZM["DET"] = SUI.panel("SkyyBzDetail", "well", h=BZ_DET_H, layout="Left", anchor={"top": BZ_TOP})
BZ_DIN = BZ_DET_H - 2 * SUI.WELL_PAD
BZM["DICON"] = SUI.icon_cell("SkyyBzDIcon", SUI.J("id", "Ore_Copper"), state="static", w=BZ_DIN, h=BZ_DIN, icon=BZ_DIN - 16)
BZ_TXT_W = BZ_IW - 2 * SUI.WELL_PAD - BZ_DIN - 12
BZM["DTXT"] = SUI.group("SkyyBzDTxt", "Top", w=BZ_TXT_W, h=BZ_DIN, anchor={"left": 12})
BZ_DLINES = [("DNAME", SUI.label("SkyyBzDName", "", "rowName", h=28)),
             ("DBUY", SUI.label("SkyyBzDBuy", "", "default", h=22, col="success")),
             ("DSELL", SUI.label("SkyyBzDSell", "", "default", h=22, col="error")),
             ("DHOLD", SUI.label("SkyyBzDHold", "", "default", h=22)),
             ("DDEM", SUI.label("SkyyBzDDem", "", "caption", h=20)),
             ("DPROC", SUI.label("SkyyBzDProc", "", "caption", h=20, col="info"))]
assert SUI.fit([SUI.outer_size(mk)[1] for _k, mk in BZ_DLINES], BZ_DIN, "detail text lines") == 0
BZM["ACTS"] = SUI.group("SkyyBzActs", "Left", h=SUI.BTN_H, anchor={"top": BZ_TOP})
BZ_ACTS = [SUI.button("SkyyBzBuy1", "Buy 1", "primary", w=BZ_ACT_W),
           SUI.button("SkyyBzBuy64", "Buy 64", "primary", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),
           SUI.button("SkyyBzSell1", "Sell 1", "destructive", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),
           SUI.button("SkyyBzSell64", "Sell 64", "destructive", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP}),
           SUI.button("SkyyBzSellAll", "Sell all", "destructive", w=BZ_ACT_W, anchor={"left": BZ_ACT_GAP})]
BZM["AMTROW"] = SUI.group("SkyyBzAmtRow", "Left", h=SUI.BTN_H, anchor={"top": BZ_TOP})
BZ_HINT_W = BZ_IW - 170 - 220 - 2 * (10 + 150) - 14
BZ_AMT = [SUI.label(None, "Custom amount", "fieldLabel", w=170, h=SUI.BTN_H),
          SUI.text_field("SkyyBzAmtBox", "SkyyBzAmt", w=220, h=SUI.BTN_H, placeholder="Amount", max_length=12),
          SUI.button("SkyyBzABuy", "Buy", "primary", w=150, anchor={"left": 10}),
          SUI.button("SkyyBzASell", "Sell", "destructive", w=150, anchor={"left": 10}),
          SUI.label("SkyyBzAmtHint", "", "caption", w=BZ_HINT_W, h=SUI.BTN_H, anchor={"left": 14})]
BZM["LIM"] = SUI.label("SkyyBzLimits", "", "default", h=BZ_LIM_H, align="Center", col="value")
BZ_NODET_H = BZ_DET_H + 2 * (BZ_TOP + SUI.BTN_H) + BZ_LIM_H
BZM["NODET"] = SUI.panel("SkyyBzDetail", "well", h=BZ_NODET_H, anchor={"top": BZ_TOP})
BZM["NODETTX"] = SUI.label(None, "Click a product to see its prices and trade it", "default", h=BZ_NODET_H - 2 * SUI.WELL_PAD,
                           align="Center")
BZM["INFO"] = SUI.result_line("SkyyBzInfo", SUI.J("infoColor(this.info)", SUI.COLOR["success"]), h=BZ_INFO_H)
BZM["FOOT"] = SUI.group("SkyyBzFoot", "Left", h=SUI.BTN_H)
BZM["NOTE"] = SUI.label(None, "Totals are whole coins - buys round up and sells round down", "caption",
                        w=BZ_IW - SUI.BTN_MIN_W - 6, h=SUI.BTN_H)
BZM["CLOSE"] = SUI.button("SkyyBzClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel", anchor={"left": 6})


def bz_sample(selected):
    """one static page state (J() samples), for the proven-property, width and height proofs"""
    ap = SUI.Appends(BZ_SH.appends)
    ap.append(("SkyyBz", BZM["HEAD"]))
    ap.append(("SkyyBzHead", BZM["SUB"]))
    ap.append(("SkyyBzHead", BZM["PURSE"]))
    ap.append(("SkyyBz", BZM["TABROW"]))
    for t in range(5):
        if t:
            ap.append(("SkyyBzTabs", BZM["TABGAP"]))
        ap.append(("SkyyBzTabs", SUI.render(BZM["TABON" if t == 0 else "TABOFF"]).replace("SkyyBzTab0", "SkyyBzTab%d" % t)))
    ap.append(("SkyyBzTabs", BZM["TABFILL"]))
    ap.append(("SkyyBzTabs", BZM["SELLINV"].b))
    for r in range(BZ_ROWS):
        ap.append(("SkyyBz", SUI.render(BZM["ROW"]).replace("SkyyBzRow0", "SkyyBzRow%d" % r)))
        for k in range(BZ_COLS):
            idx = r * BZ_COLS + k
            mk = BZM["CELL"].a if idx == 0 else BZM["CELL"].b
            ap.append(("SkyyBzRow%d" % r, SUI.render(mk).replace("SkyyBzCell0", "SkyyBzCell%d" % idx)) if idx < 40 else
                      ("SkyyBzRow%d" % r, BZM["EMPTY"]))
    ap.extend(BZ_PAGER)
    if selected:
        ap.append(("SkyyBz", BZM["DET"]))
        ap.append(("SkyyBzDetail", BZM["DICON"]))
        ap.append(("SkyyBzDetail", BZM["DTXT"]))
        for _k, mk in BZ_DLINES:
            ap.append(("SkyyBzDTxt", mk))
        ap.append(("SkyyBz", BZM["ACTS"]))
        for mk in BZ_ACTS:
            ap.append(("SkyyBzActs", mk))
        ap.append(("SkyyBz", BZM["AMTROW"]))
        for mk in BZ_AMT:
            ap.append(("SkyyBzAmtRow", mk))
        ap.append(("SkyyBz", BZM["LIM"]))
    else:
        ap.append(("SkyyBz", BZM["NODET"]))
        ap.append(("SkyyBzDetail", BZM["NODETTX"]))
    ap.append(("SkyyBz", BZM["INFO"]))
    ap.append(("SkyyBz", BZ_SEP))
    ap.append(("SkyyBz", BZM["FOOT"]))
    ap.append(("SkyyBzFoot", BZM["NOTE"]))
    ap.append(("SkyyBzFoot", BZM["CLOSE"]))
    return ap


for _sel in (True, False):
    _ap = bz_sample(_sel)
    SUI.assert_proven(_ap)
    assert SUI.used_height(_ap, "SkyyBz") == BZ_SH.inner_h, ("page body", _sel, SUI.used_height(_ap, "SkyyBz"), BZ_SH.inner_h)
    for _row in ["SkyyBzHead", "SkyyBzTabs", "SkyyBzRow0"] + (["SkyyBzActs", "SkyyBzAmtRow"] if _sel else []) + ["SkyyBzFoot"]:
        assert SUI.used_width(_ap, _row) <= BZ_IW, (_row, SUI.used_width(_ap, _row), BZ_IW)
    assert SUI.used_width(_ap, "SkyyBzHead") == BZ_IW and SUI.used_width(_ap, "SkyyBzTabs") == BZ_IW
    assert SUI.used_width(_ap, "SkyyBzFoot") == BZ_IW
    if _sel:
        assert SUI.used_width(_ap, "SkyyBzAmtRow") == BZ_IW and SUI.used_width(_ap, "SkyyBzDetail") == BZ_IW - 2 * SUI.WELL_PAD
        assert SUI.used_height(_ap, "SkyyBzDTxt") == BZ_DIN
# 6 tabs: the narrow tab width still leaves the filler >= 0
assert BZ_TABROOM - BZ_MAXT * BZ_TW6 - (BZ_MAXT - 1) * SUI.TAB_GAP >= 0
for _mk in (BZM["TABON"], BZM["TABOFF"]):
    SUI.check_markup(_mk)
    assert SUI.render(_mk).count(BZ_SENT) == 1
BZ_J = {
    "SHELL": BZ_SH.java("b"),
    "HEAD": "\n".join([SUI.java_append("SkyyBz", BZM["HEAD"]), SUI.java_append("SkyyBzHead", BZM["SUB"]),
                       SUI.java_append("SkyyBzHead", BZM["PURSE"])]),
    "TABROW": SUI.java_append("SkyyBz", BZM["TABROW"]),
    "TABGAP": SUI.java_append("SkyyBzTabs", BZM["TABGAP"]),
    "TABON": SUI.java_value(BZM["TABON"]),
    "TABOFF": SUI.java_value(BZM["TABOFF"]),
    "TABFILL": SUI.java_append("SkyyBzTabs", BZM["TABFILL"]),
    "SELLINV": SUI.java_append("SkyyBzTabs", BZM["SELLINV"]),
    "ROW": SUI.java_append("SkyyBz", BZM["ROW"]),
    "CELL": SUI.java_append("SkyyBzRow" + SUI.J("r", "0"), BZM["CELL"]),
    "EMPTY": SUI.java_append("SkyyBzRow" + SUI.J("r", "0"), BZM["EMPTY"]),
    "PAGER": BZ_PAGER.java("b"),
    "NODET": "\n".join([SUI.java_append("SkyyBz", BZM["NODET"]), SUI.java_append("SkyyBzDetail", BZM["NODETTX"])]),
    "DET": "\n".join([SUI.java_append("SkyyBz", BZM["DET"]), SUI.java_append("SkyyBzDetail", BZM["DICON"]),
                      SUI.java_append("SkyyBzDetail", BZM["DTXT"])] + [SUI.java_append("SkyyBzDTxt", mk) for _k, mk in BZ_DLINES]),
    "ACTS": "\n".join([SUI.java_append("SkyyBz", BZM["ACTS"])] + [SUI.java_append("SkyyBzActs", mk) for mk in BZ_ACTS]),
    "AMT": "\n".join([SUI.java_append("SkyyBz", BZM["AMTROW"])] + [SUI.java_append("SkyyBzAmtRow", mk) for mk in BZ_AMT]),
    "LIM": SUI.java_append("SkyyBz", BZM["LIM"]),
    "INFO": SUI.java_append("SkyyBz", BZM["INFO"]),
    "FOOT": "\n".join([SUI.java_append("SkyyBz", BZ_SEP), SUI.java_append("SkyyBz", BZM["FOOT"]),
                       SUI.java_append("SkyyBzFoot", BZM["NOTE"]), SUI.java_append("SkyyBzFoot", BZM["CLOSE"])]),
}
assert not any("@" in v for v in BZ_J.values())
# the result line's colour by its words (the 0.1.2 texts carry no + / - / = mark): green done, red refused / failed, yellow asks
BZ_INFO_COLOR = SUI.java_color_by_text("infoColor", [
    ("startsWith", "bought ", "+"), ("startsWith", "sold ", "+"),
    ("contains", "FAILED", "-"), ("contains", "tell an admin", "-"), ("contains", "could not", "-"), ("contains", "not loaded", "-"),
    ("contains", "did not answer", "-"), ("contains", "failed", "-"), ("startsWith", "you need ", "-"), ("startsWith", "not enough", "-"),
    ("contains", "inventory is full", "-"), ("startsWith", "you have no", "-"), ("startsWith", "you only hold", "-"),
    ("contains", "worth 0 coins", "-"), ("startsWith", "that is not", "-"), ("contains", "price moved", "warning"),
    ("contains", "again within", "warning"), ("contains", "click Confirm", "warning"), ("contains", "click Buy or Sell", "warning")],
    empty="=", default="=")
print("page: %d x %d plain window, %d products a page (%d x %d), parts %s, kit %s" % (BZ_W, BZ_H, BZ_PER, BZ_COLS, BZ_ROWS, BZ_PARTS, KIT_ID))

page.addField(CtField.make("public String cat;", page))
page.addField(CtField.make("public String sel;", page))
page.addField(CtField.make("public String[] cells;", page))
page.addField(CtField.make("public String[] tabs;", page))
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public long confirmUntil;", page))
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
  @PKG@.Product p = @PKG@.Catalog.get(sel);
  this.cat = p == null ? null : p.cat;
}"""), page))
page.addMethod(CtNewMethod.make("""
public void disarm() {
  this.armId = null;
  this.armBQ = 0;
  this.armBuy = -1L;
  this.armSQ = 0;
  this.armSell = -1L;
  this.armUntil = 0L;
}""", page))
# event data for a binding; while the amount field is on the page every binding also carries its current text (@BzAmount)
page.addMethod(CtNewMethod.make(f"""
public {EVD} evd(String a, boolean amt) {{
  {EVD} d = {EVD}.of("a", a);
  if (amt) d = d.append("@BzAmount", "#SkyyBzAmt.Value");
  return d;
}}""", page))
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
  int held = {PKG}.Inv.count(p, id);
  int room = {PKG}.Trader.room(p, id);
  int afford = -1;
  if ({PKG}.Coins.ready()) {{
    long purse = {PKG}.Coins.get(u);
    if (purse >= 0L) afford = {PKG}.Market.maxBuyable(id, purse, room < {PKG}.Trader.MAXQ ? room : {PKG}.Trader.MAXQ);
  }}
  return new int[] {{ afford, room, held }};
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
# the whole page (build() only resolves the player; render() is also what the offline markup check calls)
page.addMethod(CtNewMethod.make(jt(r"""
public void render(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ player) {
  java.util.ArrayList cats = @PKG@.Catalog.categories();
  if (this.cat == null || !cats.contains(this.cat)) { this.cat = cats.isEmpty() ? null : (String) cats.get(0); this.pageNo = 0; }
  if (this.sel != null && !@PKG@.Catalog.usable(this.sel)) this.sel = null;
  boolean coinsOk = @PKG@.Coins.ready();
  boolean confirming = System.currentTimeMillis() <= this.confirmUntil;
  @PKG@.Product sp = @PKG@.Catalog.get(this.sel);
  boolean amtOn = sp != null && player != null;
  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : @PKG@.Catalog.inCat(this.cat);
  for (int i = 0; i < raw.size(); i++) { @PKG@.Product q = (@PKG@.Product) raw.get(i); if (@PKG@.Catalog.usable(q.id)) list.add(q); }
  int total = list.size();
  int pages = total <= 0 ? 1 : (total + @PER@ - 1) / @PER@;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int from = this.pageNo * @PER@;
  int n = total - from;
  if (n > @PER@) n = @PER@;
  if (n < 0) n = 0;
  long pv = coinsOk ? @PKG@.Coins.get(u) : 0L;
  boolean purseOk = coinsOk && pv >= 0L;
  String purse = coinsOk ? (pv >= 0L ? ("Purse  " + pv + " coins") : "Purse unavailable - coin bank error") : "SkyyCoins is not loaded - trading is off";
  int nt = cats.size() < @MAXT@ ? cats.size() : @MAXT@;
  int hidC = cats.size() - nt;
  String sub = "Instant buy and sell with the market - prices move with every trade and drift back over time";
  if (hidC > 0) sub = hidC + " more tabs do not fit the page (" + @MAXT@ + " tabs) - tell an admin";
@SHELL@
@HEAD@
  b.set("#SkyyBzSub.Text", sub);
  b.set("#SkyyBzPurse.Text", purse);
  int tw = nt <= 5 ? @TWA@ : @TWB@;
  int gap = @TABROOM@ - nt * tw - (nt > 1 ? (nt - 1) * @TG@ : 0);
  if (gap < 0) gap = 0;
@TABROW@
  this.tabs = new String[nt];
  for (int i = 0; i < nt; i++) {
    String c = (String) cats.get(i);
    this.tabs[i] = c;
    boolean ton = c.equals(this.cat);
    if (i > 0) { @TABGAP@ }
    b.appendInline("#SkyyBzTabs", (ton ? (@TABON@) : (@TABOFF@)).replace("@SENT@", tabText(c)));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzTab" + i, evd("tab:" + i, amtOn));
  }
@TABFILL@
@SELLINV@
  ev.addEventBinding(@BT@.Activating, "#SkyyBzSellInv", evd("sellinv", amtOn));
  this.cells = new String[@PER@];
  for (int r = 0; r < @ROWS@; r++) {
@ROW@
    for (int k = 0; k < @COLS@; k++) {
      int idx = r * @COLS@ + k;
      if (idx < n) {
        @PKG@.Product p = (@PKG@.Product) list.get(from + idx);
        this.cells[idx] = p.id;
        boolean con = p.id.equals(this.sel);
@CELL@
        int held = player == null ? 0 : @PKG@.Inv.count(player, p.id);
        if (held > 0) b.set("#SkyyBzCell" + idx + "Qty.Text", String.valueOf(held));
        ev.addEventBinding(@BT@.Activating, "#SkyyBzCell" + idx, evd("cell:" + idx, amtOn));
      } else {
@EMPTY@
      }
    }
  }
@PAGER@
  b.set("#SkyyBzPgPage.Text", total <= 0 ? "No products in this tab" : ("Page " + (this.pageNo + 1) + " of " + pages + "   -   " + total + " products"));
  ev.addEventBinding(@BT@.Activating, "#SkyyBzPgPrev", evd("prev", amtOn));
  ev.addEventBinding(@BT@.Activating, "#SkyyBzPgNext", evd("next", amtOn));
  if (!amtOn) {
@NODET@
  } else {
    String id = sp.id;
    long b1 = @PKG@.Market.quote(id, 1, true), b64 = @PKG@.Market.quote(id, 64, true);
    long s1 = @PKG@.Market.quote(id, 1, false), s64 = @PKG@.Market.quote(id, 64, false);
    int[] lim = limits(player, u, id);
    int held = lim[2];
    long sAll = held > 0 ? @PKG@.Market.quote(id, held > @PKG@.Trader.MAXQ ? @PKG@.Trader.MAXQ : held, false) : 0L;
    double f = @PKG@.Market.factor(id);
@DET@
    b.set("#SkyyBzDName.Text", sp.name);
    b.set("#SkyyBzDBuy.Text", "Instant buy   " + b1 + " coins for 1   -   " + b64 + " for 64   -   about " + @PKG@.BzUtil.num(@PKG@.Market.unit(id, true)) + " each");
    b.set("#SkyyBzDSell.Text", "Instant sell   " + s1 + " coins for 1   -   " + s64 + " for 64   -   about " + @PKG@.BzUtil.num(@PKG@.Market.unit(id, false)) + " each");
    b.set("#SkyyBzDHold.Text", "You hold " + held + (held > 0 ? "   -   selling all pays " + sAll + " coins" : ""));
    b.set("#SkyyBzDDem.Text", "Demand " + @PKG@.BzUtil.num(f) + "x   -   buying pushes it up and selling pushes it down - it drifts back to 1.0x");
    b.set("#SkyyBzDProc.Text", @PKG@.Catalog.procLine(sp));
@ACTS@
    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuy1", evd("buy1", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzBuy64", evd("buy64", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzSell1", evd("sell1", true));
    ev.addEventBinding(@BT@.Activating, "#SkyyBzSell64", evd("sell64", true));
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
@INFO@
  b.set("#SkyyBzInfo.Text", this.info == null ? "" : this.info);
@FOOT@
  ev.addEventBinding(@BT@.Activating, "#SkyyBzClose", evd("close", amtOn));
}""", PER=BZ_PER, MAXT=BZ_MAXT, TWA=BZ_TW5, TWB=BZ_TW6, TABROOM=BZ_TABROOM, TG=SUI.TAB_GAP, ROWS=BZ_ROWS, COLS=BZ_COLS, SENT=BZ_SENT,
   **BZ_J), page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  render(b, ev, u, player);
}}""", page))
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
    String ws = sellWhy(qs, lim[2]);
    long cb = wb == null ? {PKG}.Market.quote(id, qb, true) : -1L;
    long cs = ws == null ? {PKG}.Market.quote(id, qs, false) : -1L;
    if (wb == null && cb <= 0L) wb = "no price right now";
    if (ws == null && cs <= 0L) ws = cs == 0L ? "worth 0 coins - sell more at once" : "no price right now";
    disarm();
    this.armId = id;
    if (wb == null) {{ this.armBQ = qb; this.armBuy = cb; }}
    if (ws == null) {{ this.armSQ = qs; this.armSell = cs; }}
    if (wb == null || ws == null) this.armUntil = now + 15000L;
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
  if (why != null) {{ this.info = (buy ? "Buy " : "Sell ") + nm + " - " + why; disarm(); return; }}
  boolean armed = now <= this.armUntil && id.equals(this.armId) && (buy ? (this.armBuy > 0L && this.armBQ == q) : (this.armSell > 0L && this.armSQ == q));
  if (!armed) {{
    // max / all is worked out again on every click; if this side was priced for a different max a moment ago (prices, the purse or
    // the inventory changed), say so instead of a plain re-quote (a fixed number that moved is reported by Trader.buyN0 / sellN0)
    int was = 0;
    if (v == -2L && now <= this.armUntil && id.equals(this.armId)) was = buy ? (this.armBuy > 0L ? this.armBQ : 0) : (this.armSell > 0L ? this.armSQ : 0);
    long c = {PKG}.Market.quote(id, q, buy);
    disarm();
    if (c <= 0L) {{ this.info = c == 0L ? q + " " + nm + " is worth 0 coins right now - sell more at once" : "price error - tell an admin"; return; }}
    this.armId = id;
    if (buy) {{ this.armBQ = q; this.armBuy = c; }} else {{ this.armSQ = q; this.armSell = c; }}
    this.armUntil = now + 10000L;
    String pre = was > 0 && was != q ? "your max changed from " + was + " to " + q + " - " : "";
    this.info = pre + (buy ? "Buy " : "Sell ") + q + " " + nm + " for " + c + " coins - click " + (buy ? "Buy" : "Sell") + " again within 10 s to confirm";
    return;
  }}
  long seen = buy ? this.armBuy : this.armSell;
  {TR} r = null;
  if (buy) r = {PKG}.Trader.buyN(p, u, who, id, q, seen);
  else r = {PKG}.Trader.sellN(p, u, who, id, q, seen);
  disarm();
  if (r == null) return;
  if (r.moved && r.price > 0L) {{
    this.armId = id;
    if (buy) {{ this.armBQ = q; this.armBuy = r.price; }} else {{ this.armSQ = q; this.armSell = r.price; }}
    this.armUntil = now + 10000L;
  }}
  if (r.alert) this.playerRef.sendMessage({MSG}.raw("[Bazaar] " + r.msg));
  this.info = r.msg;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
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
    // any click other than the Sell inventory button itself cancels a pending "Confirm sell"
    // (selecting another item or trading must never leave the full-inventory sell armed)
    boolean sellInvClick = a.equals("sellinv");
    if (!sellInvClick) this.confirmUntil = 0L;
    // the same for a priced custom amount: only the amount field / its Buy and Sell buttons keep it armed
    boolean amtAct = a.equals("amt") || a.equals("abuy") || a.equals("asell");
    if (!amtAct) disarm();
    // 0.1.3: the footer Close (the vanilla way out next to Esc) and the grid pager (Prev on page 1 / Next on the last page do nothing)
    if (a.equals("close")) {{ close(); return; }}
    if (a.equals("prev")) {{ if (this.pageNo > 0) this.pageNo = this.pageNo - 1; this.info = ""; rebuild(); return; }}
    if (a.equals("next")) {{ this.pageNo = this.pageNo + 1; this.info = ""; rebuild(); return; }}
    for (int i = 0; this.tabs != null && i < this.tabs.length; i++) {{
      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.pageNo = 0; this.info = ""; rebuild(); return; }}
    }}
    for (int i = 0; this.cells != null && i < this.cells.length; i++) {{
      if (this.cells[i] != null && a.equals("cell:" + i)) {{ this.sel = this.cells[i]; this.info = ""; rebuild(); return; }}
    }}
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    String who = {PKG}.BzUtil.safe(this.playerRef.getUsername()).replace(' ', '_');
    if (amtAct) {{ amountAction(p, u, who, a, now); rebuild(); return; }}
    {TR} r = null;
    if (a.equals("buy1")) r = {PKG}.Trader.buy(p, u, who, this.sel, 1);
    else if (a.equals("buy64")) r = {PKG}.Trader.buy(p, u, who, this.sel, 64);
    else if (a.equals("sell1")) r = {PKG}.Trader.sell(p, u, who, this.sel, 1);
    else if (a.equals("sell64")) r = {PKG}.Trader.sell(p, u, who, this.sel, 64);
    else if (a.equals("sellall")) r = {PKG}.Trader.sell(p, u, who, this.sel, 0);
    else if (sellInvClick) {{
      // no "sell N items - click Confirm sell" preview that every sell0 would then refuse (profile crash recovery at join)
      if ({PKG}.Trader.busy(u)) {{ this.info = "your profile is still loading - try again in a moment"; this.confirmUntil = 0L; rebuild(); return; }}
      if (now > this.confirmUntil) {{
        long[] pv = {PKG}.Trader.preview(p);
        if (pv[0] <= 0L) {{ this.info = "nothing to sell - no bazaar items in your inventory"; this.confirmUntil = 0L; }}
        else {{ this.info = "sell " + pv[0] + " items for about " + pv[1] + " coins - click Confirm sell within 10 seconds"; this.confirmUntil = now + 10000L; }}
        rebuild();
        return;
      }}
      this.confirmUntil = 0L;
      r = {PKG}.Trader.sellInventory(p, u, who);
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
  String mig = @PKG@.Catalog.migrate();
  String mig14 = @PKG@.Catalog.migrate14();
  int n = @PKG@.Catalog.load();
  @PKG@.Market.load();
  if (@PKG@.Market.SPREAD < 0.10) @PKG@.BzUtil.warn("market.properties spread " + @PKG@.Market.SPREAD + " is below 0.10 - the build's no-money-loop proof assumes 0.10 (processed goods cap their premium at " + @PKG@.BzUtil.num(@PKG@.BzCfg.maxSafe() * 100.0) + "%)");
  @PKG@.Catalog.reprice();
  @PKG@.Market.publishAll();
  @PKG@.Catalog.flushIfDirty();
  @PKG@.Catalog.warnLoops(@PKG@.Market.SPREAD);
  if (mig != null) @PKG@.Market.log(mig);
  if (mig14 != null) { for (int i = 0; i < @PKG@.Catalog.M14_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M14_LOG.get(i)); }
  @PKG@.Catalog.M14_LOG.clear();
  getCommandRegistry().registerCommand(new @PKG@.BzCmd());
  getCommandRegistry().registerCommand(new @PKG@.BzAdminCmd());
  @OCU@.registerSimple(this, @PKG@.SkyyBazaarPlugin.class, "SkyyBazaar", new @PKG@.BzPageFactory());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.BzTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBazaar] @VER@ ready - /bazaar (/bz), " + n + " products in " + @PKG@.Catalog.categories().size() + " tabs, spread " + @PKG@.Market.SPREAD + ", processed goods premium " + @PKG@.BzCfg.PREMIUM + "% (coins bridge " + (@PKG@.Coins.ready() ? "found" : "NOT found yet") + ", @KIT@)");
  // LAST: the admin config kit reads config.properties after BzCfg.load and publishes config:def:SkyyBazaar + config:fn:SkyyBazaar
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""", OCU=OCU, HSV=HSV, VER=VERSION, KIT=KIT_ID), pl))
pl.addMethod(CtNewMethod.make(jt(r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.Market.decay(System.currentTimeMillis()); @PKG@.Market.flush(); } catch (Throwable t) { }
  try { @PKG@.Catalog.flushIfDirty(); } catch (Throwable t) { }
  try { @PKG@.Market.unpublishAll(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.BzUtil.warn("config kit flush at shutdown failed: " + t); }
  super.shutdown();
}"""), pl))

ALL = (utl, coin, prod, cat_, mkt, inv_, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, pl, cfgc)
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
assert len(_aitems) == len(ALL) + 7 and AUDIT_N > 2000, (len(_aitems), AUDIT_N)
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used from their "
      "own subclass: %s" % (AUDIT_N, len(_aitems), ", ".join(AUDIT_USED) or "none"))

jar = os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)
m = B.manifest("SkyyBazaar", VERSION, "SkyWynn bazaar: /bazaar instant buy and sell of the Magic Bag materials (Mining, Foraging, Farming, Combat, Smithing tabs) against a demand-driven market maker; processed goods cost a premium over their raw inputs. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBazaarPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    raise SystemExit("0.1.3: no --deploy from a build script - deploys go through python tools/deploy_set.py --yes (the SET)")
