# Skyy's review: test list 84-116 + open questions (2026-10-14)

A snapshot for checking on GitHub. The living files stay the source of truth: TEST-CHECKLIST.md / docs/tests/2026-10.md (tests)
and OPEN-QUESTIONS.md (questions). Every question below is already running on its default in [brackets] - answer any you want changed
(a PR comment is fine; the main session records it word for word in docs/answered/ and closes it).

Big picture: STATUS.md. Before testing: make a FRESH profile for the 3 starter islands; `/zone 1` for the new zones; send the
server AND client logs afterwards (the ability rune keys are the big unknown - `/cast` is the backup).

## 1. Test list at a glance (84-116)

- [ ] 84. AUTO-PICKUP 2: F-harvest to the Void, Q-drop not eaten, Void full -> inventory -> feet (pet kills wait for SkyyPets)
- [ ] 85. LOST TOOL: /pickaxe etc. summon your exact tool from chest / Vault / Requip, else an exact copy; one working tool only
- [ ] 86. TOOL PERKS: Vein Mine +1 ore / level, Tree Feller on the lifelong tool only, cap 8
- [ ] 87. REBIRTH R1+R2: skills unchanged, half Farming XP above tool tier, /rebirth Nexus page + tooltip (admin view, feature OFF)
- [ ] 88. HARVEST GATE: crops 2+ tiers above your hoe refused (click + F), 1 up = half XP
- [ ] 89. PET OWNER key: ready line names pets:fn:ownerOf (pet-kill loot waits for fighting pets, SkyyPets 0.4)
- [ ] 90. AH CLOSEALL: /ahadmin closeall (+ confirm) cancels your listings to claims, once
- [ ] 91. VAULT FETCH hook: /vault info normal + ready line (the /pickaxe part comes with SkyyGear 0.3.5)
- [ ] 92. LOST LOOT: new pile looks, reveal cards, /exploreadmin airdrop supply drop claim once
- [ ] 93. REBIRTH R3: /rebirthadmin dryrun / rebirth / crashtest on a test profile, coins pay again x0.9
- [ ] 94. SHARDS: /shardadmin give, place on island, Enter, Collect, Grow, menu tile
- [ ] 95. ABILITIES: Ability 2/3 + crouch cast Mage / Priest runes; /tree class ability panel; levels + modifiers; send logs (U1-U10)
- [ ] 96. QUESTS: /questadmin npc add board / marlow, markers, daily jobs, pole once
- [ ] 97. SIGILS: apply on the Anvil, AH yes / Bazaar no; Mining armor follows Mining level; hoe tills an area
- [ ] 98. ADMIN PAGE: /modconfig admin, 4 tabs, confirm buttons, permission hiding
- [ ] 99. REBIRTH TREE: /rebirthadmin points all 50, buy / rows / refund; Continue closes AH listings
- [ ] 100. TOTEMS: Totems tab, place / pick up exact tier, craft, booster; shard credit counts
- [ ] 101. PERFECT DODGE + Fishing / Ranching / Orchard XP (/skills stats fishing)
- [ ] 102. GEAR 0.3.5: /pickaxe from closed Vault, bare hands = Crude on crops, identify reveal cards, /pole lifelong rod, multitool after rebirth 1
- [ ] 103. MONK + ASSASSIN: Enable in /tree class, Ability 2/3 + crouch casts, God Killer on a boss, per-ability modifiers
- [ ] 104. HUD: Fishing / Ranching / Orchard lines, Farming (F / R / O), ability names show (Lv N)
- [ ] 105. ECON: /skills shows 12 rows, coin factor 0.8 row + Undo, AH buy from own other profile refused, /rebirthadmin crashtest parses
- [ ] 106. REBIRTH 0.3.2 + GUILDS 0.1.8: admin rebirth resets lifelong tools, Void-Forged Pick node, guild bank coins stay with the depositing profile
- [ ] 107. SOUNDS: /soundtest list / next / more, quest + reward + NPC + portal + pet + claim + interest sounds, Server Setup sound rows; Admin page rebirth buttons
- [ ] 108. SHARDS 0.3: /shardadmin give <you> <kind> for the 5 new shards, enter, collect, compactor / time compressor, Soul Cage; fish / animal / fruit collection XP to the new skills
- [ ] 109. WARRIOR / BERSERKER / ARCHER: ability keys + crouch alts, shields Warrior-only, Blood Frenzy toggle, Banner, nets, Explosive Arrow; send logs
- [ ] 110. REBIRTH STATS + SKILL SOUNDS: level-up / overall / perfect-dodge sounds, Vitality / Focus nodes raise max Health / Mana (admin test)
- [ ] 111. SEARCH: /settings + /modconfig search find settings across mods, Go to jumps; Mod sounds switch; Admin Shards buttons
- [ ] 112. SOUNDS 2: Void full / upgrade, collection tier, big /pay, accessory equip / upgrade, Bazaar buy / sell, AH buy / sell / claim, shard collect / grow / totem; Mod sounds switch mutes them
- [ ] 113. GATHERING ARMOR: bark / crop / angler sets level + tier up, pole perks on /toolpoints, gear sounds
- [ ] 114. SPELLBLADE: Momentum, Breach + Sunder, Imbue element; rebirth slots 3-4; Fishing tree Sea Legs; Farming tree uses the average
- [ ] 115. 3 STARTER ISLANDS: fresh profile -> island 1 / 2 / 3, gather, crude tools, bridge, tasks 11 + 19 tick; old islands unchanged
- [ ] 116. ZONES: /zone 1-5 floating islands (new world skywynn_zones), /zone info, Zone 5 Onyxium; /zone old = old island

## 2. Test steps (each section = one deploy)

