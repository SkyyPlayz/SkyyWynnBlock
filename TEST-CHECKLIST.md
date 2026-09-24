# SKYY'S TEST CHECKLIST — 5 mods, one world load
*Updated 2026-09-22 20:45. All five are deployed to your Mods folder and enabled for the "HUD mod" world. No .ui files
are used any more, so a plain RECONNECT is enough after a redeploy (no client restart needed).*

## Deployed versions
0.3.5 SkyyHud · 0.7.1 SkyySacks (not deployed yet) · 0.2 SkyyAccessories · 0.1 SkyySkills · 0.1 SkyyBazaar · 0.1 SkyyEssentials · 0.1.3 SkyyCoins · 0.1.3 SkyyCollections · 0.1 SkyyBank · 0.4.2 SkyyIslands (HyperEssentials DISABLED - crashes on death) · 0.1 SkyyRolls · 0.1.2 SkyyCoins · 0.1.2 SkyyCollections · 0.1.1 SkyyParty

## The moment you spawn (automatic)
- [ ] **SkyyHud**: widgets appear ~2s after spawn — coords (top-left), zone (top-right), game clock (bottom-left), coins (bottom-right) — updating every second
- [ ] **SkyyCoins**: chat "[SkyyCoins] Welcome! You received 10,000 starter coins" (first join only)
- [ ] **SkyySacks**: (grant removed in 0.1.4) any ore/stone you put in STORAGE while holding a sack vanishes into it within ~4s

## HUD editor v2 (0.3.2)
- [ ] `/skyyhud` opens: big 16x9 canvas (2/3 of your screen) with one chip per visible widget (map = coords, sign = zone, lantern = game clock, scroll = real clock, sunflower = day, torch = session, flag = online, gold bar = coins); legend line under it shows each widget's live text
- [ ] Dropping a chip anywhere never produces a stretched bar (corners only now)
- [ ] "Widgets / Settings" button bottom-right: list of all widgets with ON/OFF + Settings; Back returns to the editor
- [ ] Drag a chip to another cell: the widget moves there on the HUD after closing the editor (info line says "moved ...")
- [ ] Click a chip: the bar shows `<` `>` `^` `v`, Size-/Size+, "X hide", "Settings"; arrows nudge 10 px, X hides it (it appears under "Hidden widgets")
- [ ] Click a hidden widget's button: it comes back
- [ ] Settings: ON/OFF, Background ON/OFF (widget box disappears, text stays), size presets, Snap to TL..BR, Back to editor
- [ ] `/skyyhud profile save mine`, `/skyyhud reset`, `/skyyhud profile load mine`, `/skyyhud profile list`
- [ ] If drag or click does nothing: tell me — the server log records the raw payload

## Coins
- [ ] `/balance` (or `/bal`, `/coins`, `/purse`) shows 10000
- [ ] `/deathpenalty` (no argument) shows the current range; `/deathpenalty 5%` then `/deathpenalty 5%-10%` both accepted
      (if it says you lack permission, tell me — the command is gated on `skyycoins.admin`)
- [ ] `/coinsgive 500` adds 500 (same permission gate)
- [ ] Die once (jump off something) — chat says how many coins you lost; `/balance` reflects it. Respawn, die again — it applies again (once per death)

## Magic Bags (0.4.0)
- [ ] Bags in the inventory are named "Small Mining Bag" etc. with pocket-dimension flavor text
- [ ] Right-click a Mining bag: page opens on the Mining tab; only categories you carry a bag for show as tabs
- [ ] Capacity line: "Mining bag - holds up to 640 of each item - N stored" (Medium 2240, Large 20160; best bag counts)
- [ ] Grid: one icon per item with count; left click = 64 into storage (stays there; sweep-exempt 10 min), right click = 1
- [ ] Pick up all / Deposit all work; Deposit all pulls from storage, hotbar AND backpack
- [ ] Drop every bag, run `/pd`: "You need a magic bag on you to reach in"; pick a bag back up: everything is still there
- [ ] Put sticks + fibre in STORAGE: they pool into the Foraging bag (0.5.1)
- [ ] Open a WORKBENCH with copper only in the bag: the recipe list shows copper recipes as craftable; craft one; the bag's copper count drops and nothing appears/disappears in the inventory
- [ ] `/craft` (or the Craft button in `/pd`): tabs per basic crafting category; rows show icon, name, have/need counted from inventory + bags; Craft / x10 / All. Craft a campfire with sticks+rubble that are ONLY in the bag: it appears in your inventory and the bag counts drop
- [ ] `/pd`, `/bags` and `/sacks` all open it (0.3.0 experiment: does the inventory panel show under the page when opened by command?)

## Collections
- [ ] Break ~10 blocks of anything → `/collections` (or `/coll`) shows the counts, sorted high→low
- [ ] Break 50 of one block type → chat "Collection milestone! <block> I"

## Multiplayer isolation (needs a 2nd player)
- [ ] Both players carry a Mining bag; each pools different ore; `/pd` shows only your own; a bench opened by player A only counts A's bag (B's items never appear)
- [ ] A withdraws; B's pool file is untouched; coins/collections/layouts likewise per player

