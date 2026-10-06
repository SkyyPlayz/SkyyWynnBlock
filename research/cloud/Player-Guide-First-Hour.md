# Player guide - Your first hour on SkyWynn

Cloud draft, 2026-10-06. Paper writing only; nothing built. Inputs read: `Story-Script-Draft.md`, `Starter-Shards-Plan-2.md`, `Starter-Shard-Layout.md`, `Outposts-List.md`, `research/classes/README.md`, `RESUME.md`, `HANDOFF.md` (sections 1 + 3), `docs/handoff/state-2026-09.md` and `design-locks.md` (command names).
For the team: this guide is for players. Every step is tagged **[LIVE]** (in the deployed 26-mod SET today) or **[PLANNED]** (only in a cloud spec). Planned things appear only inside "Coming later" boxes. Nothing here is tested by Skyy yet (RESUME: the 2026-10-05 deploy is untested), so treat "LIVE" as "deployed", not "verified".

---

## Welcome, Arrival #4,000,000,001

**What SkyWynn is:** a Hytale server pack that mixes Hypixel SkyBlock (skills, collections, bags, a market) with Wynncraft (classes, gear levels, zones).
**The one-line lore:** you did not spawn. You were *processed*. The Void has a Department of Arrivals, it is very busy, and your ticket number is **#4,000,000,001**. The board says "NOW SERVING #3". Nobody has explained this. Please take a seat.
**Rule of thumb for your first hour:** open the menu, pick a class, hit things, put things in bags, spend little, ask your party.

> **Coming later - the real welcome (PLANNED, Story-Script-Draft + Starter-Shards-Plan-2)**
> You wake up floating on a shard. **Pebble**, a talking rock who has been "here four thousand years" (and gives terrible advice with total confidence), walks you through a 12-quest tutorial across three small floating shards: chop wood, craft a table, mine copper, grow wheat, open the Collections book, repair a broken bridge, craft crude armor, fight your first mobs, build your own bridge, get the Portal Shard from the toll hut, and step through a portal with a sad face on it. That chain, Clerk Mossby (a sleepy Kweebec clerk) and the ticket are **not in the game yet**. Today you start on your island; follow this guide instead.

---

## 1. Your island and the SkyWynn Menu  [LIVE]

1. **Your island.** Type `/island`. It creates your private island the first time and teleports you there. `/hub` takes you back to the hub (the temple town). Co-op members and visitors are possible (island settings).
2. **The SkyWynn Menu item.** You get a menu item the first time you use a profile. Right-click it. If you lost it (or a new profile has none), type `/skymenu` (also `/menu`).
3. **What is in the menu:** Profile, Teleport (island, hub, spawn, warps), Pocket Dimension (your bags), Accessory Bag, HUD Editor, Crafting, Skills, Collections, Bazaar, Bank, Players, Party, Mods, and your own **Settings**. Hover a button for a tooltip.
4. **Everything is a click away.** Every page has a Close button; you never need to remember commands. The commands exist for speed.

> **Tip:** in Settings you can switch off what you do not want. Server owners can change almost every number in Server Setup (menu), so your server may differ from this guide.

> **Coming later - the Stats page (PLANNED, Stats-Page-Spec)** Your Profile will grow into a SkyBlock-style stats sheet. Not built yet.

---

## 2. Pick a class  [LIVE]

Open the class page with `/class` (or the menu). Your **first choice is free**. Your class decides which weapons deal damage, so choose before you swing.

| Class | Role | Weapons (2 types each, no sharing) | Live today? |
|---|---|---|---|
| Warrior | Tank + crowd control | Swords (incl. longswords), Spears | LIVE (kit: Crude Sword + Wood Shield) |
| Archer | Crowd control + focus marker | Shortbows, Crossbows | LIVE |
| Mage | Burst damage, glass cannon | Staffs, Spellbooks | LIVE (staffs work; spellbooks UNVERIFIED) |
| Priest | Healer + protector | Wands, Soul Orb | LIVE (wands; Soul Orb is PLANNED, `Soul-Orb-Spec.md`) |
| Assassin | Priority killer + debuffer | Daggers, Kunai | LIVE |
| Berserker | Damage buffer + sustained melee | Axes (incl. battleaxes), Maces / clubs | UNVERIFIED (the notes say it was pulled and is pending) |
| Monk | Self-speed disruptor | Bo staff, Fist weapons | PLANNED (designed, `Monk-Kit-Spec.md`) |

