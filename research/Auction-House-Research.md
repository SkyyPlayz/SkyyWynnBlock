# Auction House research

*For Skyy. Written 2026-09-24, for SkyyAuctions 0.1 (BIN-only, bid auctions added later without a data migration).*

Tags: **VERIFIED** = stated consistently across sources found this session. **UNVERIFIED** = only one source said it, or sources disagreed. Everything below is paraphrased in our own words from public wiki/forum content, not copied.

**Source note:** the official wiki at wiki.hypixel.net now redirects to a Hypixel forum thread announcing the wiki was shut down (staff post, dated July 2026 in search results) with no official replacement; Hypixel is pointing players at community wikis instead. For this research I used the two active community mirrors (`hypixelskyblock.minecraft.wiki` and search-result summaries of `hypixel-skyblock.fandom.com`/`hyblock.fandom.com`, which blocked direct fetching but surfaced via search snippets), plus current Hypixel Forums threads. Numbers below are cross-checked across at least two of these where possible; anything not cross-checked is flagged UNVERIFIED.

---

## Hypixel SkyBlock

### 1. Two listing types

| Type | How it works | Tag |
|---|---|---|
| **BIN (Buy It Now)** | Seller sets one fixed price. First buyer to click "Buy Item Now" gets it instantly, no bidding, no waiting. A short grace period (about 20 seconds) right after creation blocks purchases, presumably to stop a seller's own alt or a bot from insta-buying to fake activity | VERIFIED |
| **Normal (bid) auction** | Seller sets a starting bid and a duration. Other players outbid each other; whoever holds the highest bid when time runs out wins and the item is theirs to claim, coins go to the seller. Outbid players get their coins refunded automatically once someone tops their bid | VERIFIED |

Both types share one listing pool, one browse UI, and one per-player/per-co-op active-listing cap (see below) — a BIN is not a separate system, it's a flag on an auction row with `highest_bid_amount == starting_bid == buy_it_now_price` conceptually. That single-table shape is exactly why our data model should add a nullable "current bid / top bidder" side to an otherwise BIN-shaped row later, rather than bolting on a second table.

### 2. Creating a BIN listing (the flow)

1. Open the Auction House menu (see UI note below), choose **Create Auction** (also called "Create BIN" when the BIN toggle is on).
2. Pick the item from a page that shows the player's inventory; clicking an item selects it for listing.
3. Set the price by clicking a gold-bar/price slot, which opens a numeric input (typed amount, sometimes with quick +/- buttons for common increments).
4. Toggle **BIN** on (a lever/dye item in the menu) instead of leaving it as a normal auction.
5. Choose a duration: preset buttons from 1 hour up to a longest preset, with a custom/"other" option for anything in between, up to a hard cap. Sources agree the maximum any auction (BIN or normal) can run is **336 hours (14 days)**; the exact set of preset buttons (candidates seen: 1h/3h/6h/12h/1d/3d/7d) is UNVERIFIED — treat only the 14-day cap as solid.
6. Confirm. The fee (see below) is deducted from the seller's coin purse immediately, on listing creation — not on sale.

Price bounds found: minimum listing price **1 coin**; maximum listing price **50,000,000,000 (50 billion) coins** as a hard ceiling (UNVERIFIED — only one source; treat as a sanity-check number, not a spec to hard-code). There is also a rule that a common/vanilla-tier item's starting price can't be set more than 5x its NPC sell price, presumably to stop using the AH to "sell" junk to yourself or launder coins through a near-guaranteed self-flip (UNVERIFIED, single source).

### 3. Fees (the money side)

Two separate fees on **creation**, plus a tax on **claiming proceeds**. All are paid by the seller.

#### 3a. BIN listing fee (tiered by price)
| Listing price | Fee |
|---|---|
| Under 10,000,000 coins | 1% of price |
| 10,000,000 – 100,000,000 coins | 2% of price |
| Above 100,000,000 coins | 2.5% of price |

VERIFIED — this exact three-tier breakdown showed up consistently across search summaries of the community wiki and a forum "fee optimization" math thread.