## Party
- [ ] `/party` shows help; `/party list` says you're not in a party
- [ ] `/party accept` with no invite → "No active party invite"; `/pc hello` → "You're not in a party"
- [ ] (needs a 2nd player later) invite/accept/leave, leader handoff when the leader leaves, party chat

## If ANYTHING crashes or misbehaves
Just tell me what you did — I read the exact error from your client log the moment it happens.
Client log: `UserData\Logs\<latest>_client.log`; server log: `UserData\Saves\HUD mod\logs\<latest>_server.log`.

## Test-build extras
None left. The 10,000 starter coins are a real feature (kept).

## SkyyBank 0.1 (new)
- [ ] `/bank` shows Bank 0 / Purse <your coins> and the interest line
- [ ] `/bank deposit 1000` -> purse drops, bank rises; `/bank withdraw all` reverses it; `/bal` agrees
- [ ] die with coins in the bank -> bank untouched, purse penalty as before
- [ ] (admin) `/bankconfig 5 1` then wait ~1-2 min -> "[Bank] You earned ..." message; `/bankconfig` shows next payout

## SkyyIslands 0.2 (spike + hub)
- [ ] FIRST: in the overworld stand at the spot you want as hub and run `/sethub` (needs group Admin - you have it); reply says the world name
- [ ] (HyperEssentials removed after the death crash) vanilla `/warp set <name>` + `/warp <name>`, `/spawn set` + `/spawn` work; `/hub` is ours
- [ ] die once (bear...) -> no crash, coins penalty message as before
- [ ] log out while standing on your island, log back in -> you appear at the hub with the welcome line
## (0.1 checks, still valid)
- [x] `/island` creates + teleports (verified 09-23); `/sethub` + `/hub` verified
- [ ] 0.2.2: island grass no longer black ~4s after arriving (relight); server log `[SkyyIslands] relight queued for ... (9/9 chunks)`
- [ ] walk around; `/island info` shows the world name (loaded)
- [ ] `/hub` -> the /sethub point (or default spawn if none set)
- [ ] `/island` again -> same island, instantly (still loaded) - chest/tree still there
- [ ] leave it empty for a minute, `/island info` should say (unloaded); `/island` -> "Loading the island..." -> same island with blocks intact (THE key test)
- [ ] log out on the island, log back in -> where do you spawn? (report)
- [ ] two players: A `/island invite B`, B `/island visit A`; B `/island` goes to B's OWN island, not A's
- [ ] server log `Saves/HUD mod/logs/*_server.log`: grep `[SkyyIslands]` for "starter island placed" and any "failed"

## SkyyRolls 0.1 (spike: does item metadata persist?)
- [ ] `/rolls give` -> a copper longsword appears; chat shows "gave: <Reforge> Weapon_Longsword_Copper dmg +x% ..." and a raw JSON line
- [ ] hold it, `/rolls read` -> same numbers
- [ ] relog, hold it, `/rolls read` -> SAME numbers (the whole point of the spike)
- [ ] drop it, pick it up, `/rolls read`; put it in a chest, take it back, `/rolls read`
- [ ] `/rolls reroll` -> new numbers on the same sword
- [ ] `/rolls read` on a vanilla item -> "no rolls (metadata keys: ...)" tells us what vanilla stores

## SkyyCollections 0.1.3
- [ ] `/collections unlocks` -> count of unlocked recipes (0 is fine on a fresh profile; break 50 of one block first)
- [ ] reach a milestone -> message ends with "+N recipe(s) unlocked - /craft"; `/craft` Collections tab lists them
- [ ] `Saves/HUD mod/mods/Skyy_SkyyCollections/unlocks.properties` exists with the comment header and `auto=true` on its own line

## SkyyAccessories 0.1 + SkyySacks 0.6.1 (bench accessories)
- [ ] craft an Accessory Bag in pocket crafting (4 wood + 4 cotton scrap); right-click it -> Accessory Bag page with 6 empty slots
- [ ] at a real Workbench craft "Workbench Accessory I" (Workbench + 4 copper bars); it shows under "Accessories in your inventory" -> Equip
- [ ] `/craft` now has a "Workbench I" tab listing Workbench recipes (tier-1 only) and crafts them from inventory + magic bags
- [ ] Unequip -> item returns to storage; the tab disappears from `/craft` (reopen it)
- [ ] relog -> bag contents still there (`/acc`)
- [ ] craft "Workbench Accessory II" (Accessory I + 30 copper bars, 20 iron bars, 20 linen scrap), Equip -> tab becomes "Workbench II", tier-2 recipes appear, Accessory I is handed back
- [ ] server log: `[SkyyAccessories] 0.1 ready`, no "failed" lines

## SkyyHud 0.3.3 (editor previews + screen-edge frame)
- [ ] green frame around the canvas with a small "screen edge" tag top-left
- [ ] under each drag handle (all handles are now the same white crystal) the widget's live text shows with its HUD background
- [ ] if NO preview text is visible: `/skyyhud preview front`, reopen the editor -> visible? and does dragging a handle still work? (report both)
- [ ] `/skyyhud preview off` hides them

## SkyyIslands 0.3.1 (protection) - needs a second account
- [ ] player B `/island visit A` works WITHOUT an invite ("look, don't touch") and B cannot break/place blocks or pick up drops there ("[Island] You can only build on islands you are a member of", at most once per 3s)
- [ ] A runs `/island invite B` -> B can build on A's island; B's own `/island` is still B's own island
- [ ] the owner builds normally; an admin (you, group Admin -> perm skyyislands.admin) can build anywhere