### 84. AUTO-PICKUP 2: SkyySacks 0.8.4 + SkyyMobs 0.1.8 (harvest to Void, pet-kill path) (DEPLOYED 2026-10-14 05:58, backup deploy-20261014-0558)
1. Plant wheat, let it ripen, press F: wheat + seeds go into the Void (Farming) with a "Wheat > Void" card (the vanilla "picked up" popup may still flash).
2. /pd: the Farming count went up; the wheat is not in your inventory.
3. Fill the Farming part of the Void, harvest: the wheat stays in your inventory.
4. Inventory full of junk, Void has room: harvest goes to the Void, never on the ground.
5. Inventory AND Void full: the extra drops at your feet.
6. Right after harvesting, press Q on wheat: it drops normally (does not vanish into the Void).
7. Sickle through ripe crops: Farming XP still comes, crops go to the Void, one card per item.
8. Crop collection + any gather quest still count after F-harvesting.
9. Replant after harvesting - tell me if seeds should stay in the inventory instead of the Void.
10. Server Setup: switch off "Auto-pickup: block drops", read the help line, harvest (wheat stays in inventory, no card); switch it back on.
11. F on a loose rock / stick: it goes into the Void.
12. Kill mobs: drops + top-damager loot as before. Pet kills do nothing new yet (needs a SkyyPets update).
### 85. LOST TOOL: SkyyGear 0.3.2 (exact tool back / summon) (DEPLOYED 2026-10-14 05:58, backup deploy-20261014-0558)
1. Put your pickaxe in a chest, close it, walk a little away, type /pickaxe: the SAME pickaxe comes back (name, rarity, lines) and the chest is empty.
2. Put it in a chest and close at once, /pickaxe: you get the real one or an exact copy - tell me which.
3. Chest still open with the pickaxe inside, /pickaxe: it jumps into your inventory.
4. Vault OPEN with the pickaxe: /pickaxe pulls it out. Vault CLOSED: you get an exact copy and the message says it is in your Vault.
5. Pickaxe in Requip, /pickaxe: it comes out of Requip.
6. Inventory full + pickaxe in a chest, /pickaxe: "No room", the pickaxe stays in the chest.
7. Pickaxe in a chest, go far away / another world, /pickaxe: exact copy + a message why. /pickaxe again: wait about 600 seconds.
8. Right after that, put the copy in Requip and /pickaxe: it comes out with no wait.
9. Go back and take the original out of the chest: the original works again and the copy vanishes - only one pickaxe mines.
10. Repeat step 7, reforge the copy on the Anvil, then take the original: the copy stays yours, the original shows "Retired"; /lifelong on it refuses ("exact copies of each other").
11. A pickaxe already in a chest BEFORE this update gives a copy (chests are remembered from now on).
12. With a 2nd player: they open the chest holding your pickaxe while you /pickaxe - it disappears from their view at once.
13. /toolpoints: a tool you are not carrying says "Not on you - /pickaxe brings it back", not cut off.
### 86. TOOL PERKS: SkyyTrees 0.3.6 (Vein Mine + Tree Feller from the lifelong tool) (DEPLOYED 2026-10-14 05:58, backup deploy-20261014-0558)
1. /toolpoints -> Tools tab: Vein Mine (pickaxe) and Tree Feller (hatchet) can be bought (no "comes with the next SkyyTrees update").
2. Iron (T2)+ lifelong pickaxe with 3+ free Upgrade Points: buy Vein Mine 1 (3 points; levels 2 / 3 cost 5 / 8 and need T3 / T4).
3. Holding it, mine one ore of a big vein: "Vein Burst! +N ore" is exactly 1 more than the Mining tree alone gives (+1 with no tree Vein Burst).
4. Same ore with a different pickaxe: back to the tree-only number.
5. Optional: levels 2 and 3 each add one more ore; tree + tool never past level 8.
6. Tree Feller 1 on an Iron+ lifelong hatchet, chop the bottom log of a wide tree: "+N logs" goes up if your Foraging Tree Feller is 4 or lower, same at 5+. Another axe: back down.
7. Mining / chopping speed feel unchanged.
8. Switch profile, mine + chop: the bonus follows the profile you are on.
### 87. REBIRTH R1+R2: SkyySkills 0.4.35 + NEW SkyyRebirth 0.1 (feature OFF) (DEPLOYED 2026-10-14 06:26, backup deploy-20261014-0626)
1. Join and open /skills: every level, XP bar and "level X of Y" looks exactly like before.
2. Break a crop one tier above your hoe: about half the usual Farming XP. A crop your hoe matches: full XP.
3. A crop two tiers above your hoe: also about half XP.
4. Sickle swing on crops one tier above your sickle: half XP; matching sickle: full XP.
5. Harvest by hand with F: XP as before, never halved.
6. Server Setup -> Skills -> gathering: set "Farming XP one tier above your tool" (0.5) to 1, step 2 now gives full XP; set it back to 0.5.
7. As admin type /rebirth: dark "NEXUS OF THE VOID" circle in the middle, 8 coloured arm names with rows of dark squares; left panel "Your rebirth", "Nexus asleep", "Rebirths 0 / 10", red "Rebirth is OFF (admin view)"; nothing overlaps.
8. Hover the Nexus: a tooltip lists REQUIREMENTS, the Bazaar / AH line and WHAT YOU WOULD GET. Tell me if no tooltip shows or you get disconnected.
9. Requirement lines: "Class level X / 100", "Rebirths done 0 / 10"; on someone else's island the place line says NO, on your own island / hub OK.
10. Hit a mob and reopen /rebirth at once: "NO In combat - wait N s".
11. Click Close: the page closes.
12. A non-admin types /rebirth: only the chat line "Rebirth is not switched on on this server yet."
13. Server Setup -> Rebirth: 6 settings, "Rebirth (whole feature)" off.
14. OPTIONAL caps test (game closed): note your coins; back up Skyy_SkyyRebirth\players\<profile key>.properties and Skyy_SkyySkills\players\<profile key>.properties; put n=1 in the rebirth file; start: /skills says "of 110" (Exploration stays "of 100"), no false OVERALL LEVEL UP; /rebirth shows "Rebirths 1 / 10" and "Void-Touched II". XP already past 100 pays its coins once - expected.
15. OPTIONAL Nexus awake: switch Rebirth ON (confirm question), max your class with /skills xp, own island, no combat, /rebirth: green "Nexus awake", only OK lines, tooltip ends "Every requirement is met - the rebirth button comes in a later update"; a non-admin can now open it. Switch it back OFF.
16. OPTIONAL max (game closed): n=10 -> "Max rebirths reached", every arm "max reached", /skills caps "of 200" (Exploration 100).
17. After the optional tests, with the game closed, restore both backed-up files.
### 88. HARVEST GATE: SkyyGear 0.3.3 (no harvesting 2+ tiers above your hoe) (DEPLOYED 2026-10-14 08:35, backup deploy-20261014-0835)
1. Hold a Crude or Copper hoe and left-click a ripe Potato, Cauliflower or Tomato: the crop stays, nothing drops, a red "Too tough for your ... Hoe" popup says it needs at least an Iron hoe.
2. Same hoe, press F on that ripe crop: also refused with the same popup, the crop stays ripe.
3. Same hoe on a Carrot (one tier up): it breaks, less Farming XP, no bonus drops.
4. Same hoe on Wheat: breaks normally.
5. Iron hoe on a Potato: breaks at half XP; Thorium hoe: normal.
6. Swing a Crude sickle over Potatoes: every ripe crop is still harvested (sickles stop at Iron, so they are never two tiers below a crop).
7. Empty hand (F or punch) on a ripe Potato: still harvests (open question).
8. Server Setup -> Gear: turn "Tool tier gate" off, the Crude hoe now breaks the Potato; turn it back on.
### 89. PET OWNER: SkyyPets 0.2.5 (pets:fn:ownerOf) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Close the game. Deploy SkyyPets 0.2.5 on its own; SkyySacks 0.8.4 and SkyyMobs 0.1.8 are already live.
2. Start the world and open the server log. The `[SkyyPets] 0.2.5 ready` line should include `pets:fn:ownerOf (pet kills: loot + credit to the owner)`.
3. The SkyySacks ready line should say "pets count for their owner". If it says "not fighting yet", SkyySacks just started before SkyyPets, and the lookup still works when it's used.
4. Put a pet in your pet slot and a fighter in your summon slot. They follow you as before, and your attacks pass through them.
5. Kill a mob yourself. The loot still goes straight to your inventory or the Void.
6. Log out and back in, then change worlds. Your pets despawn and come back as before, with no errors in the log.
7. "Pet kills a mob -> loot to you" and "pet damage makes you top damager" can't be tested until pets fight in SkyyPets 0.4. Add both to the test list for then.
### 90. MARKET CLOSEALL: SkyyBazaar 0.1.11 + SkyyAuctions 0.1.5 (rebirth R4 market side) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Make 2 listings with `/ah sell <price>`.
2. On a second account, buy one of them. Don't claim the coins on the seller.
3. On the seller, type `/ahadmin closeall`. It should show 1 listing as "would be cancelled" and 1 line "SOLD - N coins unclaimed - BLOCKS".
4. Type `/ahadmin closeall confirm`. It should say `-> err:blocked:0:1`, then `now open: ok:1:1:...`. The listing should still be up in `/ah`.
5. Open `/ah` > Manage and claim the coins. Your purse should go up by the sale amount, once.
6. Type `/ahadmin closeall confirm` again. It should say `-> ok:1`, then `now open: ok:0:0:...`, and you get the "listing was cancelled" chat line.
7. In Manage, claim the cancelled item. You should get it back exactly once.
8. Type `/ahadmin closeall confirm` once more. It should say `ok:0`.
9. Make a listing, close the game, restart, and run `/ahadmin closeall confirm`. It should say `ok:1`.
10. `/bazaar` should trade as before. It has nothing to close.
### 91. VAULT FETCH: SkyyVault 0.1.6 (lifelong tool fetch hook) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Put your lifelong pickaxe in your Vault and close the Vault.
2. Type `/pickaxe`. The same pickaxe (same rarity, rolls and level) lands in your inventory, and the Vault slot is empty when you open `/vault`.
3. Open `/vault`, keep it open on the page with the pickaxe, and type `/pickaxe`. You should see it vanish from the Vault window and appear in your inventory.
4. Fill your inventory completely, put the pickaxe in the Vault, and type `/pickaxe`. It should refuse and the pickaxe should stay in the Vault.
5. Switch profile, wait 30 seconds, and type `/pickaxe` on the other profile. It must not take the first profile's pickaxe.
6. Right after a profile switch, type `/pickaxe`. It should say to wait a moment, not make a copy.
7. `/vault info` should look normal, with no "items this server does not have" line.
### 92. LOST LOOT: SkyyExploration 0.2.8 (new looks, reveal page, supply drops) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Close the game. Deploy as usual (backup, then `deploy_set --yes`), then open the HUD mod world.
2. Type `/exploreadmin luggage tier 1`. Tier I should sparkle orange.
3. Type `/exploreadmin luggage clear`, then `luggage tier 3`: it should sparkle white and glow. Clear again, then `luggage tier 4`: it should be a gold treasure pile ("Lost Treasure").
4. Press F on it. The chat line shows the loot and a window opens with face-down cards. Click "Open next", then "Open all". A Rare or better bag plays a sound and the bottom line says "Best find: ...". Click Close.
5. Run `/exploreadmin luggage tier 2`, press F, then press Esc right away. Check the loot is still in your inventory.
6. Run `/exploreadmin luggage clear`, then `/exploreadmin airdrop`. Fireworks should fall from the sky 10–20 blocks away, with a chat line giving distance and direction. After about 10 s a crate lands with a tall light beam.
7. Walk about 60 blocks away and check the beam is still visible. Then press F on the crate: the reveal page opens and the crate is gone. Press F on that spot again: nothing is left.
8. With a second account, run `/exploreadmin airdrop` and have both players press F at once. Only one gets loot; the other sees "already claimed".
9. Run `/exploreadmin airdrop` again and leave the crate alone for 10 minutes. It should disappear.
10. Run `/exploreadmin reveal`. Three mystery bags flip into an Iron Sword, an Iron Chestplate and a Mithril Sword. Check that "< Back" opens `/explore`. This is the identify animation SkyyGear will use.
11. Turn off "Loot reveal page" in your player settings and claim one. You should get the chat line only, and `/exploreadmin reveal` should say it is switched off.
12. In Server Setup → Exploration, check the tab is called "Lost Loot", its rows say Lost Loot, and the Airdrops tab has 13 rows.
13. Type `/exploreadmin stats` and check the supply drop counters show.
14. Send screenshots of the sparkles, the treasure pile, the falling fireworks, the beam from far away, and the reveal page.
### 93. REBIRTH R3: SkyyRebirth 0.2 + Skills 0.4.36 + Coins 0.1.7 + Bank 0.1.11 + Profiles 0.1.13 (rebirth OFF) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Use a throwaway test profile on an account with `skyyrebirth.admin`. Have at least 1M coins split across purse and bank. Note `/skills`, `/balance` and `/bank status`.
2. Open Server Setup → Rebirth. Check that "Rebirth (whole feature)" is off and that its help says Bazaar / AH are not checked yet. Check the bank bonus rows: scale 0.25, max per rebirth 1, max in total 3. Under SkySkills, check the level-coin factor 0.9.
3. Type `/rebirthadmin dryrun`. Chat shows each mod's numbers and "Would commit …". Nothing changes.
4. Type `/rebirthadmin rebirth`, then again within 10 s. Chat says "rebirth 1 done … Void-Touched I", and the bank bonus is above 0.00 %.
5. Every skill except Exploration is 0, the purse and bank are 0, and `/bank status` names a "rebirth bonus".
6. Type `/rebirth`. It shows "Rebirths 1 / 10" and +10 caps.
7. Earn a few skill levels. The level coins are 90 % of normal.
8. Type `/rebirthadmin crashtest 3` twice. `/rebirthadmin status` shows the rebirth OPEN and "stopped after point 3".
9. While it is stuck, try `/pay`, a bank deposit and a profile switch. All three are refused.
10. Type `/rebirthadmin recover`, or restart the server. It finishes within seconds: rebirth 2, a single reset, and the bonus added once (capped by the max per rebirth and the +3 total).
11. Repeat with `crashtest 1` and a restart. Nothing changes on the profile.
12. Deposit some coins after the rebirth. After the next daily payout, `/bank status` shows more interest than the brackets alone.
13. Optional, with no open Bazaar orders or AH listings: Turn "Rebirth (whole feature)" on. Have your class at max, be on your island and out of combat, then open `/rebirth`. Press Rebirth once. The note should read "Resets skills, purse and bank to 0! Press again within 10 s." A fast double-click does not start the rebirth. A second press 1–10 s later closes the page, and chat says "The void is imprinting…" and then "done". Turn the feature off again afterwards.
### 94. SHARDS: NEW SkyyShards 0.1 + Islands 0.5.8 + Menu 0.3.22 (Farming shard) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Close the game. Deploy SkyyShards 0.1 + SkyyIslands 0.5.8 + SkyyMenu 0.3.22 together, then start the game.
2. In Server Setup → Collections, add `,shard` to "Sources other mods may credit".
3. In Server Setup → Shards, check the rows: `shards.on` on, "Co-op may collect and upgrade" off. Set "Grow to Medium: collection tier" to 0.
4. Use `/give` for 5 `Skyy_Ench_Wheat` and at least 8 `Plant_Seeds_Wheat_Eternal`. Make sure you have at least 10,000 coins (5,000 for storage + 5,000 for Grow).
5. Run `/shardadmin give <you>`. Open the SkyWynn Menu → Shards tile and click Enter Shard. It should refuse with "No Farming Shard is placed".
6. Go to `/island` and place the shard. "Your Farming Shard is placed" should appear about 1 s later. Try placing a second one: it should be refused.
7. Right-click the portal. The menu opens on Collect and shows Wheat Island 1, with Enter Shard and Pick up Shard. The Totems tab row should say "60 items / hour - kept in the shard until you collect".
8. Click Enter Shard. You should land on the plaza, with sparkles above the totem pillar.
9. Try breaking soil, placing a block, or hoeing. All of it should be refused. Breaking or harvesting wheat should work.
10. Jump off the island edge. You should respawn with every item kept.
11. Right-click the stand and click Back to Island. You should land at your portal.
12. Wait about 5 minutes and note the stored amount N. Click Collect all. You should get N Wheat and exactly 2×N Farming XP, and the Wheat collection should go up by N. The tab should then say "Last collected ... ago".
13. Fill your inventory, leaving fewer free spaces than the stored amount, then Collect. What does not fit should stay in the shard, and the message should say so.
14. On the Upgrades tab, buy Storage tier 2 (1 Enchanted Wheat + 5,000 coins). On the Islands tab, pick slot 1 and Grow (8 seeds + 5,000 coins). Enter again: the island should be bigger.
15. Have a co-op member right-click your portal. They should see Enter but no Pick up. Enter should work; Collect should be refused. A visitor should be refused.
16. Run `/sethub` somewhere other than the default spawn. While you are inside your shard, switch profile with `/profiles switch`. Within about 1 s you should land at the `/sethub` spot, and the menu should refuse.
17. On your second profile, get and place a shard. Enter: it should be a separate world with its own storage.
18. Set `shard.maxLoaded` to 1. Have a second player with their own shard try to Enter while yours is loaded. They should get the queue message, then be told when it is free. Set it back to 20.
19. Turn `shard.coopCollect` on. The co-op member's Collect should now work and pay them. Turn it off again.
20. Leave the shard empty for 2 minutes, then run `/shardadmin info <you>`. It should say "(unloaded)". Enter again and everything should still be there.
21. Restart the server. Storage, the placed portal and the island size should all be kept.
22. Turn `shards.on` off. Enter and Collect should say "Shards are switched off". Turn it back on.
23. Click Pick up Shard twice. The shard comes back to your inventory, and `/shardadmin info` should show the stored amount no longer rising. Place it again: "placed" appears and production starts.
24. If it's convenient: reset your island. Open the Shards tile. It should say "Your island was reset", and storage should stop rising. Click Pick up Shard twice, then place it on the new island.
### 95. ABILITIES IN THE TREE: SkyyClasses 0.1.22 + SkyyTrees 0.3.7 (rune keys, ability panel, levels + modifiers; Mage + Priest) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Deploy SkyyClasses 0.1.22 and SkyyTrees 0.3.7, then join as an existing Mage holding a staff. About 8 s after joining, chat says "Your ability Meteor is off: open /tree, class tab, and click Enable (free)…". Press Ability 2: nothing happens, because the slot has no rune yet. Type `/cast 1`: it refuses with "enable it in your class tree".
2. Type `/tree` and open the class tab. Click A1 (Meteor, "Unlock free"). Within about 2 s Meteor's rune is in the Ability 2 slot with its icon.
3. Press Ability 2: Meteor casts, and chat shows "Meteor! -.. Mana". Press it again at once: "Meteor is ready in .. s", and no Mana is spent. When the cooldown ends, `/cast 1` also casts Meteor (the backup).
4. Raise Sorcery to 30 with `/skills xp sorcery 3.1m`, repeating until `/skills` shows 30. Then click A2, A3 and A4 (all free). Mana Barrier is now in the Ability 3 slot.
5. Hold crouch and press Ability 2, then Ability 3: your two alts cast. On the A1-alt card, "Other alt" switches between the two A1-alt choices.
6. Click M1A and M1B (free). Type `/classadmin abil <you> maxlevels`: chat names the backup file it made. Every ability is now at its top level and every modifier is unlocked.
7. On Meteor's card, press slot 1 and pick Power+, then slot 2 and Power+ again. Both slots show Power+ (double effect). Change slot 2 to Echo and cast Meteor: a weaker second Meteor lands 1 s later. Then use Unequip on slot 2: it shows "Empty slot 2".
8. Press Swap on Meteor, then "Move here" on Mana Barrier. The cards swap, and so do the runes in the rune bar.
9. Switch profile: the cards and runes follow the other profile, and an active Ward is dropped. Relog: your cooldowns are cleared.
10. As a Mage, take any game rune from the creative item list and put it in the Ability 2 slot (empty it first). Press Ability 2: nothing casts, and one line says "Game runes are blocked for Mages. Move … to your rune bag". Move it out, and your Meteor rune comes back within about 2 s.
11. As a Priest: in Server Setup, Trees, set "Test: extra AP" to 20. Use `/skills xp divinity 3.1m` until Divinity is at least 65. In `/tree` class, click A1–A4, then buy the path nodes up to PB3 (Layered Ward) and PB4 (Spirit Shield).
12. Cast Shield Bubble: its line says "Two layers…", and the bubble lasts 2 s less.
13. Take a killing blow, for example a long fall: you are saved at 20% Health, and the line says "Spirit Shield: 4 s bubble."
14. Optional: `/classadmin abil <you> resetlevels` puts every level back to Lv 1, and the line names its backup file. Set "Test: extra AP" back to 0 afterwards.
15. If you want to run `/aprobe`, use a profile that isn't Mage or Priest, or turn "Ability rune keys" off first.
16. Afterwards, send both the server and client logs so I can check U1–U10.
### 96. QUESTS Q3: SkyyQuests 0.3 + Hud 0.3.23 + Fishing 0.1.4 (markers, board + daily jobs, Marlow pole) (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Press F on the Quest Board on a profile still in the tutorial: the tutorial's "Visit the hub" quest-board step completes.
2. Press F on Marlow and choose "Not now": no pole, the line does not start. Press F again: he offers the pole again.
3. Two players on different profiles stand by Marlow. One has a catch to show and sees a "?". The other has not started and sees a "!". Each sees only their own sign.
4. Turn on Server Setup "Board from anywhere", then run `/quests board` far away: it opens. Turn it off: it tells you to go to the board.
5. Stand in another world and run `/questadmin npc add marlow`, then go back to the pier. Within a few seconds the old "!" is gone and there is no "!" over empty ground.
6. Remove SkyyFishing (or test on a set without 0.1.4): Marlow has no floating "!" and says the fish are not biting.
7. Get the pole, re-rig it at the Fishing Bench (or craft the Copper rod from it), then have an admin run `/questadmin repay` for the pole claim. No second rod arrives.
### 97. SIGILS + ARMOR LEVELS + HOE AREA: SkyyGear 0.3.4 + Armory 0.1.24 + Collections 0.2.13 (DEPLOYED 2026-10-14 11:04, backup deploy-20261014-1104)
1. Type `/give <you> Skyy_Sigil_Legendary 2`, `/give <you> Skyy_Sigil_Rare 1` and `/give <you> Skyy_Sigil_Mythic 1`. Check the icons in your hotbar and in your hand.
2. Hold a Common sword and type `/upgrade`. The Sigil strip should read like "Rare Sigil (x1): Normal -> RARE" in a big font, with no "Reforge" tail.
3. Click "Other" to show the Legendary Sigil, then "Apply sigil", then "Confirm sigil". The item turns Legendary at once and one Legendary Sigil is used. Reforge it and check the empty slots fill.
4. Try the Rare Sigil on that item. It should refuse, because Sigils only go up.
5. Try the Mythic Sigil on that Legendary item. "Other" should never show it. With only the Mythic Sigil in your inventory, the strip says "Mythic is boss-only - a Mythic Sigil cannot be used on this server." Then turn on Server Setup -> Gear -> "Mythic Sigil works on the Anvil" (`sigil.mythicUse`), apply it, and check the item turns Mythic. Turn the row off again.
6. Pick a Copper Mining helmet on the Anvil while carrying a Sigil. The strip should read "Set rarity stays - gathering armor levels with your Mining and tiers up on the Anvil instead." in a readable font.
7. Put a Sigil on the Auction House (it should list). If the Bazaar shows a Sigil, try selling it there (it should refuse with "never sold on the Bazaar").
8. Wear a Copper Mining helmet. Its "[Lv N]" should match your Mining level (up to 18). Break ore to level up Mining and check the helmet updates within about a second.
9. With Mining 15 or higher and one Enchanted Iron Ingot, upgrade the Copper helmet on the Anvil. It should become an Iron helmet, still green Set, at your level.
10. On your island, right-click dirt with your lifelong hoe. Crude should till 1 block, Copper or Iron a 3x3, Thorium a 5x5. Blocks under stone should stay untouched. Then plant seeds on an edge block and the centre block and check both behave the same (they accept seeds and look and dry the same).
11. In the hub, the same hoe should till only 1 block. Left-click tilled soil with the hoe and check nothing extra gets tilled.
12. Kill a Duke, Chieftain, Dragon, Guardian (including Golem_Guardian_Void) or Hedera in Zone 2+ several times and watch for a rare Sigil. Yetis, Skeleton Elites, Rex and every other Golem (Firesteel, Crystal) should never drop one.
13. Check these Server Setup rows exist with their help text: Gear: `part.sigils`, `sigil.mythicUse`, `hoe.areaOn`, `hoe.area`, `hoe.areaElsewhere` Armory: `sigil.drops`, `sigil.bossWords`, `sigil.chance.*`, `sigil.zone.*`
14. Reach Wheat collection tier VI, or join if you're already past it. With SkyyProfiles loaded, the Unique Sigil should arrive about 30 to 60 seconds after the tier-up or join, with a chat line. The collection page shows "+1 Unique Sigil" on tier VI. Join again and check you don't get a second one.
15. Switch to a profile that is already past tier VI (with nothing owed on the old profile). The Sigil should arrive about 30 to 60 seconds later, on the new profile only.
### 98. ADMIN PAGE: SkyyMenu 0.3.23 (/modconfig admin) (DEPLOYED 2026-10-14 12:42, backup deploy-20261014-1242)
1. Log in as an op and type `/modconfig admin`. A window titled "Admin" opens with the tabs Server, Economy, Players and Diagnostics.
2. Type `/modconfig`: there is an "Admin" button left of the search box, and it opens the same page.
3. Server tab: click "Reload ranks". A green line says it ran, the answer shows in chat, and the page stays open.
4. Click "Set hub here" once. It turns red and says "Press again". Wait more than 10 s, then click it once. The line says "The 10 s ran out", and nothing has run yet. Wait about a second and click it again. The hub is now set, so only do this where you want the hub. Two clicks less than half a second apart count as one click.
5. Players tab: the Player box shows your name. Use < and > to pick someone, then click "Class info". Chat shows that player's class.
6. Type `a b` into the Text box and click "Go to zone" (Server tab). A red line says no spaces, and nothing runs.
7. Economy tab: "AH status" prints the status in chat, including "paused false". Click "Pause AH" then "AH status", which now says "paused true". Click "Resume AH".
8. Economy tab: "My AH close preview" lists what would close on your own profile and changes nothing. Only press "Close my AH listings" twice on a test profile.
9. Economy tab: "AH listings" shows the open count next to the command.
10. Players tab, page 2: click "Airdrop here" once. One crate drops. Double-click it fast and only one more drops.
11. Players tab: "Quest places", then "Mining spot here". Chat confirms, and "Quest places" now lists hub.mining. Repeat for Foraging, Farming and Fishing at the real spots.
12. Players tab: "Quest NPCs", then "Quest Board here". The Board appears, and pressing it again does not make a second one.
13. Players tab: "Rebirth status" answers in chat.
14. Type a guild's tag into the Text box and click "Guild info". Chat shows the guild.
15. Players tab has 2 pages: use "Next >" and "< Prev" at the bottom.
16. Diagnostics tab: lines show how many Skyy mods are running and any with a different version. "CPU stats" and "Memory stats" answer in chat.
17. A non-admin types `/modconfig admin` and gets "no permission". A test account with only `skyyauctions.admin` plus `skyymenu.modconfig` sees only the 10 Auction House buttons.
18. Bottom buttons: "< SkyWynn Menu" goes back, "Server Setup" opens Server Setup, and "Close" or Esc closes the page.
### 99. REBIRTH TREE + CONTINUE: SkyyRebirth 0.3 (R4 + R8, feature OFF) (DEPLOYED 2026-10-14 12:42, backup deploy-20261014-1242)
1. With the game closed: back up and deploy. Stay an admin and leave Rebirth off (Server Setup > Rebirth > "Rebirth (whole feature)").
2. Make a spare test profile in the profile menu and switch to it. Do steps 3-13 on that profile only. Step 9 really resets skills, purse and bank, and nothing undoes the rebirth count.
3. Server Setup: "Rebirth tree" should show 9 rows: price growth, levels to open a row, and the 7 node strengths. "Rewards" should show 2 new rows: All stats per rebirth, All stats cap. Changing "Tree price growth" or either stats row should ask for a confirm. Cancel it.
4. `/rebirthadmin points all 50`, then `/rebirth`. Row 1 should be open, row 2 should show "0/8" and the rest should be dark. The footer should say "8 levels in a row open the next row".
5. Click a Mining row 1 node. The left panel shows its name, cost and your points. Press Buy: the disc changes colour and the points go down. Double-click Buy fast: only one level is bought.
6. Buy 8 levels in Mining row 1: row 2 opens, and a row 3 node says "Locked". The Void Dust node should read "+25 % Mining Dust" at level 1.
7. Change "Wisdom node: XP a level" to 3, then reopen /rebirth. The Mining Wisdom text should show the new number. Set it back to 2.
8. Keystone: Run `/rebirthadmin points mining 500`. Buy 8 levels in each of Mining rows 1-4 (row 5 is locked until row 4 holds 8). Then buy the Mining keystone. `/rebirthadmin status` should show "Title: Mining Ascendant" and the Mining points without a cap at 1000. Log out and back in, and later restart the server. The levels, points and title should all be kept.
9. Turn Rebirth on. Stand on your island or at the hub. Bring this profile to max class with `/skills xp combat <amount>` (class level 100 on rebirth 0). List one item on the AH. /rebirth should show "1 to close - Continue". Click the Nexus once: it arms and the warning shows. Click it again 1-10 s later: the listing is cancelled (the item waits in /ah > Manage), then the rebirth runs.
10. Disarm check (on any page with Rebirth or Continue offered): Click the Nexus once (armed), click any node, then click the Nexus again. That click only arms again and the warning shows. Nothing is reset. Close the page without confirming.
11. Sale-coins block (needs a second account): list an item on another test profile, buy it from the second account, and don't claim the coins. /rebirth should say "Claim AH sale coins first" with no Continue, and clicking the Nexus does nothing. The Bazaar half of Continue can't be tested yet: Bazaar 0.1.x has no orders.
12. Switch Rebirth off again. From a second account that is not an admin (or after removing your admin), /rebirth should not open.
13. Clean up: `/rebirthadmin points all reset`. Every tree level and point goes, and the keystone title goes back to "Void-Touched I". The profile stays at rebirth 1 with its rebirth rewards and the reset skills, purse and bank. Switch back to your normal profile.
### 100. TOTEMS: SkyyShards 0.2 + Collections 0.2.14 + Armory 0.1.25 (totems, R9, shard credit) (DEPLOYED 2026-10-14 12:42, backup deploy-20261014-1242)
1. As admin: `/shardadmin give <you>`. Place the shard on your island, right-click it and open the Totems tab. You should see one Harvest Spirit I and 60 an hour.
2. `/give <you> Plant_Crop_Wheat_Item 256`, `/give <you> Skyy_Ench_Wheat 16`, `/give <you> Ingredient_Life_Essence 64` and `/give <you> Ingredient_Water_Essence 8`. Give yourself 200,000 coins with the coins admin command.
3. `/shardadmin totem <you> rain 3`. On the Totems tab, press Place on the Rain Totem III row. A statue should appear on a pad and the rate should rise 15%.
4. `/shardadmin totem <you> fertilizer 1` and place it. The rate should rise another 5%. Then `/shardadmin totem <you> harvest_spirit 5` and place it. The rate line for that worker should say 12 / min or less (the cap).
5. With two or more statues placed, stand next to one statue and right-click a different one. The menu should select the statue you clicked, not the one you are standing next to.
6. Craft a Wider Area modifier and add it to the Rain totem. Add a booster (1 Water Essence); it should say "60 min left". Press Pick up twice. The item should still say Rain Totem III with Wider Area and about 60 minutes of booster. Place it again.
7. Craft tab: craft a Harvest Spirit I. Wheat should drop by 128, Life Essence by 8 and coins by 500.
8. Press Show range. Sparkles should mark the circle.
9. Craft tab, Farming Shard on your main profile: it should say "needs rebirth 2 (you: 0)". On a test profile with two rebirths: If that profile has ever placed a shard, it should say "You already have your Farming Shard". Pick the shard up and put it in a chest: it should still say that. On a test profile with two rebirths that never had a shard, the craft should work once. Then put the new shard in a chest: crafting again should be refused.
10. Wait a few minutes, then press Collect all in Adventure mode. Wheat XP and the Wheat collection should both rise. Repeat in creative: the collection count should wait and be paid at the next Collect in Adventure.
11. Server Setup → Collections → set Max per credit to 100, then Collect a stack of more than 256. The Wheat collection should rise by the full amount. Set it back to 256.
12. Server Setup → Shards → Totems → Harvest Moon Enchanted chance: set it to 100. `/shardadmin totem <you> harvest_moon 1`, place it, wait a couple of minutes (night is a fixed 40% share in the maths, not the world clock), then check `/shardadmin info <you>` for an Enchanted count. Set the chance back to 0.05.
13. Server Setup → Collections: "Sources other mods may credit" should read `skills:double,shard`, with an Undo row on the Changes tab. On a test profile, `/rebirthadmin rebirth`, then open a collection at its last tier (`/give` enough items, then Collect or harvest). It should show "Rebirth rank 1: x / y" instead of MAXED.
14. With a co-op member and `shard.coopCollect` on: their Place, Pick up, modifier and booster clicks should all say "Only the island owner can place, pick up or change totems."
15. `/shardadmin totem <player> rain` for a player in another world should say they are in another world. During that player's profile switch it should say "is switching profile".
16. Check the statue size and look, and send a screenshot.
### 101. PERFECT DODGE + NEW SKILLS: SkyySkills 0.4.37 (Fishing / Ranching / Orchard) (DEPLOYED 2026-10-14 12:42, backup deploy-20261014-1242)
1. Close the game and deploy as usual. Run `/skills stats fishing`, then `ranching`, then `orchard`: each opens at level 0. The Orchard and Ranching pages show "Gathering XP x3 ..." and "Shares the Farming tree".
2. Sprint-tap a roll just as a monster swings. You should see "Perfect dodge! ... +5 Acrobatics XP", take no damage, and get no knockback shove.
3. Hit the monster right after: about a quarter more damage. A second hit, or any hit after 0.75 s, is normal.
4. Roll late, well after the swing: still safe through the normal roll protection, but no "Perfect dodge" line.
5. Chain 11 or more perfect dodges within a minute: after 50 XP the line drops the XP part.
6. In a PvP-off world, have a friend swing at you while you roll: no "Perfect dodge" line. In a PvP-on world, the line shows with no XP text.
7. Turn off "Perfect dodge line" in `/settings` (combat): the line stops, but the dodge still works.
8. Catch a fish with a SkyyFishing rod: you should see "+N Fishing XP". Check that `/skills top fishing` works.
9. Kill a chicken and pick up the raw chicken: Ranching XP about x3 at low level. Pick up an egg: about +9.
10. Drop an egg and pick it back up: no XP. With only 1 free slot, walk over a stack of eggs: XP for 1 egg only.
11. Shear a sheep, then milk a cow with a bucket, and tell me whether any Ranching XP appeared (still unverified).
12. Harvest a ripe apple or berry bush, then wheat, at about the same level. Orchard and Farming should pay similar boosted XP.
13. Open Server Setup → Skills. Acrobatics shows 6 Perfect dodge rows, Gathering shows 3 Ranching rows and an Orchard block, and Overall shows "Farming counts as the average".
14. Afterwards, send me the server and client logs so I can check them for our warnings.
15. **Restart:** earn some Fishing, Ranching and Orchard XP and a level-up's coins, then restart the server. The XP and levels are unchanged, and no coins are paid a second time.
16. **Rebirth:** do a rebirth with XP in Fishing, Ranching, Orchard and Exploration. Fishing, Ranching and Orchard reset to 0, and Exploration stays.
17. **Overall switch:** in Server Setup → Overall, turn "Farming counts as the average" on. `/skills` Overall now lists "Farming (avg of 3) N", and the Overall Level drops if Ranching and Orchard are lower. The Farming stats page adds "counts in your Overall Level". Turn it off again afterwards.
18. **Farming page:** `/skills stats farming` has a last line "Farming level (average of Farming - Ranching - Orchard) N" that matches the Ranching and Orchard pages.
19. **Acrobatics page:** with Acrobatics tree nodes bought, `/skills stats acrobatics` still shows the "Skill tree:" line. "Perfect dodge - roll at most 50 ms ..." is the last line, or missing if the list is full.
20. **Perfect Parries:** perfect-dodge a monster, then land a parry counter-hit within 0.75 s. The damage should be the parry's alone, not a quarter more on top. A plain hit after a perfect dodge is still a quarter stronger.
### 102. VAULT SUMMON + HANDS + LIFELONG POLE: SkyyGear 0.3.5 + Fishing 0.1.5 + Merchants 0.1.4 (identify reveal, rebirth R7 part, Sigils never in shops) (DEPLOYED 2026-10-14 12:55, backup deploy-20261014-1255)
1. Put your pickaxe in `/vault`, close the Vault and type `/pickaxe`. It should come back with the same name and rarity and say "came back from your Vault".
2. Type `/pickaxe` twice quickly. The second should say "try again in a few seconds" and never make a copy.
3. With a full inventory and the pickaxe in the Vault, type `/pickaxe`. It should say "No room - free one inventory slot" and the tool stays in the Vault.
4. With an empty hand, left-click and press F on a Potato. Both should say "Too tough for your bare hands". Left-clicking a Carrot should be slow, and Wheat should be normal.
5. Hold a sword and try to harvest a Potato: refused. A hoe or sickle two tiers below the crop: refused. A hoe or sickle at the crop's own tier: harvests normally.
6. Put a mystery bag on the Anvil and click Identify. The card page should open. Flip the card, then "< Back" should reopen the Anvil.
7. Click Identify all with 12 or more bags. The subtitle should say "Showing your 10 best of N", the best card should come last, and chat should show "[Identify] Identified N items…".
8. Re-identify an item. The page should say "Re-identified!".
9. On a fresh profile, take Marlow's pole. The tooltip should end with "Lifelong fishing pole - can't be dropped. Lost it? /pole", and Q should refuse to drop it.
10. Leave the pole in a far chest that isn't loaded, wait `lifelong.reclaimSec` (600 s) and type `/pole`. You get a copy that says the reel and parts stay on the old pole. A second `/pole` within 600 s is refused. When you find the old pole it becomes yours again and the copy goes. If you upgraded the copy at the bench first, the old one is retired instead.
11. Give your pole to a second player. They should get "someone else's lifelong fishing pole - it won't cast for you".
12. Upgrade the pole to Copper at the Fishing Bench. It should still show the lifelong line.
13. On a profile with no pole, hold a crafted rod and type `/lifelong`. It should be refused ("Only the fishing pole from Marlow's quest…"). Hold the rod Marlow gave you before this update and type `/lifelong` again: it becomes your pole.
14. Open `/multitool`, click your lifelong pickaxe and any hatchet. The line under the Merge button should say "cannot be merged yet - … later update". Plain tools should still merge normally, even with SkyyRebirth loaded.
15. In Server Setup → Merchants, the never-sold list should end with `Skyy_Sigil_*`, and the change log should show the update with an Undo button.
### 103. MONK + ASSASSIN ABILITIES: SkyyClasses 0.1.23 + SkyyTrees 0.3.8 (rune keys, panel, rebirth R5/R6 parts) (DEPLOYED 2026-10-14 13:03, backup deploy-20261014-1303)
1. Rebirth (R5 / R6) cannot be tested in game until SkyyRebirth adds "classes" and "trees" to its `RbJournal.PARTS` list (another round). All other steps work now.
2. Make a Monk profile at class level 30 or higher and hold a Bo staff. Open `/tree`, go to the class tab, and click Enable on all four ability cards (free).
3. Modifiers unlock at ability Lv 2, 4, 6, 8 and 10. Lv 2 needs about 5 counted uses, and a Flowing Form use only counts once you reach 5 combo. Use each ability about 5 times before step 10.
4. Press Ability 2 to start Flowing Form. Hit a mob several times: you run faster, and the mob loses track of you for about a second. When the aura ends, your speed returns to normal. There is no attack-speed bonus yet (question 4).
5. Press Ability 3 to cast Palm Strike on a mob within 4 blocks that you are looking at: it is stunned and pushed. Crouch + Ability 2 casts Cyclone Kick (alt slot 1): everything within 3 blocks is hit and pushed.
6. In the panel, set the Ability 1 alt to Still Water. Crouch + Ability 3 casts it (alt slot 2). Let a mob hit you: the hit is blocked and the mob takes damage back. In creative mode no counter happens (expected). Your own swing in progress is not cancelled yet (a known gap).
7. Make an Assassin and hold daggers. Ability 2 = Cloak: you look see-through and mobs lose you. Your next hit does +50 % and ends the cloak.
8. Look at the ground and press Ability 3 (Toxin): a poison cloud hurts mobs every second.
9. Crouch + Ability 2 arms God Killer (alt slot 1). Hit a boss (for example a Goblin Duke) from behind within 12 s: about 3x damage and the "God Killer!" line. Crouch + Ability 3 casts Vanishing Act (alt slot 2).
10. In `/tree` class, unlock the modifier slots (M nodes) for a Monk and an Assassin ability and equip modifiers. Each ability levels its own modifiers.
11. Optional: after a class respec, do a Dust-tree respec right away. It should say to wait (10 min cooldown).
12. After the session, check the server and client logs for SkyyClasses or SkyyTrees warnings.
### 104. HUD SKILLS + ABILITY LEVELS: SkyyHud 0.3.24 (DEPLOYED 2026-10-14 13:19, backup deploy-20261014-1319)
1. Join the test world and open `/skyyhud`. Pick the Skills widget and open its Settings. There should be a third row of buttons: Fishing, Ranching, Orchard.
2. Turn on Farming, Fishing, Ranching and Orchard. Farming should read like "12 (F 15 / R 9 / O 12)", and the whole line should be visible with nothing cut off.
3. Catch a fish. A "+XP" should flash on the Fishing line, and the Farming line should still not be cut off.
4. Pick up an egg or wool and check that Ranching flashes. Harvest an apple or berry bush and check that Orchard flashes.
5. Turn Fishing off and catch another fish. It should flash as a temporary row if "XP of hidden skills" is on Show.
6. As a Mage or Priest, check the Abilities widget. Each owned ability should show its level, like "Meteor (Lv 1)", and the cost should be fully visible on the right. Locked rows should still say "Lv 10" etc.
7. Have an admin run `/classadmin abil <you> maxlevels`. Within about 5 seconds, "Mana Barrier (Lv 25)" and its full cost should show without being cut off.
8. Hold crouch. The alt abilities should also show their levels without being cut off.
9. In `/skyyhud`, set the Abilities and Skills widgets to 170 % and check that nothing is cut off. Check that boxes you placed earlier are still where you left them.
### 105. COIN FACTOR 0.8 + NO OWN-PROFILE TRANSFERS: Skills 0.4.38 + Coins 0.1.8 + Auctions 0.1.6 + Rebirth 0.3.1 (DEPLOYED 2026-10-14 13:38, backup deploy-20261014-1338)
1. Open /skills. You should see 12 rows, with Fishing, Ranching and Orchard after Farming, all on screen with no clipping. Click STATS on Fishing. It opens, and the new rows have no TREE button.
2. Go to SkyWynn Menu → Server Setup → Skills → general. "Level coins after each rebirth" shows 0.8. Changes shows exactly one Undo line from SkyySkills 0.4.38. Restart the server twice. There is still only one Undo line, and the value is still 0.8.
3. Go to Server Setup → Coins. "Block coins between own profiles" is ON. Turning it off asks you to confirm. Cancel, so it stays on.
4. On profile 1, list an item on /ah. Use /profiles to switch to profile 2 and try to buy it. The listing page shows the reason instead of a Buy button. The buy is refused with "You can't buy from your own other profile - coins never move between your own profiles on this server." Neither profile's coins change.
5. If a second player is online, they can buy it normally.
6. Turn the Coins switch OFF, confirm, and repeat step 4. The buy goes through. Turn the switch back ON.
7. On a fresh test server only, delete `mods\Skyy_SkyyAuctions\config.properties` and restart. The `otherProfileBuy` comment now says "SkyyCoins' switch decides". On an existing server the file keeps its old comment, and that is expected.
8. As admin, type `/rebirthadmin crashtest 3`. It is accepted, not refused with a usage error, and asks you to type it again within 10 s. Only confirm on a test profile, because it resets the active profile. Also try `/rebirthadmin points Farming 5` and `/rebirthadmin refund Farming`. Both are accepted.
9. Open /rebirth (admin view). The Farming arm counts Farming, Ranching and Orchard together. Check: with Farming maxed and Ranching and Orchard at 0, the Farming arm shows 4 points, not 8.
10. Known and expected for now: coins can still move between your own profiles through a Bazaar buy order that your other profile fills, and through guild bank deposit/withdraw. That is question 3, not a bug in this round.
### 106. REBIRTH RESETS TOOLS + GUILD BANK OWN-PROFILE BLOCK: SkyyRebirth 0.3.2 + SkyyGuilds 0.1.8 (DEPLOYED 2026-10-14 17:27, backup deploy-20261014-1727)
1. Rebirth stays OFF; these are admin tests on a TEST profile. With a lifelong pickaxe that has an upgrade point, type /rebirthadmin dryrun: one line starts with "gear:".
2. /rebirthadmin status says "Every part is loaded (4)".
3. /rebirthadmin rebirth twice within 10 s: chat says the rebirth is done and your lifelong tools are Crude again; the pickaxe is Crude with no points.
4. /rebirthadmin backups lists 4 lines, including Skyy_SkyyGear.
5. /rebirthadmin points Mining 50, open /rebirth, buy Void-Forged Pick: the panel says "Works now (SkyyGear...)" and the pickaxe's Power / Fortune / Wisdom go up.
6. Guild: on profile 1 create a guild and /guild bank deposit 1000; switch to profile 2 and /guild bank withdraw 1: refused, naming profile 1.
7. Back on profile 1, withdraw: works.
8. On profile 2, /guild disband: refused. On profile 1: works.
9. Server Setup -> Coins: turn "Block coins between own profiles" off, profile 2 can now withdraw; turn it back on.
### 107. SOUND PASS 1 + /soundtest: Quests 0.3.1, Exploration 0.2.9, Bank 0.1.12, Islands 0.5.9, Pets 0.2.6, Menu 0.3.24 (DEPLOYED 2026-10-14 17:41, backup deploy-20261014-1741)
1. Type /soundtest list to see the numbered sounds the mods use now.
2. /soundtest 1, then /soundtest next a few times: each plays only for you and says where it is used.
3. /soundtest more shows sound ideas for later; try one, e.g. /soundtest 15.
4. /modconfig admin -> Diagnostics: Sound list, Next sound; type a number in the Text box and press Play sound.
5. Players tab: type Mining in the Text box, press Rebirth test points (+100 points in chat); Refund rebirth arm needs two presses. Rebirth crash test needs a page confirm AND the command's own repeat - only on a test profile.
6. Chop 10 logs for the tutorial task: a checkpoint sound when it finishes, a coin sound when the reward is paid.
7. F on Marlow or the Quest Board: a soft paper sound.
8. /island, then /hub: a portal sound each time you arrive.
9. /pets: put a pet into a slot (sparkle-up), take it out (fade-down).
10. Claim a Lost Loot pile: chest-open sound; the reveal page still makes its rare / legendary sounds.
11. Wait for a bank interest payout: a sound with the "You earned..." line.
12. Server Setup -> Quests -> Sounds: turn "Task done sound" off, finish a task: silent, rewards still sound.
13. Set any sound id row to SFX_Nope: refused with "The game has no sound event...".
### 108. FIVE MORE SHARDS: SkyyShards 0.3 + SkyyCollections 0.2.15 (Mining / Foraging / Orchard / Ranching / Combat, compactor, time compressor, Soul Cages) (DEPLOYED 2026-10-14 18:01, backup deploy-20261014-1801)
1. Soul Cage, data orb protection: Put a SkyyGear Soul Orb in your hotbar and a second one in your backpack. Have 128 Bone Fragments, 8 Void Essence and 2,000 coins. In the Shards menu Craft tab, select the Soul Cage Totem. The right panel shows "Takes a plain Soul Orb first, the one in your hotbar last." Craft it. The backpack orb is used and the hotbar orb stays.
2. Repeat with a plain Soul Orb as well. The plain one is used first.
3. Repeat with fewer than 2,000 coins. The craft is refused, and every orb keeps its stats and tooltip.
4. A given shard counts as had: In SkyWynn Menu, go to Server Setup, then Shards, then Costs. Set "Rebirths to craft a shard" to 0. On an alt with no Mining Shard, run `/shardadmin give <alt> mining`. Put the shard in a chest without placing it. Try to craft a Mining Shard. Expected: "You already have your Mining Shard".
5. Full inventory: Fill the alt's inventory and run `/shardadmin give <alt> foraging`. Expected: "Their inventory is full." Make room. Crafting a Foraging Shard is still allowed while the setting is 0. Set the setting back to 2.
6. Server Setup, then Shards, then Costs: the rows read "Storage tier 2-5 upgrade items".
7. On each shard's Islands tab, the caption says "more island types come in a later update".
8. On the Shards tab, the sidebar reads "A shard you never had can be crafted from rebirth 2 (one of each kind)."
9. Void rescue: With only a Mining Shard placed (no Farming), enter it and walk off the island. You should land back on the Mining hub with "[Shards] You fell - back to the Mining Shard hub." No death and no fall loop. Repeat in the Orchard region if you have one placed.
10. Open the Mining Upgrades tab with no compactor bought. It says "Next: Compactor I - needs an Auto-Smelt Pole" in the warning colour.
11. Run every `/shardadmin` line above in chat and confirm none is refused.
### 109. WARRIOR + BERSERKER + ARCHER ABILITIES: SkyyClasses 0.1.24 + SkyyTrees 0.3.9 (DEPLOYED 2026-10-14 18:17, backup deploy-20261014-1817)
1. **Setup as Warrior:** Pick Warrior, then type `/classadmin abil <you> grant` and `/classadmin abil <you> maxlevels`. Open `/tree`, go to the class tab and buy A1 to A4 (they are free). If you need the kit, type `/classadmin kit <you> Warrior`. It holds a sword and a Wood Shield; the shield goes into the off-hand.
2. **Panel:** Open the ability panel on the `/tree` ability card. The rune items should sit in the two ability slots. Equip, level and unequip Echo on Rallying Guard. Equip Floor and Duration+ together on Blood Frenzy, and Seeker and Ricochet together on Rapid Fire (do these once you are on each class). Each pair should be refused.
3. **Game runes blocked:** put a game rune (not one of ours) in an ability slot. It should be blocked with a chat hint. Repeat this as Berserker (step 10) and as Archer (step 17).
4. **Rallying Guard:** You should take less damage, and nearby mobs should turn on you. With Echo, the damage cut should last about 3 s longer. A party member 10 blocks away should be covered; a non-party player 8 blocks away should not.
5. **Shield Shockwave with the shield in the off-hand:** use it on a group. They should be hit and stunned. With Echo, a weaker cone follows 1 s later.
6. **Shield Shockwave with no shield:** take the shield out of the off-hand and press it again. It should be refused with "needs a shield in your hand or off-hand - nothing was spent", and your Mana should not move.
7. **Iron Chain:** use `/cast swap` (or the panel) to put it in. Use it on a mob 10 blocks away; the mob should be yanked to you.
8. **Challenge and Guardian's Oath:** Type `/classadmin abil <you> pickA` and use Challenge on a mob. You should take less damage from it, and some should reflect. Type `pickB` and use Guardian's Oath on a party member. Part of their damage should move to you.
9. **Shields for other classes:** have a non-Warrior friend hold a shield. Their weapon hits should deal no damage.
10. **Switch to Berserker:** Type `/profileadmin setclass <you> <profile n> Berserker`. Type `/classadmin kit <you> Berserker` (the kit does not drop automatically after an admin class change). Run grant and maxlevels again, then buy A1 to A4 in `/tree`.
11. **Enrage:** Have a player 6 blocks away and a party member 12 blocks away, then use Enrage. Then have them walk 30 or more blocks away. Their buff should stay until it ends, because targets are picked once and it is not an aura. Your hits should grow stronger.
12. **Whirlwind and Earthsplitter:** Use Whirlwind. It should spin and heal you a little; with Echo, a weaker spin follows. Swap and use Earthsplitter. It should send a line shockwave.
13. **Blood Frenzy:** Turn it on and swing at the air. Mana and Stamina should drop on every swing. Hit mobs; the stacks should climb. Have an ally step out of the aura (over 8 blocks for a player, 16 for party) and back in. Their buff should go and come back. Swing a pickaxe at a block. It should cost nothing. With Floor equipped, reach 5 stacks, stop hitting for 10 s, and check that the stacks stay at 5 (10 at Lv 2). Press it again to turn it off.
14. **Blood Frenzy and changing world:** turn it on, then type `/hub`. You should see "Blood Frenzy off - you changed world", and the next press should turn it ON.
15. **Warlord's Banner:** Plant it. You should get +16 %, your party +12 % and other players +8 %, for both damage and defence (getting hit should hurt less). Kill mobs inside it; its time should grow. Leave its range. It should fall, and the 40 s cooldown should start at the fall. Plant it again, then `/hub`. You should see "banner fell - you changed world".
16. **Banner and quitting:** plant it, quit, and rejoin within 40 s. The Banner should be ready, not on cooldown.
17. **Switch to Archer:** Type `/profileadmin setclass <you> <n> Archer`, then `/classadmin kit <you> Archer`. Run grant, maxlevels, buy A1 to A4, and pickA or pickB as needed. Equip Seeker on Rapid Fire and Echo on Explosive Arrow and Arrow Rain in the panel.
18. **Archer abilities:** Pinning Shot: the mob should be rooted and marked. Rapid Fire with Seeker: arrows passing near enemies should hit them. Explosive Arrow: use it, then shoot a bow at a Marked mob in a group. It should blast; the neighbours should take no more than the plain blast. With Echo, a second blast follows 1 s later. Arrow Rain with Echo: a second shower should follow. Hunter's Net: mobs inside should be rooted.
19. **Server Setup:** open SkyWynn Menu, then Server Setup, then "Warrior Bers. Archer". Change one number and recast; the change should show.
20. **Logs:** send both the server and client logs afterwards. `/classadmin abil <you> info` shows "frenzy swings paid".
### 110. REBIRTH STATS + SKILLS SOUNDS: SkyySkills 0.4.39 + SkyyRebirth 0.3.3 (DEPLOYED 2026-10-14 19:30, backup deploy-20261014-1930)
1. Mine until a skill levels up. You should hear the "upgrade" sound with the SKILL LEVEL UP line. If your Overall Level also goes up, you hear only the Overall sound.
2. Roll just before a monster hits you. You should hear a whoosh with "Perfect dodge!".
3. In /settings, hide "Skill level-ups", then level up again: no line and no sound. Turn it back on.
4. This needs SkyyMenu 0.3.25 deployed. In /settings turn Sounds off, then level up a skill and do a perfect dodge: both should be silent. Turn Sounds back on.
5. As admin (rebirth can stay OFF): Note your max Health. Run `/rebirthadmin points class 100`, then /rebirth → Class arm → buy Vitality levels. Within about 1 s, max Health goes up 1 % per level, and the node panel says "now (SkyySkills: max Health)". To test Focus, play as a Mage or read the Stats page. The gain is small for a non-Mage (5 levels add about +0.5 Mana).
6. Buy Class Wisdom levels, then earn class XP. You should get about +2 % XP per level. Gathering skills such as Mining should not change.
7. Per-rebirth boost: test this on a throwaway profile, because a rebirth resets your skills, coins and bank. Run `/rebirthadmin dryrun` first. Then type `/rebirthadmin rebirth` twice within 10 s. This works with rebirth OFF. Max Health, Mana and Stamina should each rise 3 %. The Stamina change is small, so check the Stats page.
8. With SkyyProfiles, switch profile while you have Vitality levels. The extra Health should go away within about 1-2 s and not come back on a profile without nodes. Switch back and it should return.
9. Run `/rebirthadmin refund class`. The extra Health and the class XP bonus should be gone within about 1 s.
10. Go to SkyWynn Menu → Server Setup → Skills → General and switch "Rebirth stat boosts" off. Every rebirth bonus should disappear. Turn it back on.
11. Go to Server Setup → Skills → Sounds: Switch "Skill level up sound" off: no sound. Type `SFX_Nope` as an id: it should be refused with a message. Enter any id from /soundtest: that sound should play instead.
### 111. SETTINGS SEARCH + MOD SOUNDS SWITCH + SHARDS ADMIN BUTTONS: SkyyMenu 0.3.25 (DEPLOYED 2026-10-14 19:30, backup deploy-20261014-1930)
1. /settings, search "sound" and press Enter. "Mod sounds" shows as "General: ..." with no mod name in brackets.
2. Search "interest". The Bank interest result reads "Coins (SkyyBank): ...".
3. Search "party". `party.chat` shows but Mod sounds does not. Search "General" and the General rows show.
4. Turn Mod sounds OFF, leave and rejoin within a few seconds, and wait about 30 s. SkyWynn sounds should stay muted once the sound mods read the switch. Then turn it back ON.
5. In /settings, click a tab while search results are showing; it should leave the search. Clear empties the box.
6. /modconfig: search "interest" and "shard.maxLoaded", then use "Go to" on a result.
7. Admin > Players, Next > to page 3: Clear shard portal (press twice) Shard info Give Farming Shard (press twice) Unload shard world
8. Check the server and client logs for SkyyMenu warnings.
### 112. SOUND PASS 2: Sacks 0.8.5, Collections 0.2.16, Coins 0.1.9, Accessories 0.5.14, Bazaar 0.1.12, Auctions 0.1.7, Shards 0.3.1 (DEPLOYED 2026-10-14 19:43, backup deploy-20261014-1943)
1. Pick up items with your Void and inventory both full. You should hear one "error" sound with the chat warning, and none again for 30 s.
2. On the Void page, Upgrade a category and Pay. A short "upgrade done" sound plays instead of the old craft click.
3. Gather until a collection tier goes up. One sound plays with the COLLECTION UP line.
4. Collections owed reward: a reward paid later (not with its tier-up) plays a chest sound. A reward paid at the same moment as its tier-up plays only the tier sound.
5. Server Setup, SkyyVoid and Crafting, Sounds tab: type `SFX_Player_Craft_Item_Inventory` in the upgrade id row and redo step 2. The old click is back. Clear the id row (empty): no sound.
6. Have a second player /pay you 10,000 coins. Only you hear a coin sound. With 500 coins there is no sound.
7. In the Accessory Bag, equip a new accessory (gem sound), then a higher tier of the same line ("unlock" sound).
8. Bazaar: buy 1 of something and sell 1 (one coin sound each). Sell inventory plays just one sound.
9. Auction House: list an item on one player and buy it on another. The buyer hears one sound and the seller another. Then Claim all on the seller with several owed rows: exactly one chest sound. Claim all again with nothing owed: no sound.
10. Once SkyyMenu 0.3.25 is in, turn sounds off in /settings and repeat any step above: no sound for you, while other players still hear theirs. This mute covers only these 7 mods for now. Quests, Exploration, Bank, Islands, Pets, Skills, Classes, Armory and Fishing sounds still play.
11. Shards menu: Collect (crystal sound), Grow an island, Place a totem (one sound each).
12. Server Setup: open Coins, Bazaar, Auctions (a new page with only a Sounds tab), Collections, Accessories, SkyyVoid and Crafting, and Shards. Each has a Sounds tab. Switching one row off silences that sound right away.
13. In any Sounds tab, empty an id row. That sound goes silent, the same as switching it off.
### 113. GATHERING ARMOR + POLE PERKS + REBIRTH DAMAGE / DEFENCE + GEAR SOUNDS: SkyyGear 0.3.6 + SkyyFishing 0.1.6 (DEPLOYED 2026-10-14 21:33, backup deploy-20261014-2133)
1. At the Armor Bench, craft a Grove Bark Helm (Oak logs, Tree Sap, Plant Fiber). It should be a green Set item with "[Lv N]" equal to your Foraging level and show "Foraging Fortune +0.25".
2. Wear 3 Grove Bark pieces. The tooltip should say "Set: Grove Bark (3/4)" with no full-set line. Add the 4th piece: it should say "(4/4)" and "Full set: +1 Foraging Fortune". Chop logs and watch for extra drops.
3. Craft the Wheat Harvest pieces (Wheat + Plant Fiber) and the Copper Angler pieces (Copper bars + light leather + fibre). Check how they look on you; both are placeholder art. Wear the full Copper Angler set. The tooltip should show Fishing Speed, Treasure Chance and the full-set double catch. Fish: bites should come a little faster.
4. Put on a piece above your skill band, for example an Autumn Bark piece with Foraging under 15. It should show no lines and should not count toward the set.
5. Get 1 Enchanted Maple (Bazaar, or compact Maple logs). With Foraging 15+, put a Grove Bark Helm on the Anvil. It should become an Autumn Bark Helm, still green Set, showing "Set: Autumn Bark".
6. Tier up a Wheat piece to Carrot (Enchanted Carrot from the Bazaar or by compacting, Farming 15+). Tier up a Copper Angler piece to Iron Angler (Enchanted Iron, same sources, Fishing 15+).
7. Hold the lifelong fishing pole and run `/toolpoints`. It should open on the pole, with five tool rows. Buy Fortune 1, then fish. A "Double catch" message should show sometimes. With an Iron rod, buy Wisdom 1 (Fishing XP per catch should go up about 1 %) and Steady Line 1 (the fish should pull a bit slower).
8. Hold the pole. Its name should show "[Lv N]" matching your Fishing level.
9. Identify, reforge, use a Sigil, tier something up on the Anvil, and use `/pickaxe` with your pickaxe in a chest. Each should play a sound.
10. Open Server Setup → Gear. The Sounds tab should list its rows. The "Gathering armor" tab should show `garmor.foragingOn` / `farmingOn` / `fishingOn`, `garmor.gatherShare` and the ladders. Turn `garmor.fishingOn` off. A newly crafted Copper Angler piece should still be green Set, give no fishing lines, and refuse a reforge. Turn it back on. Check that all 16 Gear tabs fit on screen.
11. Turn the /settings sound switch off, then identify an item. It should be silent.
12. Optional, if rebirth is on: after one rebirth, hits should do about 3 % more damage. A tier-2+ gathering armor piece made before the rebirth should go back to tier 1, keeping its rarity.
13. After playing, send both the server and client logs.
### 114. SPELLBLADE + SETTINGS SPLIT + REBIRTH MODIFIER SLOTS + FISHING TREE: SkyyClasses 0.1.25 + SkyyTrees 0.3.10 (DEPLOYED 2026-10-14 21:33, backup deploy-20261014-2133)
1. Deploy SkyyClasses 0.1.25 and SkyyTrees 0.3.10 together.
2. Pick Spellblade on the class page and hit mobs with a longsword. Run `/classadmin abil info <you>`: the line "Spellblade: Momentum N (...)" should go up as you hit, then fall about 4 s after you stop. The HUD does not show Momentum yet (that is a later SkyyHud round). Swing speed does not change yet either; that part is not built.
3. Open Server Setup, category "Abilities", and set "Ability 1 unlock level", "Ability 2 unlock level", "Ability 2 alt unlock level" and "Ability 1 alt unlock level" to 0. Open the class tab and buy Abilities 1-4 and the modifier slots (they are free). Put the values back to 1 / 10 / 20 / 30 after testing.
4. With the default loadout, Ability 2 casts Arcane Breach, Ability 3 casts Elemental Imbue, crouch + Ability 2 casts Sunder, and crouch + Ability 3 casts Rift Cleave. Look at a mob and press Ability 2 (Breach), then crouch + Ability 2 (Sunder). The mob should take extra damage. Sunder should refuse to cast with no target.
5. Open Elemental Imbue's details and press Change: the element should change. Press Ability 3 and hit a mob; the status should show.
6. To reach Burning Rift, open Server Setup, Trees, "Class trees": Set "Test: extra AP" to 50. In "Class level per node", set Spellblade.ROOT, Spellblade.PA1 and Spellblade.PA2 to 0. In the class tree, buy the root, then Twin Attunement (PA1), then Burning Rift (PA2). Long Arm (T1) waits for SkyyArmory and is skipped. Make sure the A/B pick is Rift Cleave, not Shattering Arc. Cast Imbue (Ability 3), then Rift Cleave (crouch + Ability 3). The patches under the enemies you hit should apply the status, for example burning damage. Afterwards put the extra AP back to 0 and restore the three levels (or remove those lines).
7. Rebirth slots: Set Server Setup, "Ability levels", "Rebirths per extra modifier slot" to 1. On a throwaway profile, run `/rebirthadmin rebirth`. It works while rebirth is off, but it resets that profile's skills, coins and bank. Open an ability, press Next slot twice and equip a modifier into slot 3. Slot 4 should say "opens at rebirth 2" (at 5 it would say rebirth 10). A second `/rebirthadmin rebirth` opens slot 4. Set "Most extra modifier slots" to 1 and slot 4 should say "no more slots on this server". Put the two values back to 5 and 2.
8. With an ally nearby at 7 or more Momentum, the ally should move a little faster. An ally Monk in flow should keep their own higher speed without flickering.
9. Check that the Monk's class icon is the Bo staff and the Spellblade's is a longsword.
10. Open the Fishing tab and buy Sea Legs: max Health should go up by 1 per level. Sea Legs is a stand-in; the other nodes should say "Coming with ...".
11. Set Farming, Ranching and Orchard to different levels. The Farming tree should use their average, even right after a profile switch. Turn off "Farming tree uses the average" (Server Setup, Trees, General) and it should use the plain Farming level.
12. Scan the server and client logs afterwards.
### 115. 3 STARTER ISLANDS: SkyyIslands 0.5.10 + SkyyQuests 0.3.2 (DEPLOYED 2026-10-14 21:33, backup deploy-20261014-2133)
1. Close the game. Deploy SkyyIslands 0.5.10 together with SkyyQuests 0.3.2.
2. Start the game and make a fresh profile, so you get a brand-new island. Arrival may take about 1 s longer than before.
3. You land on island 1. The chest next to you should hold exactly one starter kit. Look east (and slightly south) to see island 2 across the gap.
4. Get your Crude tools with /pickaxe and /hatchet (they can't be crafted). Break bushes, stick piles and loose rocks for materials, and place the workbench from the kit.
5. Check the starter plot just east of the chest. It should be tilled, with 9 young wheat plants. Break one: you should get wheat seeds. Plant them on the free row and check later that they grow.
6. Find the little cave in the rocky hill **south-east** of the spawn, on the same side as island 2. Mine the stone and copper inside.
7. Bridge east to island 2 (3 blocks past the plank stub) and walk onto it. "Bridge to island 2" should tick a few steps in.
8. Before that tick, check that the quest arrow for "Bridge to island 2" points east toward island 2.
9. Bridge on to island 3 (5 blocks past the stub) and walk onto it. "Bridge to island 3" should tick, and the arrow should then point at the broken portal frame on the summit.
10. Look under the ruined walls and pillars: there should be dirt, not grass, and nothing should change while you stand near.
11. Check an old profile's island: it must look exactly as before.
12. On a profile that already has an island, use `/island reset` (24 h cooldown). You should get the 3 islands with exactly one kit in the chest.
13. As admin, run `/questadmin place list`. It should show 8 island places marked "from SkyyIslands".
14. Optional: Server Setup → Islands → Starter kit → set "Starter islands" to Classic island. Make another new profile and confirm you get the old small island. Then set it back.
15. After the session, check the server log for "Task took … com.skyy.islands.FillTask". There should be none.
### 116. ZONES AS FLOATING ISLANDS: SkyyWorldGen 0.6 (vanilla 0.7 generation, Zone 5 Onyxium + Mithril) (DEPLOYED 2026-10-14 21:45, backup deploy-20261014-2145)
1. Start the game as admin in the usual test world.
2. Type /zone 1: the first time builds the new zone world (a few seconds) and lands you at spawn on the Zone 1 island.
3. /zone 2, /zone 3, /zone 4, /zone 5 hop between the islands (each lands in the middle of that island).
4. /zone info shows which island you are on, the vanilla biome and the island list.
5. Walk to a coast and look down: void, stone drips and roots under the rim; note the flowers / pillars / spikes / basalt / crystals per island.
6. On Zone 5, dig into the rock for dark Onyxium ore; mine it with a Mithril pickaxe and check you get Onyxium Ore.
7. /zone leave goes back. Old worlds unchanged: /zone old is the old test island, /zone proof the old proof world.
8. Send logs (chunk loading while flying, lighting, landing spots).

## 3. Open questions (defaults are live)


#### project
- RELEASE: start with a GitHub 'server pack' zip, CurseForge modpack later? [yes] (research/Release-Packaging-Plan.md)
- RELEASE: OK to redistribute our jars although 4 of them (Skills / Armory / Gear / Trees) hold edited vanilla JSONs / assets generated from game files at build time - check Hytale's modding terms first? [check the terms first, then release] (research/Release-Packaging-Plan.md)
- RELEASE: Dynamic Seasons + More Crossbow Tiers have no stated pack permission - ask the authors now, list them optional until they reply? [yes, ask now, optional until a reply] (research/Release-Packaging-Plan.md)
- RELEASE: pack version number and name? [0.9.0 'SkyWynn'] (research/Release-Packaging-Plan.md)
- RELEASE: which tuning scripts ship with the pack (Perfect Parries per class)? [a small apply script, off by default] (research/Release-Packaging-Plan.md)
- LOAD TEST: OK to refactor tools/smoke_test.py into reusable functions (no behaviour change) so the load tool shares its safety checks? [yes, small lean round] (research/Load-Test-Plan.md)
- LOAD TEST: spend a day on the bot-client spike (phase 3), or rely on layers A-C plus a real friends test? [layers A-C first, spike only if they miss something] (research/Load-Test-Plan.md)
- LOAD TEST: how many players should the public server handle at release (sets N)? [50 online, 200 profiles on disk] (research/Load-Test-Plan.md)
- LOAD TEST: make 'no com.skyy task took over 25 ms' a release gate in the smoke test? [yes, warn only until the Core ticker lands] (research/Load-Test-Plan.md)

#### world
- EXPLORATION: names Lost Loot / Lost Treasure / Supply Drop OK? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: tier IV Lost Loot is a gold treasure pile? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: one supply drop per world every 30 min, one at a time, first claim takes all? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: reveal page (face-down cards) on by default for everyone? [yes; per-player setting 'Loot reveal page'] (SkyyExploration 0.2.8)
- EXPLORATION: the supply drop is a firework flash falling, then the crate appears (no falling crate model) - OK? [yes] (SkyyExploration 0.2.8)
- EXPLORATION: drops land 32-64 blocks from the chosen player (was 32-96) so the flash can be seen? [yes] (SkyyExploration 0.2.8)
- STRUCTURES: OK to message joszza (OpenStructure + Dungeons and more Structures: modpack use, merchant camp off switch)? [yes; you send it or Claude drafts the text] (research/Structure-Mods-Survey.md)
- STRUCTURES: more world structures at all before release, or keep zones vanilla + our loot piles? [keep vanilla, loot piles first] (research/Structure-Mods-Survey.md)
- STRUCTURES: boss dungeons from Adathan (Tower of Shiva, Void Asylum) as end-game: one ask message for all four? [no, our own capstone dungeon] (research/Structure-Mods-Survey.md)
- STRUCTURES: if no author agrees, build a small prefab placer into SkyyWorldGen? [only if loot piles need it] (research/Structure-Mods-Survey.md)

#### mobs

#### skills
- PERFECT DODGE (SkyySkills 0.4.37): 50 ms window, x1.25 counter-hit for 0.75 s, +5 Acrobatics XP (max 50 XP / min, monsters' hits only)? [yes; widen to 100 ms if 50 feels too tight]
- PERFECT DODGE: base roll behaviour for everyone, not an Acrobatics perk? [base behaviour] (SkyySkills 0.4.37)
- PERFECT DODGE: show it as a HUD flash or sound instead of a chat line? [chat line now, HUD later] (SkyySkills 0.4.37 / SkyyHud)
- PERFECT DODGE: when a hit is both a Perfect Parries counter-hit and a dodge counter-hit, only the parry multiplier applies? [yes, no stacking] (SkyySkills 0.4.37)
- OVERALL LEVEL: count Farming as the average of Farming / Ranching / Orchard now? [off until Ranching and Orchard have real XP sources] (SkyySkills 0.4.37)
- RANCHING: cap of 200 XP a minute (after boosts) plus 'items a player dropped pay nothing' enough protection against farming? [yes] (SkyySkills 0.4.37)
- /skills page: Fishing / Ranching / Orchard have no rows yet (open with /skills stats <name>) - fine until a later page round? [yes] (SkyySkills 0.4.37)
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

#### gear
- HARVEST GATE (SkyyGear 0.3.3): a Crude / Copper SICKLE sweeps Potatoes at half XP while a Crude hoe is refused (vanilla sickles stop at Iron, the sweep has no skip hook). Keep, or measure sickles against the crop's real tier (needs a client-side probe first)? [keep]
- HARVEST GATE: an F-harvest one tier up may still pay full Farming XP (SkyySkills only halves left-click breaks and sickle swings) - fix in SkyySkills? [yes, next Skills round]
- VAULT FETCH (SkyyVault 0.1.6): on a normal server stop the 30 s 'tool on the way' notes are not cleared, so a lifelong tool in flight can show twice (Vault + inventory) after a crash; clearing them risks losing the tool if the player was not saved first. Accept the duplicate-note trade-off? [yes, keep]
- SIGILS: Unique Sigil comes from the Wheat, Oak Log, Cobblestone and Bone collections at tier VI? [yes] (SkyyGear 0.3.4 / Collections 0.2.13)
- SIGILS: players already past tier VI get their Unique Sigil at their next join? [yes] (SkyyGear 0.3.4)
- SIGILS: Mining Set armor refuses Sigils (fixed set bonus; it levels and tiers up instead)? [yes, refuse] (SkyyGear 0.3.4)
- SIGILS: which bosses drop Sigils? [Boss, Guardian, Duke, Dragon, Chieftain, Hedera (incl. Golem_Guardian_Void); not Elite, Ogre, other Golems, Yeti, Rex] (SkyyGear 0.3.4)
- SIGILS: should a Mythic Sigil work on the Anvil (sigil.mythicUse)? [off - Mythic is boss-only, 2026-10-08 lock] (SkyyGear 0.3.4)
- SIGILS: roll back Collections 0.2.13 together with SkyyGear 0.3.4 and put Sigils in a chest before any Gear rollback - add to the deploy rollback notes? [yes] (SkyyGear 0.3.4)
- ARMOR HANDS: Cobalt and Adamantite armor hands cost 1 Enchanted ingot (spec said 0)? [1] (SkyyGear 0.3.4 / Armory 0.1.24)
- HOE AREA: the bigger hoe area also works outside islands? [off] (SkyyGear 0.3.4)
- HOE AREA: the extra tilled blocks cost hoe durability? [no] (SkyyGear 0.3.4)
- MINING ARMOR: lock the higher-tier recipes later (spec: craft the first set once, then only upgrade)? [leave craftable for now] (SkyyGear 0.3.4)
- LOST TOOL (SkyyGear 0.3.2): after you get an exact copy and reforge / tier it up, the original stays Retired for good if it turns up (no swap back, sell or salvage) - else a bad reforge could be undone for free. OK? [yes]
- LOST TOOL: tool in a CLOSED Vault -> /pickaxe gives an exact copy (SkyyVault has no fetch hook yet). OK for now? [yes; add a Vault hook later]
- TOOL PERKS (SkyyTrees 0.3.6): the Tree Feller log table stops at level 6 (1,2,4,5,6,10), so the hatchet perk adds nothing once your tree is level 5+. Give it 8 numbers (e.g. 1,2,4,5,6,10,12,14) as the new default, or will you edit it in Server Setup -> Trees? [8 numbers]
- TOOL PERKS: Vein Mine = +1 ore per tool level on top of the tree's Vein Burst number, total capped at 8. Intended? [yes]







#### economy
- AUCTION HOUSE + REBIRTH (SkyyAuctions 0.1.5): unclaimed AH sale coins block a rebirth until the player claims them (then they are lost with the purse). Or should Continue claim them into the purse automatically? [block, ask the player to claim first]
- BAZAAR + REBIRTH (SkyyBazaar 0.1.11): should the Bazaar also refuse trades while a rebirth is busy (today it relies on SkyyCoins 0.1.7 refusing spends; Bazaar sales are income and still land)? [no, rely on SkyyCoins]
- ECONOMY AUDIT: add a real coin sink (the Tab or slayer costs from the old plan) before more faucets? [yes, after rebirth R3; numbers from a measured session] (research/Economy-Audit-1014.md)
- ECONOMY AUDIT: count goods bought with coins before a rebirth in the bank-bonus balance (they are kept either way)? [yes, at 90% of base value] (research/Economy-Audit-1014.md)
- ECONOMY AUDIT: scale merchant prices up 25% per rebirth once rebirth is on? [yes, off until rebirth is on] (research/Economy-Audit-1014.md)

#### bags
- AUTO-PICKUP 2 (SkyySacks 0.8.4): seeds / saplings from a harvest go to the Void (not the inventory), so replanting means pulling them out. Keep? [Void]
- AUTO-PICKUP 2: the vanilla 'picked up' popup still flashes next to our feed card. Keep it? [keep]

#### classes
- ABILITIES IN THE TREE (SkyyClasses 0.1.22 / SkyyTrees 0.3.7): A (ability) and M (modifier-slot) nodes are free, so turning an ability on is a free click; existing players' abilities start OFF until they click Enable (one-time chat hint)? [yes]
- ABILITIES: a game rune placed on a Mage / Priest Ability 2 / 3 key does nothing and shows a hint (the rune stays in the slot until moved)? [yes, blocked as M2]
- ABILITIES: which modifiers may go in both slots? [Power+, Radius+, Duration+, Efficiency, Pierce, Chain, Slow, Knockback+] (SkyyClasses 0.1.22)
- ABILITIES: Priest Spirit Shield gives the saved player a 4 s personal shield worth 15% of max Health (stands in for 'a small bubble that blocks projectiles')? [15% personal shield] (SkyyClasses 0.1.22)
- ABILITIES: Layered Ward splits the bubble in two equal halves, the inner half regrows 3% of the bubble's HP a second? [yes] (SkyyClasses 0.1.22)
- ABILITIES: lingering burn time 2 s + 0.5 s per level (2.5 s at Lv 1; the Mage class file says 3 s)? [2 s + 0.5 s / level] (SkyyClasses 0.1.22)
- ABILITIES: build the 4 waiting nodes next round (Priest Elemental Bubble PB2, Mage PA4 + PC2, Priest PA2; Guiding Light stays out)? [yes, next round] (SkyyTrees 0.3.7)
- ABILITIES: show ability levels in the SkyyHud ability widget? [later, as a SkyyHud change]
- ABILITIES: class tab is 1600 px wide, the other trees stay 1440? [yes] (SkyyTrees 0.3.7)
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]





#### pets
- PET KILLS (SkyyPets 0.2.5 / SkyyMobs 0.1.8 / SkyySacks 0.8.4): pet-kill loot + 'pet damage makes you top damager' are built but cannot be tested until pets fight (SkyyPets 0.4). Keep them idle until then? [yes]
- DRAGON as a pet with Aures' Dragon Nestkeeper: our secondary pet slot summons their dragon, or their mod owns the dragon and our slot links it, or our own dragons later? [(1) summon via our slot if Aures allows + it works, else (2) - docs/answered/pets.md 2026-10-06; decide after the survey + Aures' answer]