- **Starter kit:** your class gives you a small kit straight into the hotbar (once per profile).
- **Weapons from other classes deal no damage to you** if you have a class. Pick up a sword as a Mage and it is just a stick with opinions.
- **Staff and wand attacks:** TAP = a quick shot, HOLD = a charged shot (costs Mana). Mana comes from your Mage/Priest levels.
- **Charged attacks (traversals):** every weapon type has its own charged attack, most from vanilla Hytale.
- **No paid class switch.** Want to try another? Make a new **profile** (section 8) - each profile is a full separate save with its own class.

> **Coming later - class abilities (PLANNED, Class-Ability-Spec-Draft / Class-Tree-Paths)**
> Each class will get 5 designed abilities (you own 4, equip 2 in rune slots), each levelled by use, each with its own modifier tree (4 modifiers, 2 equipped), plus a Wynncraft-style class tree of paths. Not in the game yet; class trees are currently switched OFF.

---

## 3. First tools and crude gear  [LIVE: tools, Crude gear is PLANNED]

1. **Use your class kit weapon** and the vanilla tools you find. Hit trees with an axe, rocks with a pickaxe, crops with a sickle or by pressing F on ripe crops.
2. **Craft a Workbench** and put your Accessory Bag in your pocket (right-click it or `/accessories`).
3. **Your bags help crafting.** Items in Magic Bags (section 5) count towards recipes at a bench and in your inventory crafting. `/craft` opens the craft page.
4. **Tool levels:** a tool such as a Copper Pickaxe has a level (for example "Lv 10 - Requires Mining 10"). Today the requirement is shown in grey as "coming later" and the tool still works.

> **Coming later - Crude armor and the gear ladder (PLANNED, Crude-Armor-Design, Gathering-Tiers-Draft)**
> Crude gear (Fibre + sticks + stone rubble) is meant to be your first armor on a starter shard. Armor types (Heavy for Warrior and Berserker, Light for Archer, Assassin and Monk, Cloth for Mage and Priest) and tool levels that raise speed and Fortune are also designed, not built. Metal bands you will see on gear: Wood/Crude 1-13, Copper 10-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril/Onyxium 40-49.

---

## 4. Skills and Collections  [LIVE]

**Skills** (`/skills`, or the menu): Mining, Foraging, Farming, Combat, plus Acrobatics, Exploration, Cooking, Alchemy, Smithing and your class skill. You gain XP by doing the thing: breaking blocks, harvesting, killing, crafting, rolling when you land (crouch for a rolled landing: bonus XP, no fall damage where fall damage is on).
- Levels go to 100. Early gathering levels pay extra XP (x3 up to level 10, falling to x1.5 from level 20).
- Killing mobs above your skill level pays more; far below it pays less.
- Level-ups pay coins. `/skills top` shows the leaderboards (deleted profiles are skipped).
- **Skill trees** (`/tree`) exist for gathering, Acrobatics, Exploration, Alchemy and Smithing. Class trees are OFF for now.

**Collections** (`/collections`, or the menu): the book that remembers everything you ever picked up. Gather an item, reach **tier I**, and its recipes unlock. Unknown items show as ???.
- **Coins never buy a collection tier.** The Bazaar and shops will never sell you the unlock - you have to gather.
- `/collections top` shows the leaderboard.

> **Coming later - the gathering ladder (PLANNED, Gathering-Tiers-Draft, Enchanted-Materials-Draft)**
> SkyBlock-style tiers per zone: gather the first tier's material, unlock the recipes for the next tier's gear, then "Enchanted" compressed materials. Skyy has asked for this as a spec; the first Sap-and-Lantern recipes are queued.

---

## 5. Bags and sacks  [LIVE]