## SkyyIslands 0.4 (starter kit)
- [ ] on your next `/island` the chest at the corner holds: workbench, 10 oak logs, 8 dirt, 8 sticks, 5 bread, Accessory Bag (once; server log `[SkyyIslands] starter kit placed ... (6 stacks)`)
- [ ] jump off the island: you die below y=-32 and respawn on the island (report where you respawn and whether the coins penalty fired)

## SkyyAccessories 0.2
- [ ] Replace the 0.1 jar with SkyyAccessories-0.2.jar and check that the server log shows '[SkyyAccessories] 0.2 ready ... 15 talismans (stat effects on)' with no 'talisman effects failed' or 'bag page event failed' warnings.
- [ ] Speed: time a sprint over a fixed distance with and without a Speed Artifact in the bag. It should be about 12% faster, not about 25%. Take the talisman out and speed should return to normal within about 1 second. Also try with the talisman equipped: mount and dismount a horse or change /gamemode, then unequip. Speed must return to normal.
- [ ] Equip refusal: with a Vitality Ring in the bag, press Equip on a Vitality Talisman. You should get 'bag is full, or the same or a better Vitality talisman is already equipped' and the talisman must STAY in your inventory. Fill all 9 bag slots and try a 10th item: same message, and the item stays.
- [ ] Upgrade: with a Vitality Talisman in the bag, equip a Vitality Ring. You should get 'upgraded to Vitality Ring - Vitality Talisman returned' and the old talisman should be in your inventory.
- [ ] Stats: equip and unequip each of Vitality, Endurance and Intelligence and check the Health, Stamina and Mana maximums change and change back. With Regeneration equipped, Health should rise every 2 seconds.
- [ ] /craft (SkyySacks 0.6.1) with talismans and bench accessories equipped: the bench tabs should show, with NO 'itality Talisman I' style tab.
- [ ] Hold and drop a talisman: it should look like a coloured crystal shard, not a backpack. Bench accessories still look like the backpack; decide whether that is OK for now.
- [ ] Two players open the bag and equip or unequip at the same time: no hitching, and each only sees their own bag.

## SkyySkills 0.1
- [ ] F-harvest a ripe eternal crop or berry bush once: expect one '+N Farming XP' line and the crop resets. Spam F on the same (now unripe) plant: no more XP.
- [ ] In a world with block gathering disabled (or anywhere HarvestCrop fails), spam F on a ripe crop for 10 s: expect NO Farming XP at all (before this fix it paid on every press).
- [ ] Walk along a row of ripe eternal crops pressing F on each: every block pays once (the gate is per block, not per player).
- [ ] Break a ripe (non-eternal) wheat crop: Farming XP. Then F-harvest an eternal crop and immediately break it: only the harvest pays.
- [ ] With SkyyCoins disabled, level up a skill: the level-up line shows no coins. Enable SkyyCoins, restart, gain any XP in that skill: expect '[Skills] +X coins for earlier <Skill> level ups...', your coin balance goes up once, and <Skill>.paid in Skyy_SkyySkills/players/<uuid>.properties catches up to your level.
- [ ] With SkyyCoins on, level up normally: '+N coins' on the level-up line and exactly one balance increase per level.
- [ ] Join with an existing skills file and do nothing for about 5 s: /skills and anything reading skill:<uuid> (e.g. HUD) show your levels.
- [ ] Two players break and harvest blocks in the same area at the same moment: each player's /skills shows only their own XP.
- [ ] Server log: 'coins:fn:add did not pay ...' should appear (at most once a minute) only while SkyyCoins is off or broken.

## SkyyBazaar 0.1
- [ ] Confirm cancel: click 'Sell inventory' so the button reads 'Confirm sell', then click a DIFFERENT product cell. The button must go back to 'Sell inventory', and clicking it again must only show the preview text, not sell. Repeat with Buy 1 and with a category tab instead of the product click.
- [ ] Normal sell-all: click 'Sell inventory', then 'Confirm sell' within 10 s. Items are sold, the page shows 'sold X items of Y kinds for Z coins' and the same line appears in chat.
- [ ] Partial buy: fill your inventory to one free slot, pick an item with max stack below 64 and click Buy 64. You get what fits, the message says 'inventory full so N coins were refunded', and your purse matches.
- [ ] Full inventory buy: with no space at all, Buy 1 should say 'nothing bought and your coins were refunded' and the purse should be unchanged.
- [ ] /bazaaradmin info Ore_Copper after a few buys/sells: the lifetime bought/sold numbers go up.
- [ ] Without SkyyCoins loaded: /bz says trading is off and every button is refused.
- [ ] Open Skyy_SkyyBazaar/trades.log: there should be BUY/SELL lines, and no REFUND-FAILED / PAY-FAILED / *-ERROR lines during normal play.