#### 3b. Normal-auction listing fee
Flat **5%** of the starting bid, VERIFIED, notably higher than BIN's tiered 1-2.5% — this is presumably Hypixel's way of nudging most casual sellers toward BIN, which fits Skyy's instinct to ship BIN-only first.

#### 3c. Duration fee
An extra flat-ish coin fee stacked on top of the % fee, scaling with how long the listing runs; the only hard number found is a **maximum duration fee of 55,200 coins** at the 14-day cap (UNVERIFIED exact curve — one source only, no confirmed per-hour rate). Treat this as "longer listings cost a bit more up front" rather than a formula to copy exactly.

#### 3d. Claim / collection tax (on the proceeds, when the seller claims coins)
A tax of **up to 1%** is taken off the sale proceeds when the seller claims their coins, but only on sales/BINs **above 1,000,000 coins**, and it's capped so the seller's payout never drops below **1,000,000 coins** net (i.e. the tax can't eat into the first million). One in-game "Mayor" event (a rotating month-long global buff/debuff in SkyBlock, not relevant to us directly) was reported to **quadruple only this collection tax**, leaving the creation/duration fees untouched — worth noting only because it confirms the collection tax is tracked as its own separate number in Hypixel's model, not folded into the listing fee. All of 3d is UNVERIFIED beyond the 1%/1,000,000-floor pairing (single detailed source), but two independent sources agreed a claim-time tax exists separately from the creation fee.

**Design implication for us:** Hypixel's fee model is really two knobs — a creation-time fee (deducted up front, never refunded) and a claim-time tax (deducted from proceeds, only above a floor). Our config/bridge block list is separate from this (item eligibility), but the fee shape (tiered % capped fee on create + small % tax floor on claim) is a reasonable pattern to mirror loosely, tuned to our own coin economy rather than copying Hypixel's exact numbers.

### 4. Limits

- **Max active listings:** base **14** per player, **+3** per additional co-op member on a shared profile, up to **35** total for an 8-player co-op. No rank-based (VIP/MVP) bonus to listing count was found in any source — unlike some other Hypixel systems, AH slots appear to scale by co-op size only, not by purchased rank (UNVERIFIED absence, but consistent — nobody mentioned a rank bonus while several sources gave the co-op numbers precisely).
- **Min price:** 1 coin.
- **Max price:** ~50,000,000,000 coins (UNVERIFIED, see above).
- Listings count against the cap whether they're BIN or normal, and whether or not they've sold/been bid on yet — only claiming or cancelling frees a slot.

### 5. Who can buy / access restrictions

- **Game-mode restrictions:** players on **Ironman**, **Bingo**, and **Stranded** profiles cannot use the Auction House at all (VERIFIED, multiple sources agree). Ironman and Stranded profiles are pushed toward a separate "Special Bazaar" instead; Bingo blocks it as part of a broader trading lockdown (also blocks direct player trading and gifting). This is the closest real-game precedent for the "off the market entirely" bridge block-list Skyy already planned — Hypixel's version is a whole-profile-type gate rather than a per-item gate, but the principle (some profiles/items just don't touch the market) is the same shape.
- **Co-op:** a listing belongs to the co-op profile, not the individual player — any co-op member can create, cancel, or claim any other member's auction/BIN (this is the same "shared everything" model already used for the shared Bazaar orders on a co-op profile). This is a real scam/trust risk Hypixel accepts; worth flagging to Skyy as a design question for SkyyProfiles' co-op story later, not something to solve in 0.1.
- **Can't buy your own listing:** widely assumed/expected by players, but no source gave a citable line confirming a hard server-side block distinct from the 20-second grace period. Flag as UNVERIFIED — for SkyyAuctions we should decide this ourselves rather than copy an unconfirmed rule (a same-profile self-buy block is easy to add and closes an obvious self-laundering exploit either way).

### 6. What happens on sale, expiry, and cancel

