# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `DESIGN-STATUS.md` "Open questions".

## Answer first (they block or shape the next builds)
1. **Settings menu: refuse or hide?** When a player switches off party invites, teleport requests or private messages, should the other
   player be refused (Hypixel style), or should the message just be hidden? Staff bypass? [not built yet - these 3 switches wait for you]
   (`research/Settings-Spec.md` section 6)
2. **SkyyEconomy merge:** go ahead once you have tested the separate Bank 0.1.3, Bazaar 0.1.2 and Auctions 0.1? [yes, next round after your test]
3. **Bags:** do the Mining bag upgrades come from the Cobblestone or the Iron collection? Which collections grow Foraging, Farming, Combat and
   the new Smithing bag? [today every bag is crafted at a Workbench]

## Numbers picked in the beta round (live now)
- **Vault:** 2 free pages, max 10, page 3 costs 50,000 and each next page +25,000. A page bought on one profile is shared by all your
  profiles (Wynncraft style). [as written]
- **Tree Feller:** 1 / 2 / 3 / 4 extra logs on the same height, then the whole layer at max level; 5 s cooldown. [as written]
- **Double Jump:** tier II of the Acrobatics tree (replaces Quick Dodge 1:1), costs 2 Stamina, crouch in mid-air. Or tier III? [tier II]
- **Tree felling:** every felled log pays full Foraging XP and counts for collections; felled leaves pay their normal XP (about 1 each);
  placed logs never pay. [fell.xpFactor 1.0, fell.leafXpFactor 1.0]
- **Party combat XP:** members within 48 blocks in the same world get 50% of the killer's combat XP (the killer keeps 100%). [as written]
- **Menu hover tooltips:** on by default; the book switch turns them off if the stuck tooltip after Esc still happens. Default off? [on]

## Auction House (`research/Auction-House-Spec.md` section 12)
1. Hypixel's fees for our smaller economy: listing 1% / 2% / 2.5%, duration fee 20-1,200, 1% tax above 1,000,000? [Hypixel's numbers]
2. Durations 1h / 6h / 12h / 24h / 48h, default 24h - or up to 7-14 days? [up to 48h]
3. Bazaar items refused on the AH (like Hypixel)? [refused]
4. Never buy your own listing, even from another profile? [never]
5. Creative players: browse and claim only? [yes]
6. 14 listings per profile? [14]
7. Second click for buys of 10,000 coins or more? [10,000]
8. Cancelling keeps the fee (Hypixel)? [kept]
9. `/ah sell <price>` opens the filled-in page for one click (or lists straight from chat)? [page]
10. New listings wait 20 s before anyone can buy? [20 s]
11. `/ah` works anywhere, or later only at an Auction Master NPC in the hub? [anywhere]
12. Late-game items that leave both markets? [none yet - the list is ready and empty]
13. Bid auctions: when and with which rules? [later]
14. Claims of a deleted profile? [kept; admin can regrant]
15. Magic Bags / Accessory Bag on the AH ("contents not included")? [tradeable]
16. Ask before Claim all puts 100,000+ coins in the purse? [yes]

## /trade (`research/Trade-Spec.md` section 20)
1. The 3 s countdown after both click Ready IS the confirm (no extra click)? [yes]
2. Max coins per trade: flat server number, or tied to a level later? [flat, 0 = no cap]
3. Taking damage cancels the trade? [yes]
4. 16 slots per side (4x4)? Bigger? [16]
5. Trades stay private (no chat line to party/guild)? [private]

## Islands (`research/Island-Settings-Spec.md`, live in SkyyIslands 0.5.1)
- Co-op size 5 including the owner. [5]
- Island Admins can't invite co-op members (only the Owner). [can't]
- Admins may expel, ban and untrust visitors/helpers; only the Owner kicks members. [as written]
- Trusted = build only (no harvesting crops, no beds, no chests). [as written]
- No visits to your own old island while you are in someone's co-op. [no]
- Old "build rights" invites became Trusted, not members. [done]
- `/island reset` cooldown 24 h (3 confirms). [24 h]
- Visitor limit 5. [5]
- Biome change: free, unlocks tied to exploration later. [free]
- What visitors may use by default (doors today). [doors, seats]

## In-game server setup (`research/Server-Setup-Spec.md` section 9)
1. Who sees Server Setup? [ops only, node skyymenu.modconfig can be given to staff]
2. Which changes ask for a confirm? [money, penalties, rates, caps, curves, switching a part off, imports, restores, undos]
3. How many old versions of each config file to keep? [20]
4. When a part is off, can players still take out what is theirs (bank withdraw, auction claims)? [yes]
5. Bank interest for the time the bank was off? [no back-pay]
6. NPC shops: buy + sell-back per item, infinite stock by default, optional limited stock + restock timer? [yes]
7. NPC shops in SkyyEconomy 0.1 or 0.2? [0.2]
8. Ranks in their own mod (SkyyRanks)? [yes - built, 0.1 live]
9. Seeded ranks: only "Member"; you make the rest in game? [yes]
10. Chat order `[Rank] [Title] Name`? [yes]
11. Player Settings and Server Setup as two menu versions? [done as 0.2 + 0.3]
12. Island template box size for the future template editor: 3 x 3 chunks, y 96-191? [yes]
13. Hide SkyyClasses' class-switch settings while switching is locked? [hidden]
14. Quest hooks now or with SkyyQuests? [with SkyyQuests]
15. Rank perks later (extra vault pages, bigger parties)? [later]
16. How does a player raise the profile cap above 6? [no default - your call]
17. SkyyRanks before the other mods' settings pages? [done]
18. Warps page can also move the world spawn (with a confirm)? [yes]

## Player Settings (`research/Settings-Spec.md` section 6)
- Settings icon in the menu: slot 51 (bottom row) or next to Mods? [51]
- Anything that should stay always on (never switchable)? [the section 2.3 list]

## Known limits you should know about (not questions)
- A hard server crash within about a second of an auction listing, vault move or trade can leave an item in two places (the forced save
  shortens the window; admins can repair lost claims). It is the same for every mod that stores items.
- Permission nodes of Skyy commands contain the mod version (e.g. `skyy.0.5.1_skyyislands.command.island`), so a `/rank grant` or `deny`
  of one stops applying after that mod updates. Stable names are planned (Server-Setup-Spec 8.4.6).
- A player literally named accept / deny / cancel / claim can't be targeted with `/trade <name>`.
- `/r` (reply), `/hub` (SkyyIslands) and `/p` (party) take over vanilla shortcuts (/redo, CreativeHub's /hub, /prefab's alias) on purpose.