## SkyyEssentials 0.1
- [ ] Two accounts, neither OP: /tpa, /tpahere, /tpaccept, /tpaccept <name>, /tpdeny, /tpacancel, /msg, /tell, /reply should all work. A request expires after 60s, and a second request within 10s shows the cooldown message.
- [ ] OP only: /fly toggles flight on and off and survives a world change. Revoke skyyessentials.fly while flying: flight should switch off within about 10s. A non-OP typing /fly should get the vanilla no-permission message.
- [ ] Return point fix: player A stands in the hub, player B stands on their own island. A runs /tpa B and B accepts, so A arrives on B's island. A runs '/instance exit': A should land back at the hub spot where they typed /tpa, not at B's island-creation spot and not at the default spawn.
- [ ] Island to island: A is on their own island (via /island) and does /tpahere B. B accepts and arrives on A's island. B runs '/instance exit': B should return to their own island at the spot where they accepted.
- [ ] Same world: two players on the same island do a /tpa, then one of them does /island visit or a vanilla portal: nothing odd should happen (no return point is recorded when the world does not change).
- [ ] SkyyIslands /hub should still get everyone out from any island, however they arrived.

## SkyySacks 0.6.2 (bigger bag page) + the chest-style question
- [ ] the bag page is ~35% bigger (86 px cells, bigger tabs, buttons and text) and nothing overflows the dark panel
- [ ] KEY QUESTION: type `/pd` (NOT right-click). Does your inventory appear under the bag page like a chest? Right-click opens without it. Report yes/no.

## SkyySacks 0.6.3 / 0.6.4 (craft page)
- [ ] /craft: tabs wrap onto 2+ rows inside the panel, first tab "< Back to bags" opens the bag page
- [ ] Furnace tab: put ~10 copper ore in the Mining bag, press Craft (1), then x10 -> bars appear in your inventory, the info line says "crafted ..."
- [ ] `Saves/HUD mod/mods/Skyy_SkyySacks/crafts.log` has one line per craft with done=... given=... and before->after counts (send it to me if anything vanishes again)
- [ ] NO refund needed: your 165 copper bars, the campfire and 8 torches are in your inventory's BACKPACK section. From 0.6.5 crafted items land in storage/hotbar first

## SkyySacks 0.6.6 (craft sorting)
- [ ] rows you can craft now are at the top, then copper -> bronze -> iron -> thorium -> cobalt -> adamantite -> mithril
- [ ] "Craftable only: OFF/ON" button next to Next > hides what you can't make; clicking a Craft button still crafts the right recipe after toggling

## SkyySacks 0.6.7 (life essence + Combat bag)
- [ ] life essence in your storage is pulled into the Farming bag within a few seconds
- [ ] craft a Small Combat Bag at a workbench (3 wool bolts + 4 bone fragments); bones/hides/feathers/essences you pick up go into it; the bag page shows 4 tabs that fit
- [ ] arrows stay in your inventory

## SkyySacks 0.6.8 (merged craft tabs)
- [ ] /craft shows only: < Back to bags | Crafting | Processing (if you have a Furnace/Campfire/Tannery/Salvage accessory) | Collections (if unlocked)
- [ ] Crafting lists pocket recipes + every equipped bench (armor, weapons, alchemy...) sorted craftable-first; Processing lists smelting/cooking

## SkyyHud 0.3.4 editor + 0.3.5 pages
- [ ] Select Zone (top right), press > with Step 25 until it touches the right edge, then press < until it touches the left edge. Open Settings and click 200%. Back in the editor and on the live HUD, the widget must be fully on screen and the preview must match the live HUD.
- [ ] In the Widgets / Settings page, hide a widget, open its Settings, change the size to 200%, then press ON. It must appear fully on screen.
- [ ] Run /skyyhud import Coords=1,tl,5000,-40,100,1 and check that Coords appears at the top-right edge of the screen, not off screen.
- [ ] Check that the previous behaviour still works: click and hold to drag the two top-right widgets apart, click one to select it, nudge it with the arrows at Step 1 and 5, use Size- and Size+, Hide it and bring it back from the Hidden row.
- [ ] Relog and reopen /skyyhud. The Step setting resets to 5 px (STEPS is pruned on leave) and every saved position is kept.
- [ ] Widgets page and each widget's Settings page are much bigger; '< Back' on Settings opens the Widgets list, '< Back' on Widgets opens the editor

## SkyyIslands 0.4.2 (grass tint)
- [ ] go to your island (/hub then /island if you are already there): grass tops turn green; server log '[SkyyIslands] relight queued ... re-tinted N columns'

## SkyyMenu 0.1 (not deployed yet)
- [ ] Player B types /tpahere A. Player A opens /skymenu > Players > Accept Teleport Request: the menu closes at once, A is teleported to B, and both get [TPA] chat messages.
- [ ] Player A types /tpa B. Player B accepts from the menu: B's menu closes and A arrives at B.
- [ ] With no pending request, click Accept Teleport Request: the menu closes and chat says [TPA] You have no pending teleport requests.
- [ ] Click Deny Teleport Request: the menu stays open with the status line '/tpdeny - see your chat'.
- [ ] Mods > SkyyBazaar: the info box shows 4 command lines. Also check the SkyyMenu line and all 8 SkyyEssentials lines: none should be cut off at the right edge. Check the SkyySacks and SkyyHud descriptions in the top info line to see whether the end is cut off.
- [ ] Hover the SkyWynn Menu item in your inventory: a blank line should appear before 'Lost it? Type /skymenu...'.
- [ ] As a normal player without a mod's permission, click that mod's entry: the menu stays open and shows 'You do not have permission for /x (node). Ask an admin.'
- [ ] Join with a new account and a full inventory: you get the 'inventory full' message. Free a slot, disconnect and reconnect within 30 seconds: the menu item should arrive about 4 seconds after joining (this is the finding 5 fix).