- **On BIN sale:** the item transfers to the buyer's claimable items immediately; the buyer does not need to do anything further to receive the item beyond the purchase confirm click. The **seller does not get paid automatically** — coins sit as a claimable balance that the seller must actively collect from the Manage Auctions / claim screen (a "Claim" or "Claim All" button). There is no proactive auto-deposit into the seller's purse; multiple sources describe players getting confused and asking how to claim, which confirms this is a manual step, not automatic. (A "Claim All" tooltip warns the player with something like "that's a lot of coins!" once the pending claim total passes 100,000 coins — a nice, cheap anti-fat-finger nudge worth borrowing conceptually.)
- **On expiry (normal auction, nobody won a BIN):** if a BIN never sold, or a normal auction's timer ran out, the **item** goes back to the seller as a claimable item (not requeued automatically). If a normal auction did get bid on and expired with a winner, the **winner claims the item** and the **seller claims the coins** — both are separate manual claim actions, both are pulled from the same Manage Auctions/claim screen.
- **On cancel:** an auction/BIN can be cancelled at any time before it sells or (for normal auctions) before anyone has bid on it — once a bid exists, it appears you can no longer freely cancel out from under a bidder. Cancelling returns the **item** to the seller. **The creation fee is NOT refunded on cancel** (VERIFIED, multiple sources) — this is a real money sink Hypixel uses to discourage relisting spam / price-fishing, worth mirroring in our config even at 0.1 (cancel returns the item, keeps the fee).
- **Bids specifically:** a losing bidder is refunded automatically as soon as they're outbid — they do not have to manually claim a refund, only the *winning* claim (coins for seller, item for winner) is a manual step. A bidder cannot cancel their own bid once placed; the only way out is getting outbid or waiting out the auction. (This whole section is the "BID auction" data-model note for later — see section 14.)

### 7. Browse UI

- **Categories:** Weapons, Armor, Accessories, Consumables, Blocks, Tools & Misc — this matches almost exactly the six buckets already named in the task brief, so Hypixel's own grouping is a safe default to imitate.
- **Sort options:** reported inconsistently across sources — one gave "Highest Bid / Lowest Bid / Ending Soon / Most Bids", the brief's own framing said "highest price / lowest price / ending soon / random." Treat the exact fourth option (random vs most-bids) as UNVERIFIED; "highest price," "lowest price," and "ending soon" are the three that show up everywhere and are the safe minimum to build.
- **BIN filter:** a three-way toggle — show everything, BIN-only, or auctions-only (icon-based toggle in the menu, e.g. a rail/ingot icon pair). For our BIN-only 0.1, this collapses to nothing (everything is BIN), but the config should leave room for the toggle once bid auctions exist.
- **Rarity filter:** a checklist covering all item rarity tiers (Common through the top special tiers). Not relevant to us yet since SkyyGear (rarities) isn't built — matches the brief's instruction not to build any of it. Our 0.1 browse screen should simply skip a rarity filter until a rarity system exists.
- **Search:** a text-entry item (styled as a sign) opens a name search, filtering the current category/tab by substring match against item display name.
- **Pagination:** results are paged (the underlying API itself is paginated, ~1000 auctions/page), and the in-game UI pages through results a screen at a time with next/previous buttons — a standard inventory-GUI pagination pattern, nothing exotic.

### 8. Item view / buy confirmation page

Clicking a listing opens a detail view showing: seller name, price (or current bid + minimum next bid for normal auctions), time remaining, and the item itself with its full tooltip (so enchants/reforges/stats are visible before buying — directly relevant to us, since our rolled items and graded dishes carry metadata that must show correctly here). Buying requires a second click on a confirm control — it's a two-step "click to view, click again to confirm" flow rather than a single-click purchase, which is a cheap, real anti-misclick safeguard we should keep for SkyyAuctions BIN purchases (open page -> confirm buy -> page rebuilds/closes), fitting naturally with the project's existing "rebuild only on click, never auto" UI rule.

### 9. Manage Auctions & View Bids pages

- **Manage Auctions:** lists everything the player (or their co-op) currently has listed, whether pending, sold, or expired, with claim buttons per item/coin payout and a "Claim All" for everything at once. If the player has zero active listings, this button is replaced in the main menu by a direct "Create Auction" shortcut — a small UX nicety (don't show an empty management screen, show the action that's actually useful).
- **View Bids:** lists auctions the player has bid on, so they can track whether they're winning/losing and claim items they've won or coins from an outbid refund if it somehow wasn't auto-returned. This page is pure "BID auction" territory — not needed for our BIN-only 0.1, but its existence tells us our later data model needs a `bids` side-table keyed by bidder, independent from the main listing row (see section 14).

