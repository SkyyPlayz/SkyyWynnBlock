# SkyyBazaar 0.2 - the order book (build-ready spec)

Status: DRAFT for Skyy's answers (section 11). Written 2026-10-20 from SkyyBazaar 0.1.22 (`SkyyBazaar/build_skyybazaar_0.1.22.py`, GENERATED; its
docstring "PLANNED 0.2" is the starting design), `tools/bazaar_0_1_11_patch.py` (the closeall / wouldclose KEY CONTRACT), `tools/auctions_0_1_5_patch.py`
+ `SkyyAuctions` 0.1.11-0.1.14 (the escrow / claim / closeall pattern to copy), `SkyyRebirth/build_skyyrebirth_0.3.6.py` (RbCheck = the caller),
`research/cloud/Rebirth-Spec.md` 2.4 / 4.3, `docs/answered/economy.md`. Why now: RESUME "Bazaar 0.2 must implement closeall + wouldclose for real"
(docs/log 2026-10-19: 0.1.22 answers `ok:0` / `ok:0:0:0:0` because it has no orders).

## 1. What it is, in one paragraph
Today (0.1.x) every trade is INSTANT against one server market maker (MM): buy at B, sell at S (B > S, spread 10 %, demand factor moves both).
0.2 adds a player book on top: a BUY ORDER (bid) and a SELL OFFER (ask) per product. Orders rest between S and B, are filled only by other
players' INSTANT buys / sells (Hypixel style), and are held in ESCROW (coins for bids, items for asks). The MM stays as the fallback for
everything the book cannot fill, so the whole 0.1 price model, loop checks and migrations stay exactly as they are.

## 2. Locked rules to follow (docs/answered/economy.md) - nothing here may break them
- "if it goes in the bag, it goes in a matching section in the bizzar" (2026-10-03): orders use the same product list / tabs; bag items are sold into offers
  through the SAME sacks bridge as 0.1.5 (`sacks:fn:take/put`).
- COINS NEVER SKIP COLLECTIONS OR BAGS (R3): orders can buy items you have not unlocked, never tiers / recipes / bags. Magic Bags (`Skyy_Sack_*`) refused (0.1.5).
- Mythic / UT / Sets are walled from Bazaar + AH (2026-10-08) and `market:veto` stamped gear is refused: same checks as sell0. Bazaar items stay refused on the AH.
- Rebirth Q9 (2026-10-13): rebirth needs no open Bazaar orders; "Continue" auto-closes all (refund items + coins). Q15: buying goods with coins before a
  rebirth stays allowed. 2026-10-16 "BAZAAR + REBIRTH": no extra Bazaar refusal while a rebirth runs - EXCEPT that order creation / claim pause on `rebirth:busy`
  (same as the AH), because escrow must not move mid-transaction. Instant trades keep 0.1 behaviour (coins mod refuses spends).
- 2026-10-15 CONFIRM button + threshold: the armed button becomes CONFIRM; under the Server Setup threshold (default 3,000) the first click works.
  Order creation / instant trades through the book use the same flow (the armed total includes book fills).
- 2026-10-16 sort by tier everywhere (tools/tier_tags.py, then name); Farming order crop / Enchanted / seeds / Eternal; price floor (cheapest instant sell 2).
- Eternal-flame coin loop accepted ("Leave it"); no new money loops: see section 6 (book trades are player-to-player, zero-sum minus tax).
- Server Setup for every number; times in seconds. Pack mods: only by item id at runtime, no overriding.

## 3. Money model (why no money loop can open)
- Bid price p and ask price q are WHOLE coins per unit, with `S < p < B` and `S < q < B` at placement (S, B = MM instant sell / buy right now, `Catalog`).
  A product whose B - S < 2 whole coins has "no room" (cheap items): the order buttons show "Use Buy / Sell - too cheap for orders". (Tenth-coin prices: Q3.)
- The book NEVER crosses: a bid must be below the best ask, an ask above the best bid (else "an offer is already at that price - use Buy / Sell"). So orders never
  match each other; they are only hit by INSTANT actions, at the RESTING order's own price. Escrow is therefore exact: no refund of price difference, no rounding.
- MM legs are exactly 0.1 (cost / pay from `Catalog` + demand-factor step by real MM units only). Order fills do NOT move the demand factor (Q4; stops free price
  manipulation by trading with yourself). Coins only change hands player-to-player on a fill, minus TAX (the only new sink, section 7).