## SkyyClasses 0.1.1 (not deployed yet)
- [ ] Bomb test (finding 1): as a Berserker, throw a Weapon_Bomb at an NPC. Try it with a stack in hand and also with your last bomb, then swap to your axe before it explodes. Expect no damage and the chat line 'No class can fight with bombs yet'. Then set unassignedBlocked=false, run /classadmin reload, and the bomb should hurt.
- [ ] Arrow swap test: as a Warrior, fire a shortbow at an NPC and swap to a sword before the arrow lands. Expect 0 damage and 'Only Archers can use bows'. About 10 s later (or once the arrow is gone), sword hits work again.
- [ ] Archer control test: an Archer's shortbow/crossbow hits do damage. Kunai thrown by an Assassin do damage. A Warrior throwing their LAST kunai gets no damage.
- [ ] Legacy projectile test (finding 2): as an Archer, charge-throw a spear (a Warrior weapon) and log out or change world while it flies. It should deal no damage.
- [ ] Knockback test (finding 3): as a Warrior with a Kunai in the utility slot, hit an NPC with a sword. Expect 0 damage, no hit sound and NO knockback. A blocked bomb is still expected to push the target.
- [ ] Join test (finding 4): a classless player joins. The chat hint and the class page (about 2 s later) still appear. Switch worlds and nothing repeats. With promptEveryLogin=false, the page opens only on the very first join.
- [ ] Mage card is selectable; a Mage deals damage with a staff, not with a sword; a Warrior deals no damage with a staff or wand