### 10. Anti-scam / anti-manipulation notes

Hypixel's Auction House itself has very few built-in guardrails beyond the ones already covered (grace period, two-step buy confirm, fee-not-refunded-on-cancel, claim-tax floor). Most "anti-scam" material found was player-education (check lowest BIN before buying, use search to verify a seller's claim before bidding on their say-so, screenshot everything) rather than server-enforced. No confirmed source described a hard "confirm again if price is way above market" warning, per-item cooldowns, or a coin-earned cap tied specifically to the AH — those all appear to be community-guide advice, not engine features. **Takeaway for us:** don't over-build anti-scam tooling into 0.1 beyond the two real, confirmed mechanics (grace period + two-step confirm) — Hypixel itself leans on UI friction and player education, not automated fraud detection, for this particular system.

### 11. Interaction with the Bazaar

An item is sellable on the Bazaar **or** the Auction House, not both — Bazaar handles fungible, stackable commodities traded via buy/sell orders at a moving market price, while the Auction House handles one-off, often-modified items (gear with reforges/enchants, pets, unique drops) sold individually. This lines up exactly with Skyy's SkyyBazaar/SkyyAuctions split and with the shared config/bridge block-list idea already locked for SkyyAuctions — the same empty-by-default block list should logically apply to both systems so a late-game item can be pulled off Bazaar and Auction House together with one entry, not two separate lists to keep in sync.

### 12. Co-op / profile rules

Already covered in section 5: listings, claims, and cancellations on a co-op profile are shared across all members with no per-member ownership lock — any member can act on any other member's listing. This is consistent with the project's locked design that bank/coins/skills are per-profile (`pkey(uuid)`): Hypixel's AH data is likewise profile-scoped, not account-scoped, which matches how SkyyAuctions should key its listings (per profile, not per player uuid alone).

### 13. API / price history

The official Hypixel API exposes a paginated `/skyblock/auctions` (and newer `/v2/skyblock/auctions`) endpoint listing all currently-active auctions across the whole game, including a `bin` flag distinguishing BIN from normal listings; there is no first-party historical-price endpoint. Third-party sites (Coflnet and others) poll this endpoint continuously and build their own price-history databases and "lowest BIN" lookups on top of it — that history is a community add-on, not something Hypixel stores itself. Not directly relevant to a single-server mod (we have no cross-server API to expose), but worth noting: if Skyy ever wants a "lowest active BIN for this item" price-check command, that's a live query over our own active-listings table, not a stored history — the same shape as Hypixel's own approach.

### 14. What a BID (normal) auction needs — for later, without a migration

So the 0.1 data model can add this cleanly later, a normal/bid auction needs, on top of everything a BIN row already has:

- A **starting bid** (separate concept from "buy it now price" — for 0.1 these can just be the same field, since BIN has no separate starting bid).
- A **current top bid amount** and **current top bidder** (nullable — no bids yet is a valid state).
- A **minimum next-bid rule**: Hypixel requires each new bid to beat the previous by at least ~2.5% (UNVERIFIED exact percentage, single source, but the *shape* — "must beat by some increment, not just any higher amount" — is worth keeping even if we pick our own number).
- A **bid history / refund side-table** keyed by (auction id, bidder), so an outbid player's coins can be auto-refunded without touching the main listing row — this is exactly the extra table the View Bids page implies.
- A **timer-extension rule**: a bid placed inside the last stretch of an auction (Hypixel uses 2 minutes) resets the remaining time back up to that stretch, to stop last-second snipe-bidding. Worth designing for even at the schema level (a `last_bid_at`/`ends_at` pair that a bid handler can bump) even though 0.1 has no bids yet.
- A **won-but-unclaimed item** state distinct from "sold BIN, unclaimed" only in that the *winner* claims the item and the *seller* claims the coins as two separate actions — our BIN claim path already needs "seller claims coins, buyer already has item" so this mostly reuses that shape; the new part is just that the buyer side isn't resolved until the auction *ends*, not at purchase time.

