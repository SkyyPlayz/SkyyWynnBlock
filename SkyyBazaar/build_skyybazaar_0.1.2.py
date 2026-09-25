"""SkyyBazaar 0.1.2 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.2.py            -> SkyyBazaar/SkyyBazaar-0.1.2.jar   (build only; --deploy only with Skyy's OK)
       python build_skyybazaar_0.1.2.py --deploy   -> also copies to Mods/SkyyBazaar.jar and enables it in the HUD mod world
       (0.1.2 is generated from build_skyybazaar_0.1.1.py by tools/bazaar_0_1_2_patch.py; 0.1.1 is generated from 0.1 by
       tools/bazaar_0_1_1_patch.py; both older scripts are kept as they were)

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
import sys, os, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.2"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SPREAD = 0.10

# ================= products (id, category, base price, display name = official en-US name) =================
PRODUCTS = [
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

check_assets({p[0]: float(p[2]) for p in PRODUCTS}, SPREAD)
for pid, cat, base, name in PRODUCTS:
    assert all(c.isalnum() or c == "_" for c in pid), pid
    assert "," not in cat and "," not in name and "=" not in name, pid

# ================= javassist =================
J = B.start()
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

# ================= Catalog (products.properties, file order kept) =================
seed = ", ".join('"%s=%s,%s,%s"' % (pid, cat, ("%g" % base), name) for pid, cat, base, name in PRODUCTS)
cat_.addField(CtField.make("public static java.nio.file.Path FILE;", cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList LIST = new java.util.ArrayList();", cat_))
cat_.addField(CtField.make("public static final java.util.HashMap BY_ID = new java.util.HashMap();", cat_))
cat_.addField(CtField.make("public static final java.util.HashSet WARNED = new java.util.HashSet();", cat_))
cat_.addField(CtField.make("public static final String[] SEED = new String[] { %s };" % seed, cat_))
cat_.addField(CtField.make('public static final String HEADER = "# SkyyBazaar products - one per line: <ItemId>=<Category>,<basePrice>,<Display Name>\\n# Tabs appear in file order. basePrice may be fractional (0.5). Keep base(B) < 1.22 x base(A) for any recipe A -> B (no money loops).\\n# After editing run /bazaaradmin reload. /bazaaradmin price <itemId> <base> rewrites this file.\\n";', cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.Product get(String id) {{
  if (id == null) return null;
  return ({PKG}.Product) BY_ID.get(id);
}}""", cat_))
cat_.addMethod(CtNewMethod.make("""
public static synchronized java.util.ArrayList all() {
  return new java.util.ArrayList(LIST);
}""", cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.ArrayList categories() {{
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < LIST.size(); i++) {{
    String c = (({PKG}.Product) LIST.get(i)).cat;
    if (!out.contains(c)) out.add(c);
  }}
  return out;
}}""", cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.ArrayList inCat(String cat) {{
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < LIST.size(); i++) {{
    {PKG}.Product p = ({PKG}.Product) LIST.get(i);
    if (p.cat.equals(cat)) out.add(p);
  }}
  return out;
}}""", cat_))
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
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized int load() {{
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.util.ArrayList seed = new java.util.ArrayList();
      for (int i = 0; i < SEED.length; i++) seed.add(SEED[i]);
      writeLines(seed);
      {PKG}.BzUtil.info("seeded " + FILE + " with " + SEED.length + " products");
    }}
    java.util.List lines = java.nio.file.Files.readAllLines(FILE, java.nio.charset.StandardCharsets.UTF_8);
    java.util.ArrayList list = new java.util.ArrayList();
    java.util.HashMap map = new java.util.HashMap();
    for (int i = 0; i < lines.size(); i++) {{
      {PKG}.Product p = parse((String) lines.get(i));
      if (p == null) continue;
      if (map.containsKey(p.id)) {{ {PKG}.BzUtil.warn("products.properties: duplicate " + p.id + " ignored"); continue; }}
      list.add(p); map.put(p.id, p);
    }}
    LIST.clear(); LIST.addAll(list);
    BY_ID.clear(); BY_ID.putAll(map);
    WARNED.clear();
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("could not load products: " + t); }}
  return LIST.size();
}}""", cat_))
cat_.addMethod(CtNewMethod.make(f"""
public static synchronized boolean setBase(String id, double base) {{
  {PKG}.Product p = get(id);
  if (p == null || !(base >= 0.01 && base <= 1000000000.0)) return false;
  p.base = base;
  try {{
    java.util.ArrayList lines = new java.util.ArrayList();
    for (int i = 0; i < LIST.size(); i++) {{
      {PKG}.Product q = ({PKG}.Product) LIST.get(i);
      lines.add(q.id + "=" + q.cat + "," + {PKG}.BzUtil.num(q.base) + "," + q.name);
    }}
    writeLines(lines);
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("could not save products: " + t); }}
  return true;
}}""", cat_))

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

# ================= BzPage (inline page; syntax copied from SkyySacks 0.6.1 SacksPage/CraftPage) =================
# 0.1.2: about 1.4x (root 1080 wide; 640 high with one grid row, +94 per extra row, 828 max), a custom amount row (TextField
# #SkyyBzAmt - SkyyGuilds 0.1 Amount field / SkyySacks 0.7.3 search pattern: Enter = Validating, buttons = Activating, the typed text
# arrives as "@BzAmount"), and every action matched exactly with jsonStr(data, "a") (typed text can never look like a payload).
BS_BROWN = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 17, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_ON    = "Style: TextButtonStyle(Default: (Background: #e0b060, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #f0c878, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #b08040, LabelStyle: (FontSize: 17, TextColor: #1a1000, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_BUY   = "Style: TextButtonStyle(Default: (Background: #2f5a34, LabelStyle: (FontSize: 16, TextColor: #dfffe0, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3f7a46, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #1f3a22, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
BS_SELL  = "Style: TextButtonStyle(Default: (Background: #6a2e2e, LabelStyle: (FontSize: 16, TextColor: #ffe0e0, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a4040, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #4a1e1e, LabelStyle: (FontSize: 16, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));"
for s in (BS_BROWN, BS_ON, BS_BUY, BS_SELL):
    assert '"' not in s and "{" not in s

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
page.addConstructor(CtNewConstructor.make(f"""
public BzPage({PR} pr, String sel) {{
  super(pr, {LIFE}.CanDismiss);
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
  {PKG}.Product p = {PKG}.Catalog.get(sel);
  this.cat = p == null ? null : p.cat;
}}""", page))
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
# the whole page (build() only resolves the player; render() is also what the offline markup check calls)
page.addMethod(CtNewMethod.make(f"""
public void render({UCB} b, {UEB} ev, java.util.UUID u, {PLA} player) {{
  java.util.ArrayList cats = {PKG}.Catalog.categories();
  if (this.cat == null || !cats.contains(this.cat)) this.cat = cats.isEmpty() ? null : (String) cats.get(0);
  if (this.sel != null && !{PKG}.Catalog.usable(this.sel)) this.sel = null;
  boolean coinsOk = {PKG}.Coins.ready();
  boolean confirming = System.currentTimeMillis() <= this.confirmUntil;
  String bs = "{BS_BROWN}";
  String on = "{BS_ON}";
  String buyS = "{BS_BUY}";
  String sellS = "{BS_SELL}";
  {PKG}.Product sp = {PKG}.Catalog.get(this.sel);
  boolean amtOn = sp != null && player != null;
  java.util.ArrayList list = new java.util.ArrayList();
  java.util.ArrayList raw = this.cat == null ? new java.util.ArrayList() : {PKG}.Catalog.inCat(this.cat);
  for (int i = 0; i < raw.size(); i++) {{ {PKG}.Product p = ({PKG}.Product) raw.get(i); if ({PKG}.Catalog.usable(p.id)) list.add(p); }}
  int n = list.size() < 27 ? list.size() : 27;
  int rows = (n + 8) / 9;
  int h = 640 + ((rows < 1 ? 1 : rows) - 1) * 94;
  b.appendInline((String) null, "Group #SkyyBz {{ Anchor: (Width: 1080, Height: " + h + "); Background: #0b1524(0.96); Padding: (Horizontal: 22, Vertical: 14); LayoutMode: Top; }}");
  b.appendInline("#SkyyBz", "Group {{ Anchor: (Height: 3); Background: #e0b060; }}");
  b.appendInline("#SkyyBz", "Group #SkyyBzHead {{ Anchor: (Height: 44); LayoutMode: Left; }}");
  b.appendInline("#SkyyBzHead", "Label {{ Anchor: (Width: 420, Height: 44); Text: \\"Bazaar\\"; Style: (FontSize: 24, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
  long pv = coinsOk ? {PKG}.Coins.get(u) : 0L;
  String purse = coinsOk ? (pv >= 0L ? ("Purse " + pv + " coins") : "Purse unavailable - coin bank error") : "SkyyCoins is not loaded - trading is off";
  b.appendInline("#SkyyBzHead", "Label {{ Anchor: (Width: 616, Height: 44); Text: \\"" + {PKG}.BzUtil.safe(purse) + "\\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + (coinsOk ? "#ffd766" : "#e07070") + ", HorizontalAlignment: End, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyBz", "Group #SkyyBzTabs {{ Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }}");
  int nt = cats.size() < 6 ? cats.size() : 6;
  int tw = nt <= 4 ? 146 : (804 - nt * 8) / nt;
  this.tabs = new String[nt];
  for (int i = 0; i < nt; i++) {{
    String c = (String) cats.get(i);
    this.tabs[i] = c;
    b.appendInline("#SkyyBzTabs", "TextButton #SkyyBzTab" + i + " {{ Anchor: (Width: " + tw + ", Height: 40); Text: \\"" + {PKG}.BzUtil.safe(c) + "\\"; " + (c.equals(this.cat) ? on : bs) + " }}");
    b.appendInline("#SkyyBzTabs", "Label {{ Anchor: (Width: 8, Height: 40); Text: \\"\\"; }}");
    ev.addEventBinding({BT}.Activating, "#SkyyBzTab" + i, evd("tab:" + i, amtOn));
  }}
  int gap = 1036 - nt * (tw + 8) - 224; if (gap < 4) gap = 4;
  b.appendInline("#SkyyBzTabs", "Label {{ Anchor: (Width: " + gap + ", Height: 40); Text: \\"\\"; }}");
  b.appendInline("#SkyyBzTabs", "TextButton #SkyyBzSellInv {{ Anchor: (Width: 220, Height: 40); Text: \\"" + (confirming ? "Confirm sell" : "Sell inventory") + "\\"; " + sellS + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyBzSellInv", evd("sellinv", amtOn));
  // the page holds 6 tabs x 27 products (0.1.1 caps; more rows / tabs need a client check of the height and tab width first). Anything
  // past them is named here in the same fixed-height line instead of being hidden without a word.
  int hidP = list.size() - n;
  int hidC = cats.size() - nt;
  String sub = "Instant buy and sell with the market. Prices move with every trade and drift back over time.";
  if (hidP > 0 || hidC > 0) sub = (hidP > 0 ? hidP + " more products in this tab" : "") + (hidP > 0 && hidC > 0 ? " and " : "") + (hidC > 0 ? hidC + " more tabs" : "") + " do not fit the page (6 tabs of 27 products) - tell an admin";
  b.appendInline("#SkyyBz", "Label #SkyyBzSub {{ Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: " + (hidP > 0 || hidC > 0 ? "#ffb070" : "#9fb8cc") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyBzSub.Text", sub);
  this.cells = new String[27];
  if (n == 0) b.appendInline("#SkyyBz", "Label {{ Anchor: (Height: 94); Text: \\"No products here.\\"; Style: (FontSize: 17, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int r = 0; r < rows; r++) {{
    b.appendInline("#SkyyBz", "Group #SkyyBzRow" + r + " {{ Anchor: (Height: 94); LayoutMode: Left; Padding: (Top: 6); }}");
    b.appendInline("#SkyyBzRow" + r, "Label {{ Anchor: (Width: 99, Height: 87); Text: \\"\\"; }}");
    for (int c = 0; c < 9; c++) {{
      int idx = r * 9 + c;
      if (idx < n) {{
        {PKG}.Product p = ({PKG}.Product) list.get(idx);
        this.cells[idx] = p.id;
        int held = player == null ? 0 : {PKG}.Inv.count(player, p.id);
        String bg = p.id.equals(this.sel) ? "#4f7fb0" : "#1d3a5f";
        b.appendInline("#SkyyBzRow" + r, "Button #SkyyBzCell" + idx + " {{ Anchor: (Width: 87, Height: 87); Style: ButtonStyle( Default: ( Background: " + bg + " ), Hovered: ( Background: #2f5a8f ), Disabled: ( Background: #1a2c3c ) ); ItemIcon {{ Anchor: (Width: 64, Height: 64, Left: 11, Top: 6); ItemId: \\"" + p.id + "\\"; }} Label {{ Anchor: (Width: 81, Height: 20, Right: 4, Bottom: 3); Text: \\"" + (held > 0 ? String.valueOf(held) : "") + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); }} }}");
        ev.addEventBinding({BT}.Activating, "#SkyyBzCell" + idx, evd("cell:" + idx, amtOn));
      }} else {{
        b.appendInline("#SkyyBzRow" + r, "Group {{ Anchor: (Width: 87, Height: 87); Background: #142030(0.9); }}");
      }}
      b.appendInline("#SkyyBzRow" + r, "Label {{ Anchor: (Width: 6, Height: 87); Text: \\"\\"; }}");
    }}
  }}
  b.appendInline("#SkyyBz", "Group {{ Anchor: (Height: 10); }}");
  if (!amtOn) {{
    // same height as detail (168) + trade row (58) + amount row (58) + limits line (28), so selecting a product never resizes the page
    b.appendInline("#SkyyBz", "Group #SkyyBzDetail {{ Anchor: (Height: 312); LayoutMode: Top; Background: #10233a(0.9); }}");
    b.appendInline("#SkyyBzDetail", "Label {{ Anchor: (Height: 312); Text: \\"Click a product to see its prices and trade it.\\"; Style: (FontSize: 18, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  }} else {{
    String id = sp.id;
    long b1 = {PKG}.Market.quote(id, 1, true), b64 = {PKG}.Market.quote(id, 64, true);
    long s1 = {PKG}.Market.quote(id, 1, false), s64 = {PKG}.Market.quote(id, 64, false);
    int[] lim = limits(player, u, id);
    int held = lim[2];
    long sAll = held > 0 ? {PKG}.Market.quote(id, held > {PKG}.Trader.MAXQ ? {PKG}.Trader.MAXQ : held, false) : 0L;
    double f = {PKG}.Market.factor(id);
    b.appendInline("#SkyyBz", "Group #SkyyBzDetail {{ Anchor: (Height: 168); LayoutMode: Left; Padding: (Top: 8); Background: #10233a(0.9); }}");
    b.appendInline("#SkyyBzDetail", "Group {{ Anchor: (Width: 140, Height: 152); ItemIcon {{ Anchor: (Width: 118, Height: 118, Left: 11, Top: 8); ItemId: \\"" + id + "\\"; }} }}");
    b.appendInline("#SkyyBzDetail", "Group #SkyyBzDTxt {{ Anchor: (Width: 880, Height: 152); LayoutMode: Top; }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 34); Text: \\"" + {PKG}.BzUtil.safe(sp.name) + "\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("Instant buy   " + b1 + " coins for 1   -   " + b64 + " for 64   -   about " + {PKG}.BzUtil.num({PKG}.Market.unit(id, true)) + " each") + "\\"; Style: (FontSize: 17, TextColor: #9fe8a2, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("Instant sell   " + s1 + " coins for 1   -   " + s64 + " for 64   -   about " + {PKG}.BzUtil.num({PKG}.Market.unit(id, false)) + " each") + "\\"; Style: (FontSize: 17, TextColor: #ffb0a0, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 28); Text: \\"" + {PKG}.BzUtil.safe("You hold " + held + (held > 0 ? "   -   selling all pays " + sAll + " coins" : "")) + "\\"; Style: (FontSize: 17, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzDTxt", "Label {{ Anchor: (Height: 26); Text: \\"" + {PKG}.BzUtil.safe("Demand " + {PKG}.BzUtil.num(f) + "x   -   buying pushes it up and selling pushes it down - it drifts back to 1.0x") + "\\"; Style: (FontSize: 14, TextColor: #8fa4b8, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBz", "Group #SkyyBzActs {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzBuy1 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Buy 1 for " + b1) + "\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzBuy64 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Buy 64 for " + b64) + "\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSell1 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell 1 for " + s1) + "\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSell64 {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell 64 for " + s64) + "\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzActs", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzActs", "TextButton #SkyyBzSellAll {{ Anchor: (Width: 196, Height: 42); Text: \\"" + {PKG}.BzUtil.safe("Sell all " + held) + "\\"; " + sellS + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyBzBuy1", evd("buy1", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzBuy64", evd("buy64", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSell1", evd("sell1", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSell64", evd("sell64", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzSellAll", evd("sellall", true));
    // 0.1.2 custom amount row (inline TextField exactly like SkyyGuilds' #SkyyGAmount / SkyySacks' #SkyyCSearch)
    b.appendInline("#SkyyBz", "Group #SkyyBzAmtRow {{ Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 8); }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 176, Height: 42); Text: \\"Custom amount\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyBzAmtRow", "Group #SkyyBzAmtBox {{ Anchor: (Width: 220, Height: 42); Background: #16263a; }}");
    b.appendInline("#SkyyBzAmtBox", "TextField #SkyyBzAmt {{ Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 12; PlaceholderText: \\"Amount\\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 18); Style: (TextColor: #ffffff, FontSize: 18); }}");
    if (this.amount != null && this.amount.length() > 0) b.set("#SkyyBzAmt.Value", this.amount);
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "TextButton #SkyyBzABuy {{ Anchor: (Width: 170, Height: 42); Text: \\"Buy\\"; " + buyS + " }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 10, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "TextButton #SkyyBzASell {{ Anchor: (Width: 170, Height: 42); Text: \\"Sell\\"; " + sellS + " }}");
    b.appendInline("#SkyyBzAmtRow", "Label {{ Anchor: (Width: 14, Height: 42); Text: \\"\\"; }}");
    b.appendInline("#SkyyBzAmtRow", "Label #SkyyBzAmtHint {{ Anchor: (Width: 266, Height: 42); Text: \\"\\"; Style: (FontSize: 14, TextColor: #9fb8cc, VerticalAlignment: Center); }}");
    b.set("#SkyyBzAmtHint.Text", "Enter shows the price");
    ev.addEventBinding({BT}.Validating, "#SkyyBzAmt", evd("amt", true), false);
    ev.addEventBinding({BT}.Activating, "#SkyyBzABuy", evd("abuy", true));
    ev.addEventBinding({BT}.Activating, "#SkyyBzASell", evd("asell", true));
    int mq = {PKG}.Trader.MAXQ;
    String lt;
    if (!coinsOk) lt = "SkyyCoins is not loaded - trading is off.";
    else if ({PKG}.Trader.busy(u)) lt = "Your profile is still loading - trading is paused. Click again in a moment.";
    else if (lim[0] < 0) lt = "The coin bank did not answer - buy limit unknown. You can sell up to " + (held > mq ? mq : held) + ".";
    else {{
      int mb = lim[0];
      String why = mb >= mq ? "the per-trade limit" : (mb >= lim[1] ? (lim[1] <= 0 ? "your inventory is full" : "inventory room") : "your purse");
      lt = "You can buy up to " + mb + " (" + why + ") and sell up to " + (held > mq ? mq : held) + ".   Amounts like 500, 2k or max.";
    }}
    b.appendInline("#SkyyBz", "Label #SkyyBzLimits {{ Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 15, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyBzLimits.Text", lt);
  }}
  b.appendInline("#SkyyBz", "Label #SkyyBzInfo {{ Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd766, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyBzInfo.Text", this.info == null ? "" : this.info);
  b.appendInline("#SkyyBz", "Label {{ Anchor: (Height: 25); Text: \\"Totals are whole coins - buys round up and sells round down. Sell inventory and custom amounts ask you to confirm.\\"; Style: (FontSize: 14, TextColor: #6f879c, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
}}""", page))
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
    for (int i = 0; this.tabs != null && i < this.tabs.length; i++) {{
      if (a.equals("tab:" + i)) {{ this.cat = this.tabs[i]; this.info = ""; rebuild(); return; }}
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
adm.addMethod(CtNewMethod.make(f"""
public static void run({PR} pr, String action, String itemRaw, String valueRaw) {{
  try {{
    if (action == null) {{
      pr.sendMessage({MSG}.raw("[Bazaar] " + {PKG}.Catalog.all().size() + " products, spread " + {PKG}.Market.SPREAD + ", impactCoins " + {PKG}.Market.IMPACT + ", halfLifeMinutes " + {PKG}.Market.HALFLIFE + ", coins bridge " + ({PKG}.Coins.ready() ? "found" : "MISSING")));
      pr.sendMessage({MSG}.raw("[Bazaar] /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>"));
      return;
    }}
    String a = action.trim().toLowerCase();
    String item = itemRaw != null ? itemRaw.trim() : null;
    if (a.equals("reload")) {{
      {PKG}.Market.flushLog();
      int n = {PKG}.Catalog.load();
      {PKG}.Market.load();
      {PKG}.Market.publishAll();
      pr.sendMessage({MSG}.raw("[Bazaar] reloaded " + n + " products in " + {PKG}.Catalog.categories().size() + " categories; spread " + {PKG}.Market.SPREAD + ", impactCoins " + {PKG}.Market.IMPACT + ", halfLifeMinutes " + {PKG}.Market.HALFLIFE));
      return;
    }}
    if (item == null) {{ pr.sendMessage({MSG}.raw("[Bazaar] which item? /bazaaradmin " + a + " <itemId>")); return; }}
    if (a.equals("reset")) {{
      if (item.equalsIgnoreCase("all")) {{ {PKG}.Market.reset((String) null); pr.sendMessage({MSG}.raw("[Bazaar] every demand factor reset to 1.0")); return; }}
      if ({PKG}.Catalog.get(item) == null) {{ pr.sendMessage({MSG}.raw("[Bazaar] " + item + " is not a bazaar product")); return; }}
      {PKG}.Market.reset(item);
      pr.sendMessage({MSG}.raw("[Bazaar] " + item + " demand reset to 1.0"));
      return;
    }}
    {PKG}.Product p = {PKG}.Catalog.get(item);
    if (p == null) {{ pr.sendMessage({MSG}.raw("[Bazaar] " + item + " is not a bazaar product - add it to products.properties and /bazaaradmin reload")); return; }}
    if (a.equals("info")) {{
      long bo = {PKG}.Market.getBought(item); long so = {PKG}.Market.getSold(item);
      pr.sendMessage({MSG}.raw("[Bazaar] " + p.id + " (" + p.name + ", " + p.cat + "): base " + {PKG}.BzUtil.num(p.base) + ", demand " + {PKG}.BzUtil.num({PKG}.Market.factor(item)) + "x, buy 1 = " + {PKG}.Market.quote(item, 1, true) + ", sell 1 = " + {PKG}.Market.quote(item, 1, false) + ", lifetime bought " + bo + " sold " + so + ", known item " + {PKG}.Catalog.usable(item)));
      return;
    }}
    if (a.equals("price")) {{
      if (valueRaw == null) {{ pr.sendMessage({MSG}.raw("[Bazaar] /bazaaradmin price " + item + " <base>  (now " + {PKG}.BzUtil.num(p.base) + ")")); return; }}
      double v;
      try {{ v = Double.parseDouble(valueRaw.trim()); }} catch (Throwable t) {{ pr.sendMessage({MSG}.raw("[Bazaar] that is not a number")); return; }}
      double old = p.base;
      if (!{PKG}.Catalog.setBase(item, v)) {{ pr.sendMessage({MSG}.raw("[Bazaar] base must be 0.01 .. 1000000000")); return; }}
      {PKG}.Market.publish(item);
      {PKG}.Market.log("ADMIN-PRICE " + {PKG}.BzUtil.safe(pr.getUsername()).replace(' ', '_') + " " + pr.getUuid() + " " + item + " " + {PKG}.BzUtil.num(old) + " -> " + {PKG}.BzUtil.num(v));
      pr.sendMessage({MSG}.raw("[Bazaar] " + item + " base " + {PKG}.BzUtil.num(old) + " -> " + {PKG}.BzUtil.num(v) + " (buy 1 = " + {PKG}.Market.quote(item, 1, true) + ", sell 1 = " + {PKG}.Market.quote(item, 1, false) + "). Keep recipe outputs under 1.22x their inputs."));
      return;
    }}
    pr.sendMessage({MSG}.raw("[Bazaar] unknown action " + a + " - price | reload | reset | info"));
  }} catch (Throwable t) {{
    {PKG}.BzUtil.warn("/bazaaradmin failed: " + t);
    pr.sendMessage({MSG}.raw("[Bazaar] Usage: /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>"));
  }}
}}""", adm))

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
  }} catch (Throwable t) {{ {PKG}.BzUtil.warn("tick failed: " + t); }}
}}""", tick))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyBazaarPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.BzUtil.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyBazaar");
  {PKG}.Catalog.FILE = dir.resolve("products.properties");
  {PKG}.Market.FILE = dir.resolve("market.properties");
  {PKG}.Market.LOGFILE = dir.resolve("trades.log");
  int n = {PKG}.Catalog.load();
  {PKG}.Market.load();
  {PKG}.Market.publishAll();
  getCommandRegistry().registerCommand(new {PKG}.BzCmd());
  getCommandRegistry().registerCommand(new {PKG}.BzAdminCmd());
  {OCU}.registerSimple(this, {PKG}.SkyyBazaarPlugin.class, "SkyyBazaar", new {PKG}.BzPageFactory());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.BzTick(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBazaar] {VERSION} ready - /bazaar (/bz), " + n + " products, spread " + {PKG}.Market.SPREAD + " (coins bridge " + ({PKG}.Coins.ready() ? "found" : "NOT found yet") + ")");
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Market.decay(System.currentTimeMillis()); {PKG}.Market.flush(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Market.unpublishAll(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (utl, coin, prod, cat_, mkt, inv_, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyBazaar-%s.jar" % VERSION)
m = B.manifest("SkyyBazaar", VERSION, "SkyWynn bazaar: /bazaar instant buy and sell of commodities against a demand-driven market maker. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBazaarPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyBazaar.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyBazaar" % VERSION, disable_prefix="Skyy:")