## Command-rule builds (test as an ordinary player, not op)
### SkyyHud
- [ ] Only with Skyy's OK: run python build_skyyhud_0.3.6.py --deploy (or copy SkyyHud-0.3.6.jar to Mods by hand) and restart the server.
- [ ] As an ordinary player (group hytale:Adventurer, no op): /skyyhud and /shud open the HUD editor.
- [ ] /skyyhud export prints a code that uses ':' between fields (e.g. Coords=1:tl:8:8:100:1;...).
- [ ] Move a widget, then /skyyhud import <paste the exported code>: you get 'imported 8 widget layout(s)' and the HUD snaps back.
- [ ] /skyyhud reset puts the defaults back. /skyyhud preview prints the 'always on since 0.3.4' note.
- [ ] /skyyhud profile prints the usage line. Then /skyyhud profile save pvp, /skyyhud profile list shows pvp, move a widget, /skyyhud profile load pvp restores it, /skyyhud profile delete pvp, and /skyyhud profile list shows (none).
- [ ] /skyyhud profile save my layout saves the profile as 'mylayout'.
- [ ] Legacy form (the review fix): /skyyhud --action profile --code "save x" should reply 'saved profile x' (0.3.5 printed the usage line). /skyyhud --action profile --code "list" should list x.
- [ ] An old comma code still imports when quoted: /skyyhud import "Coords=1,tl,8,8,100,1;Zone=1,tr,8,8,100,1".
### SkyyCoins 0.1.3 -> 0.1.4
- [ ] As an ordinary player (not op, default Adventurer group): /balance, /bal, /coins and /purse each show 'Balance: N coins'.
- [ ] As the ordinary player: /pay <otherPlayer> 100 moves 100 coins and both players get the message. /pay <otherPlayer> 0 says 'Amount must be positive.' /pay yourself says 'You can't pay yourself.'
- [ ] As the ordinary player: /coinsgive 100, /deathpenalty and /deathpenalty 5% must all be refused with no permission.
- [ ] As admin (op / '*' or skyycoins.admin): /deathpenalty shows 'Death penalty is currently X% of carried coins...'.
- [ ] As admin: /deathpenalty 5% -> 'Death penalty set: 5% of carried coins.' Then /deathpenalty 5%-10% -> 'Death penalty set: 5%-10% of carried coins.' Then /deathpenalty shows 5%-10%.
- [ ] As admin: /deathpenalty abc -> 'Usage: /deathpenalty 5%  or  /deathpenalty 5%-10%   (currently ...)'. /deathpenalty 50%-10% -> 'Invalid range. Use 0-100, min <= max.'
- [ ] As admin: the old form /deathpenalty --percent 7% still sets 7%.
- [ ] Expected to fail: /deathpenalty 5% 10% (with a space) gives a wrong-number-of-parameters error. Type 5%-10% as one word.
- [ ] Check Skyy_SkyyCoins/config.properties (read-only look): penaltyMin/penaltyMax match the last setting. Die while carrying coins and confirm the loss falls in the range.
- [ ] Server log line should read '[SkyyCoins] 0.1.4 ready - /balance /pay /deathpenalty (current ...)'.
### SkyyCollections
- [ ] As a normal player (default group hytale:Adventurer, not op): /collections opens the Collections page, and /coll does the same
- [ ] As a normal player: /collections unlocks prints '[Collections] N recipe(s) unlocked...'. /collections recipes and /collections UNLOCKS do the same
- [ ] As a normal player: /collections reload is refused with the engine's no-permission message
- [ ] As a normal player: /collections --action unlocks still prints the unlock list. /collections --action reload prints '[Collections] no permission'
- [ ] As a normal player: /collections unlocks extra and /collections bogus give the engine's wrong-number-of-parameters error
- [ ] As an admin with skyycollections.admin (or '*'): /collections reload prints '[Collections] unlocks.properties reloaded (N explicit rule(s), auto=...)'. /collections --action reload does the same
- [ ] Break 50 of one block type, then run /collections unlocks and confirm the recipe count went up. /craft (Collections tab) shows the same recipes
### SkyyParty
- [ ] Test with a player who is NOT in hytale:Admin (a second account, or a player with no entry in permissions.json). Before this fix every command gave the no-permission error.
- [ ] /party and /p: the help line appears.
- [ ] /party invite <other player>: 'Invited X to your party (60s).' appears, and the target gets the invite message.
- [ ] As the target, /party accept: everyone in the party sees 'X joined the party!'.
- [ ] /party list: shows 'Party (2): A [leader], B'.
- [ ] /pc hello there everyone: every member sees '[Party] A: hello there everyone' with all words present.
- [ ] /party leave as the leader of a party of 3: the next member is promoted. In a party of 2 the party is disbanded.
- [ ] Repeat one command as Skyy (admin) to confirm admins still work.
- [ ] Negative checks: '/pc' with no text gives the engine's wrong-number-of-parameters usage message; '/party invite' with no name does the same.
### SkyyBank
- [ ] Copy SkyyBank-0.1.1.jar in by hand only after Skyy approves (the build did not use --deploy). Restart and check the log shows '[SkyyBank] 0.1.1 ready'.
- [ ] As an ordinary player (hytale:Adventurer, no '*'): /bank shows bank and purse. /bank balance shows balances. /bank deposit 500, /bank deposit all, /bank deposit 2k and /bank withdraw all move coins. /bank deposit on its own asks 'How much?'.
- [ ] As that same ordinary player: /bankconfig, /bankconfig 3 30 and /bankconfig 3 30 5m are all refused (no skyybank.admin).
- [ ] As an admin: /bankconfig shows the settings. /bankconfig 3 30 sets 3% every 30 min and leaves maxPrincipal as it was. /bankconfig 3 30 5m also sets max principal 5000000. /bankconfig abc 30 replies with the usage line and logs no warning (same as 0.1).
- [ ] Old flag forms still work: /bank --action deposit --amount all and /bankconfig --percent 2 --minutes 60.
- [ ] Wrong token counts (/bank a b c, /bankconfig 1 2 3 4) get the engine's usage error.
### SkyyIslands 0.4.2 -> 0.4.3
- [ ] Do these tests with a NON-admin account (no "*", default group). /island and /is should create or teleport you to your island. /island home and /island go should do the same.
- [ ] /island info should print two [Island] lines: world, loaded or unloaded, member count; then 'You are in world: ...'.
- [ ] With a second player online: /island visit <name> (and /island warp <name>) should teleport you to their island with the 'look, don't touch' note. Try breaking a block there: it should be blocked with the build-rights message.
- [ ] /island invite <name> (and /island add <name>): you get the 'can now BUILD' message and the target gets 'gave you build rights ... /island visit <you>'. The target types exactly that /island visit <you>: it should work, and they can now build on your island.
- [ ] Edge cases: /island invite <yourself> should say 'That is you.' Invite the same player twice: 'already a member'. /island visit <player without an island>: 'That player has no island yet.'
- [ ] /island visit with no name, and /island Steve (a bare name), should give the engine's wrong-number-of-parameters/usage error (expected). /island visit <offline name> should give the engine's player-not-found error.
- [ ] /hub and /lobby as the non-admin should warp to the hub (or to the default spawn if no hub is set).
- [ ] /sethub as the non-admin should say no permission. As an admin it should set the hub as before.
- [ ] Old flag form: in SkyyMenu 0.1's Players Online menu, 'Visit Their Island' and 'Give Island Build Rights' (they send /island --action visit|invite --player X) should still work. Typing /island --action info should still work too.
### SkyyBazaar
- [ ] As an ordinary non-op player (default group hytale:Adventurer): /bazaar opens the Bazaar page, and so does /bz.
- [ ] Same player: /bazaaradmin, /bazaaradmin reload and /bazaaradmin price Ore_Copper 5 are each refused with no-permission.
- [ ] As an admin ("*" or skyybazaar.admin): /bazaaradmin shows the status line and usage.
- [ ] Admin: /bazaaradmin price Ore_Copper 5 sets the base price; /bazaaradmin price Ore_Copper shows it; /bazaaradmin info Ore_Copper shows prices, demand and volume.
- [ ] Admin: /bazaaradmin reset Ore_Copper, then /bazaaradmin reset all, then /bazaaradmin reload. Each replies with success.
- [ ] Admin: the old form /bazaaradmin --action info --item Ore_Copper still works; /bazaaradmin price with no item gives a wrong-number-of-parameters error.
- [ ] Check trades.log: the admin price change is logged as in 0.1.
### SkyyRolls 0.1 -> 0.1.1
- [ ] As an admin ("*"): /rolls give -> a Weapon_Longsword_Copper appears with '[Rolls] gave: ...' and '[Rolls] raw: {...SkyyRolls...}'.
- [ ] /rolls give Weapon_Sword_Iron (or any valid item id) -> that item is given with rolls. Try a bad id to see how the engine reacts (the error is caught and shown as '[Rolls] error: ...').
- [ ] Hold the rolled item: /rolls and /rolls read -> both print the same rolls and raw JSON.
- [ ] /rolls reroll -> the item in the same hotbar slot gets new rolls; with an empty hand it says '[Rolls] hold an item first'.
- [ ] Old form still works: /rolls --action give --item Weapon_Sword_Iron and /rolls --action read.
- [ ] /rolls help (or /help rolls) -> the usage lists the read/reroll/give subcommands and give's <itemId> variant.
- [ ] As a normal player (hytale:Adventurer, no "*"): /rolls, /rolls give and /rolls give X must all be refused with no-permission. This is intended; the mod stays admin-only.
- [ ] Repeat the 0.1 persistence protocol with the new forms: give -> read -> relog -> read -> drop and pick up -> read -> chest in and out -> read.