- Self-trade: an instant action skips resting orders of the same pkey AND of any other profile of the same UUID (no item / coin shuttle between your own profiles).
- Invariant tested at build and in the harness (section 10): total coins (purses + bid escrow + claims) + tax burned is constant over any trade sequence; total
  items (inventories + bags + ask escrow + claims) is constant. A stale resting order (the MM price drifted past it) just trades at a worse price for its owner;
  it cannot make coins.

## 4. Saved data (all under `Skyy_SkyyBazaar/`, atomic tmp + move, written under the Market lock)
| File | Content | Notes |
|---|---|---|
| `book.properties` | one line per ORDER and per CLAIM (one file = one atomic write per mutation, so a fill + its settlements can never half-apply) | ~100 KB at 100 players x 14; shard per product only if > 5,000 lines (not in 0.2) |
| `journal.log` | append-only intent / commit lines (write-ahead for external effects) | replayed at start; trimmed when all committed |
| `orders.properties` | Server Setup config (section 8), written with defaults when missing | kit file, hand edits checked like other kit files |
| `history/<itemId>.csv` | hourly OHLCV (round R3) | appended by the 10 s tick, pruned at `history.keepSeconds` |

Order line: `o.<id>=<uuid>|<pkey>|<BID or ASK>|<itemId>|<price>|<qty>|<filled>|<createdMillis>|<expiresMillis>|<status>`; status OPEN / DONE / CANCELLED / EXPIRED.
Claim line: `c.<id>=<uuid>|<pkey>|<COINS or ITEMS>|<itemId or ->|<amount>|<fromOrderId or txid>|<createdMillis>|<status>`; status OPEN / CLAIMED. Ids = base36 time + counter
(unique, monotonic = time priority; ties by id). Claim cap 200 per pkey (older DONE rows pruned after 30 days; OPEN rows are never pruned).
Owner = the profile key (`profile:fn:key`, else `uuid.toString()`), per PROFILES-CONTRACT; the order stays on the profile it was placed on, the uuid is kept so
coins / items can be paid when that player is online on that profile.

## 5. Operations (every external effect is write-ahead journalled; "intent" before, "commit" after)
1. PLACE BID: checks (enabled, not `profile:busy` / `rebirth:busy`, open < `orders.maxOpen`, price in range + book not crossed, qty 1..`maxQty`, total <= 1e15, coins bridge
   present) -> journal INTENT-BID -> `coins:fn:take(uuid, qty x p)` (refused = stop, nothing written) -> add order line + atomic write -> journal COMMIT.
   Replay: INTENT without COMMIT and no order id in the book = coins were maybe taken -> a COINS claim for the amount (so a crash never loses coins; a take that
   failed shows a claim of coins that were never taken: avoided by journalling the take RESULT line `TAKEN id` right after the bridge answers true; replay refunds only
   when `TAKEN` exists).
2. PLACE ASK: same checks + item rules (plain ids only, no metadata / `market:veto` / Mythic / UT / Sets / Magic Bags) -> INTENT-ASK -> remove the items with the 0.1
   count-verified slot removal (inventory first, then bags via `sacks:fn:take`, remembering the bag part) -> journal `REMOVED id <n>` -> order line + write -> COMMIT.
   Replay: INTENT + REMOVED, no order -> an ITEMS claim for the removed amount. A removal short of qty places the order for what really left.
3. CANCEL / EXPIRE: under the lock, one atomic write: order -> CANCELLED / EXPIRED and the UNFILLED remainder becomes ONE claim row (COINS = rest x price for bids,
   ITEMS = rest for asks). Nothing external happens, so it cannot fail halfway. The 10 s tick expires orders past `expiresMillis` (default 7 days).
