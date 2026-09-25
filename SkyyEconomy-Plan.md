# SkyyEconomy - plan (Skyy, 2026-09-24)

One mod for the whole money side of SkyWynn. Skyy's call: roll Coins, Bank, Bazaar and the Auction House together, and put the
future NPC shops and item value tools in the same mod. Built as the round AFTER the current one, so the separate Bank 0.1.3, Bazaar 0.1.2
and Auctions 0.1 are tested first. A bug found after the merge is then a merge bug, not a feature bug.

## What goes in

| Part | Comes from | What it does |
|---|---|---|
| Coins (the core) | SkyyCoins 0.1.5 | Purse per profile, `/balance`, `/pay`, `/deathpenalty`, `/coinsgive`, the `coins:fn:*` bridge every other mod uses |
| Bank | SkyyBank 0.1.3 | Bank account per profile, interest, `/bank` page |
| Bazaar | SkyyBazaar 0.1.2 | Instant buy/sell of bulk items, custom amounts |
| Auction House | SkyyAuctions 0.1 | Buy It Now listings (bid auctions later), `/ah` |
| NPC shops (later) | new | Shop NPCs a server owner places and fills IN GAME (items, prices, stock) |
| Item value (later) | new | One price for any item from bazaar prices and the cheapest BIN listing; feeds networth, NPC sell value, price hints |

## What stays out (and where it lives)

- **`/trade`** (player-to-player trading window) goes in **SkyyEssentials** (Skyy): most servers have it, even ones without money.
- **Vault** (`/vault`) stores items, not money: stays its own mod (fits next to SkyyProfiles, since it is shared across profiles).
- **Guild bank** stays in SkyyGuilds; **reforge** stays in SkyyRolls (later the gear mod). Both keep calling `coins:fn:*`.
- **Coin rewards** in Skills, Collections, Exploration, Trees, Classes, Menu, Vault stay in those mods and keep calling `coins:fn:*`.

## Merge rules (nobody loses a coin)

1. **Same save folders:** keep reading and writing `Skyy_SkyyCoins`, `Skyy_SkyyBank`, `Skyy_SkyyBazaar`, `Skyy_SkyyAuctions` exactly as today
   (the old mods use `getDataDirectory().resolveSibling("Skyy_<Mod>")`). No data conversion.
2. **Same bridge keys** (`coins:fn:add|get|take|takeKey`, bank / bazaar / auction keys) with the same arguments and return values, so the
   11 mods that call coins need no change.
3. **Same command names and admin permission nodes** (`skyycoins.admin`, ...), so a server's permission setup keeps working.
4. **Coins start first; every other part starts inside its own try/catch.** A broken bazaar switches off only the bazaar, never coins.
5. **An on/off switch per part** (bazaar, auction house, bank, NPC shops) in the config AND in game (see `SkyWynn-Server-Setup-Plan.md`),
   for servers that want coins without a market.
6. **Deploy:** `tools/deploy_set.py` gets a RETIRED list that switches off the old SkyyCoins, SkyyBank, SkyyBazaar and SkyyAuctions keys in
   the world config. Today it only switches off older versions of the SAME mod, so without this both would load: duplicate commands and
   two coin systems.
7. **Proof:** snapshot every purse, bank account, bazaar state and auction listing before the first start and compare after. Must match.
8. **Code layout:** one build script, but each part keeps its own section and classes, and the coins core is only touched when it has to
   change (a bazaar tweak must not risk balances).

## Open for Skyy
- NPC shop details (buy-only or also sell-to-NPC, limited stock, restock timer) - when we get to it.
- Item value sources and networth display (SkyBlock shows networth; wanted?).