## SkyyAccessories 0.4 (not deployed yet)
- [ ] Skyy approves, then run: python build_skyyaccessories_0.4.py --deploy (deploy with SkyySkills 0.2 if movement stacking is to be tested), then reconnect
- [ ] As a non-op (hytale:Adventurer) player, run /accessories, /acc and /accbag: the bag page must open
- [ ] With an old Vitality Ring (0.3 item) in the inventory, open the bag: the inventory row reads 'Rare Vitality Ring - old' with a blue RARE label. Equip it: the bag row reads 'Rare Vitality Talisman' and the info line says it was converted
- [ ] Check max Health: 100 base + armour, and a Rare Vitality should add 6% of that flat total (e.g. 100 -> 106; with Adamantite chest +24 -> 124 x 1.06 = 131.44). Eat a meat buff: max becomes flat x 1.06 x 1.05, not x2.15
- [ ] Unequip the Vitality talisman: you receive 'Rare Vitality Talisman' (not the old Ring) and max Health returns to the flat value. At a Workbench, the Epic Vitality recipe should accept it
- [ ] Craft a Common Speed talisman and upgrade it step by step to Legendary; each step's inventory tooltip should show the right quality colour/label. Equip the Legendary: bonus line '+10% Speed', and movement is 1.10x (x Acrobatics factor if SkyySkills 0.2 is on)
- [ ] Regeneration: take damage with a Legendary Regeneration talisman equipped: about 3 HP every 2 s at 100 max HP
- [ ] Craft the Omni (13 top-tier bench accessories at a Workbench), equip it next to e.g. Workbench II: /craft must show every bench's recipes up to max tier (Farming VII, Alchemy IV, ...) with SkyySacks unchanged. Equipping a second Omni must be refused
- [ ] Server log: '[SkyyAccessories] 0.4 ready - ... 30 bench accessories + Omni, 25 talismans in 5 rarities (percent layer on)' and no 'talisman effects failed' warning
- [ ] Two accounts: each player's bag, bonuses and Omni stay per player

## SkyySkills 0.3 (not deployed yet)
- [ ] Once Skyy approves: run 'python build_skyyskills_0.3.py --deploy' from SkyySkills/, together with SkyyAccessories 0.3 and SkyyClasses (with Mage flipped on), then Reconnect.
- [ ] Server log should say '[SkyySkills] 0.3 ready ... acrobatics on, perks on, max level 100 ... combat = class skill (SkyyClasses found)'. In Saves/HUD mod/mods/Skyy_SkyySkills/xp.properties the levels= line now has 100 entries under a 'SkyySkills 0.3: max level 100' comment, and the perk.* section appears exactly once.
- [ ] As a normal (Adventurer) player run /skills and /skill. Every row has a 'Stats' button. The Combat row reads 'Combat - choose a class with /class' without a class, or your class skill (for example 'Archery 2' with a bow icon) with one.
- [ ] Click Stats on each row and check the title 'X - level L of 100', the XP line, 'Boosts right now', 'Level L+1 adds' with its coins, and the how-to line. '< Back' should return to /skills. 'Top 10' should show the leaderboard, and its Back should return to the list.
- [ ] Try /skills stats acrobatics, /skills stats archery, /skills top combat, /skills top mining and /skills quiet. /skills reload should be refused for a normal player and work for an admin.
- [ ] Stat perks: set perk.mining.staminaPerLevel=1 and perk.farming.healthPerLevel=5, then run /skills reload. Within 1 second max Stamina should rise by your Mining level and max Health by 5 x your Farming level. Put the values back and reload.
- [ ] Double drops: set perk.foraging.doubleDropPerLevel=1.0 and reload. At Foraging level 1 or higher, chopping a natural oak trunk should add an extra Wood Oak Trunk to your inventory with a 'Double drop! +1 Wood Oak Trunk (Foraging perk)' chat line. A log you placed yourself must not double.
- [ ] Repeat the double-drop test for Mining (copper ore should give an extra Ore Copper and Cobble) and for Farming (breaking ripe wheat, and pressing F on a ripe berry bush). Put the rates back afterwards.
- [ ] Without SkyyClasses: killing a monster should print '[Skills] Combat XP comes from your class skill, but SkyyClasses is not installed...' once per session and give no XP.
- [ ] With SkyyClasses and no class: a kill should print 'Choose a class with /class...' once. Then choose Archer. If you had old Combat XP you should see '[Skills] Your old Combat XP (level N) now counts for Archery.'
- [ ] As an Archer, a kill with a shortbow should give Archery XP. A kill with fists or a pickaxe should give none, with a one-time message: 'Only kills with your Archer weapons (Shortbow / Crossbow / Arrow) earn Archery XP.'
- [ ] Run /classadmin set <you> Warrior. The Combat row should switch to Swordsmanship with its own level. Switch back and the Archery level should be intact. players/<uuid>.properties should contain Combat.Archer and Combat.Warrior.
- [ ] Damage perk: temporarily set perk.combat.damagePerLevel=0.5 and reload. Class-weapon hits on monsters should become clearly stronger, while hits on players stay unchanged. Put it back afterwards.
- [ ] Level up any skill and check that the coins (level x 100) are still paid. Check that the bridge text shown in /menu now includes the class skill.

