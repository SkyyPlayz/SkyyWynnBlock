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
- LOCKED 2026-09-25 (Skyy): one-time chat notice about the swing-speed change, plus a free respec. The default was already yes.

## Crossbows stay loaded (`research/Crossbow-Loaded-Spec.md`, SkyySkills 0.4.5 - building after round 6)
- LOCKED 2026-09-25 (Skyy): Archery level 5, Archer class only, crossbows only (not shortbows). [already the live defaults]
- LOCKED 2026-09-25 (Skyy): loaded bolts survive teleports. Was: drop the load and reload once after a teleport. [0.4.5 still wipes on a world change; the next Skills build keeps the load. Relog, death, and profile switch still drop it]
- LOCKED 2026-09-25 (Skyy): keep the big-arrow ability meter across a slot switch. Was no. [0.4.5 still resets it]
- LOCKED 2026-09-25 (Skyy): a sound and a chat hint when the bolts go back in. Was no. [0.4.5 stays quiet]
- LOCKED 2026-09-25 (Skyy): `/settings` switches so a player can turn the meter, the sound, and the chat hint off individually. Was no. [0.4.5 has no player switches]
- APPROVED 2026-09-25 (Skyy), to build: Archery level 15+ upgrades that raise a crossbow's max bolt capacity, up to +4 extra bolts. Not in 0.4.5.
- APPROVED 2026-09-25 (Skyy), to build, late-game only: near the top of the Archer tree, a holstered crossbow reloads itself in about 30 s while you use another weapon. Not an early or mid-tier node. Not in 0.4.5.

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

## Islands (`research/Island-Settings-Spec.md`, live in SkyyIslands 0.5.1)
- LOCKED 2026-09-25 (Skyy): co-op size 5 including the owner. [5, already the default]
- LOCKED 2026-09-25 (Skyy): Island Admins may invite co-op members. Was: only the Owner. [yes; 0.5.2 still defaults coop.adminsInvite to false]
- LOCKED 2026-09-25 (Skyy): Admins may expel, ban and untrust visitors and helpers. Only the Owner kicks co-op members. [as written, already the default]
- LOCKED 2026-09-25 (Skyy): Trusted cannot harvest crops or open chests. Beds are in the visitor set. Crafting stations stay at trusted. [crops and chests stay member]
- LOCKED 2026-09-25 (Skyy): no visits to your own old island while you are in someone's co-op. [no, already the default]
- Old "build rights" invites became Trusted, not members. [done]
- LOCKED 2026-09-25 (Skyy): `/island reset` cooldown 24 h with 3 confirms. [24 h, already the default]
- LOCKED 2026-09-25 (Skyy): visitor limit 10. Was: 5. [10; 0.5.2 still writes defaults.visit.limit=5]
- LOCKED 2026-09-25 (Skyy): biome change is free. Unlocks tied to exploration come later. [free, already the default]
- LOCKED 2026-09-25 (Skyy): visitors may use doors, seats, and beds. Chests and crafting stations stay closed to visitors. Was, briefly: chests and crafting stations open. [beds visitor; chests member; crafting trusted; 0.5.2 still writes beds=member]