4. INSTANT BUY of N (taker pays): quote walks asks cheapest first (time priority; own-UUID orders skipped) for k units, remaining N - k from the MM. Book leg: journal
   INTENT-TAKE txid -> `coins:fn:take(k-leg cost)` -> journal `TAKEN txid` -> ONE atomic write: asks filled (`filled` += units, DONE when full), a COINS claim per ask owner
   (units x q minus tax, tax logged), and an ITEMS claim for the taker (OPEN) -> COMMIT -> the taker's ITEMS claim is delivered at once (rule 6). MM leg afterwards via the
   unchanged 0.1 `buy0`. If the book write throws after the coins were taken, replay (or the same call's catch) pays the coins back as a COINS claim and nothing is filled.
5. INSTANT SELL of N (taker sells): walks bids highest first for k units, the rest to the MM. Book leg: INTENT-TAKE -> remove the k items (count-verified, inventory then
   bags) -> `REMOVED txid n` -> ONE atomic write: bids filled, an ITEMS claim per bid owner, a COINS claim for the taker (gross - tax) -> COMMIT -> pay the taker's COINS claim at
   once. MM leg via `sell0`. Replay: INTENT + REMOVED without a fill in the book = ITEMS claim back to the seller.
6. CLAIM (a row, or CLAIM ALL): refuse on `profile:busy`/`rebirth:busy`, owner not online on that profile (rows show "log in on that profile"). Mark CLAIMED + atomic write FIRST, then
   pay (`coins:fn:add`; items: vanilla storage-first add, measured per container, `new ItemStack(id, qty)` only - never a metadata stack into an ItemGridSlot). A failed or short pay writes
   the unpaid rest back as a new OPEN row (never reported as done; trades.log `CLAIM-FAILED`). A crash between mark and pay loses at most that one claim (logged `CLAIM id` first; same
   at-most-once rule as the AH). Items that do not fit stay in the row; nothing is ever dropped.
7. Admin (permission `skyybazaar.admin`, each subcommand `setPermissionGroups(new String[0])`): `/bazaaradmin book` (counts), `book orders <player>`, `book cancel <orderId>` (as 3),
   `book check` (escrow = orders + claims reconciliation; the rollback gate, section 9). The Bazaar admin NEVER edits the book by hand.
8. Every operation appends one trades.log line (ORDER-BID / ORDER-ASK / FILL / CANCEL / EXPIRE / CLAIM / TAX / CLOSEALL) like the 0.1 lines; failures are WARN lines.

## 6. The bridge contract SkyyRebirth calls (keeps 0.1.11's keys; java.lang types only on `skyy.bridge`)
Both are `java.util.function.Function`, `apply(Object)`; the argument is the profile key String (`profile:fn:key(uuid)` or `uuid.toString()`); never throw, never call another mod back,
any thread (the book is under the Market lock; no world-thread need). Published at plugin setup, removed at shutdown. Rebirth reads them in `RbCheck.ask/head/detail/market/marketClear/closeAll/closed`.

`bazaar:fn:wouldclose` - READ-ONLY, writes nothing:
- null / empty / non-String / not a valid key -> `err:bad-key`. A broken book -> `err:book`.
- line 1 `ok:<closable>:<blocking>:<claims>:<coins>` - exactly four non-negative longs (RbCheck.head needs 5 fields):
  - closable = OPEN orders of the key + COINS claims auto-claim can pay (see closeall rule A) - what Continue would do now;
  - blocking = OPEN orders `closeall` cannot touch now: only an order inside an unfinished journal step (INTENT without COMMIT, i.e. mid-placement); 0 normally;
  - claims = ALL OPEN claim rows of the key (information; ITEMS claims never block, they are kept through a rebirth, as the AH);
  - coins = the SUM of OPEN COINS claim amounts (information).
- then one line per open order / claim, tab separated (`RbCheck.detail` reads fields 1, 2, 3, 5; needs >= 6 fields): `<id>\t<kind>\t<qty>\t<price or coins>\t<createdMillis>\t<item display name>`;
  kind 1 = closable order (qty = unfilled remainder, field 4 = unit price), kind 0 = blocking order, kind 2 = COINS claim that CANNOT be auto-paid (blocks; Rebirth shows "claim your <coins>
  coins first"), kind 3 = COINS claim closeall pays into the purse first (qty 1, field 4 = coins; Rebirth 0.3.6 ignores kind 3 in the list but counts it in closable).
- SkyyRebirth continues only when the re-read after closeall is `ok:0:0:...` (its `marketClear` requires closable + blocking = 0 for both markets).

`bazaar:fn:closeall` - the real thing, IDEMPOTENT, crash-safe:
- bad key -> `err:bad-key`; bridge/coins missing while COINS claims exist -> `err:blocked:<n>:<b>` and NOTHING is closed (a rebirth that cannot go on never costs orders - AH 0.1.5 FIX 2 rule).
- Rule A (copied from the AH 0.1.11 decision, Q2 below): OPEN COINS claims of the key are paid INTO THE PURSE first (oldest first, each through the claim step 6, CLAIMED written before
  `coins:fn:add`), requires the coin owner online on that profile; otherwise `err:blocked:0:<b>`. The purse then resets with the rebirth.
- Then ONE atomic write cancels every OPEN order of the key (status CANCELLED, remainder -> ONE claim row each: bids' refund as a COINS claim, asks' refund as an ITEMS claim). A bid refund is
  itself a COINS claim, so closeall's second pass pays it into the purse the same call (unfilled bid escrow returns to the player, then the reset takes it like any purse coin - Skyy's
  words: "refund items + coins"). ITEMS claims stay in `/bazaar` > MY ORDERS, kept through a rebirth (no auto-delivery, unlike the 15 s AH queue).
- Answer `ok:<n>` with n = orders cancelled + coin claims paid by THIS call (0 on a repeat call: idempotent). `err:busy` if a journal step of the key is in flight (Rebirth retries);
  `err:store` if the atomic write failed (nothing changed); `err:exception` on anything else (logged WARN).
- One `CLOSEALL key=<k> closed=<n> paid=<m>` line in trades.log; the online owner gets one chat line.
- `/bazaaradmin book closeall <player or key> [confirm]` previews / runs the same (the Rebirth patch has one for the AH too).
Tests: both keys present after setup, gone after shutdown; wouldclose before == closeall work done == wouldclose after = `ok:0:0:<claims>:<coins>` with claims counting only the ITEMS rows.

Other new bridge keys (Long / Integer / String only): `bazaar:bid:<itemId>` / `bazaar:ask:<itemId>` best resting prices (absent = none), `bazaar:orders:<uuid>` open count, `bazaar:claims:<uuid>` open
claim count (join notice for other mods). Existing `bazaar:buy:<id>` / `bazaar:sell:<id>` / `bazaar:products` stay the MM prices (other mods price by them) - unchanged.

## 7. Tax, limits, history
- TAX `orders.taxPct` default 1.25 (Hypixel; design doc): taken from the SELLER's proceeds whenever the buyer is a player order (ask filled, or instant sell into a bid). MM sales untaxed.
  tax = floor(gross x pct / 100) per fill, logged, destroyed (coin sink; counts in the "Even mix" coin-sink goal 2026-10-18). Min order total `orders.minTotal` default 10 coins.
- Limits (Server Setup): open orders per profile 14, order life 604,800 s (7 days), max qty per order 100,000 and total <= 1e15, price range as section 3.
- Price history (round R3): hourly OHLC + volume per product from MM and book trades; a "Price history" panel (last 24 hourly closes, 24 h low / high / average, 7-day average) in the product
  detail; no chart widget until the kit has one (Style Guide). File pruned to `history.keepSeconds` (default 2,592,000 = 30 days).

## 8. Menu (research/Menu-Pattern.md; Market hub, no back button, top bars always there)
- Page stays inside Market > Bazaar at the hub size (M2: 1600 x 980; 0.1.18 ships ~1094 wide - the sweep decides, do not invent a size). Row 2 [BAZAAR][AUCTION HOUSE] switch unchanged.
- Category tab strip gets ONE new tab at the end: MY ORDERS (shows the open count as a badge). No pager: lists are scroll lists (M5). Sorted by tier then name (tools/tier_tags.py).
- Product detail (right panel): the 0.1 BUY / SELL buttons (BUY STACK / SELL STACK, custom amount, CONFIRM flow) now say the blended price when book units are included ("12 from offers, 38 from
  market"); new row under them: [BUY ORDER] [SELL OFFER] opening an in-page editor (no new window): qty steppers (-stack -10 -1 +1 +10 +stack, plus the custom-amount field), price steppers
  (-10 -1 +1 +10, BEST+1 / BEST-1 (undercut), MARKET), total + tax preview, one CONFIRM per the threshold rule. A depth strip lists the best 5 bids and 5 asks (price x qty).
- MY ORDERS tab: section "Open orders" (rows: side colour-coded per Style Guide 15, item icon via `new ItemStack(id, qty)`, filled / qty, price, expires in s, [CANCEL]) then section "To claim"
  (rows [CLAIM], header [CLAIM ALL]). Orders of other profiles: one summary line "N orders on other profiles". Search box reuses the 0.1.6 field.
- Tooltips / flavour: colour-coded (bid green, ask amber, tax red) per Style Guide section 15; tier tag first for tiered items.
- Commands: `/bazaar orders` (and `/bz orders`) opens the tab; `/bazaar claim`; each with `setPermissionGroups(new String[] { "hytale:Adventurer" })`. Join notice: "N Bazaar claims waiting".
- No periodic page updates (HANDOFF section 2): the page redraws on a click only; the claim count refreshes on open.

## 9. Server Setup rows (tools/CONFIG-CONTRACT.md; Server Setup > Bazaar > "Order book", file `orders.properties`, kit `emit(... KEEP=10)`)
| Row | Type | Default | Live? |
|---|---|---|---|
| `orders.enabled` | switch | ON (no dev gates: finished features default ON) | live |
| `orders.maxOpen` | int 1-50 | 14 | live |
| `orders.expireSeconds` | seconds 3,600-2,592,000 | 604,800 | live (affects new orders; running ones keep theirs) |
| `orders.taxPct` | decimal 0-10 | 1.25 | live |
| `orders.minTotal` | coins | 10 | live |
| `orders.maxQty` | int | 100,000 | live |
| `orders.factorMove` | switch | OFF | live (Q4) |
| `orders.rebirthPayCoins` | switch | ON (closeall pays coin claims into the purse) | live (Q2) |
| `history.keepSeconds` | seconds | 2,592,000 | live (R3) |
Switching `orders.enabled` OFF stops NEW orders only; cancel / claim / closeall / expiry keep working (escrow can always be reclaimed).

## 10. Build, migration, rounds
- Derive from the CURRENT pin: `tools/bazaar_0_2_patch.py` reads `SkyyBazaar/build_skyybazaar_0.1.22.py` (or the newest pin) and writes `build_skyybazaar_0.2.py` (never edit the generated file). No lambdas
  / enhanced-for / inner classes / generics (AGENT-BRIEF). New classes: `BzBook` (store + lock + journal), `BzOrders` (place / cancel / expire), `BzFill` (walk + settle), `BzClaim`, `BzOrdPage` (tab),
  `BzOrdCfg`; `BzRebirthFn` is REPLACED (same class name, real bodies); `Trader.buy0 / sell0` call `BzFill` first, then their old MM path. Version texts in CfgFn / CfgRows.
- SAVED-DATA MIGRATION (PROJECT-RULES 4): 0.2 changes NO existing line. First start: create empty `book.properties` + `orders.properties` (defaults; a hand-made file kept byte for byte), one
  `MIGRATE-0.2` trades.log line with its undo, marker `migrated.0.2` in pricing.properties (run-once). products / pricing / market files keep bytes and line endings. No History snapshot needed (nothing rewritten),
  but take the verified snapshot anyway before the first start (cheap).
- ROLLBACK FLOOR (add to `tools/deploy_set.py` + HANDOFF): rolling back to 0.1.x is safe ONLY when `book.properties` has no OPEN order and no OPEN claim (`/bazaaradmin book check`), because 0.1.x ignores the book and
  its `bazaar:fn:closeall` would answer `ok:0` over stranded escrow. Before a rollback: `/bazaaradmin book cancelall confirm` then every player claims, or an admin runs the check.
- Build checks: the 0.1 loop scan unchanged and green; plus a conservation fuzz (random place / cancel / instant buy / sell / expire / claim / closeall sequences, fixed seed, 10,000 steps; coins + tax and
  items constant); crash injection at EVERY journal step (`CRASH_AT` like AhStore) then restart + replay: nothing lost, nothing duplicated; a fake coins bridge that refuses / throws; metadata and
  walled items refused; profile switch and `rebirth:busy` refusals; closeall idempotent; the exact answer shapes of section 6 parsed by SkyyRebirth's own `RbCheck.head/detail/closed` copy.
- Smoke test (`python tools/smoke_test.py`) must show `[SkyyBazaar] 0.2 ready` and no SEVERE; then `skywynn-deploy`. After the round: refresh the Class Balance Workbench only if coin numbers moved (tax does not).
- Rounds (split because it is large; deploy only after R2, as ONE jar):
  - R1 STORE + ESCROW + CLOSEALL (full round, ultracode lens set: money, dupe, crash, permissions): book / journal / replay, place bid / ask, cancel, expire, claim, MY ORDERS tab (place + cancel + claim),
    REAL closeall / wouldclose, config rows, limits, admin `book`. Instant trades unchanged. (Satisfies the RESUME item; orders exist but nothing fills yet.)
  - R2 MATCHING + TAX: instant buy / sell walk the book, settlement claims, tax, blended-price quote + CONFIRM cap, depth strip, bridge keys bid / ask / orders / claims, fuzz + crash tests for fills.
  - R3 HISTORY + POLISH (lean): hourly OHLC files + panel, join notice, Style Guide tooltips, admin `book orders`. Needs no new escrow code.
  Cross-check (`python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py` 0 fails); SkyyRebirth needs NO change (contract kept) - only its "0.1.11+" texts may say "0.2".

## 11. Existing-mods survey (PROJECT-RULES 2; shallow - web search only, no pages opened, licences UNCHECKED)
- Skyy's Mods folder (read-only listing): only our `SkyyBazaar.jar` and `SkyyAuctions.jar` match; no other bazaar / market / order-book mod installed.
- CurseForge / web search 2026-10-20: no Hytale mod found with a price-sorted buy-order / sell-offer book (the Hypixel "Bazaar Utils" / "btrbz" hits are Minecraft client mods). Closest:
  Yet Another Shop (player shops WITH buy orders: sold items go to the owner's storage, unused budget refunded when an order is removed or changed, per-player transaction / daily / weekly limits);
  Better Shop-Auction (shop + auction + "Offer House" on one economy, auto-detects economy plugins); BuiltByBit "Hytale Shop | Bazaar - Black Market" (paid, not CurseForge).
- Verdict: nothing to pack or fold - none fits a market-maker-plus-book design, and all want their own economy. LEARN (idea only, nothing copied): refund the unused budget exactly on cancel (our
  remainder claim), per-player limits as Server Setup rows (maxOpen, minTotal, maxQty), items to storage not the floor. Hypixel: "BEST+1" undercut button, 5-deep order depth, taxed sellers.
  Re-run a CurseForge page check (licence + class names) before R1 if Skyy wants to be sure; use the `skywynn-mod-check` skill on any candidate Skyy names.

## 12. Questions for Skyy (each with the recommended default)
1. Ship the order book at all in the next round, or only closeall / wouldclose (R1)? [R1 + R2 together as 0.2.0; R3 later]
2. Rebirth Continue and COIN refunds: pay unfilled bid money and sold-offer coins INTO THE PURSE (then the purse reset takes them, like AH sale coins) - or keep them in Bazaar claims across the rebirth
   (a way to carry coins through a reset)? [Pay into the purse first, same as the AH; items stay claimable]
3. Cheap items (B - S < 2 coins, e.g. most T1 materials) get no orders; or allow tenth-coin prices (more rounding code, more risk)? [No orders for cheap items in 0.2; tenths only if you ask]
4. Should order fills move the MM demand factor like instant trades? [No - fills are player-to-player; prevents self-trading to move prices]
5. Tax 1.25 % on the seller when the buyer is a player order, 0 % on market-maker sales. OK? [Yes, 1.25 %]
6. Order life 7 days, 14 open orders per profile, minimum total 10 coins. OK? [Yes; all editable in Server Setup]
7. Fills for an online owner: claim by button only, or auto-pay when online on that profile (needs a pay-at-most-once tick like the AH)? [Button + join notice in 0.2.0; auto-pay later]
8. Should the Hub item (Market) show the Bazaar claim count badge on Home? [Yes, a number on the MY ORDERS tab only; Home badge later]

## Files / mods touched (when built)
- NEW: `tools/bazaar_0_2_patch.py`, `SkyyBazaar/build_skyybazaar_0.2.py` (generated), `SkyyBazaar/test_skyybazaar_0.2.py`; runtime `Skyy_SkyyBazaar/book.properties`, `journal.log`, `orders.properties`, `history/`.
- EDIT: `tools/deploy_set.py` (pin + rollback floor), `tools/tier_tags.py` NOT touched (read), HANDOFF.md versions + floor, docs/log, RESUME, TEST-CHECKLIST (via `tools/record_deploy.py`), `research/Menu-Pattern.md` notes (MY ORDERS tab).
- READ-ONLY / unchanged: SkyyRebirth 0.3.6 (contract kept), SkyyAuctions, SkyyCoins (bridge `coins:fn:get/take/add`), SkySacks (`sacks:fn:*`), SkyyProfiles (`profile:fn:key`, `profile:busy:<uuid>`), SkyyGear (`market:veto`).