**Magic Bags** (the Pocket Dimension; `/sacks`, `/pd`, `/bags`): bags that open onto your pocket dimension. Carry a bag of a category (for example Mining) and it **auto-collects** that kind of item as you pick it up, and can **auto-refill** your hotbar.
- You must **carry** the bag to open it or withdraw from it. The pool itself keeps its contents.
- Bags are **not tradeable** (they are blocked in `/trade`).
- Items in bags count towards crafting.
- **Accessory Bag:** 6 slots for accessories. Equip and Unequip with the buttons. Includes the **Lantern** line (a torch glow on you): Normal -> Unique -> Rare -> Legendary, each crafted from the previous.

> **Tip:** put your first bag in the first hotbar-adjacent slot of your inventory so you never forget to carry it.

> **Coming later (PLANNED, `docs/answered/bags.md`, RESUME next list)** Sell straight from your bags at the Bazaar (take buttons + Sell Inventory) is the next build - today you take items out first, then sell.

---

## 6. Your first coins  [LIVE]

- **Starter coins:** a new profile starts with a purse (10,000 starter coins in the 2026-09 test; your server may differ). `/pay` sends coins to a friend.
- **Dying costs a little from your purse only.** Coins in the bank cannot be taken by the death penalty.
- **Bank** (`/bank`, or the menu): `deposit` and `withdraw` amounts like `500`, `2k`, `1.5m` or `all`. The bank pays interest (default about 2% every real hour on up to 10 million; both numbers are Server Setup rows). Put coins you do not need in the bank.
- **Bazaar** (`/bazaar` or `/bz`): an instant-trade market with a market maker. Tabs per bag type plus Smithing. Buy 1 / 64, Sell 1 / 64 / all, and **Sell Inventory** (asks you to confirm for about 10 seconds).
  - **The Bazaar buys low and sells high:** you buy at about base x 1.10 and sell at about base x 0.90, so flipping the same item loses you about 20%. Prices grow about x2 per progression tier.
  - Stack buttons use the item's real stack size (ore 25, most things 100) - planned tweak, see below.
- **Auction House:** buy-it-now listings (`SkyyAuctions`).
- `/trade` and `/tpa` (SkyyEssentials) work between players; `/tpahere` brings a friend.

> **Tip:** do not spend your first coins on anything you can craft. Sell extras, keep the rest.

> **Coming later - shops and coin sinks (PLANNED, NPC-Shops-Spec, Tab-Economy)** NPC shops in outposts will sell tools and food but never collection unlocks or accessories. A tab system and bounty-style sinks are on paper only.

---

## 7. Identify your gear and understand levels  [LIVE]

- **Rarity:** every weapon and armor piece has one. In order: Normal, Unique, Rare, Legendary, Fabled, Mythic, Set. Higher rarity means more modifiers and bigger numbers.
- **Item level:** every gear piece has a level and a requirement (levels per material; see the metal bands in section 3). Hover to read the tooltip.
- **Unidentified drops:** mob drops and every chest's gear start **unidentified**. Use `/identify` (opens the identify menu) to reveal the item and its roll. Identified items show their numbers; unidentified ones hide the damage box on purpose.
- **Crafted gear** rolls its rarity when you craft it and pays Smithing XP.
- **Reforge** (SkyyGear) swaps the bonuses on a piece; higher rarity gives a wider roll range.
- **Crits** show a small crit popup.

> **Coming later - the loot round (PLANNED, SkyyGear 0.2.x queue)** Tool rarities and rolls, reforge level-ups, weapon speed tiers (Slow / Medium / Fast / Super Fast, same DPS) and the "mob curve" that matches mob levels to zones. In the next builds.

---

## 8. Party and profiles  [LIVE]

- **Party** (`/party`, or the menu): create or join a party, see your party in the HUD widget. Kill XP is shared per member's own skill level. Use the **TPA / Accept TPA** buttons on the party page to meet up.
- **Profiles** (`/profiles`, menu: Profile): a profile is a **full save** (default cap 6). Each has its own class, island, inventory, skills and coins. `/profiles list`, `/profiles switch`, `/profiles delete` (with a 6-hour undo, `/profiles restore`). You cannot delete your active or your last profile.
- **Guilds** (`SkyyGuilds`) have a guild bank and are live; open them from the menu (UNVERIFIED which menu entry).
- **Vault** pages give you extra storage.

