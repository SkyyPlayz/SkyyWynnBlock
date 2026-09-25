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

## SkyyClasses 0.1.1 (historical spike — not the current jar)
0.1.2+ removed Berserker and set `ALLOW_SWITCH=false` (no paid class switch). Current code is 0.1.4 and still has no Berserker. Design as of 2026-09-24 wants Berserker back, status PENDING — these steps are not a test of that future class. "As a Berserker" below only applied to the 0.1.1 jar.
- [ ] Bomb test (finding 1): as a Berserker (0.1.1 jar only), throw a Weapon_Bomb at an NPC. Try it with a stack in hand and also with your last bomb, then swap to your axe before it explodes. Expect no damage and the chat line 'No class can fight with bombs yet'. Then set unassignedBlocked=false, run /classadmin reload, and the bomb should hurt.
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

## SkyyRolls 0.1.2 (built 2026-09-23 22:45, NOT deployed - needs Skyy's OK; admin-only test tool)
- [ ] /rolls give mithril bow -> gives Weapon_Shortbow_Mithril with rolls (a real bow, not "Invalid Item").
- [ ] /rolls give weapon_shortbow_mithril (any capitals) -> the same bow.
- [ ] /rolls give iron sword -> gives nothing and suggests Weapon_Longsword_Iron, Weapon_Sword_Iron.
- [ ] /rolls give (no name) -> the default copper longsword.
- [ ] Metadata test (the point of the spike): /rolls read on the bow, relog, /rolls read again (same numbers), drop + pick up, chest in/out.

## Profiles set (SkyyProfiles 0.1 + per-profile Coins/Bank/Sacks/Skills/Collections/Accessories/Islands/Classes) - built + integration-checked 2026-09-24, NOT deployed
0. **Deploy the set and start the server.** The log shows a ready line for every Skyy mod, including "[SkyyProfiles] 0.1 ready". SkyyClasses says "SkyyProfiles found - class per profile" and SkyyIslands says "island protection on …". No "already registered" lines and no load errors.

**A: new player** (an alt account that has never joined)

1. **Join.** Expect the Menu item in slot 9, the HUD, the chat lines "Welcome! Create your profile" and "10,000 starter coins", and exactly one page, Create Profile, after about 2–3 s. No SkyyClasses picker. HUD shows Coins 10,000.
2. **Relog, and right-click the Menu item within 2 s.** The Menu stays open. The Create page appears about 1 s after you close the Menu.
3. **Press Later, then run `/class`.** Expect "You have no profile yet" and no Choose buttons.
4. **`/profiles` → pick Warrior → Create profile.** The page closes with "Profile … created", no teleport, and the inventory is unchanged. Within 2 s `/class` shows Warrior locked, and `/balance` shows 10000 (profile: name).

**B: your own account** (log out on your island before deploying)

5. **Join.** Expect "Welcome back! You start in the hub", then about 1 s later the Create page, once, with your old class pre-selected. The log has no "could not open the Create Profile page".
6. **Create profile 1.** Coins, bank, `/skills`, `/pd`, `/acc`, `/collections` and `/island` are all unchanged.

**C: create profile 2**

7. **`/profiles` → Create new → another class.** Expect "Switched to …", an empty inventory except the Menu item, a loading screen, and arrival on a new island whose chest holds the starter kit, including an Accessory Bag.
8. **Within about 2 s of arriving:**
   - coins: "New profile: 10,000 starter coins", HUD Coins 10,000, `/balance` shows profile 2;
   - `/bank` 0, `/skills` all 0 with the new combat skill, `/acc`, `/pd` and `/collections` empty;
   - `/class` locked to the new class;
   - `/island info` shows the `…-p2` world;
   - the Menu profile tooltip agrees.
9. **Check the files.** `Skyy_SkyyProfiles/inventories/<uuid>.json` exists, the file in `switching/` disappears about 30 s after the switch, and `switches.log` has a SWITCH line.

**D: switch back**

10. **Switch to profile 1.** Every item is back in its slot (armor and backpack size too). You land on the old island, the HUD shows profile 1's coins, there is no starter-coins message, and everything else matches step 6. `inventories/<uuid>-p2.json` now exists.
11. **Hit a mob, then try to switch.** Refused with "You are in combat - wait N s".

**E: crash**

12. **Switch profiles, and within 5 s kill `java.exe`. Restart and join.** Expect a RECOVER line in the log and the "interrupted by a server stop" chat. You are on the profile named in the players file (`active=`), with that profile's inventory and coins. Switch back and check that no item is in both profiles. If you spawned on an island, you are sent to the hub.

**F: relog on profile 2**

13. **On profile 2, log out on its island, wait 15 s, log back in.** Expect the hub, "Playing profile … (class)" and no Create page. The HUD shows profile 2's coins within 1 s. `/skills`, `/bank`, `/acc`, `/pd` and `/island info` all show profile 2 on the first try. The log shows no "profile switch" or "now uses … -p2" lines at login.
14. **Graceful `/stop`, restart, and repeat step 13.** Same result.

## Build round 2026-09-24: SkyySkills 0.4, SkyyCooking 0.1, SkyyTrees 0.1, SkyySacks 0.7.3, SkyyAccessories 0.4.2, SkyyCollections 0.2 (built, reviewed, cross-checked, NOT deployed)
Deploy the whole 17-mod set together (python tools/deploy_set.py, only after Skyy says deploy). Riskiest first.

1. **Server log.**
   - Expect: `[SkyyCooking] 0.1 ready … SkyySkills found`.
   - Expect: no asset errors naming `Skyy_Cook_`.
   - Expect: `[SkyySkills] 0.4 ready … trees bridge on … SkyyTrees found`.
   - Expect: `[SkyyTrees] 0.1 ready - /tree; 48 of 48 nodes on …; SkyySkills trees bridge found`.
   - Expect: `[SkyySacks] 0.7.3 ready` and `config: craft page search box ON`.
   - Expect: `[SkyyAccessories] 0.4.2 ready … (6 retired …)` and `[SkyyCollections] 0.2 ready` / `started - …`.
2. **Cooking assets.** Run `/cookadmin give pie_meat 5`.
   - Expect: "Meat Pie (Grade 5)" in Rare colour; tooltip 30% heal, 4% every 2 s, +30% max health, 12:00.
   - Hover an Accessories item too: both mods' names show, not raw keys (three mods now ship `server.lang`).
3. **Cooking Stats page.** Open `/skills` → Cooking → Stats.
   - Expect: Grade lines from SkyyCooking.
   - Expect: NO line "WARNING - graded dish assets are not loaded". If it shows, the asset pack failed; food stays plain.
4. **Eating.**
   - Grade 5 pie: regen 12:00 and +30% max health.
   - Grade 10 pie, then a Grade 5 skewer: the pie's buffs stay.
   - Two Grade 5 dishes stack in one slot; Grade 5 and Grade 6 do not.
5. **New Cooking Bench recipes.** A placed Cooking Bench lists Cooked Wildmeat, Grilled Fish and Roast Vegetable.
6. **Search box.** Open `/craft`.
   - If the client disconnects with "Failed to parse or resolve document": set `craftSearch=false` in `Saves/HUD mod/mods/Skyy_SkyySacks/config.properties`, wait 10 s, reconnect. `/craft` must then open without the box.
   - If it opens: type `iron sword`, press Enter. Expect results from Crafting, Smithing and Farming, and the text stays in the box.
   - Search button: same result. Clear: back to normal.
   - `/craft copper` opens already searching.