## SkyySacks 0.7.0 / 0.7.1 (timed Furnace + Tannery, merged Crafting, not deployed yet)
- [ ] With no accessories equipped, run /craft. Tabs should be '< Back to bags' | Crafting (+ Collections if any), and Crafting should list the Fieldcraft recipes.
- [ ] Equip Workbench, Alchemy Bench, Furnace and Tannery accessories in the accessory bag and reopen /craft. Tabs should be Crafting | Alchemy | Furnace | Tannery. Crafting should show workbench recipes but no bars, leathers or potions; Alchemy should show potions and craft instantly.
- [ ] Double-deduction fix: note a bag item count in /pd, craft something in Crafting that needs it from the bag (the inventory must lack it), and check that the bag dropped by exactly the recipe amount. crafts.log should show matching counts.
- [ ] Furnace tab: with copper ore on you or in bags, click x10 on Copper Bar. The ore count should drop by 10, the queue should read 'Copper Bar x10 (10 / 256 units)', the progress line should say OUT OF FUEL, and one 'ran out of fuel' chat message should appear.
- [ ] Click a Load fuel button (e.g. Wood Oak Trunk x64). The progress bar should advance about every 2s: 10s per bar at Furnace I, 7s at Furnace II. Charcoal should appear in 'Ready' every 2 logs burned.
- [ ] Hover over buttons while the bar is updating and confirm the client does not crash. If a click is ignored during an update, press it again and note how often that happens.
- [ ] Click Collect. The bars should go to storage, 'Ready' should empty, and crafts.log should get a COLLECT line with given/left.
- [ ] Close the page for 30s and reopen: progress should have continued. Log out for about 1 minute and log back in: expect 'Your Furnace is done...' if it finished.
- [ ] Queue 5 more, then click Cancel queue: all 5 ores come back (including the one in progress). Click Unload fuel: the unburned logs come back.
- [ ] Tannery tab: there should be no fuel row and it should say 'needs no fuel'. Light hide to leather should take 20s at Tannery I and 12s at Tannery II.
- [ ] Restart the server mid-queue. On rejoin the elapsed time should count, and Skyy_SkyySacks/processing/<uuid>.properties should hold the queue.
- [ ] Unequip the Furnace accessory while items are still queued. The Furnace tab should stay with no Queue buttons and 'accessory not equipped (queued items still finish)', and should disappear once everything is collected.
- [ ] Regression checks from 0.6.8: bag page tabs, Pick up all / Deposit all, the auto-sweep, crafting at a real workbench from bags, the Craftable-only toggle, and '< Back to bags'.
- [ ] as an ordinary player (not op): /sacks, /pd, /bags, /craft and /recipes all open

## SkyyMenu 0.1.2 (built 2026-09-23 22:40, NOT deployed - needs Skyy's OK)
- [ ] Open the menu (right-click the SkyWynn Menu item). It should be clearly bigger (about 1.4x) with the info box ABOVE the icons.
- [ ] Hover the top icon (Your Profile). The whole tooltip should be on screen.
- [ ] Click Pocket Dimension, then click the Craft tab in the bag page. The craft page must open (0.1.1 hung on "Loading...").
- [ ] From the menu open: Crafting (click Craftable only + a tab), Bazaar (click a product), HUD editor (select a widget), Collections, Skills. Every button must react.
- [ ] From the menu use a teleport entry (Island / Hub / Spawn / a warp). The menu should close and you should teleport.
- [ ] A keep-open entry (e.g. a bank action) should leave the menu open with a status line.

## SkyyClasses 0.1.4 (built 2026-09-23 22:40, NOT deployed - needs Skyy's OK)
- [ ] As an Archer, hit a mob with a sword. A popup (notification toast) should show the sword icon, "You can't use this weapon" and "Only Warriors can use ...". The hit does no damage.
- [ ] Keep hitting: at most one popup every 1.5 s, the chat line at most every 3 s.
- [ ] With no class (fresh player, no SkyyProfiles), hit with a weapon: the popup title should be "Choose a class first".
- [ ] Put a Kunai in the utility slot as a non-Assassin and hit: the popup text should mention the utility slot.
