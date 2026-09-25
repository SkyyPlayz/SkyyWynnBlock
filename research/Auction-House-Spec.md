# Auction House: build spec (SkyyAuctions 0.1, Buy It Now only)

*Written 2026-09-24 by the auction-house spec pass. Only this file and `research/Auction-House-Research.md` changed; no build script, mod folder or game file was touched.*
*Revised 2026-09-24 after a review pass: 12 findings checked, 10 applied, 2 applied only in part. Section 13 says which and why.*
*Builds on `research/Auction-House-Research.md` (Hypixel facts + server-plugin patterns), the newest scripts of SkyyBazaar (0.1.2), SkyyCoins (0.1.5), SkyyProfiles (0.1), SkyySacks (0.7.5), SkyyRolls (0.1.4), SkyyGuilds (0.1.1), SkyyMenu (0.1.3) and SkyyAccessories (0.4.3), and `tools/PROFILES-CONTRACT.md`. Owner: Skyy (they/them).*

**Skyy's ask (2026-09-24):** "we also need a auction house to go with the bizzaar. (check hypixle skyblock to see how it works, and how to set it up. (im not a big fan of actions, id start with BIN (buy it now) auctions and maybe add the other kind later."

**Legend.** VERIFIED = seen in `HytaleServer.jar` / `Assets.zip` (read-only), in a verified-in-game page of ours, or in our own live scripts. UNVERIFIED = design that still needs the tests in section 11. `[SKYY?]` = a default Skyy should confirm (all collected in section 12).

---

## 0. Verdict (plain words)

**One new standalone mod, one build round, no other mod changes.** SkyyAuctions 0.1 is a Hypixel-style Auction House with **Buy It Now listings only**. A player puts an item up at a fixed price. The first player who pays that price gets it. Nobody bids. The data is shaped so bid auctions can be added later without converting any file (Appendix A).

| Piece | Size (Java in the build script) |
|---|---|
| Listing store: records, the one lock, state changes, atomic files, log | ~700 lines (`AhStore`, `AhRec`, `AhCfg`, `AhLog`) |
| Item snapshot / restore, category, rarity, name, inventory helpers | ~300 lines (`AhItem`) |
| One inline page, 4 views (Browse, Item, Create, Manage) | ~700 lines (`AhPage`) |
| `/ah` + subcommands, `/ahadmin` + subcommands, join notices, tick, bridge | ~400 lines |

**What players get:** `/ah` (also `/auction`, `/auctionhouse`) opens the Auction House. They can:
- browse 6 categories, search, sort 4 ways and filter by rarity;
- open an item to see its full tooltip text (rolls included), then buy it;
- sell any item from their own inventory through our own page, with the fee shown before they list;
- manage their listings: cancel, claim coins, claim items, Claim all;
- get told on their next join what sold or expired while they were away.

**Who owns what:** the **profile** that listed an item owns the listing. Coins and returned items are claimed into that profile. Buyers pay from whichever profile is active.

**Money:** LOCKED 2026-09-25: Hypixel fee defaults stay, and every fee value is a Server Setup row so it can be tuned live (SkyyEconomy auctions category). Until that menu ships, the same numbers live in `config.properties`:
- listing fee 1% / 2% / 2.5% by price, plus a flat duration fee on 1h, 6h, 12h and 24h. A 48h listing pays double that listing fee (LOCKED 2026-09-25);
- 1% tax on proceeds above 1,000,000 coins;
- 14 active listings per profile, 1 to 50 billion coins, durations 1h / 6h / 12h / 24h / 48h, default 24h (LOCKED 2026-09-25).

**Safety:** one lock, a strict state machine, and every change written before it counts. No item or coin is ever created. The only possible loss is a logged hard-crash window, and an admin can repair it (section 6).