#### social
- GUILD info takes names with spaces? Needs a fix in SkyyGuilds (and the same left-out-button fix in SkyyShards / SkyyRebirth), not the menu. [yes, small Guilds fix] (SkyyMenu 0.3.23 Admin page)

#### profiles

#### rebirth
- BANK BONUS (SkyyRebirth 0.2 / SkyyBank 0.1.11): bonus is worked out on the profile's share of min(account total, 10M), the same cap as the brackets? [yes]
- BANK BONUS: it is flat on the whole capped balance - at the +3 total cap that is about +300k a day on a full 10M bank, ~3.5x the 85k base interest. Keep the Q7 numbers or lower / weight by bracket? [keep the Q7 numbers; refresh the Balance Workbench]
- REBIRTH stays OFF for real players until Skyy has tested R1-R4 (Bazaar / AH open-order check is in 0.3)? [keep OFF until Skyy has seen the Nexus tooltip]
- NEXUS: Rebirth / Continue work from both the Nexus click and the left-panel button? [both] (SkyyRebirth 0.3)
- ADMIN TEST REBIRTH works while the feature is OFF and skips the class / place / combat checks? [yes] (SkyyRebirth 0.2)
- R3 resets skills, purse and bank only; tree nodes and ability levels follow in R5 / R6? [ok] (SkyyRebirth 0.2)
- TREE: players cannot respec the tree themselves (admin refund only)? [yes] (SkyyRebirth 0.3)
- TREE: node list right (Wisdom / Dust / Echo / Fortune / tool / stat / keystone titles)? [yes, as built] (SkyyRebirth 0.3)
- TREE: a keystone title replaces 'Void-Touched N' until the next rebirth (newest earned title shows)? [yes] (SkyyRebirth 0.3)
- TREE: +4% points per Echo level (up to +40%), editable? [yes] (SkyyRebirth 0.3)
- TREE: opening row 2 costs 15 points and one maxed skill pays about 8, so the first rebirth cannot open row 2. Keep the spec curve or make early levels cheaper (Tree price growth 1 = every level costs 1)? [keep 1.08] (SkyyRebirth 0.3)

