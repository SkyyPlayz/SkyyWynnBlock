# Price tooltips - spec (2026-10-23)

Where this goes: `research/` (INDEX.md row "research/"). Answers to the questions at the end go to `docs/answered/economy.md`
(`python tools/qa_append.py economy ...`); build results go to `docs/log/2026-10.md`. Written by a spec agent and not built yet.

Skyy 2026-10-23 sent screenshots of a Hypixel SkyBlock client mod. The 'Decent Axe' tooltip ends with Lowest BIN Price / 3 Day Avg. Price /
Est. Item Value / Current Lowest Bin / 1d Average Bin. The 'Enchanted Oak Log' tooltip ends with NPC Sell Price: 640 Coins (320 each) /
Bazaar Buy / Sell / Insta-Sell / Insta-Buy. Skyy: "this is a mod i have for hypixle skyblock that shows the auction house, and bazaar prices
at the bottom of the flavor text. this would be very nice to build into our pack." (docs/answered/economy.md line 167).

**Short answer:** this works on the server, with no client mod. The client already supports it: the server can send any player a new
text for any lang key while they play (`UpdateTranslations` AddOrUpdate). Every item tooltip reads its description key
(`server.items.<id>.description`), so we send each player that key's normal text with a price block added. **No item stack is touched**,
so stacking, Sacks, the Bazaar, Collections and the AH work exactly as they do today. Two things need a probe before the build (R0):
whether the client redraws a tooltip after the key changes, and whether a gear tooltip can carry a translation part.

---

## 1. Where the prices live (all PROVEN in the SET build scripts)