**VERIFIED building blocks (this pass):**
- `ItemStack.getDisplayName()` and `getDisplayDescription()` read the native `ItemDisplayMetadata` first (HytaleServer.jar bytecode), which is where SkyyRolls writes its reforge name and roll lines. They fall back to the item's translation. So the item view can show the same text as the native tooltip.
- `UICommandBuilder.set(String, Message)` exists. `#Id.TextSpans` set to a `Message` is used by many installed mods (TheArmoryMod ScribingPage, JET, EyeSpy, MMOSkillTree). It is **new to our repo** (UNVERIFIED on Skyy's client, and it has a config fallback).
- `ItemGridSlot(ItemStack)` constructor exists. `ItemGrid ... InfoDisplay: None;` is the only markup that stops the stuck-tooltip bug (SkyyMenu 0.1.3 investigation; EyeSpy uses it).
- `Item.getWeapon()`, `getArmor()`, `getTool()`, `getGlider()`, `getUtility()`, `isConsumable()`, `hasBlockType()`, `getCategories()`, `getQualityIndex()` exist. Rarity tiers in `Server/Item/Qualities`: Junk 0, Common 1, Uncommon 2, Rare 3, Epic 4, Legendary 5, and technical tiers at 8 or higher (Technical, Tool, Debug, Developer, Template).
- `SimpleItemContainer.addOrDropItemStack(...)`, `Inventory.getCombinedStorageHotbarBackpack()`, `getActiveHotbarSlot()`, `getHotbar()` / `getStorage()` / `getBackpack()`, `Player.getGameMode()` (== `GameMode.Creative`, the SkyyCollections / SkyyCooking check), `Player.markNeedsSave()`, `Universe.get().getPlayer(UUID)`, `I18nModule.get().getMessage("en-US", key)` (SkyyRolls `tr`).
- **Player save on demand (review pass, bytecode):** `Player.saveConfig(World, Holder, boolean force)` is public and returns a `CompletableFuture`. It hands the call to `PlayerStorage.save(uuid, holder, force)`. The disk storage turns the `Holder` into BSON **at once, on the calling thread**, then queues the file write on `StorageManager.doSave` (asynchronous, chained after any pending write of the same file). With `force = false` it does nothing when a save of that file is already queued. The engine calls it with `true` when a player entity leaves a world, and with `false` (plus a holder built from its own chunk data) on the 10 s tick. `markNeedsSave()` only flags `PlayerConfigData` as changed. `Store.copySerializableEntity(Ref)` / `copyEntity(Ref)` are public and return a `Holder`, so a mod can build one on the world thread (UNVERIFIED in game; see R8).
- SkyyCoins 0.1.5 writes every balance change straight to disk. `coins:fn:*` always act on the **active** profile, and there is no call to pay a profile that is not active. That is why coins are **claimed** (online, on the owning profile) instead of pushed.
- A 1120 x 840 page renders (SkyyCollections 0.2, "this is beautiful!"). A 952 px tall page renders (SkyyMenu 0.1.2).

---

## 1. Scope

**In 0.1:**
- BIN listings: browse, search, sort, rarity filter, item view, buy with a confirm step.
- Create a BIN from our own inventory picker page, or with `/ah sell`.
- Manage page, claims, Claim all, `/ah claim`, notices on join.
- Config, the empty late-game block list (file + bridge), admin commands, the log, bridge keys for later mods.

**Designed for, not built:** bid auctions (Appendix A), a "My bids" page, a Type filter (All / BIN / Auction), an Auction Master NPC (the page id `SkyyAuctions` is registered so an item or NPC can open it later), a SkyWynn Menu button (added by the main session afterwards through `/ah`), price history.

**Not built (explicit):** anything from SkyyGear (unidentified gear, level requirements, new rarities). The rarity filter reads the engine's native quality tiers, so new tiers that SkyyGear adds as quality assets show up without code changes. There is also no drag-and-drop container window (section 2.4 says why), and no automatic buyer in solo (section 4.8).

**Mod facts:** folder `SkyyAuctions/`, script `SkyyAuctions/build_skyyauctions_0.1.py`, `VERSION = "0.1"`, package `com.skyy.auctions`, main `com.skyy.auctions.SkyyAuctionsPlugin`, jar `SkyyAuctions/SkyyAuctions-0.1.jar`, display name `"0.1 SkyyAuctions"`, data `<world>/mods/Skyy_SkyyAuctions/` via `getDataDirectory().resolveSibling("Skyy_SkyyAuctions")`. Zero dependencies. Without SkyyCoins the page opens and says trading needs SkyyCoins. Without SkyyProfiles, `pkey(u)` = `u.toString()`.

---

## 2. Player-facing behaviour

### 2.1 Commands (COMMAND RULES: every player command, subcommand and usage variant calls `setPermissionGroups(new String[] { "hytale:Adventurer" })`)

| Command | What it does |
|---|---|
| `/ah` (aliases `/auction`, `/auctionhouse`) | Opens the page on **Browse** (category All, sort Lowest price). |
| `/ah sell <price>` | Subcommand `sell` with one required STRING arg. Takes the stack in the **active hotbar slot**. Default (`sellCommandOpensPage=true`): opens the **Create** view with that stack picked, the price filled in, the default duration and the fee preview, so **one click on Create BIN** lists it. With `false`, it lists straight from chat and replies with the fee and listing id. |
| `/ah sell <price> <duration>` | A usage variant of `sell` (description-only constructor + two `withRequiredArg`, added with `addUsageVariant`). The duration is `24`, `24h`, `30m` or `2d` and must match a configured preset, otherwise: "Pick one of: 1h 6h 12h 24h 48h". |
| `/ah claim` | Claims everything the active profile is owed: coins first, then items until the inventory is full. Summary in chat. |
| `/ah manage` (alias `mine`) | Opens the page on **Manage**. |
| `/ah search <words>` | Required `GREEDY_STRING` arg (SkyyGuilds `cmd()` helper pattern). Opens **Browse** with that search applied. |

Price text accepts `500`, `2k`, `1.5m`, `2b`. Commas and spaces are ignored. It must be a whole number of coins after the suffix (SkyyBazaar `parseAmt` without `all` / `max`, plus a `b` suffix).

Admin commands: section 8.

### 2.2 Browse view (the landing view)
- A header with the title, the player's purse and the active profile name. A nav row: **Browse**, **Create BIN**, **Manage** (the label shows the owed count, e.g. "Manage (2)"), **Close**.
- **Category row** (7 buttons): All, Weapons, Armor, Accessories, Consumables, Blocks, Tools & Misc. The active one is highlighted. Categories come from the item asset (section 5.4).
- **Filter row:** a search TextField, [Search], [Clear], a Sort button that cycles *Lowest price, Highest price, Ending soon, Newest*, a Rarity button that cycles *Any, Common, Uncommon, Rare, Epic, Legendary* (native quality tiers, section 5.4), and [Refresh].
- **8 result rows per page.** Each row shows:
  - the item icon and name in its rarity colour;
  - a second line with quantity, rarity and, when the stack has SkyyRolls metadata, the reforge name (e.g. "x1 - Rare - Sharp");
  - the seller name, the price (plus "(188 each)" when the quantity is over 1) and the time left ("5h 12m", "2d 4h", "45s");
  - a [View] button.
  Tags: "yours" (your own listing), "your other profile" (your account, another profile), "off the market" in red (the item was blocked after it was listed).
- **Pager:** [< Prev] "Page 2 / 7 - 53 listings" [Next >].
- A **status line**.
- Only ACTIVE, not-yet-expired listings are shown. Search is a case-insensitive substring match on the plain item name, the item id and the seller name. Ties sort by end time, then by id.
- The time left is worked out when the page is built. The page **never refreshes by itself**. [Refresh] or any click rebuilds it.

### 2.3 Item view (click [View])
- A big item preview: a 1-slot ItemGrid with the **real** restored stack, so the icon, quality background and durability show as they do in an inventory. It uses `InfoDisplay: None`, so no hover tooltip can stick.
- **Full tooltip text on the page:** the name (`getDisplayName()`, rarity colour and reforge name included) and the description (`getDisplayDescription()`, which carries SkyyRolls' stat lines). Both are set as `TextSpans`. The engine's own tooltip text is shown in full without hovering, and the metadata stays intact.
- **Facts:** rarity, quantity, durability "123 / 200" (when it has one), seller, price (and the price each), ends in, listed ago, listing number (`#1043`).
- **Cheaper-listing warning** (buyer-side twin of the Create view's price hint): when another listing of the same item id is cheaper **per item** than this one, a ninth fact line in orange says "A cheaper one is listed: 8,000 each (4 listed)". For a stack with SkyyRolls metadata it adds "- rolls are not compared", because a well-rolled copy can be worth more. It uses `AhStore.lowestBin`, the same scan behind the Create view's hint and the `auction:fn:lowestBin` bridge function (9), so it needs no new code path. When this listing is the cheapest, the line stays empty.
- **Actions:**
  - **Buy now - 12,000 coins.** At or above `confirmAbove` (default 10,000) the first click arms a confirm row: "Pay 12,000 coins for Sharp Copper Longsword?" [Confirm] [Cancel]. When the cheaper-listing line is showing, the confirm text ends with "A cheaper one is listed at 8,000 each." It is armed for 10 s, and any other click disarms it. Below the threshold, one click buys. Opening the item view is already the first step of Hypixel's two-step buy.
  - **An armed confirm belongs to one listing.** It stores the listing id and the price it was armed for (7.1). Confirm acts only when both still equal the page's `detailId` and `detailPrice` and the 10 s have not run out. Building the item view for any listing starts **unarmed**, even when a different item view was armed a moment ago. The same rule covers the cancel-confirm rows and the Claim-all confirm (2.5).
  - Your own listing (same profile): [Cancel listing] instead of Buy, with its own confirm row "Cancel? The 470 coin fee is not refunded."
  - Your account on another profile: the text "Listed by your profile Apple - you cannot buy from yourself."
  - Still in the grace period: the button reads "Buy (opens in 14 s)" and a click only explains why.
  - [< Back to results] returns to Browse with the same category, search, sort, rarity and page.
- After a buy, the page goes back to Browse with the status "Bought Sharp Copper Longsword for 12,000 coins" or "...your inventory is full, it waits in Manage".

### 2.4 Create BIN view (item input through our own page)
- **Inventory picker:** a grid of 9 x 4 cells (80 px, the SkyyBazaar product-cell pattern: `Button` + `ItemIcon` + quantity `Label`), with [< Prev] [Next >] when there are more than 36 stacks. It lists every non-empty stack in hotbar, then storage, then backpack.
  - Hidden: technical-quality items (tier 8 or higher) and `Skyy_Menu`.
  - Blocked items are shown, but picking one says why it is off the market.
  - Worn armor is not listed (unequip it first).
- **Picking a stack** selects that exact slot. A panel shows its icon, name, quantity and rarity, plus a price hint from the live listings: "Lowest BIN for this item now: 11,000 (3 listed)" or "None listed".
- **Price:** the TextField `#SkyyAhPrice` (the SkyyGuilds bank / SkyyBazaar amount pattern), with Enter or [Preview].
- **Duration buttons** (one per preset, default 1h 6h 12h 24h 48h). The selected one is highlighted.
- **Fee preview** (two lines, always current): "Listing fee 1% = 120 + duration fee (24h) = 350 -> you pay 470 coins now (not refunded if you cancel)." and "If it sells you get 12,000 coins (no tax under 1,000,000)." If the price is under 50% of the current lowest BIN for that item, a third line in orange warns: "That is less than half the lowest BIN (11,000) - check the price."
- **[Create BIN]** is a two-step guard against a mistyped price:
  - The click lists only when the price in the field **equals the price the fee preview on screen was made for**.
  - Otherwise it previews and says "Check the fee above, then click Create BIN again."
  - Enter, [Preview] and a duration click all make a fresh preview. The usual flow is therefore type, Enter, Create.
- On success the page switches to **Manage** with "Listed #1043 - Sharp Copper Longsword for 12,000 coins".
- Every Create-view binding carries `@AhPrice` = `#SkyyAhPrice.Value`, so typed text survives clicks. The rebuild puts it back with `set("#SkyyAhPrice.Value", ...)`.
- **Why no container window:** the SkyySacks `openCustomPageWithWindows` window is an empty 9-slot container opened only for the look. It is not a transfer channel. A real transfer window would hold the player's item in a temporary container that must be handed back on close, and a crash or disconnect there loses the item. The clickable list is proven (SkyyAccessories Equip rows, SkyyBazaar grid) and never holds the item: the item stays in its slot until the Create click.

### 2.5 Manage view
- **Summary row:** "Listings 3 / 14 used - to claim: 2 items, 45,000 coins", with [Claim all] and a [Create BIN] shortcut. When nothing is listed or owed, the view shows "You have no listings" and a big [Create BIN] button (Hypixel's "show the useful action" touch).
- **8 rows per page** for the active profile. Order: owed claims first (sold, then returned items), then active listings by end time. Each row has the icon, name, quantity and price, a state line, and one action button:

| State | State line | Button |
|---|---|---|
| ACTIVE | "Ends in 5h 12m" (or "in grace 12 s") | [Cancel] (with the confirm row, fee not refunded) |
| SOLD, coins owed | "Sold to Bob - 12,000 coins (tax 0)" | [Claim coins] |
| EXPIRED / CANCELLED / REMOVED, item owed | "Expired" / "Cancelled" / "Removed by an admin: <reason>" | [Claim item] |
| Bought, item owed (the buyer's inventory was full) | "Bought from Alice - waiting for inventory room" | [Claim item] |

- **Other profiles line:** "Your profile Banana has 3 things to claim - switch to it to claim them." Claims always go into the profile that owns them, so they cannot be taken from here.
- [Claim all] = the same routine as `/ah claim`.
- **Claim-all confirm** (borrowed from Hypixel's "that's a lot of coins" note, research section 6): when the coins owed to the active profile are at or above `claimAllConfirmAbove` (default 100,000), the first click on [Claim all] arms a confirm: "Claim 450,000 coins into your purse? Purse coins can be lost on death." [Yes, claim all] [No]. It uses the armed-confirm rules of 2.3 (10 s, any other click disarms it). This matters here because SkyWynn's death penalty takes part of the **purse** (10-25% by default, HANDOFF lock; `/deathpenalty` can change it), while coins waiting in the Auction House are safe. Single [Claim coins] rows need no confirm, since they show the amount on the button row. `/ah claim` from chat claims without asking, then adds "Tip: purse coins can be lost on death - /bank deposit keeps them safe." when the claimed coins reached the threshold (the `/bank` half only when SkyyBank's `bank:<uuid>` bridge key exists). `0` turns the confirm off.

### 2.6 Notices
- **On join** (first PlayerReadyEvent of the session, once-per-session guard cleared on disconnect, 3 s later on the scheduler): one chat line per unnoticed sale, expiry or admin removal of any of the player's profiles, at most 5 lines, then "...and N more". Example: "[Auction House] While you were away: Sharp Copper Longsword sold to Bob for 12,000 coins (profile Apple). /ah claim to collect." After that: "You have N things to claim - /ah claim." Each record is marked noticed.
- **Online seller:** the sale or expiry message is sent at once, and the record is written already marked as noticed.
- **Buyer:** a chat line as well as the page status.

---

## 3. Economy numbers (all in `config.properties`; Hypixel-like defaults)

| Key | Default | Meaning / source |
|---|---|---|
| `listingFee` | `0:1.0,10000000:2.0,100000000:2.5` | Tiers `fromPrice:percent`. Fee = ceil(price x percent / 100), paid on Create, never refunded by cancel. Hypixel BIN fee, VERIFIED in the research. LOCKED 2026-09-25. Server Setup `ah.listingFee`. |
| `durations` | `1h:20,6h:45,12h:100,24h:350,48h:1200` | Presets `length:fee`, at most 8. `m`, `h` and `d` suffixes are allowed. The code caps every preset at 14 days (Hypixel's VERIFIED cap). The fee numbers are Hypixel's classic presets from general knowledge; the research only verified the 14-day cap and a 55,200 maximum duration fee. LOCKED 2026-09-25: preset lengths are 1h / 6h / 12h / 24h / 48h. Fees on the first four stay 20 / 45 / 100 / 350 (Server Setup `ah.durations`). A 48h listing pays twice the listing fee, so the flat 1,200 in this default is what SkyyAuctions 0.1.1 still charges. |
| `minDurationFee` / `allowTestDurations` | `1` / `false` | **Test-preset guard.** A preset whose fee is below `minDurationFee` (e.g. the `2m:0` used in the test plan) is a test preset. With `allowTestDurations=false`, config load and `/ahadmin reload` **drop** it with a loud WARN ("dropped test duration 2m:0 - set allowTestDurations=true to use it"), and `defaultDuration` falls back to `24h` if it pointed at a dropped preset. With `true`, the preset works, but every start, every reload and the `/ahadmin` status print "TEST DURATIONS ARE ON: 2m:0". So a forgotten test preset cannot quietly become a free way to churn listings. |
| `defaultDuration` | `24h` | Must be one of the presets. LOCKED 2026-09-25. Server Setup `ah.defaultDuration`. |
| `claimTaxPercent` / `claimTaxFrom` | `1.0` / `1000000` | Tax = min(ceil(gross x 1%), gross - 1,000,000), only when gross > 1,000,000, so the net never drops below 1,000,000. Worked out and **stored at sale time** (a later config change never alters money already earned). UNVERIFIED Hypixel detail, concept cross-checked. LOCKED 2026-09-25. Server Setup `ah.claimTaxPercent` and `ah.claimTaxFrom`. |
| `minPrice` / `maxPrice` | `1` / `50000000000` | Whole coins. The max is a sanity cap (UNVERIFIED Hypixel number). |
| `maxListings` | `14` | Per **profile**. A slot counts from Create until the seller has claimed that listing's coins or item (Hypixel rule: only claiming or cancelling frees a slot; a cancel with an immediate return frees it at once). |
| `maxListingsServer` | `5000` | Keeps load time and page filtering bounded. |
| `graceSeconds` | `20` | Nobody can buy a new listing for 20 s (Hypixel, VERIFIED). In practice it gives the seller time to cancel a mistyped price before a sniper takes it. |
| `confirmAbove` / `confirmSeconds` | `10000` / `10` | A buy at or above this price needs the confirm click, armed for 10 s. 10,000 = a new profile's starting purse. `[SKYY?]` |
| `claimAllConfirmAbove` | `100000` | [Claim all] asks first when the coins owed are at or above this (2.5). `0` = never ask. Hypixel's nudge sits at about 100,000 (UNVERIFIED, one source). |
| `cancelRefundsFee` | `false` | Hypixel keeps the fee (VERIFIED). |
| `adminRemoveRefundsFee` | `false` | An admin removal returns the item, not the fee (an admin can `/coinsgive` if it was a mistake). |

---

## 4. Rules

### 4.1 Profiles (PROFILES-CONTRACT)
- **A listing belongs to the profile that made it:** `seller.key = pkey(uuid)` is resolved once when the operation starts. Cancel and every seller claim need the **active** key to equal `seller.key`. Coins go into that profile's purse (`coins:fn:add` acts on the active profile), and returned items go into its inventory.
- **The buyer pays from the active profile.** `buyer.key` is stored. A bought item that did not fit is claimable only while that profile is active.
- **The page remembers the key it was built for.** If a click arrives under another key (the profile switched with the page open), nothing happens except a rebuild: "Your profile changed - this is now profile Banana's view." (SkyyAccessories 0.4.1 pattern.)
- **`profile:busy:<uuid>` present:** every AH action is refused with "Your profile is still loading - try again in a moment." That includes coin claims, for simplicity. Browsing still works.
- Per-profile bridge values that are published (`auction:claims:<uuid>`) are keyed by UUID and republished on a `profile:epoch:<uuid>` change (contract rule 3). The first epoch seen is a baseline (rule 4.2).
- **Co-op:** SkyWynn co-op shares islands, not profiles, so listings are never shared between players (unlike Hypixel co-op profiles).

### 4.2 Who may trade
- **You cannot buy from your own account on any profile.** `buyer.uuid == seller.uuid` is refused. Otherwise one account could move coins between its own profiles with junk listings, which breaks the per-profile purse lock. `sameAccountBuy=false`. Setting it to `true` is for solo testing only.
- **Creative mode** (`blockCreative=true`): players whose game mode is Creative can browse and claim, but not create listings or buy. Creative can spawn items. Admins get no bypass. The check runs at click time.
- **Admins** (`skyyauctions.admin`) use the admin commands. In the market they follow every player rule: fees, limits, no self-buy.
- **`market:deny:<uuid>`:** a bridge String reason. When it is present, that player's active profile may browse but not list or buy, and the page shows the reason. It is empty by default and nothing sets it yet. It is the hook for future Ironman / Stranded-style profile modes (Hypixel blocks those profiles from its Auction House, VERIFIED).
- **Paused market** (`paused=true` or `/ahadmin pause`): no new listings or buys. Cancel and claims still work. A banner reads "The Auction House is paused by an admin."

### 4.3 What can be listed
Checked at Create, and again at buy time where it matters:
1. The stack is not empty and holds at least 1 item. The **whole stack** in that slot is listed: players split stacks in their inventory first (the Hypixel way, and it keeps every listing one snapshot).
2. The quality tier is below 8 (technical items are never tradeable). The item is not `Skyy_Menu` (SkyyProfiles keeps it across profiles).
3. **Not blocked** (4.4). A blocked item cannot be listed or bought. Listings made before the block show "off the market". They can still be cancelled, they expire normally, and the item goes back to the seller.
4. **Not a Bazaar commodity** (`bazaarItemsAllowed=false`): an id in the bridge `bazaar:products` gets "Sell this on the Bazaar: /bz". Hypixel keeps each item on the Bazaar or the Auction House, never both (research section 11). `[SKYY?]`
   - **Match whole ids only.** SkyyBazaar 0.1.2 publishes `bazaar:products` as **one comma-joined String** (`publishAll()`), not a Set. A plain `products.contains(id)` is a substring test and would give false hits (a short id inside a longer one). `AhItem.isBazaarItem(id)` splits the String on `,` into a `HashSet` of trimmed tokens and tests `set.contains(id)`. It caches the set and re-splits only when the bridge value is a different String (`!s.equals(lastProducts)`). An equivalent one-liner is `("," + s + ",").indexOf("," + id + ",") >= 0`. A missing key means "no Bazaar loaded": nothing is refused.
5. **The snapshot round-trip passes** (6.4 step e). An item whose data cannot be saved and restored exactly is refused: "This item cannot be listed (its data could not be saved)." This is what **guarantees that SkyyRolls metadata survives**.
6. The price is within min / max, the duration is a preset, a profile slot is free, the server cap is not reached, and the purse covers the fee.

**Bags are tradeable, but say what they are.** A Magic Bag (`Skyy_Sack_<Category>_<Tier>`) or the Accessory Bag (`Skyy_Accessory_Bag`) is only a **key**: the materials and accessories live in a per-player file (SkyySacks / SkyyAccessories), not in the item, and SkyySacks writes no item metadata. Selling one hands over a crafted bag, and the buyer opens their **own** pool with it. Nothing is created. The seller gave up the item and pays materials to craft another, like any crafted item, and "coins can bypass collections early" is a locked design fact. So 0.1 does **not** block bags. What it adds against a misunderstanding: for those ids, the Create view's selected panel and the item view's facts show "Contents are not included - a bag opens its owner's own storage." If Skyy wants bags off the market, two lines in `Skyy_Market/blocked.txt` do it (`Skyy_Sack_*` and `Skyy_Accessory_Bag`) with no code change (open question 15).

### 4.4 The late-game block list (empty by default)
- **File** `<world>/mods/Skyy_Market/blocked.txt`. It is **shared by the market mods**: SkyyAuctions now, and SkyyBazaar can read the same file later, so one entry takes an item off both markets. It is created on first run with only comment lines. The format is one entry per line: `ItemId` or `Prefix*`, with an optional ` = reason shown to players`. The default reason is "late-game item". `#` starts a comment. It is re-read by `/ahadmin reload`.
- **Bridge** `market:blocked` = a `java.util.concurrent.ConcurrentHashMap` of entry (id or `prefix*`) -> "owner|reason". The first market mod creates it with `putIfAbsent`. **Other mods add their own entries**: when SkyyCollections gets the late-game cutoff, it puts e.g. `Ore_Mithril` -> `SkyyCollections|reach Mithril tier VI`. SkyyAuctions publishes the file entries with owner `file`. On reload it removes only entries whose owner is `file`, so other mods' entries are never touched. It never removes the map on shutdown, and removes only its own `file` entries.
- **How an id is checked against `market:blocked`** (one helper, `AhItem.blockedReason(id)`, used by Create, Buy, the picker and the Browse "off the market" tag; SkyyBazaar must use the same rule when it reads the map later):
  1. `map.get(id)`: an exact entry wins.
  2. Otherwise walk `map.keySet()` (a ConcurrentHashMap iterator is safe while other mods write). For each key that ends in `*`, `id.startsWith(key.substring(0, key.length() - 1))` is a match. A plain `containsKey(id)` alone would silently ignore every `Prefix*` entry.
  3. The value's text after the first `|` is the reason shown to players.
  Matching is case-sensitive, like item ids. A bare `*` (which would block everything) is ignored with a WARN; `/ahadmin pause` is the tool for closing the market.
- **Bridge** `market:veto` = a ConcurrentHashMap of owner -> `java.util.function.Function` `apply(ItemStack)`, returning `null` (allowed) or a String reason. It is empty by default. It is for per-stack rules that an id list cannot express, e.g. a future SkyyGear "unidentified items cannot be sold". A veto that throws counts as a refusal ("could not check this item") and is logged once. Vetoes are asked after the block list, one Function per owner, on every stack (they are not keyed by id, so the prefix rule does not apply to them).
- The cutoff itself is still open (DESIGN-STATUS question 11), so nothing ships blocked.

### 4.5 Grace, own listings, expiry
- A listing is buyable only when `now >= graceUntil` (created + 20 s) and `now < endsAt`.
- A listing past `endsAt` is treated as expired **everywhere at once**: Browse hides it, and Buy refuses and expires it inside the same locked step. The tick only makes that permanent.

### 4.6 Numbers and text
- Coins are `long` everywhere. Totals above 1e15 are refused (the SkyyBazaar rule).
- Player text (search, names) is never put inside inline markup. Dynamic text goes through `b.set("#Id.Text", v)` (HANDOFF: safe for anything). Item ids are checked with `isId` before they go into an `ItemIcon` inline.

### 4.7 What happens to the item
The listed stack is **removed** from the seller's inventory and lives only in the listing record until it is bought, returned or claimed. It is never in two places, apart from the logged crash window in 6.8 (made much shorter by the forced player save, R8).

### 4.8 Solo
Everything works in solo: list, browse, cancel, expire, claim, admin tools. **Nobody buys** in solo, because the AH is a player market and you cannot buy from yourself (the Bazaar is the solo market). For a one-account test, `sameAccountBuy=true` lets profile 2 buy profile 1's listing.

---

## 5. Data model and files

### 5.1 Files (`<world>/mods/Skyy_SkyyAuctions/`)
| File | Content | Written |
|---|---|---|
| `config.properties` | Section 3 + 4 keys, written from a commented template on first run. Unknown or bad values: warn, use the default. | First run; read at start and on `/ahadmin reload`. |
| `state.properties` | `nextId=<long>` | Atomically, **before** each new id is used (an id is never reused, even after a crash). |
| `listings/<id>.json` | **One record per listing that is not closed yet** (5.2): BSON Extended JSON via `BsonDocument.toJson(JsonWriterSettings EXTENDED, indent)`, read with `BsonDocument.parse` (the SkyyProfiles `ProfInv.toJson` pattern). | Every state or claim change: `atomicWrite` (tmp + flush + fsync + ATOMIC_MOVE, 5 x 20 ms retries on `FileSystemException`; copy `ProfCfg.atomicWrite`). |
| `archive/<yyyy-MM>/<id>.json` | Closed records (terminal state + every claim done), moved with an atomic move. Kept for admins and `regrant`. Never deleted by the mod. A move never overwrites: if `<id>.json` already exists there (a record that was regranted and closed again), the target is `<id>.r<rev>.json`. | On close; a failed move is retried by the tick. |
| `listings/bad/<id>.json` | A record that could not be parsed at load time, moved aside and never deleted. Logged `WARN`. | At load. |
| `auctions.log` | One line per event (section 8.2). Rotated to `auctions-<yyyy-MM-dd>.log` when over 5 MB (by the tick). | Appended synchronously and **synced to disk** (`FileDescriptor.sync()`) per append (8.2). |
| `../Skyy_Market/blocked.txt` | The shared block list (4.4). | Created once if missing, with comments only. |

**Why one file per listing (the brief suggested one listings file plus per-owner claim files):** a trade must change the listing and the claim **in one atomic write**. Separate claim files would need two writes, and a crash between them either duplicates or loses. So each owner's claim entries live **inside** the listing record (`claims.sellerCoins`, `claims.sellerItem`, `claims.buyerItem`, and later one per bid). The per-owner view ("what does profile X have to claim") is an **in-memory scan** keyed by `seller.key` / `buyer.key`. One file per listing keeps each write small (about 2 KB instead of rewriting everything on every trade), and a damaged file affects one listing, not the market.

### 5.2 The record (schema `v: 1`)
```
{
  "v": 1,
  "id": "1043",
  "type": "BIN",                       // BIN now; AUCTION later (Appendix A)
  "state": "ACTIVE",                   // ACTIVE | SOLD | EXPIRED | CANCELLED | REMOVED   (AUCTION later adds ENDED)
  "closed": false,                     // true once terminal + every claim is CLAIMED or NONE -> moved to archive/
  "rev": 1,                            // +1 on every write
  "seller": { "uuid": "...", "key": "<pkey>", "name": "Skyy", "profile": "Apple" },
  "item": {
    "stack": { <ItemStack.CODEC encode, the exact engine form> },
    "id": "Weapon_Longsword_Copper", "qty": 1,
    "durability": 187.0, "maxDurability": 200.0, "quality": 3,
    "meta": { <getMetadata() clone, e.g. "SkyyRolls": {...}, ItemDisplayMetadata> }
  },
  "name": "Sharp Copper Longsword",    // plain text at list time (5.4)
  "search": "sharp copper longsword weapon_longsword_copper skyy",
  "category": "WEAPONS",               // one of WEAPONS ARMOR ACCESSORIES CONSUMABLES BLOCKS MISC ("All" is a filter, never stored)
  "price": 12000,                      // BIN: total for the stack
  "startBid": 12000,                   // = price for BIN; AUCTION later: opening bid
  "topBid": 0, "topBidder": null,      // AUCTION later
  "bids": [],                          // AUCTION later: [{uuid,key,name,amount,at,state}]
  "createdAt": 0, "graceUntil": 0, "endsAt": 0, "duration": "24h",
  "fee": { "listing": 120, "duration": 350, "refunded": false },
  "buyer": null,                       // { uuid, key, name, profile, at }
  "sale": null,                        // { gross, tax, net } fixed at sale time
  "claims": {
    "sellerCoins": "NONE",             // NONE | OWED | CLAIMED
    "sellerItem":  "NONE",
    "buyerItem":   "NONE",
    "sellerItemQty": 0, "buyerItemQty": 0     // what is still owed (a partial delivery lowers it)
  },
  "noticed": { "seller": false },
  "removed": null,                     // { by, reason, at } for REMOVED
  "regrants": [],                      // [{ side, by, at, qty }] one entry per /ahadmin regrant (8.1)
  "closedAt": 0
}
```
**Forward-compatibility rules (so bid auctions need no migration):**
- **Never rebuild a record from scratch on a write.** Clone the loaded `BsonDocument` and change only the fields this version owns, so fields written by a newer version survive.
- A record with an unknown `type` or `state`, or with `v` greater than 1, is **shown read-only** ("needs a newer SkyyAuctions") and is never bought, cancelled, expired or claimed by 0.1.
- A missing field reads as its default above, so older or smaller records load.

### 5.3 Item snapshot and restore (lossless; copy SkyyProfiles `ProfInv`)
- **Snapshot** (`AhItem.snap(ItemStack s)`): `stack = ((Codec) ItemStack.CODEC).encode(s)` plus the readable fields (`id`, `qty`, `durability`, `maxDurability`, `quality`, and `meta = (BsonDocument) s.getMetadata().clone()`, or none).
- **Restore** (`AhItem.restore(doc, qty)`): decode `stack` with `ItemStack.CODEC` and check that `id` matches. If decoding fails, fall back to `new ItemStack(id, qty, durability, maxDurability, quality, meta)`. Then `withQuantity(qty)` when a partial delivery lowered the owed quantity.
- **Never** build `new ItemStack(id, n)` for a delivery (SkyyBazaar `Inv.give` loses metadata; fine for commodities, wrong here).
- SkyyCooking grades are separate item ids, not metadata (research 3 checked SkyyCooking 0.1.1). The snapshot carries them either way, and covers durability, quality and any future metadata (SkyyGear).

### 5.4 Derived fields (computed at list time and stored; recomputed at load if missing)
- **Category**, first match wins, from the `Item` asset (`stack.getItem()`):
  1. `ACCESSORIES`: id starts with `Skyy_Accessory_` (except `Skyy_Accessory_Bag`) or `Skyy_Talisman_` (SkyyAccessories `isAccessory`).
  2. `WEAPONS`: `getWeapon() != null`.
  3. `ARMOR`: `getArmor() != null`.
  4. `CONSUMABLES`: `isConsumable()`, or the id starts with `Food_`, `Potion_` or `Skyy_Cook_`.
  5. `MISC` (Tools & Misc): `getTool()`, `getGlider()` or `getUtility()` is not null.
  6. `BLOCKS`: `hasBlockType()`.
  7. Anything else (ingredients, ores, fish, bars): `MISC`.
- **Rarity:** `stack.getQualityIndex()` -> `ItemQuality.getAssetMap()` asset. The filter tiers are the assets with QualityValue 1..5 (Common..Legendary), sorted by value and named by their asset id. Junk (0) shows only under Any. The colour is the asset's `getTextColor()` (the SkyyRolls `rarityColor` pattern). SkyyGear's future tiers flow in if they are quality assets.
- **Reforge** (row second line): `meta.SkyyRolls.reforge` when present.
- **Plain name:** take `getDisplayName()`. Use its `getRawText()` when that is set; otherwise `I18nModule.get().getMessage("en-US", messageId)` (SkyyRolls `tr`), joining child messages. Fall back to `tr(item.getTranslationKey())`, then the id with `_` turned into spaces.

### 5.5 In memory
- `LIVE`: `ConcurrentHashMap<String id, BsonDocument>`. Every non-closed record. **Records are never changed in place**: a change builds a clone, writes it, then swaps it in (6.1 R2). Browsing reads without the lock.
- `STACKS`: `HashMap<String id, ItemStack>`, a cache of restored stacks for display. Deliveries always restore fresh from the record.
- `DIRTY`: a set of ids whose latest in-memory version failed to write after an effect that cannot be undone (6.1 R2 exception). The tick retries them. The `WRITE-FAILED` line carries that version, so a start after a crash writes it back (6.10).
- `ARCH`: closed records that are not in `archive/` yet. A closed record whose closing write failed also waits here (and in `DIRTY`), so `/ahadmin info` and `regrant` still find it. The tick archives it only after its closed version is on disk. It never archives the older file that is still in `listings/`.
- Per-owner views: a scan of `LIVE` (at most 5000 records, fine per click).

---

## 6. Transaction safety

### 6.1 Rules every operation follows
- **R1 One lock.** Every state or claim change runs in `synchronized (AhStore.class) { return x0(...); }`. That is one call per synchronized block (javassist). It covers list, buy, cancel, expire, claim, admin remove, regrant and notice marks, across every world thread and the scheduler. Nothing inside the lock ever waits on another thread (no `world.execute` + wait, no network). Lock order: AhStore -> SkyyCoins' ledger. SkyyCoins never calls out, so there is no cycle. `pkey` is resolved **before** the lock (one key per operation, contract 4.1).
  - **Keep the lock short.** It is JVM-wide, so while one trade holds it, every other player's list, buy, cancel and claim on every world waits. **Inside** the lock go only the things whose order is the safety argument: the re-checks, the coin take / add, the inventory change, the record's write + swap, and the `*-START`, commit and `*-ABORT` log lines. **After** the `*0` call returns, still in the same world-thread task, go the forced player save (R8), chat to other players (the seller's "sold" line), bridge republishes (`auction:count`, `auction:claims:<uuid>`) and the page rebuild. The `*0` method returns an `AhResult` that says what to do afterwards (`saveNeeded`, who to message).
  - Known limit: a normal hold is one `atomicWrite` (with fsync), one or two synced log lines and SkyyCoins' own balance write, a few milliseconds on an SSD. A slow disk, or the Windows `FileSystemException` retries (up to 5 x 20 ms), can stretch one hold to a few hundred milliseconds, and everyone's trade clicks wait that long. That is accepted: trades are rare clicks, and a second lock per listing would open the cross-listing races the one lock rules out.
- **R2 Copy, write, swap.** The next version is a clone. `atomicWrite` it, then put it in `LIVE` only if the write succeeded. A failed write changes nothing in memory, and every external effect of that operation is undone. **Exception:** after an effect that cannot be undone (an item already handed over, coins already paid), memory follows the effect even if the write failed. The id goes into `DIRTY`, the tick retries the write, and `WRITE-FAILED` is logged loudly. That line carries the whole new version as one line of JSON (`doc=...`), for the start-up restore (6.10).
- **R3 The server checks at click time.** Inside the lock, the record is looked up again by the id the **page object** stored when it drew the view (never an id or price from the client). State, end time, grace, blocked, owner, key and the price the player saw are all checked again.
- **R4 Ordering, one principle:** never create an item or a coin; if something must be risked, risk a logged loss an admin can repair.
  - **Coins into the market** (fee, purchase): take the coins **first**. SkyyCoins writes to disk at once.
  - **Coins out of the market** (seller claim): write `CLAIMED` **first**, then pay. If paying fails, write the old version back. This is the SkyyGuilds bank-withdraw ordering.
  - **Items into the market** (listing): remove from the inventory **first**, then write the record.
  - **Items out of the market** (delivery, claim, return): hand the item over **first**, then write `CLAIMED`.
  - Why the item rules differ from the coin rules: the vanilla inventory only reaches disk at the engine's player save (a 10 s tick, when the player leaves a world, or our own forced save after the lock, R8), and that save takes its snapshot on the same world thread, so it cannot happen between two lines of our click handler. A crash between "inventory changed" and "record written" therefore always restarts from the inventory as it was **before** the change. That is correct in both directions.
- **R5 Count, don't trust.** A removal must leave the slot empty, the slot's stack before removal must equal the picked stack (id, quantity, metadata), and the item count must drop by exactly the stack size. A delivery counts the item id across storage + hotbar + backpack before and after, and treats `added = after - before` as the truth (the SkyySacks 0.6.4 lesson).
- **R6 Busy and key.** `profile:busy:<uuid>` means refuse. The page key must equal `pkey(u)`, or only rebuild.
- **R7 Log first.** A `*-START` line is appended **and synced to disk** before the first durable external effect of a list, buy or coin claim, and a commit or `*-ABORT` line after it (8.2). At startup the mod reads the last 2000 log lines. Every START without a matching commit or abort goes into a server-log `WARN` and into `/ahadmin` status ("possible lost coins: BUY-START #1043 buyer Bob 12,000 - check Bob's purse and #1043's state").
- **R8 Save the player right after the trade.** `player.markNeedsSave()` after every inventory change (cheap; probe it, skip it if missing). It only flags the player for the engine's 10 s save tick, so it leaves the up-to-10 s crash window of 6.8 as it is. To shrink that window, after any operation that **changed the inventory** (LIST's removal, BUY's delivery, a claimed item, a cancel's return; one save at the end of Claim all), the world-thread task calls, **after the lock is released** (R1):
  `player.saveConfig(world, store.copySerializableEntity(ref), true)`
  - What that does (bytecode, section 0): the player's state is turned into BSON at once on this thread, and the file write is queued on the engine's `StorageManager`. `force = true` (the value the engine uses when a player leaves a world) makes it save even when a tick save is already queued. It is **not** a synchronous disk flush: the window becomes "until the queued write lands", normally well under a second, instead of up to 10 s. It must come **after** the record write, never between the inventory change and the write (R4), or a crash in between would duplicate or lose in the other direction.
  - Config `forceSaveAfterTrade=true`. It is skipped silently when either probe (10.3) failed. If the call throws, it is skipped from then on, logged once, and `markNeedsSave` stays. UNVERIFIED until the test in 11.1 shows the player file's time changing right after a listing.

### 6.2 State machine
```
             buy (buyer pays)                 seller claims coins / buyer gets item
ACTIVE ─────────────────────────────▶ SOLD ──────────────────────────────────────┐
  │  cancel (seller, same profile)                                                 │
  ├─────────────────────────────────▶ CANCELLED ── seller claims item ────────────┤
  │  endsAt reached (tick or any locked read)                                      ├──▶ closed = true → archive/
  ├─────────────────────────────────▶ EXPIRED ──── seller claims item ────────────┤
  │  /ahadmin remove                                                               │
  └─────────────────────────────────▶ REMOVED ──── seller claims item ────────────┘
```
- The terminal states never go back to ACTIVE. The brief's "->CLAIMED" is the **claim flags** (`OWED -> CLAIMED` per party) plus `closed`, so the record still says *why* it ended.
- **SOLD** sets `sellerCoins = OWED` and `buyerItem = OWED`. The buyer's item goes to `CLAIMED` right away when it fits.
- **CANCELLED, EXPIRED and REMOVED** set `sellerItem = OWED`. A cancel tries to hand the item back straight away.
- Only `/ahadmin regrant` moves a flag from `CLAIMED` back to `OWED`, and only from exactly `CLAIMED`, never from `NONE` or `OWED` (8.1).

### 6.3 The delivery routine `deliver(player, rec, side)` (buy, claim, cancel return, Claim all)
- a. Refuse if busy or the key does not match. Restore the stack with the owed quantity.
- b. **Room check:** empty slots x max stack, plus room on partial stacks where `isStackableWith(stack)` is true, across storage + hotbar + backpack (SkyyBazaar `room()`). If it does not fit, return **FULL**. Nothing changes.
- c. `before = count(id)`, then `getCombinedStorageHotbarBackpack().addItemStack(stack)`, then `after = count(id)`, and `added = clamp(after - before, 0, qty)`.
- d. **All of it added:** the clone sets that claim to `CLAIMED` (and `closed` when that was the last claim). Write it, then log `CLAIM-ITEM #id side=<buyer|seller> qty=<added>` (also for BUY's immediate delivery and a cancel's return, so every delivery has a line `regrant` can show). If the write fails: R2 exception (`DIRTY`), logged.
- e. **Part of it added:** the clone lowers `<side>ItemQty` by `added`. Write it (same rule), log `CLAIM-ITEM-PART #id side qty=<added> left=<n>`. "N more wait - make room."
- f. **Nothing added:** FULL.
- The item is **never dropped on the ground**. A unique rolled item on a crowded hub floor could be taken by someone else, so anything that does not fit waits in claims (the brief's "inventory full -> keep in claims"). The one exception is the listing-failure put-back in 6.4 k.

### 6.4 LIST (Create click, or `/ah sell` when it lists directly), on the seller's world thread
- a. Before the lock: `key = pkey(u)`. Friendly checks for the page: paused, Creative, `market:deny`, busy, coins bridge ready.
- b. **Lock**, `list0`: check a. again.
- c. Read the picked slot (section: hotbar, storage or backpack; the slot number). `orig` must be non-empty and equal the pick (id, quantity, metadata). If not: "That item moved or changed - pick it again."
- d. Eligibility 4.3 (1-4, 6).
- e. `snap = AhItem.snap(orig)`. **Round-trip check:** `restore(snap)` must give the same id and quantity, `getMetadata()` equal (BsonDocument equals, both null counts as equal), durability and quality. Otherwise refuse (4.3.5).
- f. `fee = listingFee(price) + durationFee(duration)`. LOCKED 2026-09-25: a 48h listing's whole create charge is `2 * listingFee(price)` (double the 1% / 2% / 2.5% tiers). SkyyAuctions 0.1.1 still uses the sum above, so 48h still adds 1,200. `bal = Coins.get(u)`: -1 means refuse "coins unavailable"; less than `fee` means refuse "You need N more coins for the fee."
- g. `id = nextId`, then write `state.properties` with `nextId + 1`. If that write fails, refuse.
- h. Log `LIST-START #id`.
- i. `Coins.take(u, fee)`: 0 means refuse and `LIST-ABORT`; -1 means refuse, `TAKE-ERROR` and `LIST-ABORT` ("contact an admin if your purse dropped").
- j. **Remove, counting what actually left:**
  1. `before = count(id)` (storage + hotbar + backpack).
  2. `container.removeItemStackFromSlot(slot, qty)`.
  3. `after = count(id)`, and `removed = clamp(before - after, 0, qty)`. This is the only number the rollback may use.
  4. Success = the slot is empty **and** `removed == qty`. Go on to k.
  5. Otherwise roll back. If `removed > 0`, put back `orig.withQuantity(removed)` with `addItemStack` into the same container. Never put back `qty`: on a partial removal that would add items that never left (a duplicate, on top of the fee refund). Then check `count(id) == before`. If it is still short, log `ITEM-LOST` with the snapshot `snap` from e, `before`, `after` and the shortfall, so an admin can rebuild it (should never happen: those items just left this container).
  6. `Coins.add(u, fee)` (a failed refund is `REFUND-FAILED`, and the player is told they are owed it), `LIST-ABORT` (with `removed` and the put-back result), refuse "the item moved".
- k. **Write** the new record (ACTIVE, `graceUntil = now + grace`, `endsAt = now + duration`, fee, derived fields). If the write fails: put `orig` back into its now-empty slot. `addOrDropItemStack` is the last resort, used only here: the slot we just emptied cannot really be full. Refund the fee, `LIST-ABORT`, refuse "could not save the listing".
- l. `LIVE.put`, log `LIST`, `markNeedsSave`. The lock ends here.
- m. After the lock (R1): the forced player save (R8), republish `auction:count`, then status or chat.

### 6.5 BUY (item view Buy or Confirm), on the buyer's world thread
- a. Before the lock: `key = pkey(u)`. The page gives `id` and `shownPrice` (stored in the page object, never read from the client).
- b. **Lock**, `buy0`: paused, busy, Creative, deny, coins ready, and page key == `key`.
- c. `rec = LIVE.get(id)`: it must exist, have `type == BIN` and `state == ACTIVE`.
  - Past `endsAt`: expire it here (6.7) and refuse "It just expired."
  - `now < graceUntil`: refuse with the seconds left.
  - `price != shownPrice`: refuse and rebuild.
  - Blocked or vetoed: refuse.
  - `buyer.uuid == seller.uuid` and `sameAccountBuy=false`: refuse.
- d. `bal = Coins.get(u)`: less than price means "You need N more coins." (nothing taken).
- e. `fits = room(stack)`. This only chooses the delivery path; a full inventory never blocks the buy.
- f. Log `BUY-START #id buyer price`.
- g. `Coins.take(u, price)`: 0 means refuse and `BUY-ABORT`; -1 means `TAKE-ERROR`, `BUY-ABORT`, refuse.
- h. The clone gets: `state = SOLD`, `buyer = {...}`, `sale = {gross, tax, net}`, `sellerCoins = OWED`, `buyerItem = OWED`, `buyerItemQty = qty`, and `noticed.seller = (the seller is online now)`. Write it. **If the write fails:** `Coins.add(u, price)` (refund; failure = `REFUND-FAILED` plus "you are owed" in chat and on the page), `BUY-ABORT`, refuse. Nothing else changed.
- i. Swap into `LIVE`, log `BUY`.
- j. If `fits`: `deliver(buyer side)` (6.3), still inside the lock on the same thread. Otherwise: "Your inventory is full - it waits in Manage (Claim item)." The lock ends here.
- k. After the lock (R1): the forced player save when the item was delivered (R8). If the seller is online: "[Auction House] Your Sharp Copper Longsword sold to Bob for 12,000 coins. /ah claim." (`Universe.get().getPlayer(sellerUuid)`, `sendMessage`). Republish `auction:count` and both players' `auction:claims:<uuid>`.

### 6.6 CLAIM (one row, Claim all, `/ah claim`), on the claimer's world thread
- **Coins** (`SOLD`, `sellerCoins == OWED`, active key == `seller.key`):
  1. Log `CLAIM-COINS-START #id net`.
  2. Write the clone with `CLAIMED` (and `closed` if nothing else is owed). If the write fails, refuse "try again" (nothing was paid).
  3. `Coins.add(u, net)`. On 1: swap, log `CLAIM-COINS`. On 0 or -1: write `rec` back (roll back). If that write also fails, memory keeps `OWED`, the id goes into `DIRTY`, and the log says `PAY-FAILED` (with the `OWED` version as `doc=...`, for 6.10). The player is told "could not pay - try again".
- **Items** (`sellerItem` or `buyerItem` `OWED` for the active key): `deliver(...)` (6.3).
- **Claim all:** on the page, the claim-all confirm comes first when the coins owed reach `claimAllConfirmAbove` (2.5). Then every coin claim (the inventory cannot block those), then items oldest first, stopping at the first FULL. Summary: "Claimed 45,000 coins and 2 items. 1 item waits - your inventory is full."
- When a record becomes `closed` (inside the lock): move it to `archive/<yyyy-MM>/` (atomic move, never overwriting, 5.1), remove it from `LIVE` and `STACKS`.
- After the lock (R1): one forced player save if any item was delivered (R8, once per Claim all, not once per row), then republish `auction:claims:<uuid>`.

### 6.7 CANCEL, EXPIRE, REMOVE
- **Cancel** (seller, active key == `seller.key`, `state == ACTIVE`; allowed during grace):
  1. If it is already past `endsAt`, it becomes EXPIRED instead, and the player gets a claim.
  2. The clone gets `CANCELLED`, `sellerItem = OWED`, `sellerItemQty = qty`, and the fee refunded only if `cancelRefundsFee`. Write, swap, log `CANCEL`.
  3. Then `deliver(seller side)` in the same locked step. FULL means "kept in Manage".
  4. After the lock: the forced player save if the item came back (R8).
- **Expire** (tick every 10 s on the scheduler, and inline in any locked read that sees it):
  1. For every `ACTIVE` record with `now >= endsAt`, the clone gets `EXPIRED`, `sellerItem = OWED`, `noticed.seller = seller online`. Write, swap, log `EXPIRE`.
  2. It never touches an inventory, so the scheduler thread is fine.
  3. An online seller gets "Your listing of X expired - /ah claim to get it back."
- **Admin remove** (`ACTIVE` only; SOLD is refused because the buyer already paid, and an admin fixes that with coin commands):
  1. The clone gets `REMOVED`, `removed = {by, reason, at}`, `sellerItem = OWED`, fee refund only if `adminRemoveRefundsFee`. Write, swap, log `REMOVE`.
  2. An online seller is told.

### 6.8 Crash table (JVM killed between steps)
| Crash point | After restart | Result |
|---|---|---|
| LIST after the fee take (i), before the record write (k) | The fee is gone. The inventory reloads from the last engine save, so the item is still there. `LIST-START` has no commit, so there is a `WARN` | Logged fee loss. An admin refunds it with `/coinsgive`. |
| LIST after the record write, before the player's file is saved | The listing exists **and** the reloaded inventory still has the item | **Possible duplicate.** This window is shared by every mod that moves items into mod storage (bags, accessories, vault; PROFILES-CONTRACT section 5). With the forced save (R8) it lasts until the queued player write lands (normally well under a second); without it, up to the engine's 10 s tick. The `LIST` line names the id so an admin can find it. |
| BUY after the coin take (g), before the SOLD write (h) | The buyer's coins are gone and the listing is still ACTIVE. `BUY-START` has no commit, so there is a `WARN` | Logged coin loss. An admin refunds it. |
| BUY after the SOLD write, before delivery | `buyerItem = OWED` | Correct: the buyer claims it. |
| BUY or CLAIM after handing the item over, before the `CLAIMED` write | That delivery was never saved by the engine (same world task), and the record still says OWED | Correct: claim again. |
| BUY or CLAIM after the `CLAIMED` write, before the player's file is saved (same length as the row above) | The record says `CLAIMED` and the reloaded inventory lacks the item | **Possible loss** (the same pack-wide window, other direction). The archived record keeps the snapshot. `/ahadmin regrant <id> buyer\|seller` restores the claim; its preview shows the `CLAIM-ITEM` line followed by a `BOOT` with no `STOP` in between (8.1, 8.2). |
| BUY, CLAIM or CANCEL after handing the item over, when the `CLAIMED` (or partial-quantity) write **failed** (`WRITE-FAILED`, memory and `DIRTY` hold the new version), and the crash comes before the tick's retry lands | The file in `listings/` is still the older version, so the claim would look `OWED` again | The start-up restore (6.10) writes the newer copy from the `WRITE-FAILED` line back before anyone can claim (`WRITE-RESTORED`). The result is the same as the row above: no duplicate, and a possible loss that regrant repairs. |
| CLAIM COINS, pay refused (0), and the roll-back write failed (`PAY-FAILED`), then a crash | The file says `CLAIMED` (archived if it was closed), but the coins were never paid | The start-up restore (6.10) reopens it from the `PAY-FAILED` copy (`OWED`). An archived copy is renamed, never overwritten. The seller claims again. |
| CLAIM COINS after the `CLAIMED` write, before paying | The seller is unpaid. `CLAIM-COINS-START` has no commit, so there is a `WARN` | Logged. `/ahadmin regrant <id> seller`. |
| CANCEL after the write, before delivery | `sellerItem = OWED` | Correct: claim. |
| During `atomicWrite` | The atomic move means either the old or the new file, never half of one. A stray `*.tmp` is deleted at load | Correct. |
| The file cannot be read at load | Moved to `listings/bad/`, `WARN`. Never deleted | An admin inspects it (the snapshot is inside). |

### 6.9 Races and edge cases
| Case | What happens |
|---|---|
| Two buyers click the same listing (any worlds) | The global lock orders them. The second finds `SOLD` in c and gets "Someone bought it first." Its coins were never touched, because every check comes before the take. |
| Cancel vs buy | Whichever takes the lock first wins. The other gets "no longer for sale" / "already sold". |
| Buy vs the expiry tick | The lock plus the `now < endsAt` check. A tick running late never makes a sale after the end time. |
| Admin remove vs buy | The lock. Remove refuses SOLD. |
| Stale item view (opened, then sold elsewhere) | c refuses. The page rebuilds with the live state. |
| Double click on Buy / Confirm | The second click arrives after the rebuild and sees SOLD, or the confirm has already been used. Nothing is charged twice. |
| Seller offline at the sale | Nothing touches the seller. Coins are owed in the record, with a notice on the next join. |
| Buyer's inventory full | Paid, record SOLD, item owed. Claim it later. |
| Player leaves mid-page | The page holds nothing. The picked item stays in its slot until the Create click, and an armed confirm dies with the page. Nothing to clean up. |
| Profile switch with the page open | Key mismatch means only a rebuild (4.1). |
| Profile busy (crash recovery at join) | Every action is refused (R6). |
| SkyyCoins missing or its file frozen | `Coins.ready()` is false or `get()` returns -1. Every buy, list and coin claim is refused with the reason. Item claims still work. |
| Coins bridge throws during take (-1) | The operation stops, `TAKE-ERROR` is logged and the player is told. The log lets an admin reconcile. |
| Server stops mid-click | Same as the crash rows. On a graceful stop, `shutdown()` flushes `DIRTY` and the log. |

### 6.10 Start-up restore (review fix, 2026-09-25)
A write that failed after an effect that cannot be undone (R2 exception) leaves the newer version only in memory until the tick's retry lands. A crash in that window would reload the older file, and an item already handed over could be claimed a second time. To close that window, `WRITE-FAILED` and `PAY-FAILED` lines carry the version memory kept, as one line of JSON after ` doc=`. The log is synced on every append (8.2), so the copy is on disk even when the listing write is not.

In `setup()`, right after `load()` and inside the one lock, `restoreFromLog` reads those lines from `auctions.log` and the 3 newest rotated logs. It keeps the highest `rev` per id and compares it with the loaded record:
- The copy has a higher `rev` than the file in `listings/`: the write never landed. The copy goes through the same `commitForced` path as the tick's retry (write, swap, archive when closed; `DIRTY` again if the disk still fails). `WRITE-RESTORED #id rev=<new> was=<old> saved=<bool>` is logged, a `WARN` goes to the server log, and `/ahadmin` status lists it.
- The copy has the same or a lower `rev`: a later write landed, so it is ignored. Revs only go up and ids are never reused, so this test is exact.
- The listing is not in `listings/`: it was closed and archived by a later write, so it is left alone. The one exception is a copy that is **not** closed and is newer than the archived copy (the `PAY-FAILED` roll-back). It reopens the listing the same way `regrant` does, and the archived file is renamed to `<id>.r<oldrev>.json`, never overwritten.
- Read-only records (a newer schema) are never touched. They get a `WARN` instead.

---

## 7. UI layout (inline only; ids without underscores; root anchor Width/Height only; TextButton + EventData; rebuild only on a click)

### 7.1 The page
- **One page class `AhPage`** (the SkyyMenu model): one inline `CustomUIPage` whose view (`browse | item | create | manage`) switches with `rebuild()`. The page never closes itself before showing something else. `/ah` and its subcommands call `player.getPageManager().openCustomPage(ref, store, new AhPage(pr, view))` directly, which replaces whatever page is open. [Close] calls `setPage(ref, st, Page.None)`.
- **The armed confirm is not a bare boolean.** The page keeps `armAct` (`buy`, `cancel`, `mcancel:<row>`, `claimall`), `armId` (the listing id, or the owed coin total for Claim all), `armPrice` and `armUntil`. A Confirm click acts only when `armAct` matches the button, `armId` / `armPrice` equal what the current view shows (`detailId` / `detailPrice`, the row's record id, or the current owed total) and `now < armUntil`. Every click handler copies the four fields to locals and clears them at its start (the Confirm handler checks the copies); only an arming click sets them again. So opening another listing, going Back or switching views always starts unarmed (2.3).
- **Root:** `Group #SkyyAh { Anchor: (Width: 1120, Height: 880); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }`. That is 1120 wide (verified), and 880 high fits a 1080-high screen. The content box is 1080 x 852, and the heights listed below add up to at most 852 per view: Browse about 812, Item about 776, Create about 834, Manage about 774, all counting the shared 126 px top. Rows are at most 1060 wide. The builder's render check asserts both limits.
- **Fonts:** title 26 bold, row names 17 bold, secondary text 13 to 14, buttons 15 bold, status 15. The button style is the SkyyBazaar 0.1.2 `bs` string at that size. The active tab uses the highlighted variant.
- **Static markup through `appendInline`** (fixed text only). **Every dynamic text through `b.set("#Id.Text", v)`**, and the item view's name and description through `b.set("#Id.TextSpans", Message)`.
- **Events:** actions are matched **exactly** with `jsonStr(data, "a")` (SkyyBazaar 0.1.2 / SkyyGuilds), with payloads like `nav:browse`, `cat:3`, `view:5`, `buy`, `pick:17`, `dur:2`. The page object keeps `rowIds[]`, `pickSlots[]`, `detailId`, `detailPrice`, the armed confirm, `key`, view state, `query`, `priceText`, `previewPrice`, `durIdx`, `browsePage`, `invPage`, `managePage` and `status`.
- **No timers, no scheduled rebuilds, no `sendUpdate` outside a click handler, no MouseEntered/MouseExited handlers** (HANDOFF: PageManager drops clicks while an update is unacknowledged, and hover updates crash the client).

### 7.2 Shared top (all views; height 50 + 50)
| Id | Element |
|---|---|
| `#SkyyAhTop` | Group, Height 50, LayoutMode Left |
| `#SkyyAhTitle` | Label, Width 420, "Auction House" (26 bold) |
| `#SkyyAhPurse` | Label, Width 400, right-aligned, "Purse: 12,345 coins - profile Apple" |
| `#SkyyAhNav` | Group, Height 50, LayoutMode Left |
| `#SkyyAhNavBrowse`, `#SkyyAhNavCreate`, `#SkyyAhNavManage`, `#SkyyAhNavClose` | TextButton 200 x 42 |
| `#SkyyAhBanner` | Label, Height 26: paused / needs SkyyCoins / profile loading / market:deny reason (empty text otherwise) |

### 7.3 Browse (about 810 px of content)
| Id | Element |
|---|---|
| `#SkyyAhCats` | Group, Height 46, LayoutMode Left; `#SkyyAhCat0`..`#SkyyAhCat6` TextButton 148 x 40 |
| `#SkyyAhFilt` | Group, Height 46, LayoutMode Left |
| `#SkyyAhSearchBox` | Group 360 x 40, Background #16263a, holding `TextField #SkyyAhSearch { Anchor: (Full: 0); MaxLength: 40; PlaceholderText: "Search items or sellers..."; }` |
| `#SkyyAhSearchGo`, `#SkyyAhSearchClr` | TextButton 100 x 40 ("Search", "Clear") |
| `#SkyyAhSort` | TextButton 220 x 40 ("Sort: Lowest price") |
| `#SkyyAhRar` | TextButton 180 x 40 ("Rarity: Any") |
| `#SkyyAhRefresh` | TextButton 90 x 40 |
| `#SkyyAhHead` | Label, Height 22, column hints "Item / Seller / Price / Ends in" |
| `#SkyyAhRow0`..`#SkyyAhRow7` | Group, Height 62, LayoutMode Left, Background #142030(0.9). Children: Group 60 x 60 with `ItemIcon` 52 x 52; `#SkyyAhRowName<i>` Label 380 (rarity colour inline, 17 bold) above `#SkyyAhRowSub<i>` Label 380 (13); `#SkyyAhRowSeller<i>` Label 170; `#SkyyAhRowPrice<i>` Label 170 (gold #ffd36a, bold); `#SkyyAhRowTime<i>` Label 110; `#SkyyAhRowView<i>` TextButton 100 x 44 "View" |
| `#SkyyAhEmpty` | Label (only with 0 results): "Nothing listed here yet" / "No match for 'abc'" |
| `#SkyyAhPager` | Group, Height 46: `#SkyyAhPrev`, `#SkyyAhPageTxt` (Label 400, centred), `#SkyyAhNext` |
| `#SkyyAhStatus` | Label, Height 30 |

- Search binding: `Validating` on `#SkyyAhSearch` and `Activating` on `#SkyyAhSearchGo` carry `EventData.of("a","search").append("@AhSearch","#SkyyAhSearch.Value")`. **Every other Browse binding also appends `@AhSearch`**, and any Browse click applies the typed text as the query. The rebuild sets `#SkyyAhSearch.Value` back (SkyySacks CraftPage pattern).
- Rows are a Group plus a [View] TextButton, the most proven element. A whole-row clickable `Button` is an option only after a client check.

### 7.4 Item view
| Id | Element |
|---|---|
| `#SkyyAhDBody` | Group, Height 560, LayoutMode Left |
| `#SkyyAhDLeft` | Group, Width 220: `ItemGrid #SkyyAhDGrid { Anchor: (Width: 180, Height: 180); SlotsPerRow: 1; AreItemsDraggable: false; InfoDisplay: None; Style: (SlotSize: 180, SlotIconSize: 140, SlotSpacing: 0); }` + `b.set("#SkyyAhDGrid.Slots", [new ItemGridSlot(stack)])`. No SlotClicking binding. |
| `#SkyyAhDRight` | Group, Width 820, LayoutMode Top |
| `#SkyyAhDName` | Label, Height 40, 22 bold, `.TextSpans` = `getDisplayName()` |
| `#SkyyAhDDesc` | Label, Height 230, 15, `Wrap: true`, `.TextSpans` = `getDisplayDescription()` |
| `#SkyyAhDFact0`..`#SkyyAhDFact7` | Label, Height 28 each, "Rarity: Rare", "Quantity: 1", "Durability: 187 / 200", "Seller: Skyy", "Price: 12,000 coins", "Ends in: 5h 12m", "Listed: 2h ago", "Listing #1043" |
| `#SkyyAhDFact8` | Label, Height 28, orange: the cheaper-listing warning (2.3) and, for a bag, "Contents not included." (4.3; the short form, joined with " - " when both apply); empty text otherwise. The right column is then 40 + 230 + 9 x 28 = 522 of the 560 px body, so the view's total height does not change. |
| `#SkyyAhDAct` | Group, Height 60, LayoutMode Left: `#SkyyAhDBuy` TextButton 360 x 50 (or `#SkyyAhDCancel`), `#SkyyAhDConfirm` + `#SkyyAhDNo` TextButtons 220 x 50 while armed, `#SkyyAhDBack` TextButton 240 x 50 |
| `#SkyyAhStatus` | shared |

- **Fallback:** `detailTextSpans=true` in config. With `false`, the name and description are shown as plain text (5.4 plain name, and SkyyRolls' `meta.SkyyRolls` fields written out as "Reforge Sharp - Damage +5% - Strength 3 - Crit 2 - Roll quality 81%"). This is the switch an admin flips if `TextSpans` fails on a client.

### 7.5 Create BIN view
| Id | Element |
|---|---|
| `#SkyyAhInvHead` | Label, Height 26, "Pick an item from your inventory (hotbar, storage, backpack)" |
| `#SkyyAhInvGrid` | Group, Height 312, LayoutMode Top, 4 rows `#SkyyAhInvRow0`..`#SkyyAhInvRow3` (Group, Height 78, LayoutMode Left) of 9 cells `#SkyyAhInv0`..`#SkyyAhInv35`: `Button` 76 x 76 (SkyyBazaar cell) with `ItemIcon` 56 x 56 and a quantity Label `#SkyyAhInvQty<i>`. The picked cell has a lighter background. |
| `#SkyyAhInvPager` | Group, Height 40: `#SkyyAhInvPrev`, `#SkyyAhInvTxt`, `#SkyyAhInvNext` |
| `#SkyyAhSel` | Group, Height 76, LayoutMode Left: ItemIcon 60, `#SkyyAhSelName` (rarity colour), `#SkyyAhSelInfo` ("x1 - Rare - hotbar slot 3"), `#SkyyAhSelHint` (lowest BIN hint; for a bag it ends with "Contents not included.", 4.3) |
| `#SkyyAhPriceRow` | Group, Height 50: Label "Price", `#SkyyAhPriceBox` Group 300 x 42 Background #16263a holding `TextField #SkyyAhPrice { Anchor: (Full: 0); MaxLength: 16; PlaceholderText: "e.g. 12000 or 12k"; }`, `#SkyyAhPricePreview` TextButton 150 x 42 "Preview" |
| `#SkyyAhDurRow` | Group, Height 50: Label "Duration", `#SkyyAhDur0`..`#SkyyAhDur7` TextButton 100 x 42 (only the configured presets are appended) |
| `#SkyyAhFee0`, `#SkyyAhFee1`, `#SkyyAhFee2` | Labels, Height 24 (fee, proceeds, low-price warning) |
| `#SkyyAhCreate` | TextButton 360 x 52 "Create BIN" |
| `#SkyyAhStatus` | shared |

- Every binding in this view (cells, pager, Preview, durations, Create) appends `@AhPrice` = `#SkyyAhPrice.Value`. `Validating` on `#SkyyAhPrice` = Preview.
- `pickSlots[i]` stores section, slot, id, quantity and a metadata JSON hash for each visible cell (5.3 identity check at Create).

### 7.6 Manage view
| Id | Element |
|---|---|
| `#SkyyAhMSum` | Group, Height 50: `#SkyyAhMSumTxt` Label 640, `#SkyyAhMClaimAll` TextButton 200 x 42, `#SkyyAhMCreate` TextButton 200 x 42. While the claim-all confirm is armed (2.5): the summary text becomes the confirm question, `#SkyyAhMClaimAll` reads "Yes, claim all" and `#SkyyAhMClaimNo` (200 x 42, "No") takes the place of `#SkyyAhMCreate` |
| `#SkyyAhMRow0`..`#SkyyAhMRow7` | Group, Height 62: ItemIcon 52, `#SkyyAhMName<i>` Label 360, `#SkyyAhMState<i>` Label 380, `#SkyyAhMAct<i>` TextButton 200 x 44 ("Cancel" / "Claim coins" / "Claim item"); confirm-cancel arms that row's button to "Yes, cancel" + `#SkyyAhMNo<i>` |
| `#SkyyAhMPager` | Group, Height 46: `#SkyyAhMPrev`, `#SkyyAhMPageTxt`, `#SkyyAhMNext` |
| `#SkyyAhMOther` | Label, Height 26 (other profiles' claims) |
| `#SkyyAhStatus` | shared |

### 7.7 The stuck-tooltip bug (hover an item, press Esc, the tooltip stays)
The bug is the client's global tooltip layer: an **ItemGrid hover tooltip** is not cleared when Esc removes the page (SkyyMenu 0.1.3 findings), and the server cannot fix it after Esc. SkyyAuctions **never shows a hover tooltip**:
- Browse, Create and Manage use plain `ItemIcon`s, which have no native tooltip.
- The one ItemGrid (the item view preview) uses `InfoDisplay: None`, the markup that structurally prevents the bug.
- The tooltip's text is shown **on the page** instead (7.4).

So Esc can never leave a tooltip behind, and no clear-before-close step is needed.

---

## 8. Admin and logs

### 8.1 `/ahadmin` (root and every subcommand / variant call `requirePermission("skyyauctions.admin")`; SkyyBazaar 0.1.1 subcommand pattern)
| Command | What it does |
|---|---|
| `/ahadmin` | Status: ACTIVE count, owed claims, `DIRTY` count, paused on or off, the config summary (fees, durations, limits), every unmatched `*-START` found at startup, and every record the start-up restore wrote back (6.10). |
| `/ahadmin list` | The 10 newest ACTIVE listings: `#id item xqty price seller ends-in`. |
| `/ahadmin list <player>` (usage variant) | That player's live records (all profiles, any state), matched case-insensitively on `seller.name` / `buyer.name` stored on the records, so offline players work without a name lookup. |
| `/ahadmin info <id>` | Every field of one record (live or archived): state, claims, seller/buyer, fee, sale, the item id and metadata keys. |
| `/ahadmin remove <id>` | ACTIVE -> REMOVED, the item goes back to the seller's claims (6.7). Reason `"removed by an admin"`. |
| `/ahadmin remove <id> <reason...>` | Usage variant, `GREEDY_STRING` reason shown to the seller. |
| `/ahadmin reload` | Re-reads `config.properties` and `Skyy_Market/blocked.txt` (republishes the `file` entries). Never re-reads listings. |
| `/ahadmin pause` / `/ahadmin resume` | Sets `paused` and writes it to config. |
| `/ahadmin regrant <id> <seller\|buyer>` | **Preview only, changes nothing.** The repair tool for the crash window (6.8). Prints the record's state, both claims, earlier `regrants[]` entries, what would be owed, and the evidence from the log (below). Remembers "admin, id, side, rev" for 60 s. |
| `/ahadmin regrant <id> <seller\|buyer> confirm` | Usage variant (third required arg, must be the word `confirm`). Applies the regrant only if the same admin previewed the same id and side in the last 60 s **and** the record's `rev` has not changed since. |

**Regrant guardrails** (it is a duplication tool if misused, so it is admin-only, two-step and loudly logged):
- **Only from exactly `CLAIMED`.** The chosen side's claim must be `CLAIMED` right now: seller = `sellerCoins` if SOLD, otherwise `sellerItem`; buyer = `buyerItem`. `OWED` (already repaired, or never paid) and `NONE` (there was never such a claim) are refused with the current value. There is no force flag, because both refused cases would only create coins or items.
- **Evidence first.** The preview prints every log line for `#<id>` from `auctions.log` and the 3 newest rotated logs of any month (at most the last 12; a record copy on a line shows as `doc=(record copy)`), and a verdict line:
  - coins: "CLAIM-COINS-START with no CLAIM-COINS or ABORT - looks like a real interrupted payout", or "CLAIM-COINS commit found - the coins were paid; regrant would duplicate them";
  - items: "CLAIM-ITEM at 12:00:03, then BOOT at 12:01:10 with no STOP in between - a crash followed this delivery", or "no crash after the last delivery - check the player's inventory before regranting".
  A previous regrant of the same side is shown in red ("already regranted on 2026-09-30 by Skyy").
- **Quantity.** An item regrant owes the quantity of the **last** logged delivery for that side (`CLAIM-ITEM` or `CLAIM-ITEM-PART` `qty=`), not the full stack, because earlier partial deliveries were saved and still exist. With no delivery line found it falls back to the full stack and says so in the preview.
- **Same path as every other change.** Inside the one lock (R1), `regrant0` re-reads the record (from `LIVE`, or from `archive/` for a closed one), checks the claim and the `rev` again, and builds a clone: the claim `OWED`, `<side>ItemQty` set, `closed = false`, `closedAt = 0`, `regrants` + `{side, by, at, qty}`, `rev + 1`. It `atomicWrite`s the clone to `listings/<id>.json`, and only on success puts it in `LIVE` and drops the `STACKS` entry. So `/ah claim`, Manage and the per-owner scan see it at once, with no restart. A closed record's archive copy is then renamed to `archive/<yyyy-MM>/<id>.r<oldrev>.json` (kept, never deleted; a failed rename is only logged, since load reads `listings/` alone). After the lock: `REGRANT #id side qty by=<admin>` (synced), republish `auction:claims:<uuid>`, and tell the owner if online.

### 8.2 `auctions.log`
- One line per event: `<ISO time> <EVENT> #<id> key=value ...` with names, UUIDs, profile keys, `item=<id>x<qty>`, `price`, `fee`, `net`, `tax`, `by=<admin>`.
- Events: `LIST-START LIST LIST-ABORT BUY-START BUY BUY-ABORT CANCEL EXPIRE REMOVE CLAIM-COINS-START CLAIM-COINS CLAIM-COINS-ABORT CLAIM-ITEM CLAIM-ITEM-PART REGRANT NOTICE BOOT STOP`. `BOOT` is written in `setup()` and `STOP` at the end of a clean `shutdown()`, so a `BOOT` with no `STOP` before it marks a crash (regrant's evidence, 8.1).
- Error lines: `TAKE-ERROR REFUND-FAILED PAY-FAILED PAY-ERROR WRITE-FAILED WRITE-RETRY-OK WRITE-RESTORED ITEM-LOST`. `ITEM-LOST` should never happen; it carries the full snapshot JSON on one line so the item can be rebuilt. `WRITE-FAILED` and `PAY-FAILED` end with ` doc=<the record version memory kept>` on the same line, which the start-up restore reads (6.10).
- **Appended and synced:** open with `new FileOutputStream(f, true)`, write, `getFD().sync()`, close. The listing files are fsynced to survive a power loss, and this log is the only evidence of an interrupted trade, so it gets the same guarantee: a START line left in an OS buffer would vanish exactly when an admin needs it. Every append is synced. The tick writes all its `EXPIRE` lines of one pass in a single append with one sync, so a burst of expiries costs one sync. START lines are synced inside the lock, before the effect (R7); that is part of the lock-hold budget in R1. Rotated by the tick at 5 MB.

---

## 9. Bridge keys (`System.getProperties().get("skyy.bridge")`)

**Published by SkyyAuctions:**
| Key | Value |
|---|---|
| `auction:fn:lowestBin` | `Function apply(String itemId) -> Long`: the lowest **per-unit** price (ceil(price / qty)) among ACTIVE, unexpired, not-blocked BIN listings of that exact item id; `null` when there are none. Lock-free read of `LIVE`. For later mods (price hints, a SkyyMenu tooltip, SkyyGear's value display). Inside the mod, `AhStore.lowestBin(id, skipId)` returns `long[] {lowestEach, count}` for the Create hint and the item view's cheaper-listing line (2.3), with `skipId` leaving the listing being viewed out of the lowest price (the count still includes it; the Create view passes `null`). |
| `auction:count` | `Long` number of ACTIVE listings (republished on every change and tick). |
| `auction:claims:<uuid>` | `Integer` owed claims of that player's **active** profile. Republished on change, join and epoch change; for a "Manage (2)" badge on a future SkyWynn Menu button. |
| `auction:version` | `"0.1"` |
| `market:blocked` (shared) | Only its own `file` entries (4.4). |

All `auction:*` keys are removed on shutdown; the shared `market:*` maps stay.

**Read by SkyyAuctions:** `coins:fn:get` / `take` / `add` (copy the SkyyBazaar `Coins` wrapper verbatim: 1 = ok, 0 = refused, -1 = threw), `profile:fn:key` (pkey helper from the contract), `profile:busy:<uuid>`, `profile:epoch:<uuid>`, `profile:name:<uuid>`, `profile:list:<uuid>` (profile names for the "other profiles" line), `bazaar:products` (a comma-joined String, matched by whole ids, 4.3), `market:blocked`, `market:veto`, `market:deny:<uuid>`, `bank:<uuid>` (only whether it exists, for the `/ah claim` tip in 2.5).

---

## 10. Code structure and build

### 10.1 Classes (javassist: one top-level class each, no inner classes; methods added before their callers)
| Class | Job |
|---|---|
| `SkyyAuctionsPlugin` | `setup()`: dirs, config, blocked file, store load (6.8 load rules), commands, events, page id `SkyyAuctions` (`OpenCustomUIInteraction.registerSimple`, SkyyBazaar pattern), bridge functions, tick, then the `BOOT` log line. `shutdown()`: cancel the tick, flush `DIRTY`, remove `auction:*`, remove its `file` entries, write the `STOP` log line last (only when the flush succeeded), `super.shutdown()`. |
| `AhCfg` | Config template + parse, `atomicWrite` (copy SkyyProfiles `ProfCfg.atomicWrite`), `readText`, blocked-file load, duration + fee tables. |
| `AhUtil` | `bridge()`, `pkey()`, `jsonStr()`, `isId()`, `parseAmt()`, `fmt()` (12,345), `timeLeft()`, `tr()`, `plain(Message)`, `warn()`. |
| `Coins` | The SkyyBazaar wrapper, verbatim. |
| `AhItem` | `snap`, `restore`, `roundTripOk`, `category`, `qualityValue/name/colour`, `reforge`, `plainName`, `count(inv,id)`, `room(inv,stack)`, `sections(inv)` (hotbar, storage, backpack), `tradeable(stack)` (4.3 rules 2-4 + blocked + vetoes), `isBazaarItem(id)` (whole-token match on `bazaar:products`, cached set, 4.3), `blockedReason(id)` (exact then `Prefix*` walk, 4.4), `isBag(id)` (`Skyy_Sack_` prefix or `Skyy_Accessory_Bag`, for the "contents not included" note). |
| `AhRec` | Getters/setters on the record `BsonDocument` with defaults (`str`, `lng`, `sub`, `claim`, `setClaim`, `clone`), `toJson`/`parse`. |
| `AhStore` | `LIVE`, `STACKS`, `DIRTY`, `load()`, `write(rec)`, `archive(rec)`, `nextId()`, the `*0` operations of section 6 and their `synchronized` wrappers, per-owner scans, `lowestBin`, `notices(u)`. |
| `AhResult` | `ok`, `msg`, `id`, `coins`, `kept` (item waiting in claims), `alert` (owed message), `saveNeeded` (the inventory changed: run R8's forced save after the lock), `notifyUuid` / `notifyMsg` (chat to send after the lock). |
| `AhSort` | `java.util.Comparator` with a `mode` field (4 sorts). |
| `AhLog` | Synced append (8.2), `BOOT` / `STOP` lines, START scan at load, `linesFor(id, max)` for the regrant preview, rotation. |
| `AhPage` + `AhPageFactory` | The page (section 7) and the OpenCustomUI factory. |
| `AhCmd`, `AhSellCmd`, `AhSellDurCmd` (variant), `AhClaimCmd`, `AhManageCmd`, `AhSearchCmd` | Player commands (2.1), all with the Adventurer permission group. |
| `AhAdminCmd` + `AhAdminListCmd`, `AhAdminListPlayerCmd`, `AhAdminInfoCmd`, `AhAdminRemoveCmd`, `AhAdminRemoveWhyCmd`, `AhAdminReloadCmd`, `AhAdminPauseCmd`, `AhAdminResumeCmd`, `AhAdminRegrantCmd` (preview), `AhAdminRegrantOkCmd` (the `confirm` variant) | Admin (8.1), each with `requirePermission`. The Python `cmd()` helper from SkyyGuilds keeps this short. |
| `AhTick` | Every 10 s (`HytaleServer.SCHEDULED_EXECUTOR`): expire, `DIRTY` retry, archive retry, epoch check for online players, republish, log rotation. |
| `AhReady` / `AhQuit` / `AhNoticeTask` | PlayerReadyEvent once-per-session guard, PlayerDisconnectEvent clears the guard, the 3 s delayed notice. |
| `AhLowestBinFn` | The bridge Function. |

No ECS system is needed (so no `registerSystem` concerns). Nothing touches components off the world thread: inventory work runs only in page clicks and player commands (world thread). The tick and notices only touch records, the bridge and chat.

### 10.2 Reuse map (copy the logic, not other authors' code; everything below is our own repo)
| From | What |
|---|---|
| SkyyBazaar 0.1.2 | `Coins` wrapper, `parseAmt`, `jsonStr`, `isId`, amount TextField + `@Key` carry pattern, `room()`, button style, page registration, the "take coins first / count what landed / refund" discipline. **Not** `Inv.give` (loses metadata). |
| SkyyProfiles 0.1 | `ProfInv` snapshot/restore (CODEC + explicit fields), `toJson`/`parse`, `ProfCfg.atomicWrite`. |
| SkyyAccessories 0.4.3 | Inventory list scan over storage/hotbar/backpack, profile-changed-since-draw check, busy refusal wording. |
| SkyySacks 0.7.5 | Search TextField (`#SkyyCSearch` pattern), count before/after (`removedItems`). |
| SkyyGuilds 0.1.1 | `cmd()` subcommand helper, "write the durable record first, roll back exactly" payout order, `keepAmount` field restore, log paging (if `/ahadmin list` grows pages later). |
| SkyyMenu 0.1.3 | One-page-many-views model, `InfoDisplay: None`, the open-without-closing rule, `jsonInt`. |
| SkyyRolls 0.1.4 | `tr()`, `rarityColor` from `ItemQuality`, the `SkyyRolls` metadata key shape. |
| SkyyCollections 0.2 | `getGameMode() == GameMode.Creative`. |

### 10.3 Build-time probes (`B.probe`, fail early on API drift)
`ItemStack.CODEC`, `ItemStack.getMetadata`, `getDisplayName`, `getDisplayDescription`, `withQuantity`, `isStackableWith`, `getQualityIndex`, `Item.getWeapon`, `getArmor`, `getTool`, `getGlider`, `getUtility`, `isConsumable`, `hasBlockType`, `ItemQuality.getAssetMap`, `ItemGridSlot.<init>(ItemStack)`, `UICommandBuilder.set(String, Message)`, `Inventory.getCombinedStorageHotbarBackpack`, `getActiveHotbarSlot`, `getHotbar`, `getStorage`, `getBackpack`, `ItemContainer.removeItemStackFromSlot`, `addItemStack`, `SimpleItemContainer.addOrDropItemStack`, `Player.getGameMode`, `markNeedsSave`, `Player.saveConfig(World, Holder, boolean)`, `Store.copySerializableEntity(Ref)` (these two are soft probes: when missing, the build prints a warning and generates the R8 call as a no-op instead of failing), `GameMode.Creative`, `Universe.getPlayer(UUID)`, `I18nModule.getMessage`, `org.bson.BsonDocument.parse`, `toJson`, `JsonWriterSettings.builder`, `HytaleServer.SCHEDULED_EXECUTOR`, `OpenCustomUIInteraction.registerSimple`, `AbstractCommand.setPermissionGroups`, `addUsageVariant`, `setAllowsExtraArguments`, `ArgTypes.GREEDY_STRING`.

### 10.4 Build and checks (hard rules)
- **Build:** `python SkyyAuctions/build_skyyauctions_0.1.py` (plain python, **never `--deploy`**). It must end with `assembled ...SkyyAuctions-0.1.jar <n> bytes`.
- **Lint:** `python tools/ci/lint.py`, 0 fails. It checks underscore ids, `.ui` files and command permissions. `ADMIN_ONLY_OK` needs no entry because every admin command calls `requirePermission`.
- **Offline harness** (scratch only under `tools/dev/scratch/ah/`, deleted afterwards; nothing written under AppData):
  - `-Xverify:all` load of every class;
  - `parseAmt` / fee / tax / duration / `timeLeft` cases;
  - category of sample items from Assets.zip (weapon, armor, food, potion, block, ingredient, tool, a Skyy accessory);
  - a snapshot round-trip of an `ItemStack` with a `SkyyRolls` metadata document plus an `ItemDisplayMetadata` (mark UNVERIFIED if the codec needs live asset maps);
  - record write / parse / clone keeping an unknown field;
  - the state machine with fake `coins:fn:*` Functions: list, buy, claim, cancel, expire, remove, regrant, and a write failure injected at each step (checks the refunds);
  - **a partial removal at LIST j:** the fake container removes fewer than `qty` (and, as a second case, none). After the rollback the item count equals `before` exactly, the put-back stack has the original metadata, the purse equals its value before the list (fee taken and refunded, nothing else), no record exists, and `LIST-ABORT` is logged. A third case makes the put-back fail and expects `ITEM-LOST` with the snapshot;
  - **regrant guardrails:** refused on `OWED` and on `NONE`; the `confirm` variant refused without a fresh preview or after the `rev` changed; a regrant of an archived record is visible to the per-owner scan and to claim at once (no reload), and a second close archives to `<id>.r<rev>.json` without overwriting;
  - **market lookups:** `bazaar:products = "Ore_Copper,Ore_Copper_Rich"` matches `Ore_Copper` and `Ore_Copper_Rich` but not `Ore_Copp` or `Copper`; a `market:blocked` entry `Ore_Mithril*` blocks `Ore_Mithril_Rich`, an exact entry blocks only its own id, and a bare `*` is ignored with a WARN;
  - **test durations:** `2m:0` with `allowTestDurations=false` is dropped with a WARN (and a `defaultDuration=2m` falls back to `24h`); with `true` it loads and the status line says TEST DURATIONS ARE ON;
  - **armed confirm:** arm Buy on listing A, open listing B: B is unarmed, and a Confirm event replayed on B does nothing;
  - **two threads calling `buy` on one id** (exactly one SOLD, coins taken once);
  - the render markup (balanced braces / quotes / parentheses, no underscore ids, root anchor only Width + Height, every id unique).
  - The page on a real client stays UNVERIFIED until Skyy opens it.
- **Scope:** edit only `SkyyAuctions/` and the two research files. No commit. The main session afterwards adds the SkyWynn Menu button (`/ah`), pins the jar in `tools/deploy_set.py`, and adds TEST-CHECKLIST / HANDOFF lines.

---

## 11. Test plan

### 11.1 Solo (one account; set `sameAccountBuy=true`, `allowTestDurations=true` and add a `2m:0` duration for the test, then set all three back; the start-up WARN and the `/ahadmin` status line are the reminder)
1. `/ah` opens Browse: empty state text, purse and profile shown, all 7 categories and 4 sorts click and rebuild. Close works. Esc leaves nothing on screen.
2. `/rolls give` a longsword and `/rolls read` it (note the metadata). **Create BIN:** pick it, type `12k`, Enter shows the fee (120 + 350 = 470). Create lists it: the purse drops by exactly 470, the item leaves the inventory, and Manage shows it ACTIVE.
3. Browse -> Weapons shows the row (rarity colour, reforge name, "yours"). The item view shows the preview, name and roll lines as text, and facts. There is no Buy button (own listing).
4. **Cancel** from the item view (confirm row): the item comes back. `/rolls read` gives **identical metadata**. The fee is not refunded.
5. List with `2m`: after 2 minutes the Manage row reads "Expired", with a chat line if online. Claim item, then `/rolls read` again.
6. **Full inventory:** fill the inventory, let a listing expire, Claim: "make room", nothing lost. Free one slot, Claim works.
7. **Relog notice:** list with `2m`, log out for 3 minutes, log in: the "expired" notice appears once. Change world (`/hub`, `/island`): no repeat.
8. **Restart persistence:** list, stop and start the server. The listing is still there with the same time left and identical metadata after cancelling.
9. **Profiles:** list on profile 1, switch to profile 2. Manage says "Your profile <1> has 1 thing to claim" and Cancel is not offered. Profile 2 **buys it** (`sameAccountBuy=true`): profile 2's purse drops and the item arrives. Switch to 1: Claim coins pays profile 1 exactly the price (tax 0 under 1M).
10. `sameAccountBuy=false` (default): profile 2 sees "Listed by your profile ...", no Buy.
11. **Creative:** switch to Creative, try Create and Buy: refused, browsing works.
12. **Blocked:** add the item id to `Skyy_Market/blocked.txt`, `/ahadmin reload`. The picker says "off the market", an existing listing shows red "off the market" and cannot be bought, Cancel still works.
13. **Bazaar item:** try to list Copper Ore: "Sell this on the Bazaar: /bz".
14. `/ah sell 5k` with an item in hand: the page opens prefilled, one Create click lists. `/ah sell 5k 6h` sets 6h. `/ah sell 5k 7h` gives "Pick one of...". `/ah claim` and `/ah search copper` work. A non-admin gets no-permission on `/ahadmin`.
15. **Admin:** `/ahadmin list`, `list <me>`, `info <id>`, `remove <id> testing` (the item goes back to claims with the reason, and the log line appears), `pause` (Create and Buy refused, the banner shows, claims still work), `resume`. **Regrant:** `regrant <id> seller` on a claimed record prints the log lines and a verdict and changes nothing; `regrant <id> seller confirm` within 60 s brings the claim back, visible in Manage **at once** (no restart); running `confirm` again is refused ("claim is OWED, not CLAIMED").
16. The `auctions.log` lines are present for every step above, starting with `BOOT` and ending with `STOP` after a clean stop. After a clean stop, `/ahadmin` shows no unmatched START.
17. **Forced save (R8, UNVERIFIED part):** note the time of your player file in the world's player-data folder, list an item, and check the file time changed within a second or two (not only at the next 10 s tick). If the server log shows the one-time "forced save skipped" line, set `forceSaveAfterTrade=false` and report it.
18. **Claim-all confirm:** with more than 100,000 coins owed (list for 150k on profile 1, buy it on profile 2 with `/coinsgive`), [Claim all] asks first with the death-penalty line; No leaves everything owed; Yes claims.
19. **Cheaper listing:** list the same item id twice (10k and 15k, one per profile). The 15k listing's item view shows "A cheaper one is listed: 10,000 each (2 listed)", and its confirm row repeats it. The 10k listing shows no such line.
20. **Test durations off:** set `allowTestDurations=false`, `/ahadmin reload`: the WARN names `2m:0`, and the Create view no longer offers 2m.

### 11.2 Two players (A = seller, B = buyer; both Adventurer, not admins)
1. A lists a rolled item for 12k. B opens it within 20 s: "Buy (opens in N s)". After the grace, B buys through the confirm row (12,000 >= 10,000). B's purse drops by exactly 12,000 and the item arrives in B's inventory. B's `/rolls read` shows **A's exact rolls**.
2. A (online) gets the sale message at once. A's Manage shows "Sold to B - 12,000". Claim coins: A's purse goes up by exactly 12,000. The row disappears, and the record is in `archive/`.
3. **Offline sale:** A lists, logs out. B buys. A logs in and gets the notice once. `/ah claim` pays.
4. **Race:** A lists one item. B and A's second account (or a third player) both open it and click Buy/Confirm at the same moment. Exactly one gets it, the other gets "Someone bought it first", and only the winner's purse changed.
5. **Cancel vs buy:** B has the item view open. A cancels. B clicks Buy: "no longer for sale", B's purse unchanged, and A has the item back.
6. **Full inventory buy:** B fills the inventory and buys. B is charged, and "waits in Manage" appears. B frees a slot and claims it, with metadata intact.
7. **Not enough coins:** B with less than the price: "You need N more coins", nothing taken.
8. **Different worlds:** A on their island, B at the hub. Both flows work (the global lock covers every world thread).
9. **Tax check:** A lists at 2,000,000 and B buys (give B coins with `/coinsgive`). A's claim pays 1,980,000 (tax 20,000 = 1%), and Manage showed the tax before the claim.
10. **Max listings:** A creates 14 listings, and the 15th is refused with the count. A claims one sold listing and the slot frees.

---

## 12. Open questions for Skyy (the build uses the default in brackets; each is one config key)
1. **Fees and tax.** LOCKED 2026-09-25 (Skyy): keep Hypixel's numbers. Listing fee 1% / 2% / 2.5% (`listingFee=0:1.0,10000000:2.0,100000000:2.5`). Duration fees on 1h / 6h / 12h / 24h stay 20, 45, 100 and 350 (the fee half of `durations`). The 48h charge is question 2. Claim tax 1% above 1,000,000 (`claimTaxPercent=1.0`, `claimTaxFrom=1000000`). Every fee value is adjustable in Server Setup: `ah.listingFee`, the fee half of `ah.durations`, `ah.claimTaxPercent`, and `ah.claimTaxFrom`. SkyyAuctions 0.1.1 still reads `config.properties` (then `/ahadmin reload`). The menu rows ship with SkyyEconomy. A later tax edit does not change a sale that already stored its tax. New profiles still start with 10,000 coins.
2. **Durations.** LOCKED 2026-09-25 (Skyy): presets stay 1h, 6h, 12h, 24h and 48h. Default is 24h. The 48h option costs double the normal listing fee (2% / 4% / 5% on the same price tiers as the 1% / 2% / 2.5% listing fee). 1h, 6h, 12h and 24h still add their flat duration fees. SkyyAuctions 0.1.1 still adds a flat 1,200 coins for 48h. The loader's 14-day ceiling stays a safety cap if a custom preset is longer.
3. **Bazaar items on the AH.** Should Bazaar commodities be refused on the AH, like Hypixel? [refused]
4. **One account, several profiles.** Should one account never be able to buy its own listings, even from another profile? [never]
5. **Creative players.** Browse and claim only? [yes]
6. **Listing cap.** 14 per profile, with no rank or permission bonus (Hypixel's only bonus is co-op size, which we do not have). [14]
7. **Confirm threshold.** Should buys at or above this need a second click? [10,000 coins]
8. **Cancel keeps the fee** (Hypixel). [kept]
9. **`/ah sell`.** Open the prefilled page for one click, or list straight from chat? [prefilled page]
10. **Grace period.** How long should a new listing wait before anyone can buy it? [20 s]
11. **Where `/ah` works.** Anywhere, or later only at an Auction Master NPC in the hub? On Hypixel, remote `/ah` is a Booster Cookie perk; this is from general knowledge, not in the research. [anywhere; the page id `SkyyAuctions` is ready for an NPC]
12. **Late-game cutoff.** Which items leave both markets? Still open (DESIGN-STATUS question 11). [nothing blocked; the list and bridge are ready]
13. **Bid auctions.** When, and with which rules (minimum raise, last-minute extension, 5% fee)? [later; Appendix A]
14. **Deleted profiles.** Claims owned by a profile that no longer exists (SkyyProfiles 0.1 has no delete yet). [they stay in the file; an admin can use `regrant` or move them by hand]
15. **Bags on the AH.** Magic Bags and the Accessory Bag are only keys to the owner's own storage (4.3). Tradeable with a "contents not included" line, or off the market? [tradeable; two `blocked.txt` lines take them off]
16. **Claim-all confirm.** Ask before [Claim all] puts a lot of coins in the purse (death penalty 10-25%)? [yes, at 100,000 coins]

---

## 13. Review notes (2026-09-24)

Twelve review findings were checked against this spec, the live scripts and `HytaleServer.jar`.

**Applied:**
- LIST rollback formula: 6.4 j, plus a harness case.
- Regrant guardrails (preview + confirm, only from `CLAIMED`, the normal write + `LIVE` path, log evidence, `BOOT`/`STOP`): 8.1, 8.2, 5.1, 5.2, 6.2.
- Synced log: 8.2, R7, 5.1.
- Cheaper-listing line on the item view: 2.3, 7.4, 9.
- Lock kept short: R1, 6.4 m, 6.5 k, 6.6, 6.7.
- Test-duration guard: section 3, 11.1.
- Whole-token `bazaar:products` match: 4.3.
- `Prefix*` lookup for `market:blocked`: 4.4.
- Armed confirm tied to one listing: 2.3, 7.1. The old "any other click disarms it" already covered it in words; the fix makes it structural.
- Claim-all confirm: 2.5, 3, 7.6. The research's Hypixel nudge fits SkyWynn because the death penalty takes purse coins.

**Applied in part, with corrections:**
- **Forced player save (R8).** The idea holds, but two parts of the finding were wrong:
  - `Player.saveConfig` is **not** a synchronous flush. It turns the player into BSON on the calling thread, then **queues** the write on the engine's `StorageManager` and returns a `CompletableFuture`.
  - PROFILES-CONTRACT section 5 only says the engine saves a player when it leaves a world; it never calls that save synchronous.
  - The method also needs a `Holder`, which the engine builds from its own chunk data; a mod has to use `Store.copySerializableEntity(ref)` (UNVERIFIED in game).
  - Result: a soft-probed, config-gated call after the lock with `force = true`. It shortens the window from up to 10 s to "until the queued write lands", not to zero.
  - It applies to LIST, BUY delivery, claims and a cancel's return. EXPIRE and admin REMOVE never touch an inventory, so they need no save (the finding listed them).
- **Magic Bags / Accessory Bag.** Not blocked by default. The finding called bag sales a free-money exploit that breaks "no item or coin is ever created", but nothing is created:
  - The seller hands over a crafted item and pays materials to craft another, as with any crafted item.
  - SkyySacks puts no metadata on bags, so the buyer opens their own pool. Nothing of the seller's moves.
  - "Coins can bypass collections early" is locked design, and blocking bags is Skyy's call.
  - What was kept: the buyer-confusion risk is real. Bag ids now get a "contents not included" line on the Create and item views, and open question 15 names the two `blocked.txt` lines that would take them off the market.

**Also fixed while checking:**
- 4.7 pointed at the crash window in "6.6"; it is 6.8.
- An item regrant used to reset to the full stack. That would duplicate earlier partial deliveries, which were saved, so it now owes the last logged delivery's quantity (8.1).
- Every delivery now logs `CLAIM-ITEM`, so regrant always has a line to show (6.3).

---

## Appendix A: bid auctions later, with no data migration

What a later version (0.2 or later) adds, and why 0.1's files already fit:
- **Record:** `type: "AUCTION"`.
  - `startBid` = the opening bid; `price` stays for an optional buy-now price.
  - `topBid` / `topBidder` = the current best bid.
  - `bids[]` entries `{uuid, key, name, amount, at, state: HELD | OUTBID_OWED | REFUNDED | WON}`. Each bid's coins are **taken when the bid is placed** and held in its entry.
  - New state `ENDED` (the time ran out with a winner). The claim flags are reused: the winner's `buyerItem`, the seller's `sellerCoins`. Every outbid entry is its own refund claim (auto-paid when the bidder is online and on that profile, otherwise claimed like any other claim).
  - All of these fields already exist in 0.1 records as defaults (`bids: []`, `topBid: 0`), and 0.1 keeps unknown fields when it rewrites a record.
- **Rules to decide then:**
  - a minimum raise (Hypixel's roughly 2.5% is UNVERIFIED; 5% is a common choice);
  - an anti-snipe extension (a bid in the last 2 minutes resets `endsAt` to now + 2 min);
  - no cancel once a bid exists;
  - a 5% listing fee for auctions (Hypixel, VERIFIED);
  - a winner who cannot pay can never happen, because coins are held at bid time.
- **Transactions:** the same lock and R4 ordering.
  - Placing a bid = take the new bid's coins first, then write the record with the new top bid and the old top bid as `OUTBID_OWED`, then try to refund the old bidder at once if they are online on that profile.
  - The end of an auction is a tick transition like EXPIRE: it never touches an inventory.
- **UI:** a Type filter on Browse (All / BIN / Auction), a bid row on the item view (the current bid, the minimum next bid, a bid TextField), and a "My bids" tab on Manage.
- **What 0.1 must already do (and this spec requires it):** preserve unknown fields, show unknown `type` / `state` values read-only, and never use the record's `price` as a bid.

---

## 14. Build notes (SkyyAuctions 0.1 build, 2026-09-24)

Built as `SkyyAuctions/build_skyyauctions_0.1.py` -> `SkyyAuctions/SkyyAuctions-0.1.jar`. It follows this spec. Where the build differs, here is why:

- **Forced save (R8) uses `Store.copyEntity(ref)`, not `copySerializableEntity(ref)`.** In the bytecode, `Player.saveConfig` reads `MovementStatesComponent` and `UUIDComponent` from the holder. `MovementStatesComponent` has no codec, so a copy of only the serializable components would leave it out and the save would throw. The call is also skipped in worlds that do not save players (`World.isSavingLocked()` or `!WorldConfig.isSavingPlayers()`), the same guard the engine's own save tick uses. It is still UNVERIFIED in game (11.1 #17).
- **Coin claim when `coins:fn:add` throws (-1): the claim stays `CLAIMED` and `PAY-ERROR` is logged.** It is not rolled back. A pay that throws may already have landed, and rolling it back would allow a second payout, which breaks "no coin is ever created" (section 0, R4). If the purse is short, an admin repairs it with `/ahadmin regrant <id> seller`, whose verdict names the `PAY-ERROR`. A refused pay (0) still rolls back exactly as 6.6 says.
- **Reasons and search words are also read from the command's input string** (`/ahadmin remove <id> <reason...>`, `/ah search <words>`). The engine picks a usage variant by the raw token count (`AbstractCommand.checkForExecutingSubcommands`), so a reason of several words would not reach the variant. The root `remove` and `search` therefore allow extra arguments and take the words that follow.
- **Duration labels keep the text from config** (`24h` stays `24h`, it is not rewritten as `1d`), so "Pick one of: 1h 6h 12h 24h 48h" reads the same as the config.
- **Extra log events:** `PAY-ERROR`, `WRITE-RETRY-OK`, `WRITE-RESTORED`, `PAUSE` / `RESUME`. The startup START scan counts `PAY-ERROR` as the end of a coin claim.
- **Review fixes (2026-09-25):**
  - A closed record whose closing write failed now waits in `ARCH` (and `DIRTY`) instead of vanishing from memory, so `/ahadmin info` (which labels it "NOT SAVED YET") and `regrant` still find it. The tick never archives an `ARCH` entry that is still `DIRTY`, because that would move the older file still in `listings/` into `archive/`. An `ARCH` entry whose record is back in `LIVE` (reopened) is dropped, not archived.
  - A crash before the tick's retry landed could reload the older file and let a delivered claim be claimed again. That window is closed by the start-up restore (6.10): `WRITE-FAILED` and `PAY-FAILED` carry the record copy, and `setup()` writes back any copy newer than the loaded file.
  - The regrant evidence and the restore read `auctions.log` plus the 3 newest rotated logs of **any** month, sorted by file time. Before, they read only this month's, so evidence from just before a month boundary was missed.
  - Every `AhCfg` tunable is `volatile`, and `/ahadmin reload` runs inside the one lock (`AhStore.reloadCfg`). A trade therefore sees the whole old or the whole new config, never half of a new duration table.
  - `Coins.get` returns -1 (no answer) when `coins:fn:get` is missing, as the wrapper contract says. Every caller already checked `Coins.ready()` first, so nothing changed for players.
  - The plain-text rolls fallback (`detailTextSpans=false`) lists every numeric key of the `SkyyRolls` document except `reforge`, `quality` and `rolledAt`, which is SkyyRolls' own STATS convention. So a stat that SkyyRolls adds later shows up without an Auction House change.
  - The "Your profile X has N things to claim" line now reads the current name from `profile:list:<uuid>`, as section 9 says. The name stored on the record at trade time is only the fallback (no SkyyProfiles, or a profile that is no longer listed), so a future profile rename cannot leave an old name behind.
  - A second offline harness (scratch, deleted) re-verified all 35 classes under `-Xverify:all`. Its 149 checks pass: a failed closing write, crash and restore with the disk still failing and with it fixed, a partial delivery, a later write that wins, `PAY-FAILED` with an archived copy (renamed, never overwritten), the `ARCH`/`DIRTY` guards, the start scan, the regrant preview's shortened lines, `Coins.get`, the rolls fallback, the profile-name lookup, month-crossing log files, and the volatile fields.
- **Offline harness (scratch, deleted):** all 35 classes load under `-Xverify:all`. 2159 checks pass: parsers and fees, test durations, block list and Bazaar lookups, record clone and JSON, the state machine with fake `coins:fn:*` (buy, claims, cancel, expire, remove, grace, own listing, same account, write failures, refused and throwing pays, notices, START scan, a two-thread race), the regrant guardrails (including the archived and no-overwrite cases), the armed confirm, and the markup of every view (Browse 812, Item 776, Create 840, Manage 774 px of the 852 px content box). **Not covered offline:** anything that needs a live `ItemStack` (the snapshot round trip, LIST removal and put-back, delivery), because `ItemStack` needs the live item asset maps. The partial-removal cases from 10.4 are therefore UNVERIFIED until the in-game test.
