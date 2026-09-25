# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `DESIGN-STATUS.md` "Open questions".

## Answer first (they block or shape the next builds)
1. ANSWERED 2026-09-25: **block** (refuse the sender). Was: **Settings menu: refuse or hide?** When a player switches off party invites, teleport requests or private messages, should the other
   player be refused (Hypixel style), or should the message just be hidden? Staff bypass? [not built yet - these 3 switches wait for you]
   (`research/Settings-Spec.md` section 6)
2. **SkyyEconomy merge:** go ahead once you have tested the separate Bank 0.1.3, Bazaar 0.1.2 and Auctions 0.1? [yes, next round after your test]
3. ANSWERED 2026-09-25: Mining bag from **Iron**. Was: **Bags:** do the Mining bag upgrades come from the Cobblestone or the Iron collection? Which collections grow Foraging, Farming, Combat and
   the new Smithing bag? [today every bag is crafted at a Workbench]

## Numbers picked in the beta round (live now)
- LOCKED 2026-09-25 (Skyy): **Vault:** 2 free pages, max 10, page 3 = 50,000 coins, each next page +25,000. Pages are shared across all profiles
  (Wynncraft style). [as written — already the live defaults]
- LOCKED 2026-09-25 (Skyy): **Tree Feller:** same height as the cut. Extra logs 1 / 2 / 4 / 5 / 6 / 10 at levels 1–6. Level 6 jumps to 10 so a
  very large tree is not broken as a whole layer (that could crash). Cooldown 3 s (was 5). Was: 1 / 2 / 3 / 4 extra logs, then the whole
  layer at max. [new-file cooldown is 3; a file still on the old stock `feller.cooldownSec=5` keeps 5 until that line is set to 3. The
  6-level table is the next Trees build — `research/Tree-Fall-Spec.md`]
- LOCKED 2026-09-25 (Skyy): **Double Jump:** Acrobatics tier III (slot 7, replaces Sprinter; Quick Dodge returns to tier II). Jump again
  while already in mid-air, not crouch. Stamina stays 2 (tier III does not name a different cost). Was: tier II, crouch in mid-air.
  [new-file trigger is `jump`; a file still on `acro.doubleJump.trigger=crouch` keeps crouch until that line is set to `jump`. The slot
  move is the next Trees build — `research/Double-Jump-Spec.md`]
- **Tree felling:** every felled log pays full Foraging XP and counts for collections; felled leaves pay their normal XP (about 1 each);
  placed logs never pay. [fell.xpFactor 1.0, fell.leafXpFactor 1.0]
- **Party combat XP:** members within 48 blocks in the same world get 50% of the killer's combat XP (the killer keeps 100%). [as written]
- **Menu hover tooltips:** on by default; the book switch turns them off if the stuck tooltip after Esc still happens. Default off? [on]

## Vault arrows (`research/Vault-Arrows-Spec.md`, live in SkyyVault 0.1.2)
- APPROVED 2026-09-25 (Skyy): cycle pages inside the vault GUI with the existing in-chest Prev/Next arrows. Do not add a second page-switch UI.
- The arrows sit in an extra 5th row, so all 36 slots stay free. If the 5-row chest doesn't fit your screen, switch Server Setup -> Vault ->
  arrow layout to "Inside the page" (the arrows then take the bottom-left and bottom-right slots, Wynncraft-exact). [extra row]
- LOCKED 2026-09-25 (Skyy): buying a page does not use two clicks within 10 s. Server Setup coin threshold `buyConfirmCoins`, default
  50,000. A price below that buys at once. A price at or above it asks "Buy page X for Y coins?" in a confirm dialog. The gold arrow,
  the page Buy button, and `/vault buy` share that rule. [SkyyVault 0.1.2 still uses the 10 s second click; the next Vault build reads
  the row]
- LOCKED 2026-09-25 (Skyy): a plain click turns the vault page immediately, the same as shift-click. Both turn the page at once.
  [the "plain click only lifts; the page turns on put-down" note is not the UX. 0.1.2 turns the page when the server hears the click]

## Berserker, Priest, class kits (`research/Classes-Berserker-Priest-Spec.md` section 8, live in Classes 0.1.6 / Skills 0.4.4 / Profiles 0.1.2)
- LOCKED 2026-09-25 (Skyy), TEMPORARY until healing spells exist: Priest heal stays 25% of the damage to party members within 16 blocks,
  self-heal 50% of that, cap 10 HP per hit and 10 HP/s per player, party only. [current numbers; replace when spells are built]
- LOCKED 2026-09-25 (Skyy): Divinity XP from healing others stays 0.2 XP per HP. Healing yourself pays 0.25 XP per HP (was 0). Max 300 XP
  a minute unchanged. [0.4.5 still pays nothing for a self-heal; the next Skills build pays 0.25]