| Number | Source | Bridge key (java.lang) | State |
|---|---|---|---|
| Market-maker instant SELL for 1 (= our "NPC sell": the Bazaar's market maker is the NPC) | SkyyBazaar 0.2.1 | `bazaar:sell:<itemId>` -> Long | EXISTS (`SkyyBazaar/build_skyybazaar_0.2.1.py` line 865, published at 6751, only ids that changed - line 569) |
| Market-maker instant BUY for 1 | SkyyBazaar 0.2.1 | `bazaar:buy:<itemId>` -> Long | EXISTS |
| Best player buy order (top bid) | SkyyBazaar 0.2.1 order book | `bazaar:bid:<itemId>` -> Long, absent = none | EXISTS (line 127, 8233) |
| Best player sell offer (lowest ask) | SkyyBazaar 0.2.1 order book | `bazaar:ask:<itemId>` -> Long, absent = none | EXISTS |
| The product list | SkyyBazaar | `bazaar:products` -> "id,id,..." CSV (~415 ids) | EXISTS |
| AH lowest BIN, per item (price / qty, rounded up) | SkyyAuctions 0.1.15 | `auction:fn:lowestBin` Function(String id) -> Long or null | EXISTS (`SkyyAuctions/build_skyyauctions_0.1.15.py` line 4489; walks LIVE listings for that id) |
| AH recent sale averages (1 d / 3 d) | SkyyAuctions | none | **MISSING.** No average is kept. The raw history does exist: closed SOLD records in `<world>/mods/Skyy_SkyyAuctions/archive/<yyyy-MM>/<id>.json` (never overwritten) and one `BUY ... <item> price=... ` line per sale in `auctions.log` (line 3579). Needs a sales index (R1). |
| Coins | SkyyCoins 0.1.11 | `coins:fn:get / take / add / curve` | Not needed for prices (only for formatting / nothing) |
| Merchant prices | SkyyMerchants 0.1.7 | none | Roaming merchants SELL weapons / mounts / eggs. They do not buy, so they are not an "NPC sell". Out of scope (see Q6). |
| Sacks "sell bag contents" | SkyySacks via `bazaar:fn:sell` | - | Pays the Bazaar's prices, so it needs no line of its own. |

How the derived lines are defined (they match how 0.2.1 matches orders: line 865-895, "instant buy fills from the cheapest sell offers
first, then the market maker", bids < MM buy and asks > MM sell):
- **NPC Sell** = `bazaar:sell:<id>`: what selling to the Bazaar with no player orders pays (it already includes the 2-coin floor).
- **Insta-Sell** = max(`bazaar:bid`, `bazaar:sell`), **Insta-Buy** = min(`bazaar:ask`, `bazaar:buy`). With an empty book these equal
  NPC Sell / MM buy.
- **Buy Order** = `bazaar:bid` (top), **Sell Offer** = `bazaar:ask` (top). The line is hidden when there is no order.

**New bridge keys needed (R1, SkyyAuctions):**
- `auction:fn:priceTable` Function(null) -> String, ONE call for every id: `"<id>\t<lowEach|-1>\t<avg1dEach|-1>\t<n1d>\t<avg3dEach|-1>\t<n3d>\n..."`.
  It replaces ~400 calls to `lowestBin` with one LIVE walk.
- `auction:prices:version` -> Long, bumped whenever a listing or sale changes the table, so the tooltip side skips a refresh when nothing moved.
- Optional: `bazaar:prices:version` -> Long (SkyyBazaar, bumped when it publishes buy / sell / bid / ask). Today the reader can compare the
  values itself, which costs about 1,600 map reads per refresh, which is nothing.

**AH sales index (SkyyAuctions R1):** keep in memory per item id a ring of the last sales (each price, sold-at millis), at most 3 days and
200 entries per id. Rebuild it at start from `archive/<this and last month>/` SOLD records (or the `BUY` log lines) and add to it on every
buy, inside the existing AhStore lock, after the commit. Averages: **median** of each-prices (one outlier sale cannot move it; spec
choice, see Q4), shown only with >= 3 sales in the window. Nothing new is saved, because the archive is the history, so no saved-data
change and no migration.

---

## 2. How a tooltip can show LIVE numbers

### 2a. What we already do (PROVEN): per-stack tooltips on gear
`SkyyGear/build_skyygear_0.3.43.py` GearView writes `ItemDisplayMetadata` (name + description Message) **into the stack's metadata**
(line 27269 `out.withMetadata(IDM.KEYED_CODEC, new IDM(nameMsg(...), descMsg(...)))`). A stamp scan re-renders it on join, on an
inventory change and on a level-up, at most once every 250 ms per player (`SCAN_GAP_MS`, line 3610). A signature hash of every line
(`GearView.sig`) means a stack is rewritten only when its text changes. **It is per STACK, not per player:** a stack carries its text to
whoever holds it. Gear is (almost) never stackable, so splitting is no concern there. The passive scan "never splits" (line 28402).

### 2b. Plain stackables (logs, ores, crops, Enchanted items): the options
| Option | Verdict |
|---|---|
| **(i) Price block written into each stack's metadata** (on inventory entry / a timer) | **REJECTED. It breaks stacking and three mods.** A stack with metadata no longer merges with a fresh drop that has none. SkyySacks auto-store takes "plain stacks only" (`SkyySacks/build_skyysacks_0.8.28.py` line 5963: `it.getMetadata() != null && !isEmpty() -> continue`), so tagged logs would stop going into Sacks. The Bazaar's `Inv.countIn / take` send metadata stacks through the veto path (line 587), and the AH snapshots metadata. Every price tick would also rewrite every stack of every player (inventory churn, save churn, dupe surface). Never do this. |
| **(ii) A runtime lang update per player: `UpdateTranslations` AddOrUpdate** | **CHOSEN.** HytaleServer.jar (read only, reflect / bytecode, 2026-10-23): `protocol.packets.assets.UpdateTranslations(UpdateType, Map<String,String>)` is a `ToClientPacket` with `UpdateType` Init / AddOrUpdate / Remove. `I18nModule.sendTranslations` sends Init on join via `PacketHandler.writeNoCache`. `I18nModule.getUpdatePacketsForChanges` builds AddOrUpdate / Remove packets, and `I18nModule$I18nAssetMonitorHandler` (live lang hot reload) and `AssetEditorPlugin` send them **to connected clients at runtime**. So the client is built to accept new key texts while it plays. `PlayerRef.getLanguage()` + `getPacketHandler()` exist, so we can send **per player**. Item tooltips read `server.items.<id>.description`, and the engine falls back to that key even when the item JSON names none (VERIFIED earlier, research/Tier-Tags-Plan.md section 2 (a), SkyyArmory spec 1.1). Lang `\n` and `<color is="#hex">` spans work in item descriptions (PROVEN by the pet tooltips, research/Pet-Tooltip-Layout.md line 139). **Prior art:** DynamicTooltipsLib 1.6.2 (Skyy's Mods folder, read only) does exactly this in `GlobalTooltipManager.addItemGlobalTranslationLine`: it sends per-player `UpdateTranslations` (plus `UpdateItems` for virtual ids, which we do not need). |
| (iii) Server lang / asset file rewrite + hot reload | Rejected. It writes into game / mod files, is global (no per-player toggle) and we do not own the lang keys. (ii) uses the same packet without touching any file. |
| (iv) Prices only on our own pages (Bazaar / AH / Sacks hover) | **The fallback** if R0 fails. PROVEN: the Bazaar product detail already shows instant buy / sell + the best 5 orders. Note that if (ii) works, our ItemGrid slots (`new ItemStack(id, qty)`) show the price block for free, because the client draws the same item tooltip. |

**What (ii) means in practice:**
- The text we send for an id is `base + "\n\n" + priceBlock`. `base` = `I18nModule.get().getMessage(lang, key)`, the text the server
  holds right now: the vanilla line, the tier tag our owner jar wrote, or a pack mod's text. **No lang key is added to any jar, so
  `tools/ci/langdup.py` is unaffected and no file overrides anything.** When `I18nModule` fires `MessagesUpdated` (an asset reload),
  build `base` again.
- If `base` is empty (an item with no description), send only the price block.
- **Per-player toggle off** = send `base` once (one AddOrUpdate that puts the plain text back), then nothing more for that player.
- **Stacking safety:** nothing changes on any `ItemStack`. Server-side stacking, the Sacks `plain` checks, Bazaar `Inv` matching,
  Collections counting and AH snapshots never see the price. The block lives only in the client's string table. Lowest possible risk.
- **Items with their own ItemDisplayMetadata** (SkyyGear documents, totems, pets, accessories with metadata): the client shows the per-stack
  description, not the key, so (ii) alone does not show there and does no harm. For those, see 2c.
- **The stack total cannot be shown for plain stacks:** one key per item id cannot know the hovered stack's quantity. So "640 Coins (320
  each)" becomes `NPC Sell: 320 each (x64: 20,480)`: each + a full stack of that id's MaxStack. Q2.

### 2c. Gear (and other metadata tooltips): AH lines
GearView's description Message can take one extra child, `Message.translation("server.skyy.price.<id>")` (the `Message.translation` API
exists: reflect 2026-10-23; SkyyExploration already uses it for titles). The stack's text stays **stable**, so the sig does not change and
nothing is rewritten when a price moves. The numbers come from that key, which the price engine sends per player like 2b. Whether
the client resolves a translation child inside an `ItemDisplay` FormattedMessage is **UNVERIFIED (probe R0-P3)**. Fallback: GearView writes
nothing, and the gear's AH lines show only in the AH item page and `/gear` (plain text through the existing `gear:fn:describe`).
Adding the child changes every gear sig once: a one-time re-render of every stack, the same as the 0.2.19 restyle (no data change).

### 2d. Refresh, per player, performance
- **Engine owner: SkyyBazaar** (it owns the product list and the market maker, and is the Market hub's host). New class `BzTip` + a slow
  task off the world thread. It touches no component, inventory or stats, only the bridge and packets.
- **Tick:** every `tip.refreshSeconds` (default **60**, Server Setup, live). (1) Read `bazaar:*` + `auction:fn:priceTable` (only when
  `auction:prices:version` changed). (2) Render the block per id per language in use (one string each; ~415 + AH-only ids). (3) Hysteresis:
  re-send an id only when a shown number moved by >= `tip.minChangePct` (default 2 %) or `tip.maxAgeSeconds` (default 600) passed, so a
  busy book does not spam. (4) Per online player with the toggle on: ONE AddOrUpdate packet with only the changed keys.
- **On PlayerReadyEvent** (it fires on every world switch): send the full map once to that player (~500 keys, a few tens of KB, one
  packet). This also covers whether a world switch resets the client table (R0-P4).
- **Cost:** about 500 string builds a minute, plus one small packet per player when something moved. No per-stack work and no saves.
  Lighter than the Bazaar's own 10 s tick.
- **One runtime writer per key:** only SkyyBazaar's BzTip sends `server.items.*.description` at runtime. Add lint rule `runtime_lang_owner`
  (any other jar that names `UpdateTranslations` = fail) to `tools/ci/lint.py`.

---

## 3. Which lines, colour code, settings

### 3a. The block (Style Guide section 15 colours; at the very BOTTOM of the flavour text, after a blank line)
Plain stackable (a Bazaar product):
```
Market                                   (dim grey #7f93a6, the group header)
NPC Sell: 320 each (x64: 20,480)         (name #d6e4ee, number gold #e8c25a bold, the bracket dim grey)
Insta-Sell: 335 each                     (only when it differs from NPC Sell)
Insta-Buy: 372 each
Buy Order: 330  Sell Offer: 360          (only the sides that exist)
AH Lowest BIN: 300 each                  (only when listed on the AH)
AH Avg 1d / 3d: 310 / 318 (12 sold)      (only with >= 3 sales in that window)
```
Gear (via 2c): `AH Lowest BIN`, `AH Avg 1d / 3d`, `Est. Value` (Q3), the same colours. Numbers use the pack's thousands separator, for example
"20,480". Coins are written as plain numbers with no "Coins" word, because the header and gold colour carry it (Q5).
Colour rules (section 15): label = stat NAME `#d6e4ee`, coin value = gold `#e8c25a` bold (spec choice: no coin token exists, and gold
reads as money. If Skyy wants a different coin colour, add a kit token `coin` to `tools/skyyui.py` and use it everywhere, Q5), minor info
dim grey `#7f93a6`. Group order: our block goes last, after the item's own text, as Skyy asked ("at the bottom of the flavor text").

### 3b. Server Setup (tools/skyycfg.py, CONFIG-CONTRACT; SkyyBazaar > "Price lines", all **live**, times in seconds)
| Key | Label | Default |
|---|---|---|
| `tip.enabled` | Price lines in item tooltips | ON (no dev gates) |
| `tip.npc` | NPC Sell line | ON |
| `tip.insta` | Insta-Buy / Insta-Sell lines | ON |
| `tip.orders` | Buy Order / Sell Offer line | ON |
| `tip.ah` | AH Lowest BIN line | ON |
| `tip.ahAvg` | AH 1 day / 3 day average line | ON |
| `tip.estValue` | Est. Value (gear) | OFF until Q3 is answered |
| `tip.stackLine` | "(x64: ...)" full-stack total | ON |
| `tip.refreshSeconds` | Refresh every (s) | 60 (10-600) |
| `tip.minChangePct` | Re-send when a price moves by (%) | 2 (0-50) |
| `tip.maxAgeSeconds` | Re-send at least every (s) | 600 |
| `tip.avgMinSales` | Sales needed before an average shows | 3 |
New file `Skyy_SkyyBazaar/tips.properties`, kit KEEP 10. No existing line changes, so no migration.

### 3c. Per-player toggle (Settings-Spec 1.2-1.3 adopter helper)
`settings:fn:register` key **`market.priceLines`**, label "Price lines in tooltips", category Market, default ON. Read with `settings:fn:get`
on each tick (the lock-free hot-path call). Switching it off sends the base texts back once.

---

## 4. Duplicate check (PROJECT-RULES 2)
- **DynamicTooltipsLib 1.6.2** (org.herolias / MineAndCraft, CurseForge 1459711), in Skyy's Mods folder and **OFF** in NewBetaTest's
  config.json. It is a LIBRARY (per-item tooltip lines via virtual item ids + `UpdateTranslations`) and shows no prices. Its manifest says
  `ServerVersion >=0.6.0-pre.13.1 <0.7.0` and the CurseForge page lists 0.5 / 0.6 only, so it does not fit our 0.7 server. Licence **All Rights
  Reserved**, so we cannot fold it. We LEARN from it (read only): per-player `UpdateTranslations`, an outbound `PacketAdapters` filter that
  injects into the Init packet, `UpdateItems` overrides for items with no description key. We reuse only the first idea. The author notes Hytale
  now has a native per-item tooltip route (= ItemDisplayMetadata, which we use). **Not packed.**
- CurseForge web survey (2026-10-23): TheEconomy (shop GUI whose own shop tooltips show buy / sell price), Better Shop / Auction / OfferHouse,
  Marketplace, Shops, HTSellWands. Each is a whole economy that would duplicate our Bazaar / AH / Coins, and none adds price lines to every
  item's own tooltip. **No duplicate found. Build ours.** (Survey depth: two web searches + the DTL page. Not exhaustive, so the CurseForge
  "Hytale tooltip price" category is UNVERIFIED beyond that.)

---

## 5. Build split (rounds)

| Round | Size | Mods | What |
|---|---|---|---|
| **R0 probe** | lean | **SkyyUiProbe 0.9** (the combined probe, research/UI-Queue-Spec.md) | `/uiprobe tip <id> <text>` sends one AddOrUpdate for `server.items.<id>.description` to the caller. `/uiprobe tipgear` gives a test sword whose ItemDisplayMetadata description has a `Message.translation("server.skyy.probe.tip")` child, then sends that key. Probes P1-P5 below. |
| **R1** | **full** (economy data, several mods) | SkyyAuctions 0.1.16 | Sales index (in memory, rebuilt from archive), `auction:fn:priceTable`, `auction:prices:version`. No saved-data change. |
| **R2** | **full** | SkyyBazaar 0.2.2 (+ SkyyMenu only if the settings category needs a label) | BzTip engine, tips.properties + Server Setup rows, `market.priceLines` toggle, `bazaar:prices:version`, lint rule `runtime_lang_owner`. Pins with Auctions 0.1.16 (works without it: no AH lines). |
| **R3** | lean (only if P3 passes) | SkyyGear 0.3.4x | GearView adds the `server.skyy.price.<id>` translation child to identified gear (switch `view.priceLines`, default ON). The one-time re-render is look only. |
| R4 (later) | lean | SkyyPets / SkyyShards / SkyyAccessories | The same child in their metadata tooltips, if Skyy wants prices on pets / totems / charms. |

**Probes (R0, UNVERIFIED until Skyy tests them):**
- P1: after `/uiprobe tip Wood_Oak_Trunk "Test 1"`, does hovering an Oak Log in the inventory show "Test 1" (vanilla text replaced)?
- P2: run it again with "Test 2" while the inventory is OPEN. Does the next hover show "Test 2" without reopening? (If it needs a reopen,
  that is fine: say so in the help text.)
- P3: does the probe sword's tooltip show the translation child's text, and does it update after a new send?
- P4: after a world switch / `/hub` and after a relog, is the text still there? (Expected: relog = Init resets it, and BzTip resends on PlayerReady.)
- P5: does an item with NO vanilla description (Plant_Crop_Wheat_Item) show the key text? Also check the Bazaar / Sacks ItemGrid hover
  and the creative / recipe book hover.

**Harness checks (each round's test_*.py + CI):**
- No `withMetadata` / `setMetadata` in BzTip or any R1 / R2 class (grep in the generated Java), so no stack is ever touched.
- Render unit test (jpype): the fixed price inputs give the exact block text + colour spans, the hidden-line rules (no order / < 3 sales /
  equal insta = hidden), the thousands separator, the stack line uses MaxStack.
- Hysteresis test: a 1 % move = no send, a 3 % move = send, maxAge = send.
- Toggle test: off -> one restore packet with base texts, then none.
- `auction:fn:priceTable` test: median ignores one 100x outlier, the window cut-off, the rebuild from a scratch archive copy equals the
  live index.
- `python tools/ci/lint.py` 0 fails (new rule `runtime_lang_owner`), `tools/ci/langdup.py` unchanged, `python tools/ci/crosscheck.py --jar <new jars> --baseline`,
  `python tools/smoke_test.py --jar ...` (the '[SkyyBazaar] 0.2.2 ready' line, no SEVERE).

**In-game test steps (after R2, for TEST-CHECKLIST):**
1. Hover Oak Log in the inventory: the Market block at the bottom with NPC Sell each + (x64 total), Insta-Buy / Insta-Sell.
2. Place a Bazaar buy order above the market-maker sell: within ~60 s the Oak Log hover shows Buy Order and a higher Insta-Sell.
3. List an Oak Log stack on the AH: AH Lowest BIN appears. After 3 buys, AH Avg 1d / 3d appears.
4. /settings -> Market -> Price lines OFF: the hover is the plain text again. ON: the block comes back.
5. Server Setup -> Bazaar -> Price lines -> AH lines OFF: the AH lines vanish for everyone.
6. Pick up Oak Logs while carrying a stack of Oak Logs: they still merge, still go into the Sack, and Bazaar Sell all still sells them
   (stacking safety).
7. Switch worlds / relog: the block is still there.
8. (R3) Hover an identified sword that is listed on the AH: AH lines under the Ability / flavour part.

---

## Questions for Skyy (today's default in [brackets])
1. Our "NPC Sell" = what the Bazaar's market maker pays (we have no separate sell-to-NPC shop). Show it as "NPC Sell" or "Bazaar Sell"? ["NPC Sell", as in SkyBlock]
2. Plain stacks cannot show the hovered stack's own total (one text per item id). Show "each" + a full-stack total "(x64: 20,480)"? [yes]
3. "Est. Item Value" for gear: what should it be? [OFF for now. Later: the AH 3-day median for that item id and rarity]
4. AH averages: median (a single silly sale cannot move it) or a plain average? [median, shown after 3 sales]
5. Coin colour in the block: gold like level / XP, or its own coin colour? [gold #e8c25a, bold]
6. Prices on gear (needs probe P3) and later on pets / totems / charms too? [gear yes if P3 passes; pets / totems / charms later]

## For the local session (UNVERIFIED - check before launching rounds)
- R0 first: add the `tip` / `tipgear` probes to SkyyUiProbe 0.9 (lean). Skyy runs P1-P5. If P1 fails, drop 2b(ii) and build only the
  fallback 2b(iv) (prices on our pages + ItemGrid hover through our own TooltipText).
- The lang key form the client looks up (`server.items.<id>.description` vs `items.<id>.description`) and whether `I18nModule.getMessages`
  keys carry the `server.` prefix: read `I18nModule.getMessages` bytecode in R0 (tools/dev/bc.py) and send the form the Init packet uses.
- Whether `PacketHandler.writeNoCache` may be called off the world thread (I18nModule calls it from its asset-monitor thread, so it is
  probably safe) - R0.
- The AH archive SOLD record's sold-at field name (builder reads `AhRec` in `SkyyAuctions/build_skyyauctions_0.1.15.py` near line 3576).
- Survey depth for section 4 was light (two searches + one page). A Haiku / Jev pass over CurseForge "Hytale tooltip" is optional.
- Record this spec in INDEX.md (research row) + RESUME "Next", and queue Q1-Q6 as one popup.