None of this needs building now — it's here so the SkyyAuctions 0.1 schema (row per listing, nullable bid-related columns, empty for BIN) doesn't need a destructive migration when bid auctions are added.

---

### Numbers at a glance

| Fact | Value | Confidence |
|---|---|---|
| BIN listing fee, price < 10M | 1% | VERIFIED |
| BIN listing fee, 10M-100M | 2% | VERIFIED |
| BIN listing fee, price > 100M | 2.5% | VERIFIED |
| Normal-auction listing fee | flat 5% | VERIFIED |
| Max duration fee (14-day) | 55,200 coins | UNVERIFIED (single source) |
| Claim/collection tax | up to 1%, only above 1,000,000 coins, floor of 1,000,000 net | UNVERIFIED (single detailed source, but concept cross-checked) |
| Max auction/BIN duration | 336 hours (14 days) | VERIFIED |
| Min listing price | 1 coin | VERIFIED |
| Max listing price | ~50,000,000,000 coins | UNVERIFIED (single source) |
| Max active listings, solo | 14 | VERIFIED |
| Max active listings, per extra co-op member | +3 | VERIFIED |
| Max active listings, 8-player co-op | 35 | VERIFIED |
| BIN purchase grace period | ~20 seconds | VERIFIED |
| Min bid increment (normal auctions) | ~2.5% over current top bid | UNVERIFIED (single source) |
| Last-minute timer extension (normal auctions) | resets remaining time to 2 minutes | UNVERIFIED (single source) |
| Claim-all "lot of coins" nudge threshold | 100,000 coins | UNVERIFIED (single source) |
| Gamemodes blocked from Auction House | Ironman, Bingo, Stranded | VERIFIED |
| Cancel refunds the creation fee? | No — fee is kept, item is returned | VERIFIED |

---

## Server plugins (Hytale and Minecraft), and our own installed mods

*Added 2026-09-24 by the spec pass from the parallel research agent's report (its section was not in this file when the spec was written). Ideas only, summarised in our own words; no plugin code or text was copied.*

**Installed mods (read-only scan of `UserData\Mods`):** no auction, market or shop mod is installed. SkyyBazaar is the only economy mod, so there is nothing local to mirror.

**Hytale plugins on CurseForge with an auction or market feature:** Auction, Auctions, Conquest Auction House, HyMarketPlus, Shops, Better Shop/AuctionHouse, "Auction House", TradeMarket, EcotaleMarketplace. Two claims are worth noting: Conquest Auction House advertises that durability, enchantments and custom data survive a listing, so metadata loss is a known problem in this ecosystem. EcotaleMarketplace advertises that a buy with a full inventory fails safely without losing coins.

**Minecraft (Bukkit-era) auction plugins** (zAuctionHouse, AuctionHouse by klugemonkey, CrazyAuctions, AuctionMaster, PlayerAuctions) share one shape:
- a paged browse list or grid with category tabs, a name/seller search and price / newest / ending-soon sorting;
- an item view with a confirm-buy step;
- selling = pick an item from a custom picker (not the vanilla inventory screen), set the price, see the fee, confirm;
- a "my listings" page with a cancel button per row;
- a personal claim box that holds sale proceeds, expired items and cancelled items instead of pushing them into a live inventory.

**Common config knobs:** fee or tax (flat and/or percent, sometimes by rank), listing duration, max listings per player (often by permission), min/max price, an item blacklist, a sales log, admin remove-and-refund, offline sale notices (usually through the claim box), and listing or purchase cooldowns.

**Dupe and exploit patterns, and the usual fix:** double buy (two players, one listing), buy with a full inventory, cancel racing a buy, a crash mid-trade, lost item metadata, relogging during a purchase, and two players looking at the same stale page. The fixes come down to two ideas:
1. "Check the listing, take the coins, hand over the item, close the listing" runs as one locked step that re-checks everything on the server at click time. It never trusts what the page showed.
2. Anything owed goes to a persistent claim box. That also covers a full inventory, a crash and a relog.

Metadata loss is fixed by storing the full item data with the listing instead of just an id and a count.