- LOCKED 2026-09-25 (Skyy): heal chat lines stay on by default, and players can still turn theirs off. At most one line every 10 s (was
  5 s). [new-file `priestHeal.feedbackMs=10000`; a file already on 5000 keeps 5 s until that line is edited]
- ANSWERED 2026-09-25: base Mana 10, Mage/Priest 20, plus Overall Level Health/Mana. Was: **Mana:** vanilla max Mana is 0, so wand casts (25 Mana), spellbook casts (100) and the Mage staff summon (50) never work for a new
  character - only the swings. Give Priests / Mages base Mana? [not yet]
- ANSWERED 2026-09-25: wait for custom weapons. Was: **Priest weapons:** no wand or spellbook can be crafted and almost none drop - the kit's Wood Wand (never breaks) is the only way to get
  one. Add recipes/drops now or wait for custom Priest weapons? [wait]
- LOCKED 2026-09-25 (Skyy): the vanilla Healing Totem (AoE +5 HP/s, endgame recipe) is Priest only (was anyone). [0.1.6 still leaves every
  deployable unassigned, so anyone can throw it until the next Classes build]
- LOCKED 2026-09-25 (Skyy): Root wands, Stoneskin wands, and the Rekindle Embers spellbook count as Priest weapons. Confirms the existing
  yes. No behavior change (they already match the wand and spellbook prefixes).
- LOCKED 2026-09-25 (Skyy): the class kit drops straight into the hotbar immediately when a player selects or changes class. Replaces
  "into storage, about 31 s after a new profile arrives." Overflow that does not fit still waits on `/class kit`. Archer kit stays 64
  arrows. An admin `/profileadmin setclass` still does not hand out a kit by itself. [0.1.6 still uses storage and the 31 s wait]
- LOCKED 2026-09-25 (Skyy), to build: a daily arrow refill for Archer. Arrows only, claimable once per day, so Archers do not have to
  craft every arrow. Not in 0.1.6.

## Swing speed (`research/Swing-Speed-Spec.md`, live in SkyyTrees 0.2.3)
- LOCKED 2026-09-25 (Skyy): Mining Speed max is +40% faster pickaxe swings (was +25%). If 40% is still too slow, vanilla swing timing may
  need adjusting. [new-file `Mining.MSpeed.per=0.016`; a file already on 0.01 keeps +25% until that line is set to 0.016]
- LOCKED 2026-09-25 (Skyy): Chopping Speed II stays renamed Heavy Hatchet. HARD RULE: hatchet swing-speed bonuses apply only to
  tree-breaking and wood-chopping. They must not change weapon-axe combat speed for Berserker or any combat class. Weapon axes get their
  own combat swing-speed stat, untouched by Chopping Speed or Heavy Hatchet. [0.2.3 still speeds every hatchet swing, including hits on
  mobs, and has no combat swing-speed stat yet. Weapon axes are already on other roots, so Chopping Speed does not touch them today]
- LOCKED 2026-09-25 (Skyy): Heavy Pick applies to ore and rock (+40% breaking power at max). Was ore only.
- LOCKED 2026-09-25 (Skyy): Heavy Hatchet max is +100% wood breaking power, so a top hatchet (0.5 power) cuts a log in one hit. Was no,
  keep +40%. [new-file `Foraging.FSpeed2.per=0.05`; a file already on 0.02 keeps +40% until that line is set to 0.05. Chopping Speed
  swing stays +25%. This still must not change weapon-axe combat speed]
- Faster pickaxe hits on mobs stay accepted. Hatchet swings on mobs do not: see the Heavy Hatchet hard rule above. [pickaxe yes; hatchet no]
- A Farming sickle speed node later? Accessories/gear adding swing speed later? [not now]
- One-time chat notice about the change + free respec. [yes]

## Crossbows stay loaded (`research/Crossbow-Loaded-Spec.md`, SkyySkills 0.4.5 - building after round 6)
- Archery level 5, Archer class only, crossbows only (not shortbows)? [yes]
- Keep the load across teleports? [no - reload once after a teleport]
- Keep the big-arrow ability meter too? Sound/chat hint when the bolts go back in? Personal /settings toggle? [no]

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

## Server Setup pages (round 4, live)
- SkyySacks: should changing the Furnace / Tannery caps ask for a confirm (danger row)? [no confirm]
- SkyyParty: should the "party members" switch also hide "X kicked Y" and "X invited Y" lines? [no - always shown]
- SkyyGuilds: `onlineMessages` now treats off / no / 0 as OFF like every other on/off setting (before: only the word false). OK? [yes]
- Profiles: the default cap is now 6 (your 2026-09-24 decision); lowering it never deletes a profile.

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
