# Answered - Economy

Covers: coins, bank, Bazaar prices, auction house, /trade, vault, NPC shops, SkyyEconomy merge.

**How to read:** one decision per line, word for word from OPEN-QUESTIONS.md (moved 2026-10-05; still-open questions stay in OPEN-QUESTIONS.md), in that file's order:
the 'Q&A with Skyy 2026-10-02' block (rounds R1-R9, then dated lines up to 2026-10-04) BEATS every older block below it; inside a
block the LOWER line is newer and wins. Each line starts with its status: LOCKED / ANSWERED / DECIDED = Skyy
decided; LIVE / VERIFIED / TESTED = shipped + seen. An OPEN / QUESTION / ASKED line here was answered by a later line - unless OPEN-QUESTIONS.md still lists it.
New answers go in the 'New answers' block at the end and leave OPEN-QUESTIONS.md (`python tools/qa_append.py economy <file>`). Index of all topics: [README.md](README.md).

## Q&A with Skyy 2026-10-02 (all open questions, round by round - newest answers win)
- R2 LOCKED (Skyy) [TRIED 2026-10-02: NOT POSSIBLE with the current client - probes P1 + P2 showed no chest slots on our own page; the in-chest arrows stay; re-check on 0.7]: try the one-click vault arrow row on our own vanilla-look page next to the vault slots (one probe first; the in-chest arrows stay as a fallback). [next SkyyVault]
- R2 LOCKED (Skyy): Magic Bags are blocked in /trade too (same rule as the AH). [next SkyyEssentials]  *(also in: bags)*
- R3 LOCKED (Skyy): SkyyEconomy merge (Coins + Bank + Bazaar + Auctions) goes ahead after Skyy has tested the separate mods.
- R3 LOCKED (Skyy): bag unlock collections / tiers / upgrade scraps stay as they are. NEW RULE (replaces the 2026-09-24 coin-bypass lock and bypass.bagMax): COINS NEVER SKIP COLLECTIONS OR BAGS - coins can buy items you have not unlocked yet on the Auction House / Bazaar, but can never buy a collection tier, a recipe unlock or a bag (remove SkyyCollections' "Buy tier unlocks" and the bag coin unlock). Skyy: "you can just make 2 or 3 bags of a lower level if one isnt enough" -> today only the BEST carried bag counts per type (SkyySacks caps() takes the max) - see round 4 about adding them up.  *(also in: bags)*
- R4 LOCKED (Skyy): keep the late-game market wall (some late items can never be bought / sold); the list stays empty until Skyy names items.
- R9 LOCKED (Skyy): KEEP ALL the small live defaults not otherwise marked in this file - tree felling XP (felled logs full XP + collections, leaves normal XP, placed logs never), party combat XP 50% within 48 blocks, menu hover tooltips on, staff bypass on, two crossbows share one big-arrow meter, AH 48h never cheaper than 24h (xFloorPrev on), old SkyyRolls rolls not clamped (clampToLevel off), SkyyRanks placeholders (Admin = kick + Server Setup + staff bypass, no ban; Developer = Admin's; Owner = rank editor; only real ops grant op-level nodes; no grants below Member), the vanilla UI look defaults (readable text, footer Close, vanilla colours / tabs / frames, Mythic #CC66CC, current text-box look), no sickle / gear swing-speed for now, a deleted profile's AH claims stay in its archive (admin can regrant), rank perks later, the picked non-metal gear levels (ranges in SkyyGear 0.2).  *(also in: project, skills, ui, social, gear, classes)*
- LOCKED 2026-10-03 (Skyy): BAZAAR - "small medium and large leather, (allong with everything else the combat sack holds.) in the combat section, and a new smithing section with everything the smithing sack holds (and for things like orevs smelted bars, make the smelted bars and tanned leather a good bit more expensive like +15%-25% so so it actually costs you to save time and buy processed materials" -> Combat tab = every Combat-sack item + light / medium / heavy hides and leathers; new Smithing tab = every Smithing-sack item; processed goods +20% (row, 0-22% - above 22.2% a buy-ore-smelt-sell loop pays) over their raw inputs per the vanilla recipes; items can show in two tabs (one market). [LIVE: SkyyBazaar 0.1.3, 2026-10-03]
- LOCKED 2026-10-03 (Skyy, GENERAL RULE): "if it goes in the bag, it goes in a matching section in the bizzar." -> every item any Magic Bag holds is listed in the matching Bazaar tab (Mining / Foraging / Farming / Combat / Smithing); the Bazaar build derives the lists from SkyySacks' bag definitions and fails if a bag item has no product. [in the SkyyBazaar 0.1.3 round, relaunched with the rule]  *(also in: bags)*
- LOCKED 2026-10-04 (Skyy): "bizzar looks good, but in increase the prices of the more difficult items by a good margin. right now i can easily buy a stack of mithril like its nothing ... id probbly 2x each material. so copper stays. iron gets 2x. thorium gets 4x ect" -> metal ore base prices x2 per tier step: Copper 5 (x1), Iron 8 -> 16 (x2), Thorium 12 -> 48 (x4), Cobalt 18 -> 144 (x8), Adamantite 30 -> 480 (x16), Mithril 45 -> 1,440 (x32), Onyxium 58 -> 3,712 (x64); ingots follow (auto = ore x ratio + the 20% premium); selling pays the same scale. Silver / Gold (not in the tool ladder) unchanged unless Skyy says. Live now via /bazaaradmin price <ore id> <base> (told Skyy). [next SkyyBazaar build: these as defaults + the money-loop check re-run over the new table (salvage / alloy loops) - full round after the reset]
- LOCKED 2026-10-04 (Skyy): "same fore the more rare woods. we are building a progresson tree" -> logs x2 per tier step, tiers from today's Bazaar prices: T1 common (Oak, Birch, Ash, Aspen, Beech, Cedar, Dry, Fir, Jungle, Palm 3; Bamboo / Burnt 2) x1; T2 (Apple, Banyan, Bottletree, Camphor, Blue Fig, Gumboab, Maple, Palo, Poisoned, Sallow, Spiral, Windwillow, Wild Wisteria 4) x2 = 8; T3 (Amber, Redwood 5) x4 = 20; T4 (Azure, Petrified 6) x8 = 48; T5 (Crystalwood, Fire, Frostwood, Stormbark 8) x16 = 128. RULE (progression tree): every tiered material family costs x2 per tier step. [default for the SkyyBazaar 0.1.4 build: the same x2 rule for the other tiered families too (hides / leathers light-medium-heavy, cloth, gems) unless Skyy says no; planks stay as they are (made from logs, no loop); money-loop check re-run]
- LOCKED 2026-10-04 (Skyy): "and the crops in the vanilla expansion path. so what and carrots are the cheapest, and then get more expensive as you go especially for the eternal seeds." -> crops + seeds follow the vanilla farming path (tiers to be checked against the vanilla Farming Bench recipe tiers by the build), x2 per tier step; today's price tiers: T1 Wheat, Carrot, Lettuce, Potato 2 (stay); T2 Corn, Cotton, Onion, Rice, Tomato, Turnip 3 -> 6; T3 Aubergine, Cauliflower, Chilli 4 -> 16; T4 Pumpkin 5 -> 40; normal seeds follow their crop tier (1 / 2 / 4 / 8); ETERNAL seeds (today 31-201, uneven) get the steepest climb [default: x4 per tier step from a T1 base ~50 -> 50 / 200 / 800 / 3,200]. [SkyyBazaar 0.1.4 with the metals + woods; the money-loop check must cover eternal-seed recipes and cooking (crops -> food)]
- LOCKED 2026-10-04 (Skyy): "and leather id moost the cost of leather but keep the small meduim and large close to similar prices" then "(price ranges on leather are good, just double the price of all of them)" -> every HIDE x2 flat (Soft 4 -> 8, Light 6 -> 12, Medium 12 -> 24, Heavy 18 -> 36, Scaled 24 -> 48, Storm 30 -> 60, Dark 36 -> 72, Prismatic 45 -> 90); leathers follow (auto, +20%: Light 14.4, Medium 28.8, Heavy 43.2); NOT the x2-per-tier rule. [cloth + gems still open - default x2 per tier step]

## Answer first (they block or shape the next builds)
> Answered later (2026-10-05 note): the SkyyEconomy-merge question below was answered by 'R3 LOCKED (Skyy): SkyyEconomy merge ... goes ahead after Skyy has tested the separate mods' in the Q&A block above.
2. **SkyyEconomy merge:** go ahead once you have tested the separate Bank 0.1.3, Bazaar 0.1.2 and Auctions 0.1? [yes, next round after your test]

## Numbers picked in the beta round (live now)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- LOCKED 2026-09-25 (Skyy): **Vault:** 2 free pages, max 10, page 3 = 50,000 coins, each next page +25,000. Pages are shared across all profiles (Wynncraft style). [as written — already the live defaults]

## Round 8 defaults (live 2026-09-28)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- Should Magic Bags be blocked in /trade too (the auction house blocks them)? Otherwise a bag can skip its collection. [allowed]  *(also in: bags)*

## Round 9 + SkyyGear defaults (live 2026-09-29)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- Auction house 48h: "double the listing fee", but never cheaper than the 24h price (built literally, 48h cost 20 coins on a 1,000-coin item vs 360 for 24h, so everyone would pick 48h). Server Setup key `xFloorPrev` - OFF = exactly 2 x the listing fee. [on]

## Vault arrows (`research/Vault-Arrows-Spec.md`, live in SkyyVault 0.1.2)
- QUESTION 2026-09-30: the vanilla chest never tells the server when you LIFT an item (research/Vault-Arrow-Click-Research.md), so an in-chest arrow can only turn the page on put-back, shift-click or the Drop key (SkyyVault 0.1.5). A true one-click arrow is possible only if the arrow row is drawn on our own vanilla-look page next to the vault slots (not a second page-switch screen - the arrows stay in the vault window). OK to try that (needs one probe first)? [not built]
- APPROVED 2026-09-25 (Skyy): cycle pages inside the vault GUI with the existing in-chest Prev/Next arrows. Do not add a second page-switch UI.
- The arrows sit in an extra 5th row, so all 36 slots stay free. If the 5-row chest doesn't fit your screen, switch Server Setup -> Vault -> arrow layout to "Inside the page" (the arrows then take the bottom-left and bottom-right slots, Wynncraft-exact). [extra row]
- LOCKED 2026-09-25 (Skyy): buying a page does not use two clicks within 10 s. Server Setup coin threshold `buyConfirmCoins`, default 50,000. A price below that buys at once. A price at or above it asks "Buy page X for Y coins?" in a confirm dialog. The gold arrow, the page Buy button, and `/vault buy` share that rule. [SkyyVault 0.1.2 still uses the 10 s second click; the next Vault build reads the row]
- LOCKED 2026-09-25 (Skyy): a plain click turns the vault page immediately, the same as shift-click. Both turn the page at once. [the "plain click only lifts; the page turns on put-down" note is not the UX. 0.1.2 turns the page when the server hears the click]

## Auction House (`research/Auction-House-Spec.md` section 12)
1. LOCKED 2026-09-25 (Skyy): Hypixel fee defaults stay. Listing 1% / 2% / 2.5%. Duration fees on 1h / 6h / 12h / 24h stay 20 / 45 / 100 / 350. 1% tax above 1,000,000. All of those fee values are adjustable in Server Setup (SkyyEconomy rows `ah.listingFee`, the fee half of `ah.durations`, `ah.claimTaxPercent`, `ah.claimTaxFrom`). [SkyyAuctions 0.1.1 still uses config.properties; the menu rows are the next economy build. 48h is question 2]
2. LOCKED 2026-09-25 (Skyy): durations stay 1h / 6h / 12h / 24h / 48h, default 24h. The 48h option costs double the normal listing fee. [0.1.1 still adds a flat 1,200 coins on 48h]
3. LOCKED 2026-09-25 (Skyy): Bazaar items stay refused on the AH. [refused, already the default]
4. LOCKED 2026-09-25 (Skyy): a different profile may buy your listing. The same profile may not. Was: never, even from another profile. [0.1.1 still refuses the other profile unless sameAccountBuy=true]
5. LOCKED 2026-09-25 (Skyy): Creative players browse and claim only. [yes, already the default]
6. LOCKED 2026-09-25 (Skyy): 14 listings per profile stays the default cap. Progression rewards or rank perks can raise it in game later. [14; 0.1.1 has no perk raise yet]
7. LOCKED 2026-09-25 (Skyy): a second click for buys of 10,000 coins or more. [10,000, already the default]
8. LOCKED 2026-09-25 (Skyy): cancelling keeps the fee (Hypixel). [kept, already the default]
9. LOCKED 2026-09-25 (Skyy): `/ah sell <price>` opens the pre-filled page for one click. [page, already the default]
10. LOCKED 2026-09-25 (Skyy): new listings wait 20 s before anyone can buy. [20 s, already the default]
11. LOCKED 2026-09-25 (Skyy): `/ah` works anywhere. [anywhere, already the default]
12. LOCKED 2026-09-25 (Skyy): late-game items that leave both markets. The list stays empty until Skyy names the items. [none yet - the list is ready and empty]
13. LOCKED 2026-09-25 (Skyy): bid auctions are parked for later. No rules yet. [later]
14. Claims of a deleted profile? [kept; admin can regrant]
15. LOCKED 2026-09-25 (Skyy): Magic Bags and the Accessory Bag are blocked on the AH. They cannot be listed or bought. Was: tradeable. [0.1.1 still allows them until blocked.txt has Skyy_Sack_* and Skyy_Accessory_Bag]
16. LOCKED 2026-09-25 (Skyy): ask before Claim all puts 100,000+ coins in the purse. [yes, already the default]

## /trade (`research/Trade-Spec.md` section 20)
1. LOCKED 2026-09-25 (Skyy): the 3 s countdown after both click Ready is the confirm. There is no extra click. [yes, already the default]
2. LOCKED 2026-09-25 (Skyy): max coins per trade is a flat server number. 0 means no cap. [flat, 0 = no cap, already the default]
3. LOCKED 2026-09-25 (Skyy): taking damage does not cancel the trade. Trades survive hits. [no; 0.1.4 still defaults tradeCancelOnDamage to true]
4. LOCKED 2026-09-25 (Skyy): 16 slots per side (a 4x4 grid). [16, already the default]
5. LOCKED 2026-09-25 (Skyy): trades stay private. There is no chat line to party or guild. [private, already the default]

## In-game server setup (`research/Server-Setup-Spec.md` section 9)
5. LOCKED 2026-09-25 (Skyy): bank interest for the time the bank was off is paid. Players receive back-pay for interest accrued while the bank was switched off. Was: no back-pay. [yes]
6. LOCKED 2026-09-25 (Skyy): NPC shops have buy and sell-back per item, infinite stock by default, and optional limited stock with a restock timer. [yes, infinite stock stays the default]
7. LOCKED 2026-09-25 (Skyy): NPC shops are in SkyyEconomy 0.2. [0.2, already the default]

## New answers (2026-10-05 on - newest last, beats everything above)