#### shards
- CO-OP (SkyyShards 0.1 / 0.2): co-op may enter your shard but only the owner can Collect, buy storage and Grow? [yes; row shard.coopCollect is off]
- MENU TILE: the Shards tile can Enter while the shard is placed, and Collect / upgrade any time once you own one? [yes]
- A picked-up shard (or one left by an island reset) makes nothing until placed again? [yes]
- Island sizes 13 / 21 / 29 and 6 slots from the spec, not the mockup? [spec]
- Growing costs coins + Eternal Seeds + a collection tier? [yes]
- Broken crops grow back free every 90 s, so hand-farming is free wheat? [yes, as you asked]
- Allow 20 shard worlds loaded at once? [20]
- Restyle the shard menu to the Sky Window look once the UI kit has it? [yes, later]
- SkyyCollections: exempt shard credit from the 20,000-per-minute cap? [yes, next Collections round]
- Collect goes to the inventory only until SkyySacks has a give bridge, then Magic Bags first? [yes]
- The totem's numbers count the whole island although its range is smaller, so hand-farming is extra on top? [yes for 0.1; range-based later (0.2 made range decide production)]
- One worker is capped at 12 items / minute before modifiers (the spec's limit; Server Setup -> Shards -> Totems -> Worker cap)? [yes, 12] (SkyyShards 0.2)
- Range decides production: a starter Harvest Spirit I makes 1 per minute on every island size, so growing only pays once a totem's range reaches the new crops? [yes] (SkyyShards 0.2)
- Totems are placed / picked up from the menu, and totems + modifiers are crafted in the shard menu (not at a bench)? [menu] (SkyyShards 0.2)
- Rebirth collection ranks give no reward (shown and announced only)? [none] (SkyyShards 0.2 / Collections 0.2.14)
- Each rebirth rank past a collection's last tier needs that tier's amount x 2^k (rebirth.rankFactor)? [2]
- An Enchanted crop from Harvest Moon counts as 100 Wheat for XP and collections? [yes] (SkyyShards 0.2)
- Totem tier speeds 1 / 1.25 / 1.5 / 1.75 / 2, and tier-up costs Enchanted Wheat : essence 1:10, 2:25, 3:50, 5:100 (spec's later steps are 2:25 ... 8:200)? [yes; 1:10 ... 5:100]
- MIT fold of MoreTotems (repo returns 404 so the licence cannot be re-checked): keep it with the 'Copyright (c) Nagatwin' notice? [keep] (SkyyShards 0.2)
- The MoreTotems pack mod still adds its own Water Totem, so two rain totems are live (no-duplicates rule): switch the pack mod off and record it in PACK.md? [switch off; main session]
- Collects made in creative mode count toward collections only at a later Collect in Adventure? [yes]
- One Farming Shard per profile, ever; a lost one comes back only via /shardadmin give; crafting at rebirth 2 only for a profile that never had one? [yes] (SkyyShards 0.2)
- Handheld Rain Totem ('click = 30 s of rain, costs Mana') is not built: build it with the Mana round? [Mana round]

#### quests
- DAILY JOBS (SkyyQuests 0.3): daily kill jobs pay an unidentified weapon and armor piece every time (up to 3 of each a day). Keep, or gear on only one job a day (else coins + item)? [gear on every kill job]
- Marlow's pole becomes a lifelong SkyyGear tool later (a SkyyGear round)? [yes]
- Quest Board look: Kweebec clerk or a board prop? [Kweebec until the prop is proven]
- Markers: floating '!' plus your own signs, or only your own signs? [both; Server Setup switch]
- 'Catch a fish' can be skipped to finish Marlow's line early? [yes, like every tutorial task]
- Daily 'Mine 64 stone' counts only natural blocks (stops place + re-break)? [allow for now]

#### ui
- ADMIN PAGE (SkyyMenu 0.3.23, research/Admin-Page-Plan.md): one Admin page in the SkyWynn Menu (right bar, admin only), tabs Server / Economy / Players / Diagnostics? [yes, as built]
- ADMIN PAGE: buttons run the existing commands as you (chat shows output), 5 status buttons also show a one-line result on the page? [yes, option C]
- ADMIN PAGE: which buttons first? [all six first (pause AH, list merchants, reload mod, set hub spots, exploration stats, server stats), the rest after]
- ADMIN PAGE: dangerous buttons (reset, remove, repay) confirm for 5 s before they run? [yes]
- ADMIN PAGE: restyle to the final tab look after the Sky Window kit probe (/skyprobe kit)? [yes]
- ADMIN PAGE: build 'Recent warnings' and 'Economy snapshot' later (each needs a new published value from the mods first)? [yes, later]
- SOUNDS (research/Sound-Pass-Plan.md): build an admin /soundtest <id> command first so you can audition ids by ear? [yes, in the SkyyMenu admin page]
- SOUNDS: quiet things (feed cards, XP gains, double drops) stay silent; sounds only on level ups, quest done, rewards and casts? [yes]
- SOUNDS: a custom level-up / rebirth fanfare needs audio we own or CC0 - later, or vanilla-only for release? [vanilla-only for release]
- SOUNDS: ability casts - own vanilla sound per ability where one fits, or one shared cast sound? [own per ability where a vanilla one fits, shared fallback]