7. **Vanilla Furnace.** Smelt copper ore, then take the bars out by dragging, by shift-click and by double-click.
   - Expect: "+5 Smithing XP" per bar every time.
   - Expect: charcoal pays 0.
   - Expect: dragging a bar into the output slot is refused.
8. **SkyySacks Furnace tab.** Queue copper ore.
   - Expect: Smithing XP within about 1 s of each finished unit, and a `SMITHING …` line in crafts.log.
   - Expect: Tannery pays nothing.
9. **Cooking at the bench.**
   - Cook Bread at Cooking 0 (ingredients from a bag): plain Bread and 12,900 Cooking XP (→ Cooking 10). The next Bread is "Bread (Grade 1)".
   - Queue 5 Meat Skewers: 5 dishes and 5 × 5,250 XP, not 25×.
   - Only a "Cooking XP" line appears, once per dish; no other skill gains XP.
10. **Grade 5 and blocked cases.**
    - `/skills xp cooking 55.2m`, then cook a Meat Pie: exactly one "Meat Pie (Grade 5)".
    - Creative: plain pie, no XP.
    - Placed Campfire: plain food, no XP.
11. **SkyyTrees ↔ SkyySkills.**
    - `/skills` shows a "Tree" button on Mining, Foraging, Farming and Cooking only; each opens its tree, and "< Skills" comes back.
    - Buy Cooking Wisdom (tier I): the Cooking Stats page shows "Skill tree: +1% XP".
12. **Master Chef.** `/skills xp cooking 111.7m` (level 60). Buy one node per tier up to Master Chef (9 tokens).
    - Expect: dishes come out Grade 7; `/cooking` shows it.
13. **Gathering nodes.**
    - Mining Wisdom and Fortune: the block XP and "Double drop!" rate go up.
    - Spread, Vein Burst and Tree Feller: extra blocks break and each pays XP.
    - A block you placed is never broken by an ability; nothing breaks on another player's island.
14. **Craft page tabs.** With Workbench, Weapon Bench, Farming Bench, Furnace and Tannery accessories equipped:
    - Expect the tab bar: < Back to bags | Crafting | Smithing | Farming | Furnace | Tannery | Collections.
    - Crude pickaxe on Smithing, torch on Crafting, copper hoe on Farming, salvage recipes on Crafting.
    - No potions or cooked food anywhere, even with an old Alchemy, Cooking or Campfire accessory equipped.
15. **Retired accessories.**
    - The three retired items show "(retired)" in their names.
    - Equip is refused with a chat line; an equipped old copy shows "DOES NOTHING"; Unequip works.
    - The Omni recipe asks for 10 accessories, and the SkyyMenu tooltip says 10 bench accessories.
16. **Collections.**
    - Break cobblestone and wood and F-harvest crops: counts rise; the log shows "F-harvest pickups reach SkyyCollections".
    - Tier rewards pay coins and exactly +500 / 2,500 XP, even with a Wisdom node.
    - Collection-unlocked recipes show on the `/craft` Collections tab.
17. **Acrobatics falls.**
    - A safe drop pays 0.
    - A fall that hurts and that you survive pays XP, more for bigger drops, at most 2,000 per landing.
    - Landing in water or dying pays 0.
18. **Profiles.** Switch to profile 2 and back.
    - Each profile keeps its own tree nodes, Cooking level, bags and Furnace ledger.
    - XP never lands on the other profile.
19. **Regression.** SkyyMenu buttons (Skills, Collections, Craft, Bags, Accessories, Bazaar, Island, Hub) still open their pages.

## Campfire accessory back: SkyyCooking 0.1.1, SkyySacks 0.7.4, SkyyAccessories 0.4.3 (built + cross-checked 2026-09-24, NOT deployed)

1. **Server log:** check for these ready lines, no `Skyy_Cook_` asset errors and no SkyyAccessories campfire warning.
   - `[SkyyCooking] 0.1.1 ready ... Campfire accessory bridge cook:fn:campfire (Food_Wildmeat_Cooked,Food_Fish_Grilled,Food_Vegetable_Cooked)`
   - `[SkyySacks] 0.7.4 ready ... Campfire accessory tab ...`
   - `[SkyyAccessories] 0.4.3 ready ... Campfire accessory back ...`
   - In `<world>/mods/Skyy_SkyyCooking/cooking.properties`, `campfire.buffFactor=0.75` and `campfire.xpFactor=0.5` each appear exactly once.
2. **No accessory equipped:** `/craft` has no Campfire tab, and no cooked food appears in Crafting, Smithing, Farming, search or Collections.
3. **Craft and equip the accessory:**
   - At a Workbench, the Campfire Accessory recipe is 1 Campfire + 4 Copper Bars, and its tooltip does not say "(retired)".
   - Craft it and equip it in `/accessories`.
   - Reopen `/accessories`: the bottom line reads "Campfire quick cook on this server - 50% Cooking XP and 75% of your cooking bonus".
4. **Campfire tab:** `/craft` shows it after Farming, with the orange line "Campfire accessory = emergency cook: 50% Cooking XP, 75% of your cooking bonus...", exactly 3 rows and no search row.
5. **Main cook at Cooking 50** (rows say "comes out Grade 4"). Put 2 raw meat in the Farming bag only and press x10.
   - Exactly 2 "Cooked Wildmeat (Grade 4)" land in storage and the bag drops by 2.
   - The info line reads "crafted 2 of 10 x ... Grade 4 - extra materials were returned".
   - You get +1,600 Cooking XP, once (no extra craft XP from SkyySkills), plus the one-time chat hint.
   - The `crafts.log` line ends `campfire=Skyy_Cook_Food_Wildmeat_Cooked_G4`.
6. **Bench comparison:** the same dish at a placed Cooking Bench comes out Grade 5. The Grade 4 tooltip numbers are about 1.74x plain; Grade 5 is 2.00x.
7. **Other dishes:** 3 Grilled Fish give Grade 4 and 3,000 XP. Roast Vegetable pays 600 XP per dish.
8. **Levels:** Cooking 0–19 gives "comes out plain", a plain dish and half XP. Cooking 20 gives Grade 1, Cooking 100 gives Grade 8, and Master Chef makes it Grade 9.
9. **Creative mode:** the row says plain, and a craft gives a plain dish and 0 XP.
10. **Live factors:**
    - Set `campfire.xpFactor=0.25` and `campfire.buffFactor=0.6`, run `/cookadmin reload` and reopen `/craft`.
    - The banner says "25% Cooking XP, 60% of your cooking bonus", the row says Grade 3, and 2 wildmeat pay 800 XP.
    - The `/accessories` line shows 25% / 60%, and the log has one SkyyAccessories warning.
    - Then set `enabled=false` and reload: the banner says graded cooking is switched off, and crafts give plain dishes with no XP.
    - Put the defaults back.
11. **Big batch (the fix):**
    - With at least 2,000 raw meat in bags, press "All": every dish is Grade 4 and Cooking XP is about 1,500,000 (the per-minute cap).
    - The log says "a Campfire accessory batch paid 1500000 of ... base XP".
    - Another click within the minute still grades the dishes but pays no XP.