---

## 9. Where to go next

| Step | What | Status |
|---|---|---|
| 1 | Level Mining / Foraging / Farming on your island and the hub; fill your first collection tiers | LIVE |
| 2 | Cook (SkyyCooking dishes with a food Grade) and craft your first bench gear | LIVE |
| 3 | Visit the **Zone 1 test island** with `/zone 1` (admin-run today, so ask your server owner) | LIVE (admin command) |
| 4 | **Greenfield Annex**, the first outpost after the town (plains and birch, levels 1-5, a general shop and a tutorial sign, unlocks a warp) | **PLANNED** |
| 5 | Zone 1 Emerald Wilds (levels 1-20), Zone 2 Howling Sands (20-30), Zone 3 Whisperfrost (30-45), Zone 4 Devastated Lands (45-60), Zone 5 dinosaur caves (60-75) | **PLANNED** (world gen) |
| 6 | The Waiting Room quest chain: stamps for Form 27-B/6, the Zone 1 guardian, "which game are you from?" | **PLANNED** (Story-Script-Draft part 2) |

> **Coming later - outposts and warps (PLANNED, Outposts-List)** 34 unlockable outposts ("Branch Offices of the Department of Arrivals"), each with a warp, a small shop and an Exploration reward. **Greenfield Annex** (Zone 1, levels 1-5) will be your first.

---

## 10. Ten quick tips

1. **Pick your class first.** Weapons from other classes do nothing for you.
2. **Put coins in the bank** before you go adventuring. Death only touches your purse.
3. **Carry a bag of the right type** so pickups go straight into the pocket dimension.
4. **Hold to charge.** Staffs and wands: tap = quick shot, hold = charged.
5. **Hover everything.** Tooltips show levels, rarity and Mana cost.
6. **Gather to unlock.** Recipes come from collection tiers, never from coins.
7. **Use `/identify`** on every unidentified drop - a boring-looking sword may be a Rare.
8. **Do not flip at the Bazaar.** Buy high, sell low is how it works; sell only what you do not need.
9. **Use profiles to try another class.** Each profile is a full save with its own class.
10. **Check the menu first.** If you do not know a command, the SkyWynn Menu has a button for it.

*(The Void hiccups. If a rumble shakes your island, that is normal. Please do not mention it.)*

---

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Which classes the `/class` page really shows in SkyyClasses 0.1.11 (Berserker pending, Monk planned, Mage spellbooks, Priest Soul Orb). |
| 2 | Command spellings: `/class`, `/island`, `/hub`, `/identify`, `/zone 1`, `/party`, `/profiles` verified only through old notes; the 2026-10 jars may have renamed or added aliases. `/craft`, `/bank`, `/bz` come from HANDOFF section 1 and the 2026-09 state notes. |
| 3 | Whether `/identify` still opens a menu or now needs an NPC (design-locks: "`/identify` opens the menu for now"). |
| 4 | Starter coins today (10,000 in the 2026-09 note) and whether starter coins and the kit are once per profile (locked 2026-10-01 YES). |
| 5 | Which menu entries exist for Guilds and Vault. |
| 6 | Whether the Bazaar spread today is exactly buy x1.10 / sell x0.90 (brief rule) or the older spread x demand factor in state-2026-09. |
| 7 | Whether new profiles get the menu item automatically or only once per player (log 2026-10-01 says "once per player"; `/skymenu` gives it back). |
| 8 | Tool "Requires Mining N" text is shown only as "coming later" (docs/tests 2026-10 item 12). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Should this guide ship in-game (a "Guide" button in the SkyWynn Menu) or stay a wiki page? | Wiki / CurseForge page first |
| 2 | Keep the lore jokes (ticket number, Pebble) in a guide that appears before the tutorial exists? | Yes, short, in the intro and boxes only |
| 3 | Should the guide name the starter coin number? | No, say "starter coins" (a Server Setup row) |
| 4 | Show Berserker and Monk in the class table before they are playable? | Yes, tagged PLANNED / UNVERIFIED |
| 5 | Update the guide when the starter shard chain lands? | Yes, replace the first "Coming later" box with the real Pebble steps |