## In-game server setup (`research/Server-Setup-Spec.md` section 9)
1. LOCKED 2026-09-25 (Skyy): who sees Server Setup is ops only. The node skyymenu.modconfig can be given to staff. [ops only, already the default]
2. LOCKED 2026-09-25 (Skyy): which changes ask for a confirm are money, penalties, rates, caps, curves, switching a part off, imports, restores, undos. [already the default]
3. LOCKED 2026-09-25 (Skyy): old config file versions kept is 10. Was: 20. [10; skyycfg still defaults KEEP=20]
4. LOCKED 2026-09-25 (Skyy): when a part is off, players can still take out what is theirs (bank withdraw, auction claims). [yes, already the default]
5. LOCKED 2026-09-25 (Skyy): bank interest for the time the bank was off is paid. Players receive back-pay for interest accrued while the bank was switched off. Was: no back-pay. [yes]
6. LOCKED 2026-09-25 (Skyy): NPC shops have buy and sell-back per item, infinite stock by default, and optional limited stock with a restock timer. [yes, infinite stock stays the default]
7. LOCKED 2026-09-25 (Skyy): NPC shops are in SkyyEconomy 0.2. [0.2, already the default]
8. LOCKED 2026-09-25 (Skyy): ranks are in their own mod, SkyyRanks. 0.1 is live. [yes, already the default]
9. LOCKED 2026-09-25 (Skyy): seeded ranks are Member, Admin, and Developer. Admin and Developer are close to the owner and do not get full op. Was: Developer got the rank editor. The rank editing UI is for ops and players with the Owner rank. Was: ops only. Admin and Developer cannot edit rank permissions or create or modify ranks. skyymenu.modconfig does not open it. Ranks stay fully editable in that UI. Was: only Member. [Member, Admin, Developer; 0.1 still seeds only Member; 0.1 still opens /rankadmin for anyone with skyyranks.admin; 0.1 still refuses grants, delete, and ladder moves on the default rank]
10. LOCKED 2026-09-25 (Skyy): chat order is `[Rank] [Title] Name`. [yes, already the default]
11. LOCKED 2026-09-25 (Skyy): Player Settings and Server Setup are two menu versions, done as 0.2 + 0.3. [two, already the default]
12. LOCKED 2026-09-25 (Skyy): island template box default stays 3 x 3 chunks, y 96-191. Future, to build: players upgrade 3 x 3, then 4 x 4, 5 x 5, 6 x 6, 7 x 7, 8 x 8, up to 9 x 9. [3 x 3 default; max 9 x 9 later]
13. LOCKED 2026-09-25 (Skyy): SkyyClasses' class-switch settings are greyed out while switching is locked. Players can see the option and cannot use it. Was: hidden, with one read-only line. Future, to build: class changes unlock later through a special item earned from a quest, or a similar progression gate. [greyed out; 0.1.6 still leaves switchCost and cooldownMinutes off the page]
14. LOCKED 2026-09-25 (Skyy): quest hooks ship with SkyyQuests, not now. [with SkyyQuests, already the default]
15. Rank perks later (extra vault pages, bigger parties)? [later]
16. CONFIRMED intentionally open 2026-09-25 (Skyy): how a player raises the profile cap above 6 is left open. Likely linked to ranks, and undecided. Not a resolved mechanic. [parked; no way above 6 yet]
17. SkyyRanks before the other mods' settings pages? [done]
18. LOCKED 2026-09-25 (Skyy): the warps page does not move the world spawn. Was: yes, with a confirm. World spawn movement is an owner/ops-only command, for example /setspawn. [command, not the warps page]

## Server Setup pages (round 4, live)
- LOCKED 2026-09-25 (Skyy): changing the Furnace / Tannery caps does not ask for a confirm. They stay quick to tweak. [no confirm, already the default]
- LOCKED 2026-09-25 (Skyy): the party members switch does not hide "X kicked Y" and "X invited Y". Those lines are always shown. [no, already the default]
- LOCKED 2026-09-25 (Skyy): SkyyGuilds `onlineMessages` treats off, no, and 0 as OFF, the same as every other on/off setting. That stays. [yes, already the default]
- Profiles: the default cap is now 6 (your 2026-09-24 decision); lowering it never deletes a profile.

## Player Settings (`research/Settings-Spec.md` section 6)
- LOCKED 2026-09-25 (Skyy): the Settings icon sits next to the Mods button (slot 39, left of Mods at 40). Was: slot 51, the bottom row. [next to Mods; SkyyMenu 0.3.2 still uses slot 51]
- Anything that should stay always on (never switchable)? [the section 2.3 list]

## Known limits you should know about (not questions)
- A hard server crash within about a second of an auction listing, vault move or trade can leave an item in two places (the forced save
  shortens the window; admins can repair lost claims). It is the same for every mod that stores items.
- Permission nodes of Skyy commands contain the mod version (e.g. `skyy.0.5.1_skyyislands.command.island`), so a `/rank grant` or `deny`
  of one stops applying after that mod updates. Stable names are planned (Server-Setup-Spec 8.4.6).
- A player literally named accept / deny / cancel / claim can't be targeted with `/trade <name>`.
- `/r` (reply), `/hub` (SkyyIslands) and `/p` (party) take over vanilla shortcuts (/redo, CreativeHub's /hub, /prefab's alias) on purpose.