12. **Unequip with the page open:** pressing Craft shows "equip the Campfire accessory in your accessory bag to cook here", the tab disappears and nothing is used.
13. **Omni only:** the Campfire tab appears, and `/accessories` shows the campfire line.
14. **Placed vanilla Campfire:** still plain food and no Cooking XP.
15. **Profile switch with the page open:** you get the "your profile changed" or paused message. A profile without the accessory has no tab.
16. **Retired accessories:** the Alchemy Bench and Cooking Bench accessories are still refused on Equip.
17. **Optional, admin:** `/cookadmin campfire wildmeat_cooked 0` shows "bench Grade 5 -> campfire Grade 4" and "XP sent 0". Skip this if `/cookadmin` still prints nothing (the bug logged at 06:40).

Files changed, in `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\`:
- tools\cooking_0_1_1_patch.py
- SkyyCooking\build_skyycooking_0.1.1.py
- SkyyCooking\SkyyCooking-0.1.1.jar
- tools\acc_0_4_3_patch.py
- SkyyAccessories\build_skyyaccessories_0.4.3.py
- SkyyAccessories\SkyyAccessories-0.4.3.jar
- tools\deploy_set.py
- SkyySacks\SkyySacks-0.7.4.jar (rebuilt, source unchanged)

## SkyyRolls 0.1.3 (built + reviewed 2026-09-24, NOT deployed; admin-only test tool)
- [ ] /rolls give mithril bow: the item NAME reads "<Reforge> Mithril Shortbow" in its rarity colour and the tooltip lists Reforge, Damage, Strength, Crit, Roll Quality (engine ItemDisplay metadata - the SimpleEnchantments method; no DynamicTooltipsLib needed).
- [ ] Items rolled before 0.1.3 (the Heroic / Withered bows) show their rolls about 3 s after joining.
- [ ] /rolls reroll on a sack, arrows or any non weapon/armor/tool: refused with a chat line.
- [ ] Hold the rerolled Foraging sack, /rolls clear: the rolls and the display go away, the bag still works.
- [ ] Relog, drop + pick up, chest in/out: the rolls and the display stay.

## SkyyHud 0.3.7 (built + reviewed 2026-09-24, NOT deployed)
- [ ] Reconnect: the HUD looks exactly like 0.3.6; old layouts unchanged.
- [ ] /skyyhud -> Widgets / Settings -> Settings on a widget: page fits the screen; Color (13 swatches), Bold, Italic, Glow + Glow color, Preview, Reset style.
- [ ] Gold + Italic ON + Glow ON: page preview and live HUD update, no disconnect. Try glow Black, Same, Aqua.
- [ ] Glow ON at every size 50-200% and every snap position: widget stays in place, glow centred.
- [ ] Editor: styled preview drawn; click/drag still selects and moves the widget. Reset style = old look.
- [ ] /skyyhud export -> reset -> import <code> restores the style; same with profile save/load.
- [ ] Zone widget: own island 'Your Island'; other profile's island 'Island' after switching; a friend's island 'Island'; hub shows the Hytale zone name (or 'Hub'); nothing runs into the next widget.
- [ ] Client log: no "Failed to parse" / "Selected element not found".

## Exploration round: SkyyExploration 0.1, SkyySkills 0.4.1, SkyyTrees 0.2 (built + cross-checked 2026-09-24, NOT deployed; deploy all three together, never go back to Skills 0.4 once Exploration XP exists)
**In-game test plan (riskiest first)**
1. **Start with the new 18-jar set.** Expected:
   - "[SkyyExploration] 0.1 ready" with no LATE-fallback warning.
   - "[SkyySkills] 0.4.1 ready ... Exploration (via SkyyExploration, no boosters)".
   - "[SkyyTrees] 0.2 ready ... 64 of 64 nodes on (8 coming later)".
   - The Exploration block is added to `xp.properties` once and the 0.2 lines to `trees.properties` once; a second restart adds neither again. No errors.
2. **Loot chest capture.** Go into never-generated terrain and run `/exploreadmin stats`. Expected: the capture counter rises. Then:
   - First open of a world loot chest: chat line plus Exploration XP.
   - Second open: nothing.
   - A chest you placed yourself, or the island starter chest: nothing.
3. **XP arrives in Skills.** Expected:
   - `/skills` shows the Exploration row (map icon) after Acrobatics, with XP rising by exactly the chest's number.
   - `/explore` shows no "waiting for SkyySkills" text.
   - Level-ups pay coins.
4. **No boosters.** Set `multiplier=2.0`, add Exploration to `bridge.bonus.xpSkills`, then `/skills reload`. Expected: one WARN, Exploration XP still exact, Mining doubled.
5. **Map coverage.** Expected:
   - Walking into new chunks gives one combined line every 30 s.
   - `/fly` or creative gives no XP and no line.
   - Teleporting still counts.
   - `/explore quiet` hides the line.
   - Your own island pays nothing.
6. **Zones.** Entering a Zone1 region for the first time gives zone XP once. The Zones tab lists it.
7. **Titles.** Expected:
   - Pick a title with `/title`: your chat shows the [Title] prefix, and other players see it too.
   - `/title wor` asks for more letters.
   - `/title off` removes the prefix.
8. **Stamina and Health.** Expected:
   - `/skills xp exploration 1175` gives level 5 and +0.5 max Stamina on the bar.
   - Tree Second Wind 1 adds +0.2 Stamina.
   - Wanderer's Heart 1 adds +0.4 Health.
9. **Acrobatics tree** (use `debug.extraTokens` and `extraDust`). Expected:
   - Fleet Foot: faster.
   - Spring Step: higher jump.
   - Soft Landing: less fall damage.
   - Quick Dodge: longer dodge push; with `acro.dodgeBoost=false`, no push.
   - `/skills stats acrobatics` shows the "Skill tree:" line.
10. **Exploration tree.** Treasure Sense makes the `/explore` chest luck show "+ tree X%". Scavenger sometimes pays "10 x level" coins on a first-opened chest.
11. **Pages.** Expected:
    - `/skills` shows 9 rows with nothing clipped. The Acrobatics and Exploration Tree buttons open the right trees.
    - `/tree` shows 6 tabs on one row. Exploration S5-S12 are "Coming later" and Buy is refused.
    - On `/explore`, the "< Skills" and "Exploration tree" buttons replace the page cleanly.
    - The SkyyMenu profile box's skills line (now one entry longer) still fits.
12. **Profiles.** Switch to another profile. Expected:
    - Exploration level, zones, chests, title, both new trees and `/bank` balance are separate (the bank earns interest per profile).
    - The same world chest pays once again on the new profile.
    - Switching back restores everything within about 1 s.
13. **Two players, if possible.** Expected:
    - The same chest pays each player's profile once.
    - After logoff, no leftover tree speed stays on the player.
    - The other player is unaffected.

**Files:**
- `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\tools\deploy_set.py` (edited)
- `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\SkyyExploration\SkyyExploration-0.1.jar`
- `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\SkyySkills\SkyySkills-0.4.1.jar`
- `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\SkyyTrees\SkyyTrees-0.2.jar`

## TWO-PLAYER TEST (party, guild, widgets, islands): SkyyParty 0.1.3, SkyyGuilds 0.1, SkyyHud 0.3.8, SkyyIslands 0.4.5 - 2026-09-24 (S = Skyy, host; F = friend, ordinary player, first join)
0. With the game closed and Skyy's OK, run `python tools/deploy_set.py`. Start the world and check the server log for `[SkyyParty] 0.1.3 ready`, `[SkyyGuilds] 0.1 ready` and no errors.
1. **S alone (smoke test):** run `/skyyhud`. The editor should show "Party (sample)" and "[SKY] Sample Guild" at the left middle. Close it, then check `/party` opens the party page and `/guild` opens the Create guild page. **If anything disconnects here, stop: it's the HUD layout.**
2. **F joins:** F lands in the hub and gets the 10,000 starter coins message and the SkyWynn Menu item. After about 2 s the Create Profile page opens: F picks a class and clicks Create profile. No second class picker should appear. Both type a normal chat line; each sees the other's.
3. **F permissions:** `/balance`, `/skills` and `/party` all work, with no "no permission" message.
4. **S invites from the page:** S opens `/party`, types F's name (the first letters are enough) and presses Enter. S's status line says "Invited F…"; F gets "[Party] S invited you… Type /party accept… runs out in 60 s".
5. **F accepts:** F opens `/party`, sees the green box "S invited you (NN s left)" and clicks Accept. F gets "You joined S's party!" and S gets "[Party] F joined the party! (2/5)".
6. **Party widget:** within about 1 s, both HUDs show at the left middle "Party (2)", "S (L)" with HP/ST, and F with HP/ST. F takes fall damage and S's HUD shows the new HP within about 1 s. In the page, after Refresh, both rows show bars, "Online" and "Hub (with you)".
7. **Party chat:** each types `/pc hello`; both see "[Party] Name: hello".
8. **F's island:** F types `/island` → "Creating your island…" and lands there. The chest should hold the starter kit (fixed in SkyyIslands 0.4.5 - if it is empty and the log shows `starter kit failed`, the fix did not work). On S's HUD, F's line turns grey: "HP x/y - Island". S's party page shows "F's island" and F's Zone widget shows "Your Island".
9. **S visits:** S types `/island visit F` and gets "Visiting F's island - look, don't touch". Breaking a block, placing a block, opening the chest and picking up an item are all blocked with a message; doors still open. Now both are on the same island, so neither party line is grey.
10. **Co-op:** F types `/island invite S` and S gets "gave you build rights". S can now break, place and open the chest. Both use `/hub` to go back.
11. **Party leader actions:**
    - S runs `/party promote F`: "(L)" moves to F, and only F sees Promote/Kick.
    - F runs `/party kick S`: S is told, the party drops to one player and disbands, and both party widgets disappear.
    - S runs `/party invite F` and F runs `/party decline`: S gets "declined".
    - S invites again and F runs `/party accept`.
12. **Guild create:** S opens `/guild`, types "Sky Wynners" and clicks Create guild. The page shows Level 1, Leader. The widget under the party widget shows "Sky Wynners / Lv 1 (0 / 100 XP) / Online 1/1 | Leader". Then S runs `/guild tag SKY` and the widget changes to "[SKY] Sky Wynners".
13. **Guild invite:** S types F's exact name in the Invite box and clicks Invite. F gets "…Type /guild accept (or open /guild) within 5 minutes". F opens `/guild` and clicks Accept. Within about 5 s both widgets show "Online 2/2", F's shows "Member", and a names line shows "S, F".
14. **Guild chat:** each types `/gc hi`; both see a coloured "[Guild] …" line.
15. **Guild bank:**
    - F types 500 in Amount; pressing Enter only shows a hint.
    - F clicks Deposit: F's `/balance` drops 500, the bank shows 500 and a log line appears. F has no Withdraw button.
    - S withdraws 200: S's purse goes up 200.
16. **Ranks:** S promotes F on F's row. F's widget shows "Officer" and F now sees the Invite box and a Withdraw button. S then clicks Demote to put F back to Member.
17. **Guild XP:**
    - S runs `/guildadmin xp 500 Sky Wynners`: chat says "reached guild level 3!" and the widget shows "Lv 3 (150 / 400 XP)".
    - F mines for about 30 s: guild XP goes up about 10 to 20 s later. It's 10% of skill XP, and the first 10 s check only records a starting point.
18. **PvP:** hitting each other in the hub and on an island does no damage.
19. **F disconnects and rejoins:**
    - After F quits, S gets "[Party] F disconnected. The party has been disbanded." and the party widget goes. Within about 10 s S gets "[Guild] F went offline." and the widget shows "Online 1/2".
    - When F rejoins, there's no Create Profile page and F gets a guild welcome line. The guild widget comes back; the party needs a new invite. F's island is still there.
20. **Cleanup (optional):** S runs `/guild disband` twice within 10 s. The bank is paid into S's purse and the guild widget disappears for both.

**Watch the server log for:** `party stats tick failed`, `guild page click failed`, `guild XP check failed` and `/party page failed`. The `starter kit failed` warning is expected.

**If a widget disconnects someone:**
- **Party widget:** just rejoin (a disconnect removes you from the party), run `/skyyhud`, hide Party, and continue.
- **Guild widget, F kicked:** S runs `/guild kick F`, which works while F is offline. F rejoins and hides Guild in `/skyyhud`.
- **Guild widget, S kicked:** with the world closed, in `Saves/HUD mod/mods/Skyy_SkyyHud/layouts/<S uuid>.properties`, set the line to `Guild=0,tl,8,444,100,1`.


## BETA ROUND 1 - 20-mod set, DEPLOYED 2026-09-24 22:53 (auto-deploy; backup backups/deploy-20260924-2253)
New: SkyySkills 0.4.2, SkyyCollections 0.2.1, SkyyTrees 0.2.1, SkyySacks 0.7.5, SkyyBank 0.1.3, SkyyVault 0.1 (NEW), SkyyGuilds 0.1.1,
SkyyBazaar 0.1.2, SkyyRolls 0.1.4, SkyyIslands 0.5, SkyyMenu 0.1.3, SkyyHud 0.3.9, SkyyEssentials 0.1.1. Riskiest first; [2P] = needs Skyy
and a friend (the friend must NOT be opped, or permission checks don't count).
1. **Server log:** a ready line for all 20 mods, including `[SkyyVault] 0.1`, `[SkyySkills] 0.4.2` and `[SkyyCollections] 0.2.1 ... felled=true`. Also look for the Islands 0.5 migration count (with `.v4bak` copies next to the island files), the Guilds 0.1.1 "Officers are called Admin" line, and no errors.
2. **Existing islands after migration [2P]:** your `/island` still has all its blocks. Your friend's beta island is intact. Your old build rights on their island now show as Trusted in `/island menu`, not Member.
3. **Vault:**
   - `/vault`: first find out whether the vault slots appear next to the page.
   - Store items, close and reopen, relog, switch profile: the same items should be there on every profile.
   - Try **Open as chest**.
   - Buy page 3 for 50,000 coins (give yourself coins with `/coinsgive`).
   - Dupe tests: put an item in, then disconnect at once; and switch profile with the vault open. The item must exist exactly once.
4. **Reforge:**
   - Hold a rolled weapon and type `/reforge`: it goes on the anvil. Click Reforge: coins are taken and the stats change.
   - The tooltip reads like `Damage: 11-48 (+24%)`.
   - A stack bigger than 1 is refused. A double click only charges once.
5. **Bank:** `/bank` opens the page. Try Deposit all, Withdraw all, and a typed amount with Deposit or Withdraw. Pressing Enter moves nothing. The numbers match `/balance` and `/bank status`.
6. **Guild [2P]:**
   - Promote your friend to Admin. They can invite and kick Members, but cannot promote or disband.
   - Set `/guild bank limit member 100`. As a Member, your friend can withdraw 100; 101 is refused.
   - Click Expand log: it pages the log on the same page.
7. **Bazaar:** type 10 in the custom amount box and press Enter: the price shows. Click Buy or Sell. Try `max`. Check the page is bigger. Trades are refused while a profile is still loading.
8. **Felled trees:**
   - Cut a tree's base so it falls: Foraging XP and the Collections count go up for every log, not just the one you cut.
   - Placed logs pay nothing.
   - Tree Feller breaks logs only on the level you cut and shows "+N logs on this level". The deployed jar still uses a 5 s cooldown. LOCKED 2026-09-25: 3 s, and extra logs 1 / 2 / 4 / 5 / 6 / 10 at levels 1-6 (see OPEN-QUESTIONS).
9. **Party XP [2P]:**
   - Party up in the same world within 48 blocks, both with a class. You kill a mob with your class weapon: your friend sees "[Party] +N ... XP from Skyy's kill" before any SKILL LEVEL UP it causes.
   - Farther than 48 blocks, or in creative: they get nothing.
10. **Island co-op [2P]:**
    - Invite and accept: your friend's `/island` now goes to your island and they can build.
    - Check the 5 tabs of `/island menu`, the permission grid, trust and untrust, kick, and ban and expel with the Closed visit mode.
    - Your friend's HUD party line shows you as "Your Island".
    - Run `/island reset` only on a throwaway island (it needs 3 runs).
11. **Double jump:**
    - The deployed node is still Acrobatics tier II and still listens for crouch until the next Trees and Skills build. LOCKED 2026-09-25: tier III, jump again in mid-air, 2 Stamina (see OPEN-QUESTIONS).
    - Settle the trigger first: set `acro.doubleJump.debug=true` in the SkyySkills `xp.properties`, run `/skills reload`, and press the configured key in mid-air. An admin chat line should appear.
    - Then buy Double Jump in `/tree acrobatics` (Acrobatics 10 on the deployed tree; the lock moves it to tier III / Acrobatics 20).
    - One jump per airtime, costs 2 Stamina, no jump in creative, and it recharges on landing.
12. **Menu:**
    - Island Menu, Bank, Vault, Reforge, Party and Guild each open their page in place of the menu. Players -> pick a player -> 'Invite to Your Island' (co-op) and 'Let Them Build' (trust only).
    - The Hover Tooltips switch works.
    - Esc while hovering an item: the tooltip may still stick (that fix is only an experiment); with tooltips switched off it can't happen.
13. **HUD [2P]:** make a party: the Party widget lines up on the very first draw, without touching the editor. Use Snap to C, then add or remove a member: it stays centred. The Guild widget shows the Admin rank.
14. **Sacks:**
    - `/pd` with no bag opens and shows all 5 tabs; a bag you don't carry shows its recipe.
    - Craft a Small Smithing Bag (3 Bolt of Wool + 4 Light Leather at a Workbench). Bars, leather and hides go into it, and old hides from the Combat bag appear in the Smithing tab.
    - Tree sap goes into the Foraging bag.
15. **Essentials [2P]:**
    - Your friend sends `/msg`; you answer with `/r`. `/r` alone as a non-op shows usage; `/redo` still works for an op.
    - `/tpa` into an island: no warning in the server log, and `/instances exit` sends you back.
16. **Collections:** a new, untouched collection shows "No tier yet".

**Numbers that are proposals (change in the config files, or tell Claude):**
- LOCKED 2026-09-25: Vault: 2 free pages, max 10, page 3 = 50,000 and each next page +25,000; pages shared across all profiles (Wynncraft style). In-chest Prev/Next arrows are the approved page switch.
- LOCKED 2026-09-25: Tree Feller: 1 / 2 / 4 / 5 / 6 / 10 extra logs at levels 1-6 (level 6 jumps to 10 so a very large tree is not broken as a whole layer), 3 s cooldown. Double Jump: tier III, second jump in mid-air, 2 Stamina.
- Party XP share: 50% of the killer's combat XP to members within 48 blocks in the same world.
- Menu hover tooltips stay ON by default; the "Hover Tooltips" switch (book icon) turns them off if the stuck tooltip after Esc still happens.


## SkyyAuctions 0.1 - BIN auction house, DEPLOYED 2026-09-25 00:19 (backup backups/deploy-20260925-0019)
Riskiest first. The SkyWynn Menu button comes with SkyyMenu 0.2; until then use `/ah`. Open questions (fees, durations, bazaar items off the AH,
no buying from your own other profile, `/ah` anywhere vs an NPC later, the late-game block list): research/Auction-House-Spec.md section 12.

**Before you start:** in `<world>/mods/Skyy_SkyyAuctions/config.properties` set:
- `sameAccountBuy=true`
- `allowTestDurations=true`
- `durations=2m:0,1h:20,6h:45,12h:100,24h:350,48h:1200`

Then run `/ahadmin reload`. You need 2 profiles with about 50k coins each, a `/rolls give` weapon, a graded dish and admin rights. Put all these settings back after the solo steps.

**Solo**
1. `/ah`: click all 7 categories, every sort, the rarity filter, and Browse/Create/Manage. Press Close, then reopen and press Esc. Nothing should stay on screen.
2. Note the weapon's `/rolls read`. In Create BIN, pick it, type `12k` and press Enter.
   - The fee reads 470 (120 + 350). Create BIN: the purse drops by exactly 470 and the item is gone.
   - Browse → Weapons shows the rarity colour, the reforge and "(yours)". The item view shows the roll lines.
   - Cancel through Yes, cancel: the item comes back with an identical `/rolls read`.
   - Repeat with the graded dish; the grade must survive.
3. List the weapon for 12k on profile 1. Switch to profile 2 and wait 20 s. Buy → Confirm.
   - Profile 2's purse drops by exactly 12,000 and the weapon has the exact same stats.
   - Back on profile 1, Claim coins pays exactly 12,000. Double-click it: the second click says there is nothing to claim.
4. Full inventory:
   - Buy with a full inventory: you are charged and the item waits in Manage. Free a slot and claim it; stats are intact.
   - Cancel with a full inventory, then claim.
   - Partial: list 64 of a stackable item that is not sold on the Bazaar. Leave room for about 10 and cancel: it says "10 came back, 54 wait". Claim the rest. You get exactly 64 back, no more.
5. Note the player file's modified time, list an item, and check it changes within 1-2 s. Then list another item and end the server process within 2 s. After the restart the item must be listed OR in the inventory, never both.
6. Failed write, then a crash:
   - Cancel a listing with a full inventory so the item waits as a claim.
   - Make a folder `listings/<id>.json.tmp`. This blocks the listing's file write.
   - Free a slot and Claim item. The item arrives and the server log warns "WRITE FAILED".
   - `/ahadmin info <id>` shows "NOT SAVED YET".
   - End the server process, delete the folder, and start the server.
   - The log shows "restored listing #<id> … closed", `auctions.log` has `WRITE-RESTORED`, and Manage does not offer the item again.
7. Same as step 6 up to "NOT SAVED YET", but only delete the folder (no crash). Within 10 s `WRITE-RETRY-OK` is logged, the file moves to `archive/<month>/`, and `info` shows "(archived)".
8. Clean restart: the listing survives with its stats. `auctions.log` has `BOOT`, and `STOP` after the clean stop.
9. List with 2m, let it expire, and claim it back.
10. List with 2m and log out for 3 minutes. Log back in: the notice appears once, and switching worlds does not repeat it.
11. Profiles:
    - Rename profile 1 in SkyyProfiles, then list something on profile 1.
    - On profile 2, Manage shows the other-profile line with the new name.
    - Set `sameAccountBuy=false` and reload: profile 2 sees "you cannot buy from yourself".
12. In Creative, listing and buying are refused, but claiming works.
13. Add the item id to `Skyy_Market/blocked.txt` and reload. The listing shows "off the market" and cannot be bought, but the seller can still cancel it. Listing Copper Ore is refused (Bazaar item).
14. `/ah sell 5k` opens the page ready for one click; `/ah sell 5k 6h` sets 6h; `/ah sell 5k 7h` gives "Pick one of...".
15. Admin tools:
    - Try `/ahadmin list`, `info`, and `remove <id> testing`.
    - `pause`: listing and buying are refused, cancel and claims still work. Then `resume`.
    - `regrant`: the preview changes nothing, `confirm` within 60 s makes the claim show at once, and a second `confirm` is refused.
    - `/ahadmin` status lists the restore from step 6.
16. Smaller checks:
    - Claim all with more than 100k owed asks first.
    - The "cheaper one is listed" line appears on the pricier of two listings of the same item.
    - `detailTextSpans=false` shows the plain "Reforge X - Damage +N% …" line.
    - `allowTestDurations=false` plus a reload removes 2m.
    - Then put the config back.

**Two players** (A sells, B buys)
17. Cancel-vs-buy race: A lists for 12k. After the grace period, B gets the Confirm button ready while A gets "Yes, cancel" ready in Manage. Both click on a count of 3. Exactly one wins: either B paid 12,000 and has the item, or A has it back and B's purse is unchanged. Do this 3 times, within the 10 s confirm window each time.
18. B has the item view open while A cancels. B's Buy says "no longer for sale" and B's purse is unchanged.
19. A lists a rolled weapon. Within 20 s B sees "Buy (opens in N s)"; the label doesn't count down, so click to refresh it. After that, B buys through Confirm (double-click it): exactly one charge of 12,000, and B's `/rolls read` matches A's. A gets the sale message at once, and Claim coins pays exactly 12,000.
20. B buys with a full inventory: B is charged, the item waits in Manage, and it can be claimed later with stats intact.
21. A lists and logs off, B buys, A logs back in: the notice appears once and `/ah claim` pays.
22. A on the island, B on the hub: buying still works.
23. B without enough coins sees "You need N more coins".
24. A 2,000,000 sale pays 1,980,000.
25. A 15th listing is refused, and claiming one frees a slot.
26. Optional, with a third player: two buyers confirm at the same moment. Only one gets it and only that purse changes.


## Round 2 - SkyyEssentials 0.1.2 (/trade) + SkyyExploration 0.2, DEPLOYED 2026-09-25 00:54 (backup backups/deploy-20260925-0054)

**Solo**
1. Start the server with both jars. Confirm the log shows "[SkyyEssentials] 0.1.2 ready … /trade /tradeadmin (0 unsettled trade record(s); …)" and the SkyyExploration 0.2 ready line with no WARN. Confirm Essentials' `config.properties` now has all 14 keys with the old `replyShortcut` value, and Exploration's config gained the 0.2 block exactly once.
2. `/exploreadmin`: the page opens at 1120x900 with the Spots, Checklist and Island tabs. Type a name in the text box and add a spot where you stand; this also tests the unverified "three text boxes on one button". Then set radius and XP, and remove it (needs a second click within 10 s).
3. Walk into the spot: banner, sound, chat line and Exploration XP in `/skills`. Walking out and back in gives nothing. With `/fly` on, or in creative, nothing is recorded.
4. Add a secret spot: `/explore` Checklist shows "??? Secret spot" until you find it, then the real name and the Secret Keeper title.
5. Checklist: add chest, chests N, zone and custom entries; tick the custom one with `/exploreadmin check tick`. At 100%, the XP (and coins with SkyyCoins) is paid once, and `/explore` shows the %.
6. Edit `worlds/<world>.properties` by hand while the server runs. Try an in-game change: it is refused ("run /exploreadmin reload first"). After reload, the hand edit shows. Also check an unsaved change shows as "NOT saved" in `/exploreadmin stats`.
7. Switch profile, then open a new loot chest within 30 s: "Loot chests count again in N s". After 30 s it counts. The new profile can find the same spots again.
8. `/tradeadmin config` (1060x900): toggle an ON/OFF setting; set distance 5000 (refused) and 12 (saved, file updated); press Reload file. Hand-edit the file, then run `/tradeadmin reload`. Also `/tradeadmin log`, `/exploreadmin set` / `get`.
9. `/r <text>` replies; `/r` alone still runs `/redo` for a builder; `/trade` alone shows usage; `/trade claim` with nothing owed says so.

**2 players**
10. A runs `/trade B`, B runs `/trade accept`. Check the slots appear next to the page (unverified; otherwise use Open as chest). Drag items in: they leave the inventory, and the other player sees them read-only with tooltips. Both click Ready, count down 3-2-1: the items swap, with exact counts before and after.
11. Cancel paths: Cancel button during the countdown; Esc; walking more than 9 blocks away; taking damage; `/island` (world change); one player quitting. Every time, each player gets their own items back and nothing is duplicated.
12. Change an offer during the countdown: the countdown stops and both Ready marks clear. Also Not ready.
13. Receiver has a full inventory: "did not fit - /trade claim". Free space, then `/trade claim` delivers; rejoining also delivers. Test `/tradeadmin return <player>`.
14. Coins on both sides: balances are correct afterwards. One player spends coins during the countdown (`/pay`): the trade cancels and all coins come back.
15. B switches profile while the trade is open: the trade cancels, and B's items say "switch back then /trade claim". They are never delivered on the new profile; after switching back and 30 s, they are delivered.
16. Stop the server normally mid-trade: on next join, "Returned from a trade that was open when the server stopped", items complete.
17. Chest mode (`tradeOpenMode=chest` on the config page): accepting opens the vanilla chest. Closing it brings the page back without slots, and Edit my offer reopens the chest.
18. A keeps dragging items: B's page updates at most once a second, and B's Cancel click still works.
19. Open `/vault` (e.g. from SkyyMenu) while the trade page is open: the trade page closes ("trade stays open"), the vault works, and `/trade` reopens the trade. No items lost.
20. Exploration with 2 players: both get their own first discovery of a spot, the checklist % is per profile, and titles show in chat.


## Round 3 - in-game setup: SkyyMenu 0.3, SkyyRanks 0.1, SkyyIslands 0.5.1 (security), DEPLOYED 2026-09-25 02:33 (backup backups/deploy-20260925-0233)
[2P] = needs a second player who is NOT an op. Server Setup open questions: research/Server-Setup-Spec.md section 9.

1. [2P] SkyyIslands 0.5.1 hole closed: player B (not op) runs `/island reload` and `/sethub` (both refused) and tries to break a block on Skyy's island (refused).
2. Server log at start: "[SkyyMenu] 0.3 ready", "config kit folder: .../mods/Skyy_SkyyMenu", "[SkyyRanks] 0.1 ready", and no "Failed to register command". At the first join, the three command checks all say they belong to SkyyMenu.
3. [2P] `/rank create vip VIP`, `/rank prefix vip [VIP]`, `/rank grant vip skyyessentials.fly`, `/rank set B vip`:
   - The reply lists B's groups as `hytale:Adventurer` + `skyy:vip`.
   - B can still use `/bazaar`, `/skills`, `/island`, `/settings` and `/ah`; `/fly` works.
   - B's chat reads `[VIP] [title] B: hi`, and the op is unaffected.
4. [2P] `/rank clear B` leaves only Adventurer and `/fly` is refused. Assign the rank again, then `/rank delete vip`: B is back to Member and all normal commands still work.
5. [2P] Open `/rankadmin` on B, search "pay", Deny that permission: B's `/pay` is refused. Remove the deny: `/pay` works again.
6. [2P] B sees no book at slot 41, and `/modconfig` and `/rankadmin` are refused. Grant B `skyymenu.modconfig`: B sees Server Setup, but the Menu page says view only. Take the grant away while B's page is open: B's next click shows "You no longer have access to Server Setup." and only Close works.
7. `/modconfig`:
   - Menu and Ranks come first; Ranks says "3 settings - Editors: Ranks editor".
   - The 20 file-only rows show live versions.
   - Reload works on SkyyEssentials and SkyyProfiles.
   - Open on SkyyBank shows its file and `/bankconfig`.
   - Searching "prefix" finds Ranks and marks the row with ">".
8. Ranks page:
   - Setting Default rank to a rank that has grants is refused with the reason.
   - Chat prefix OFF takes effect in chat at once.
   - With Advanced ON, chat prefix order 30000 asks first, then shows amber "applies after a restart", and the list says it is waiting for a restart. Set it back to 31000.
9. [2P] Menu page: "Mods list for players" OFF hides the Mods tile from B only. Only that line of `config.properties` changes. The change shows in Changes, and Undo works.
10. [2P] In the settings defaults table, set `explore.chunkXp` off: B (who never chose) stops getting chunk-XP messages. B switches it ON in `/settings` and B's choice wins. Then set the entry back to unset.
11. `/settings`:
    - The Skills tab shows the two Exploration rows; General shows hover tooltips.
    - A changed switch survives a relog.
    - `/explore quiet` flips the same row.
    - Reset all needs two clicks, and the page fits 1080 high.
12. If tooltips were off in 0.1.3, they are still off after the update, and the book and the Settings row agree.
13. [2P] Slot 24 opens `/ah` for both players, slot 25 is Reforge, slot 51 is Settings, and the slot 41 book shows only for the op.
14. Ranks: Export puts a code in the box and a file in `exports/`. Importing that code previews "nothing to change". In History, Restore `config.properties`, then undo that restore.
15. Hand-edit `Skyy_SkyyRanks/config.properties` while the server runs, then click Reload file: Changes shows the edit as `via=file`.
16. [2P] `/rankadmin` page: New rank, Up/Down, grant search, adding a member from the online list, "< Server Setup", and the page fits 1080 high.
17. [2P] Two admins on the Ranks page: after one changes a value, the other sees it on their next click, and both changes are logged with names.


## Round 4 - every mod's settings in game (16 mods), DEPLOYED 2026-09-25 04:11 (backup backups/deploy-20260925-0411)
Skills 0.4.3, Trees 0.2.2, Collections 0.2.2, Sacks 0.7.6, Classes 0.1.5, Cooking 0.1.2, Profiles 0.1.1, Islands 0.5.2, Party 0.1.4,
Essentials 0.1.3, Exploration 0.2.1, Guilds 0.1.2, Vault 0.1.1, Rolls 0.1.5, Hud 0.3.10, Accessories 0.4.4. [2P] = needs a second, NON-op player.

1. Start the world. All 22 mods load, every "[Skyy…] ready" line appears, and the log has no "config kit", "unreadable" or "clamped" warnings. Check the files:
   - `Skyy_SkyyProfiles/config.properties` now says `maxProfiles=6`.
   - `Skyy_SkyyEssentials/config.properties` has the "added by SkyyEssentials 0.1.3" block at the end.
   - `Skyy_SkyyAccessories/config.properties` and `Skyy_SkyyHud/config.properties` now exist.
2. [2P] Player B has no Server Setup tile and `/modconfig` is refused. Each of these is refused for B:
   - `/partyadmin`, `/classadmin`, `/cookadmin`, `/profileadmin`, `/guildadmin`, `/vaultadmin`
   - `/exploreadmin`, `/tradeadmin`, `/warpadmin`, `/sethub`, `/rolls`
   - `/skyyhud default`, `/island reload`, `/skills reload`, `/tree reload`, `/collections reload`, `/accessories reload`
3. [2P] B can still run every normal command: `/island`, `/hub`, `/party`, `/pc`, `/guild`, `/gc`, `/skills`, `/tree`, `/collections`, `/skyyhud`, `/settings`, `/vault`, `/trade`, `/tpa`, `/msg`, `/profiles`, `/class`, `/cooking`, `/explore`, `/reforge`, `/accessories`, `/pd`, `/craft`.
4. Server Setup shows 18 mods as set up and 4 as file-only (Auctions, Bank, Bazaar, Coins). Open all 16 new pages: none fails to load and every page fits the screen. Searching "invite" finds Party, Guilds and Islands.
5. Dangerous changes:
   - Set Vault `maxPages` below a page that holds items: refused.
   - Set Vault `freePages` above `maxPages`: refused.
   - Lower Accessories slots to 7: it asks first, and an 8th equip is then refused.
   - Undo each change from Changes; the file changes only on that line.
6. [2P] Durations use the right unit: Party `inviteSeconds` 20 (the invite expires at about 20 s), Essentials `tpa.expireSeconds` 20, Profiles `combatSeconds` 5 (a profile switch works 5 s after a hit, not before).
7. Turn a part off and on again (Cooking "Graded cooking", then an Exploration part, then Essentials `part.tpa`). Turning it off asks first and the feature stops; turning it back on works as before.
8. Islands: "Use my hotbar" for the starter kit, then a new profile's new island chest has exactly that kit. Lowering `reset.cooldownHours` asks first; raising it does not.
9. Skills: set `levels.max` to 60 (asks first), then change another Skills row straight away. After about 1 s, `/skills` caps at 60. Put it back to 100.
10. Commands go through the kit: `/partyadmin set maxSize 6`, `/guildadmin set maxMembers 60`, `/profileadmin set openDelayMillis 3000` and `/exploreadmin set …` each show in Changes as "command" with your name.
11. Hand-edit `Skyy_SkyyGuilds/config.properties` (`maxMembers`), then press "Reload file" on the Guilds page. The value is live and logged as "file", and `/guildadmin config` shows it.
12. Export a Trees code, change a Trees value, then import the code (Preview, then Apply). The value comes back. Restore an older History version, then undo that restore.
13. [2P] In `/settings`, B turns off `party.chat`, `guild.chat` and `tpa.updates`. B stops seeing A's `/pc` and `/gc` lines and denied/expired tpa notices, but still sees B's own lines. With `skills.xpGain` off, XP still counts.
14. [2P] `islands.visitPing` off for A: B visits A's island and A gets no ping. With `classes.blockedChat` off, a blocked weapon hit is still blocked, with no chat line.
15. The restart-only row `replyShortcut` shows RESTART, and the Mods list says it waits for a restart. After a restart the tag is gone.
16. HUD: "Use my layout" makes a fresh player, or `/skyyhud reset`, get your layout. The "HUD editor" link opens the editor, and Back returns to Server Setup.
17. Rolls: edit the cost table ("Rare"), and `/reforge` shows the new cost. Sacks: lower `bag.small`; it asks first and the cap applies.
18. Profiles: with `maxProfiles` now 6, a 5th profile can be created. Lowering the value never deletes a profile.


## HOTFIX SkyyAuctions 0.1.1 + SkyyEssentials 0.1.4, DEPLOYED 2026-09-25 05:42
1. `/ah`: list a ROLLED weapon (`/rolls give mithril bow`), then Browse -> View it: no disconnect; the icon shows and the rolls are listed as text.
2. [2P] `/trade`: offer a rolled weapon; the other player sees its icon without a disconnect, and hovering the slot shows its name + rolls.


## Round 5 - SkyyMenu 0.3.1 (+ config kit 1.1), DEPLOYED 2026-09-25 05:53
1. Server log: `[SkyyMenu] 0.3.1 ready (config kit 1.1 ...)`, no config-kit warnings.
2. Mods tile as op: all 22 mods, Essentials 0.1.4, Auctions 0.1.1; 'Admin only:' lines (Essentials /warpadmin, Party /partyadmin); one click on a set-up mod opens its Server Setup page.
3. `/settings`: General shows the 3 guild switches; turning off Guild chat hides the friend's /gc lines.
4. [2P] Non-op friend: no admin lines, no Server Setup book, `/modconfig` refused, `/settings` works.


## SkyyTrees 0.2.3 - faster tool swings, DEPLOYED 2026-09-25 06:53 (backup backups/deploy-20260925-0653)
1. Server log: "swing speed ready: 80 effects, pickaxe root = SkyyTrees, hatchet root = SkyyTrees", no errors naming Skyy_Tree_Swing.
2. Adventure mode (creative breaks instantly). Buy Mining Speed 25 (Server Setup -> Trees -> Advanced 'Test: extra Dust / tokens' if needed,
   set back to 0 after). Take an Adamantite / Mithril / Onyxium pickaxe (one-hits stone).
3. Hold left-click on stone and flip Server Setup -> Trees -> 'Faster tool swings' OFF / ON (applies within 1 s): OFF ~2.9 swings/s,
   ON ~3.6 swings/s. Clearest: temporarily set Mining MSpeed.per 0.016 (+40%) -> swings back to back; set it back to 0.01.
4. Count: hold 10 s on stone -> ~28 blocks vanilla, ~35 at +25%, ~40 at +40%.
5. `/tree swing` -> "tier 25 (+25% - a swing every 0.28 s)"; `/tree mining` -> "Now: +25% pickaxe swing speed".
6. Chopping Speed + a Cobalt+ hatchet swings faster on logs; a sword swings at normal speed; a profile without the node is vanilla speed;
   no status icon shows; no blocks pop back / rubber-banding; the one-time chat notice shows once.


## Round 6 - Berserker, Priest, class kits (SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2), DEPLOYED 2026-09-25 07:11 (backup backups/deploy-20260925-0711)
[2P] = needs a NON-op second player.
1. Server log: all ready lines; SkyyClasses "class kits: N existing profiles marked"; SkyySkills "appended the Divinity section"; no config warnings. Existing profiles (Strawberry, Zucchini) get NO kit.
2. Existing profile: `/skills` shows the same levels as before (relog, check again).
3. `/profiles` -> Create new: 7 cards fit, Priest reads "AoE healer / support". Create a Priest: "kit on its way", then within ~35 s after arriving a "Class kit" popup + chat line and the Wood Wand in storage. Relog/restart: no second kit.
4. Solo Priest: take fall damage, tap-hit a monster with the wand -> you heal ("[Classes] Heals: +N HP to you", max every 5 s, no XP for self-heal). A kill gives Divinity XP; `/skills` shows Divinity.
5. [2P] Friend (non-op Warrior) in your party, hurt: wand-hit a monster within 16 blocks -> the friend heals ("Skyy healed you +N HP"), their HUD party bar rises, you get Divinity XP (~0.2 per HP). Friend at full health / 20+ blocks away / other world / not in party -> no heal.
6. [2P] Friend: `/class kit` -> "Nothing is waiting"; `/classadmin kit`, `/classadmin info`, `/modconfig classes` refused or view-only; `/settings` -> Combat "healed by others" off hides the lines (heals still happen).
7. Creative hits heal nothing; hits on players heal nothing.
8. Berserker profile: battleaxe kit; axes/battleaxes/maces/clubs deal damage; a hatchet chops and hits; a wand is blocked ("Only Priests can use wands" + popup). `/skills stats fury`; a kill gives Fury XP.
9. [2P] Party kill share: a Warrior kill gives you Divinity, your Priest kill gives the friend Swordsmanship.
10. Server Setup -> Classes: 4 tabs; add a spellbook to the Priest kit; 'Use my hotbar' on the Archer kit with a sword asks first; heal share 50%; Priest heal OFF (asks) -> no heals; back ON. Skills has 3 Divinity rows.
11. Full inventory + `/classadmin kit <you> archer` -> "did not fit ... /class kit"; make room, `/class kit` delivers; survives a relog.
12. `/class` shows 7 cards; footer "Hatchets are tools."


## SkyyVault 0.1.2 - page arrows inside the chest, DEPLOYED 2026-09-25 07:47 (backup backups/deploy-20260925-0747)
1. `/vault` (chest mode): 5 rows with your inventory still visible; read every tooltip in the bottom row. If it doesn't fit: Server Setup -> Vault -> arrow layout "Inside the page".
2. Click Next, then Prev. On an arrow try: plain click, drag to your inventory, shift-click, drop key, take half. Each time the page turns once, the arrow is back, and ~1 s later no arrow is in your inventory.
3. Try to steal an arrow: drag it to hotbar / armour / a vault slot; Take All, Sort, Put All, Quick Stack; drop an item onto an arrow and a filler; spam Next 10x; Esc mid-drag. Then check mods/Skyy_SkyyVault/vault.log + server log for STRAY / RESCUE / "Failed to run task".
4. Last page: click the gold arrow (chat asks), click again within 10 s -> coins taken once, new page opens. Wait 11 s between clicks -> it only asks again. Too few coins -> refused. At max pages -> grey "Last page".
5. Switch profiles with the vault open: it closes; for 30 s the arrows show the wait message.
6. Arrows off (Server Setup): 4 rows, shift-click and Take All still work. Creative library: searching "page"/"vault" lists no arrow items.
7. [2P] Two players flip their own vaults at the same time with no cross-effects.


## Round 7 - SkyySkills 0.4.5 (crossbows stay loaded), SkyyMenu 0.3.2, SkyyGuilds 0.1.3, DEPLOYED 2026-09-25 08:24 (backup backups/deploy-20260925-0824)
1. Server log: SkyySkills line includes "crossbows stay loaded at Archery 5 (on)"; Guilds logs "xpSkills was still the old default - added Fury and Divinity".
2. Archer, Archery 5+: load a crossbow, scroll away (vanilla gives the bolts back as Crude Arrows), scroll back -> ~0.1 s later the same bolt count returns and the same number of arrows is taken. Try with fewer arrows than bolts, with no arrows, and with a More Crossbow Tiers crossbow.
3. Scroll back to a DIFFERENT crossbow, or move the crossbow first -> nothing restored, nothing taken. Fast scrolling -> no free bolts. Profile switch / relog / world change / death -> never restored. Archery 4, Warrior, Berserker -> vanilla behaviour.
4. Archery 4 -> 5: chat "Unlocked: Crossbows stay loaded when you switch slots"; the Stats page lists it. Server Setup -> Skills: 5 new rows; OFF asks to confirm.
5. Guilds: Server Setup -> Guilds -> Skills that count ends with Fury, Divinity; a Berserker earning Fury XP raises guild XP.
6. Mods list shows Skills 0.4.5, Menu 0.3.2, Guilds 0.1.3; the SkyyClasses entry names 7 classes. [2P] non-op: no /classadmin kit line, /modconfig refused.
