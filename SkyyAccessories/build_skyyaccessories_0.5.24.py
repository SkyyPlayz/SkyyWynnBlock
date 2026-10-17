"""SkyyAccessories 0.5.24 - build script (derived from the generated build_skyyaccessories_0.5.23.py by tools/accessories_0_5_24_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.24.py            -> SkyyAccessories/SkyyAccessories-0.5.24.jar   (deploys go through tools/deploy_set.py --yes)
Test:  python test_skyyaccessories_0.5.24.py             (harness_kit: -Xverify:all, class compare 0.5.23 -> 0.5.24, the Void Charms texts)

0.5.24 (2026-10-17) = TEXT ONLY: the feature is called Void Charms everywhere a player or admin reads it. Skyy 2026-10-17: "i noticed they
are still called accessory's in the settings" (the Accessory Bag was renamed Void Charms in 0.5.22: /charms /charm /ch).
  1. SERVER SETUP: the section title (the kit's TITLE, published on config:def - SkyyMenu shows it as given) Accessories -> Void Charms;
     rows "Accessory slots" -> "Charm slots", "Craft from the bag" -> "Craft in Void Charms", "Accessory equipped / upgraded sound (id)"
     -> "Charm equipped / upgraded sound (id)"; help texts that said "the bag" / "bag page" / "bag slot" now say Void Charms.
  2. CHAT / PAGE LINES: craft and upgrade results ("it went straight into your Void Charms", "upgraded to X in your Void Charms - ...",
     "Void Charms already has ...", "kept in a free Void Charms slot", "... or Void Charms"), "crafting in Void Charms is switched off",
     "put it on from the Void Charms page", the profile-switch line, the empty Bonuses line, the retired Night Vision line, the
     /charms reload summary ("charm slots", "the Void Charms Craft tab").
  3. FILE HEADERS + the craft.bag / craft.autoEquip comments of NEW config / power / sounds files and the ready log line: "Server Setup -> Void Charms" (existing files keep their
     bytes - no migration).
  Unchanged on purpose: ids, config keys, file names, bridge keys, permission nodes, saved data; "Accessory Power" (Skyy's AP stat,
  popups 2026-10-16); single items stay "accessory"; "Old Accessory Bag" (the retired item's own name); the Workbench tab "Bags"; the
  config comment lines the 0.4.x / 0.5 migrations write or look for (OLD_COMMENTS / ADD_GROUPS).
  ROLLBACK to 0.5.23: safe (same files, same keys).

0.5.23 (the base, still true unless 0.5.24 above says otherwise):
0.5.23 (2026-10-17) = HOTFIX: Void Charms disconnected the client ("Selected element in CustomUI command was not found. Selector:
#SkyyAccGrid.Slots"). Skyy 2026-10-17: "opening the charms worked. it crashed when i tried to clikc to market in the top bar from charms".
  ROOT CAUSE: AccPage.cells (the stuck-tooltip guard's "grids drawn" count) was set by buildBag() but never reset by build(). After the
  BAG view had been drawn once, the CRAFT / POWER views (which have no grids) kept cells = 100, so the next hub-row click (Market, any
  row 1 / row 2 tab), the X or Close ran clearGrid() -> sendUpdate(b.set("#SkyyAccGrid.Slots") + "#SkyyAccInvG.Slots") on a page whose
  markup has no grid -> the client disconnects.
  FIX: 1. build() resets cells = 0 before the view is drawn (only buildBag() sets it again - the pets page's rule, SkyyPets 0.4.3);
       2. isOpen(): the page is still the player's open custom page (PageManager.getCustomPage() == this); clearGrid() sends nothing when it
          is not (a page that was replaced / dismissed never gets a command), and the "tab could not open" rebuild after a hub click
          runs only while the page is still open.
  No saved-data change. ROLLBACK to 0.5.22: safe (same files).

0.5.22 (the base, still true unless 0.5.23 above says otherwise):
0.5.22 (2026-10-16) = VOID CHARMS + ACCESSORY POWER (round AP1; research/Accessory-Power-Spec.md + Skyy's answers).
Skyy 2026-10-16 (docs/answered/gear.md): "id like to ditch the item and just use the menu" -> "void charms"; "/charm /charms and /ch drop
the accessory commands"; "pick a power. unlike hypixle we start with 5 combat. and the 4 gathering."; "and id change this to the same grid
system you used for the pets, so its easy to see all of them at once. (keep the accessory's in your inventory, and the equip/unequip, as
some will be mob drops only and of those, some can be upgraded others cant. (so the ones that can be upgraded only appear in the craft menu
when you have one equipped.)   and we still havnt given them the accessory power, and the boosts from all your accessory power." +
docs/answered/bags.md (popups): "Tank/Balance/Slayer/Lucky/Magical (Recommended)", bench accessories give AP "Yes, by rarity
(Recommended)", switching "Free, 5 s wait (Recommended)", Combat 15 Powers "Now, rename Fortune" (Jackpot) + the standing rules "we dont need
to keep commands around that longer fit." (HANDOFF section 3 rule 3) and the menu pattern (kit 1.7 hub_page, no back buttons).
  1. ACCESSORY POWER (AccPower): every accessory in Void Charms adds AP by its rarity (power.ap: Normal 10 .. Mythic 25); only the best of
     each line counts; a switched-off line, a retired accessory and the old bag item add 0; bench accessories give AP by their rarity
     (power.bench full / half / none); the Omni Accessory gives what the 11 active top-tier bench accessories would give (143 at the
     defaults) and a bench accessory next to it adds 0. Multiplier M = (AP / power.base) ^ power.curve, at most power.guard.
  2. 15 POWERS, ONE PICKED: Combat Tank, Balance (the start), Slayer, Lucky, Magical; Combat 15 (unlocked at Combat level power.unlock =
     15, SkyySkills skill:fn:level "Combat") Fortress, Harmony, Glass Cannon, Blitz, Arcane, Jackpot (the combat 'Fortune', renamed); Gathering
     Mining, Foraging, Farming, Fishing. Every number is a Server Setup row (table pw.<Power>.<stat>, per 100 AP; minus = a debuff). Fast
     waits for Attack Speed (no code yet), Mana Regen on Magical / Arcane too. Picked per profile (Skyy_SkyyAccessories/power/<pkey>.properties
     power= / switched=), free, power.wait = 5 s between switches, never written while profile:busy; no file = power.start (Balance).
  3. THE STATS REACH PLAYERS on the 1 s effect tick: Health into skyyacc_health (signed: a debuff lowers it, max Health never below 1),
     flat Mana into skyyacc_mana (after the Mana line's %), Speed % into the movement source accessories.talismans, Strength / Defense /
     Crit / Magical Power into the ONE gear:extra:<uuid> text (lines + Power, signed); gathering into skill:bonus:<uuid> source "accessories"
     (dd.<skill> = Fortune / 100, bp.<skill> / swing.<skill> = % / 100, fspd.fishing / dd.fishing / treasure.fishing = % / 100) - only the
     stats whose reader is there (Fortune: SkyySkills; bp / swing / fish: skill:bonus:reads:bp / :swing / :fish = TRUE) are published,
     listed or pickable (a Power with no working stat is hidden). The source is replaced whole, removed when empty, on profile:busy and on
     leave / shutdown. acc:power:<uuid> = "Slayer|352"; acc:fn:power get / set (SkyyWardrobe loadouts, no switch wait).
  4. VOID CHARMS = THE PAGE ON THE KIT 1.7 HUB PAGE (Character hub, its own tab hub:tab:character:accessories "Void Charms", rows 1 + 2,
     no back button): sub-tabs BAG | CRAFT | POWER, footer = the result line + Close. BAG: Accessory Power + Power + Change, filters All /
     Combat / Gathering / Benches, ALL 60 bag slots as an icon grid (rarest first, hover = rarity, effects, +AP or why it does not count,
     drop-only notes), the selected accessory with Unequip / Equip, the accessories in the inventory as a grid. CRAFT: 0.5.21's line rows
     in a scroll list, Benches / Combat / Gathering as in-page filters. POWER: every visible Power with its stats at your AP, Pick.
  5. DROP-ONLY LINES (Brawler, Runic, Stonehide, Razorfang, Feather = drop-up): no CRAFT row until one is IN THE BAG, then the next rarity's
     UPGRADE (new Unique / Rare / Legendary upgrade recipes in the bag's own category; never a from-scratch recipe).
  6. THE ACCESSORY BAG ITEM IS RETIRED: no starter bag, no lifelong rules (AccOnce* gone), no /accbag; every copy found in a player's
     inventory (storage, hotbar, backpack, utility, tools) is removed on the 5 s restamp pass - the journal line (Skyy_SkyyAccessories/
     retired.log, fsynced) first, then the removal (counted before / after); once per profile a chat line (marker
     retired/<pkey>.properties retiredBag=...). The accessories were never in the item (they live in bags/<pkey>.properties): nothing is
     lost. The item stays defined (hidden, no recipe) so a stray copy in a chest still loads; right-click opens Void Charms.
  7. COMMANDS (HANDOFF section 3 rule 3: replaced, not added): /charms (aliases /charm, /ch) + lines, power [name], admin reload / give /
     givetier; /accessories, /acc, /accbag are gone.
  8. Texts: "Accessory Bag" -> "Void Charms", "[Accessories]" -> "[Void Charms]", "/accessories" -> "/charms" (code lines only).
  New saved data: power/<pkey>.properties, power.properties, retired.log. ROLLBACK to 0.5.21: safe for the bag (same files); the bag item
  is not given back automatically (/accbag on 0.5.21 recalls one), the new upgrade recipes' items stay valid.

0.5.21 (the base, still true unless 0.5.22 above says otherwise):
0.5.21 (2026-10-16) = ACCESSORY CRAFTING LIVES IN THE ACCESSORY BAG (round accraft).
Skyy 2026-10-16 (docs/answered/gear.md, screenshot: Accessory Bag > CRAFT tab, 'Accessory recipes - 50', every tier listed, Page 1/6): "i love
this! lets keep the accessory crafting here! but change it up. instead of showing all of them in every tier. when you dont have any it shows
the T1 of every bench, and the normal of every accessory. when you craft it, it goes straight to your accessory bag. if you have a normal
lantern in your bag, the craft will show uncommon (the cost to upgrade) and an upgrade button.   (then add sub tabs. like benches. then split
the accessory's up by combat and gathering. (we will add more splits/submenus/filters as need   this way we get 1 spot to find, make and
upgrade all the accessory's in a simple easy to understand and navigate menu.  we can then remove them from the crating and the bench.
because they are crafted in the accessory bag." + the standing rule (Skyy 2026-10-16) "sort everything by tier in all shops and crafting."
  1. ONE ROW PER ACCESSORY LINE (AccCraft.lines / step / rowsFor): every line (each bench, each stat line, the Lantern, the Omni) shows
     only its NEXT step for this bag - none of the line in the bag -> its first recipe (Workbench Accessory I, Normal Lantern ...) with a
     CRAFT button; the bag holds one -> the next tier / rarity with its UPGRADE cost (the one in the bag is not listed as a cost) and an
     UPGRADE button; the top one in the bag (or the Omni Accessory in the bag, for every bench it covers) -> "RARITY - MAX", no button.
     Only the bag counts (an accessory in the inventory does not move a row on).
  2. CRAFT = straight into the bag (0.5.18 path). A craft that takes no accessory as an ingredient is refused BEFORE anything is used when
     the bag has no free slot ("free one first") - the result never lands in the inventory by surprise (auto-equip off = the inventory, as
     before). UPGRADE = IN PLACE: the materials come from the bag FIRST for the one being upgraded (CombinedItemContainer bag, inventory,
     Void - so the bag's copy is used even when another copy is in the inventory), then inventory, then Void; the bag slot is SWAPPED old ->
     new in ONE write of the bag file under the bag lock (AccCraft.swapSlot: the old one is never out of the bag on its own; a full bag
     needs no free slot). Inventory / Void parts are taken first and rolled back exactly when the swap fails. Journal BEGIN / DONE /
     ROLLBACK as every bag craft. A click is crafted only while its recipe is still that line's next step (AccCraft.stepOf): a double click
     after an upgrade, or a row drawn before the bag changed, answers "that row changed" and uses nothing.
  3. SUB TABS inside CRAFT: Benches | Combat | Gathering (one table, C9_SUBS + C9_FAM_SUB - add a row there for a new tab / line): every
     bench accessory + the Omni -> Benches; Health, Stamina, Mana, Regeneration, Speed -> Combat; the Lantern -> Gathering; a stat line the
     table does not name -> Combat. Rows sorted: Workbench Accessory I first (LOCKED 10-13, the tutorial's first craft), then by tier (the accessory's own ladder:
     bench T1..T7, rarity 1..4; the Omni last), inside a tier easiest to craft first (the 0.5.13 cost order = ItemLevel), then name.
     The hint says only this bag counts (an accessory in the inventory must be moved in to be upgraded).
  4. SCROLLING list (skyyui.scroll_list: TopScrolling + the vanilla scrollbar, proven on SkyyClasses / SkyyCollections) instead of the
     0.5.18 pager - Skyy 10-16 asked for scroll instead of pages on the crafting page.
  5. NO ACCESSORY RECIPE ON A BENCH OR IN /craft: the 50 recipes keep their ids, inputs and outputs but their BenchRequirement becomes the
     bag's own [Crafting "SkyyAccessoryBag", category "SkyyAccessoryBag"] - no block in the game is that bench, so no Workbench tab, pocket
     crafting or SkyySacks bench / /craft list (benchRecipes needs an equipped Skyy_Accessory_<bench>_T<n>) shows them; AccCraft.ours()
     reads that category. Owned accessories are untouched. The Workbench tab "Accessories & Bags" itself stays (SkyySacks' bag recipes).
     Tooltip / page texts that said "at a Workbench" now say the Accessory Bag's Craft tab.
  No saved-data format change, no new setting / command / system / bridge key.
  ROLLBACK to 0.5.20: safe (the recipes go back to the Workbench tab; bag files are the same format).

0.5.20 (the base, still true unless 0.5.21 above says otherwise):
0.5.20 (2026-10-16) = THE LIFELONG ACCESSORY BAG (round life01, with SkyySacks 0.8.12, SkyyMenu 0.3.32 and SkyyIslands 0.5.17).
Skyy 2026-10-16 (docs/answered/gear.md, screenshot after /island reset: the starter chest held an Accessory Bag while one was already in
the inventory): "when island reset, it came with a 2nd accessory bag.   (yk how you cant loose the tools, and can bring them back with a
command. lets do the same to the accessory bag, the pocket dimension, and the menu item.)"
  1. THE ACCESSORY BAG IS LIFELONG (tools/skyyonce.py, classes AccOnce*): one per profile - never dropped (Drop key / drag out refused),
     never on the ground (a death drop or a full-inventory overflow is stopped and the bag comes back into the inventory), never stored (a
     bag put into a chest / container / trade offer / the Vault goes straight back into the inventory; a second one there is removed),
     never sold (market:veto -> Auction House + Bazaar), never in a starter kit (once:item:Skyy_Accessory_Bag = TRUE -> SkyyIslands
     0.5.17 leaves it out of the starter chest: the 2nd bag after /island reset; fix round: only while starter.bag is on too). The bag ITEM holds nothing: the accessories live in the
     profile's bag file (Skyy_SkyyAccessories/bags/<pkey>.properties), which nothing here touches - an extra copy goes without loss.
  2. EXTRA COPIES CLEANED: two or more bags in the inventory -> one is kept (a copy with metadata first, else hotbar, storage, backpack,
     utility, tools order), the rest removed. HISTORY FIRST: Skyy_SkyyAccessories/lifelong/history.log gets the line (what, where, how many,
     its UNDO) fsynced before anything is removed. The first pass of each profile = the ONE-TIME CLEANUP (run-once marker
     lifelong/once/<pkey>.done, its own chat line).
  3. RECALL: /accbag (already an alias of /accessories - no new command word) gives a new bag when the inventory holds none (storage,
     hotbar, backpack - never dropped), then opens the bag page as before. /accessories and /acc do the same.
  4. NO RECIPE: the bag item has no crafting recipe any more (every profile gets one free - AccStarter - and /accbag brings it back).
  5. SERVER SETUP -> Accessories -> "Accessory Bag stays with you" (lifelong.bag, default on; a missing key = on, an existing file keeps
     its bytes). Off = the bag can be dropped / stored / sold again and extra copies stay (the recall still works; no recipe either way).
  FIX ROUND (critic life01): once:item answers LIFELONG && STARTER (starter.bag off = the kit gives the bag as before); a WORLD chest's
  copies are touched only when the viewer just put theirs in (their inventory dropped below what the last sweep left) - a copy already
  in someone's chest is never moved or removed; personal windows (Vault, trade offer) as before; pkey cached per profile epoch. A
  refused Drop key on an own-inventory section is re-sent by the engine itself (InventoryPacketHandler marks the InventoryComponent
  dirty when the request was cancelled - VERIFIED bytecode); a container window is marked changed here.
  Item tooltip: one sentence more (it stays with you, /accbag). No saved-data format change.
  ROLLBACK to 0.5.19: safe (the lifelong/ folder is ignored; the bag can be dropped and crafted again).

0.5.19 (the base, still true unless 0.5.20 above says otherwise):
Run:   python build_skyyaccessories_0.5.19.py            -> SkyyAccessories/SkyyAccessories-0.5.19.jar   (deploys go through tools/deploy_set.py --yes)
Test:  python test_skyyaccessories_0.5.19.py             (harness_kit: -Xverify:all, class compare 0.5.18 -> 0.5.19, acc:fn:bag, live start twice)

0.5.19 (2026-10-16) = BENCHES USE THE ACCESSORY BAG (round craft01, with SkyySacks 0.8.11).
Skyy 2026-10-16 (screenshot: Workbench > Accessories & Bags, the Furnace Accessory recipe shows 0 / 1 while the accessory sits in the
Accessory Bag): "accessory's go straight to the accessory bag now. but the bench cant pull from the bag to craft the next tier yet."
(docs/answered/bags.md 2026-10-16 BENCH CAN'T USE ACCESSORIES IN THE BAG).
  ONE NEW BRIDGE FUNCTION acc:fn:bag (AccBagFn, java.lang types only) for SkyySacks' bench link and /craft - this mod still owns the bag:
    apply(Object[]{"list", UUID, String key})               -> "id,id,..." = the accessories in that bag (retired ones left out), "" = empty
    apply(Object[]{"take", UUID, String key, String id})    -> Integer slot = ONE slot holding exactly id was emptied and the bag saved
                                                               (the Unequip path: AccStore lock, saveK, republish); -1 = none there
    apply(Object[]{"put",  UUID, String key, String id, Integer slot}) -> Boolean TRUE = put back (that slot if still free, else the first
                                                               free slot below the server limit) and saved; FALSE = refused (an
                                                               accessory of the same line is in the bag now, no free slot) - the caller
                                                               keeps the item in the inventory
    null = refused before anything was looked at: key is not the player's ACTIVE profile key (PROFILES-CONTRACT rule 2: never another
    profile's bag), a bag file that could not be read (never written), the profile busy / not loaded (AccStore.moveBlock), bad arguments.
  REVIEW FIX (craft01fix, A3): put refuses an id that is not one of this mod's accessories (no group / not Skyy_) and never fills a slot at
  or above the server's slot limit (the slot it came from counts only while it is below the limit).
  The caller moves the item between the bag and the live inventory itself (counted - SkyySacks' AccLink), so every accessory is in exactly
  one place: the bag OR the inventory. Saved data: the bag files, same format (one slot line less / more, as Equip / Unequip write them).
  ROLLBACK to 0.5.18: safe (same files; benches then simply do not see the bag again).

0.5.18 (the base, still true unless 0.5.19 above says otherwise):
Run:   python test_skyyaccessories_0.5.18.py --build     -> SkyyAccessories/SkyyAccessories-0.5.18.jar on the committed kit, then the harness
       python build_skyyaccessories_0.5.18.py            (plain build: whatever tools/skyyui.py is on disk; deploys go through tools/deploy_set.py --yes)
Test:  python test_skyyaccessories_0.5.18.py             (harness_kit: -Xverify:all, class compare 0.5.17 -> 0.5.18, the craft, auto-equip, migration)
KIT: build against the COMMITTED tools/skyyui.py (kit 1.5) while the working tree holds another builder's uncommitted kit 1.6 edits - the
harness's --build pre-loads `git show HEAD:tools/skyyui.py` (copied into its scratch folder) as the `skyyui` module and then runs this build
script (the SkyyTrees 0.3.17 / SkyyHud 0.3.27 runner). Once the working-tree kit is committed, a plain
`python SkyyAccessories/build_skyyaccessories_0.5.18.py` uses it.

0.5.18 (2026-10-15) = CRAFT FROM THE BAG + AUTO-EQUIP + BIGGER LANTERN LIGHT (round acc0518).
Skyy 2026-10-15 (screenshot of the Accessory Bag page, 7 of 18 slots used, 'Accessories in your inventory: None - craft accessories at a
Workbench'): "allow crafting from the accessory bag, and make crafted accessory's auto equip."; (night screenshot, the Normal Lantern lights a
small circle) "id make T1 lantern zone a bit bigger. so we should scale them all up some"; (on the proposed reach 10 / 18 / 32 / 56) "keep
same scale, but make legendary 64".
  1. CRAFT FROM THE BAG. The Accessory Bag page (right-click the bag / /accessories) gets two tabs at the top (the vanilla tab row,
     docs/answered/ui.md 'Tabs': the active one Primary, the other Secondary, equal widths): Bag (the page as before) and Craft. With
     'Craft from the bag' off the Craft tab has the vanilla Disabled look (a click says it is switched off) and the empty inventory list
     says 'craft accessories at a Workbench'. The Craft view lists every accessory recipe of this mod's Workbench tab
     (Workbench_SkyyAccessories, read from the engine's own recipe table at runtime - the Accessory Bag item itself, retired and hidden old
     ids are left out) sorted like the Workbench tab (ItemLevel 1-51 = tier, cheapest first), 9 a page with the kit pager. Each row: the
     result's icon + real name (its en-US item name) + 'RARITY - CAN CRAFT / NEEDS MATERIALS / LOCKED', every ingredient as
     'Name have/need' (green when it can be crafted), and a Craft button. Crafting there needs no bench; knowledge recipes (the four
     Lanterns, unlocked by the Tree Sap collection) stay locked until known.
     MATERIALS: the inventory first (backpack, storage, hotbar - plain stacks only: a stack with extra data is never used), then the Void
     (SkyySacks sacks:fn:count / all / take / put / commit - item ids and resource types; nothing when SkyySacks is absent or paused), then
     THIS BAG (an equipped accessory that is an ingredient: the lower rarity of an upgrade, the bench accessories of the Omni). The counting
     and the choice are the engine's own (CombinedItemContainer.canRemoveMaterials / removeMaterials over COPIES; CraftingManager.
     getInputMaterials), then exactly what the copies lost is taken from the real places, each read back.
     ONE OPERATION on the player's world thread inside the page click (a double click = two events, one after the other: the second sees
     the materials gone). Order: gates (Server Setup switch, profile:busy / unloaded profile, unreadable bag file, the recipe still on the
     list, knowledge) -> materials check -> CraftRecipeEvent$Pre fired like CraftingManager.craftItem (another mod may refuse; nothing used)
     -> journal BEGIN (Skyy_SkyyAccessories/crafts.log, flushed to the OS - no fsync on the world thread) -> take inventory, Void, bag (any failure = everything taken so far goes
     back: inventory slots restored to their exact stacks, Void put back through sacks:fn:put, bag slots put back) -> the result (2. below;
     no room anywhere = full rollback, "nothing was used") -> Void commit -> journal DONE -> player marked for save -> CraftRecipeEvent$Post
     (quests and other mods see the craft) -> the equip sound. Every click answers with a result line and a rebuild (also when something
     throws).
  2. AUTO-EQUIP. Every crafted accessory - from the bag page OR a bench / pocket crafting / /craft - goes straight into the Accessory Bag
     when the bag's own rule takes it (AccStore.canEquipK, the Equip button's rule: a new line needs a free slot below the server limit; a
     better one than the best of its line replaces that one in place and the old one comes back to the inventory - "only your best of each
     line counts"). Otherwise it stays in the inventory with one short chat line saying why. The move is the Equip button's path: canEquipK
     -> the item out of its slot (counted) -> AccStore.equipK (the bag file saved at once, under AccStore.lock) -> on a refusal the item
     back into the same slot; an upgraded-out accessory back to the inventory (else a free bag slot, else a LOST line in the log, as Equip).
     BENCH / /craft HOOK: AccAutoPre (EntityEventSystem on CraftRecipeEvent$Pre: CraftingManager.craftItem / queueCraft and SkyySacks'
     /craft fire it before they pay) and AccAutoPost (CraftRecipeEvent$Post: fired per unit before giveOutput, the timed-queue case)
     snapshot the identities of the crafter's stacks of the output id and send ONE task to the world thread (it runs after the craft call
     returned, FIFO); the task equips only stacks that were not there before (MaxStack 1: one stack = one crafted accessory, at most the
     crafted count). A Post right after its Pre (an instant craft) is skipped - the Pre task covers it. The bag page's own events are
     ignored by both (SELF).
  3. SERVER SETUP -> Accessories -> Accessory Bag: "Craft from the bag" (craft.bag) and "Auto-equip crafted accessories" (craft.autoEquip),
     both default on, live; a missing key = on (the starter.bag rule: an existing file keeps its bytes).
  4. BIGGER LANTERN LIGHT: lantern.reach defaults Normal 6 -> 10, Unique 12 -> 18, Rare 24 -> 32, Legendary 48 -> 64 (the max), and
     lantern.lights 7 -> 8: with 7 the Legendary ring stops at 61 blocks (1 light above + 6 around); 8 (+ 7 around) reaches the full 64 with
     the same soft edge (lantern.edge 96 and lantern.height 64 unchanged). The light model now gives Normal a hidden light too (10 blocks
     need more than the torch-bright glow's ~6). New table (height, level, reach, ring): Normal 10 / 24 / 10.0, Unique 25 / 50 / 18.3, Rare
     52 / 95 / 32.0 + 3 around at 3.5 blocks, Legendary 52 / 95 / 64.0 + 7 around at 45 blocks. Item descriptions follow (about 10 / 18 /
     32 / 64 blocks).
     ONE-TIME MIGRATION (PROJECT-RULES section 4, the migrate055 pattern, run after migrate051 and migrate055, before the loader): a
     config.properties whose LAST live entry of a key is a one-line entry still holding the 0.5.5 default gets the new default (value text
     only - key, separator, CR and every other byte kept); a hand-edited value is kept and logged ("kept (custom)"); the History copy of the
     old file is made and VERIFIED before the rewrite (the kit's atomic write); one config-changes.log line per changed key (Server Setup ->
     Changes -> Undo); the run-once marker is a comment line "# SkyyAccessories 0.5.18 Lantern reach ..." placed right above the first
     lantern.reach / lantern.lights entry (or at the end), also in the default text, so a fresh file never migrates. A 0.5.4 file gets
     M55 first (its own marker and History copy), then this one.
  Item ids, recipes, names, qualities, the bag's saved data format, commands: unchanged. One new bridge key (fix round 2):
  acc:lamp:reach = "10,18,32,64" (the live lantern.reach of Normal..Legendary, a String, next to acc:lamp) for SkyyGear's helmet tooltip. New classes AccCraft, AccAutoTask,
  AccAutoPre, AccAutoPost (two registerSystem: one per class). Page 952 -> 980 px high (the 44 px tab row; the bonus rows 22 -> 18 px).
  FIX ROUND (critics): Primary / Secondary tabs (the locked rule) instead of tertiary; craft.bag off -> Disabled Craft tab + the old
  'craft accessories at a Workbench' hint; a craft whose upgraded-out accessory could not be returned shows red; the auto-equip cap
  covers all three containers together; the journal no longer fsyncs (2-3 disk syncs per craft on the world thread); craft rows 74 -> 72.
  FIX ROUND 2: a bag craft no longer auto-equips an upgrade whose upgraded-out accessory would have nowhere to go (inventory AND bag
  full, the materials freed no slot): AccCraft.swapSafe; the craft is then rolled back ('no room ... nothing was used') instead of
  destroying the old one. acc:lamp:reach published (above).
  ROLLBACK to 0.5.17: safe - the bag files are the same format; 0.5.17 ignores craft.bag / craft.autoEquip and crafts.log; the migrated
  lantern numbers stay (0.5.17 reads them as custom values - Undo them in Server Setup -> Changes if wanted).

0.5.17 (the base, still true unless 0.5.18 above says otherwise):
Test:  python test_skyyaccessories_0.5.17.py             (harness_kit: -Xverify:all, class compare 0.5.16 -> 0.5.17, the starter bag)

0.5.17 (2026-10-15) = THE STARTER ACCESSORY BAG (Skyy 2026-10-15, fresh world, inventory screenshot: class sword + lifelong tools in the
hotbar, a Magic Bag + bread in the inventory, no Accessory Bag: "put the accessory bag in your inventory at spawn too")
  1. EVERY PROFILE GETS ONE Accessory Bag item (Skyy_Accessory_Bag - the right-click item that opens the bag page; normally crafted at
     Fieldcraft / the Workbench tab) put into its inventory, storage first (Inventory.getCombinedStorageHotbarBackpack().addItemStack -
     never dropped on the ground), counted before and after:
       - a NEW profile: as soon as SkyyProfiles has created + switched to it (the same moment rule as the class kits, SkyyClasses 0.1.7
         LOCKED "immediately": the 5 s AccTick sends one AccStarter task to the player's world thread; no 31 s wait);
       - an EXISTING profile that never had one: once, at its next load (the same task).
     Gates (all re-checked on the world thread inside one task, so a profile switch - itself one world-thread task - can never interleave):
     Server Setup switch on, profile:busy absent + the profile loaded (AccStore.moveBlock, PROFILES-CONTRACT rule 5), with SkyyProfiles a
     profile exists (profile:<uuid>; never during the first-join create page), the player ready (not waiting for the client), alive, still
     in the world the task was sent to. The give itself runs under AccStore.lock(uuid) with ONE pkey resolved for the whole step.
  2. NEVER A SECOND COPY - a per-profile marker in the profile's own Accessories data: Skyy_SkyyAccessories/starter/<pkey>.properties
     (PROFILES-CONTRACT rule 1: the storage key in the file name; its own folder, so AccNotice.hasOldBag's bags/<uuid>-p*.properties scan
     never sees it). Decided ONLY after the bag is really in the inventory (count after - before = 1), or when the profile already owns
     one. THE DISK WRITE IS DELAYED ~35 s (review fix 1): the answer is kept in memory at once (DONE - no second give in this run, also
     across a re-login) and in DUE (pkey -> {answer, due time}); AccTick writes due markers (tmp + fsync + move), shutdown writes every
     pending one at once. Why: the inventory reaches disk only with the engine's ~10 s player save and SkyyProfiles' crash roll-forward
     can reload the pre-switch snapshot for up to 30 s - a crash inside that window now leaves NO marker, so the next login checks the
     inventory again (bag saved -> owned-inventory, else given again: never lost, never doubled). Answers:
       - marker present -> nothing (the bag was given / owned before; dropping it, re-logging, switching profiles or a restart never give
         another); marker unreadable -> nothing, one WARN (fix or delete the file);
       - ALREADY OWNS ONE = counts as given (marker "owned-..."): a bag ITEM anywhere in storage / hotbar / backpack / utility / tools, or
         in SkyySacks' Void (sacks:fn:catOf + sacks:fn:count - asked only when catOf gives the bag a home; SkyySacks 0.8.x homes no Skyy_
         item but dishes, so today this answers 0; a paused Void (-1) waits). The bag's saved data (bags/<pkey>.properties) does NOT
         count (review fix 2: /accessories opens the bag page without the item, so a profile could have used it and never held one);
       - inventory FULL -> no marker, one short chat line, then retried SILENTLY every ~60 s in the same session (review fix 3; no second
         chat line); a new session tells once more. Never dropped. The Void fallback the task asked for is NOT possible with today's
         SkyySacks bridge: sacks:fn:deposit only takes a stack out of a hotbar slot and the Void has no category for the bag (catOf = null).
       - the inventory could not be reached (no combined container / an exception while adding): an ERROR, not "full" (review fix 4) -
         one WARN, no chat, no marker, tried again by the next tick;
       - a marker that cannot be written when due: stays pending (DONE kept, so no second give this run), one WARN, retried every 5 s.
     Profile switch: each profile has its own marker + its own inventory (SkyyProfiles swaps the vanilla inventory), so profile A's bag
     stays with A and profile B gets B's own one bag - never two in one profile.
  3. SERVER SETUP -> Accessories -> Accessory Bag: "Starter Accessory Bag" (config.properties starter.bag, default true, live; a missing
     key = on, like lantern.helmet in 0.5.10). Off = no bag is given and nothing is recorded (switching it on later still gives them).
  Item ids, recipes, names, the bag page, saves of the bag itself, bridge keys, other config rows: unchanged. New class AccStarter; changed:
  AccDefs (STARTER), AccCfg (the key + its default text), AccTick (dispatch, due marker writes, prune), the plugin (folder + shutdown flush),
  the config kit rows.

0.5.16 (the base, still true unless 0.5.17 above says otherwise):
Test:  python test_skyyaccessories_0.5.16.py             (harness_kit: -Xverify:all, class compare 0.5.15 -> 0.5.16, the metal Lanterns)

0.5.16 (2026-10-15) = THE METAL LANTERNS (Skyy 2026-10-15, screenshot of /craft search 'lant': "Skyy Talisman Lantern Common" needs Deco
Lantern 1 + Furniture Crude Torch 4 + Ingredient Bar Copper 2: "id remove the deco lantern from this rescipy, and if it takes copper to craft
it should look like copper." - the main session applied the rule to every rarity: the look follows the metal bar of its recipe)
  1. RECIPE: the Normal Lantern Accessory (Skyy_Talisman_Lantern_Common) = Crude Torch x4 + Copper Bar x2 (the Deco Lantern input is gone).
     Same Workbench tab, same KnowledgeRequired (the Tree Sap collection tier unlocks it - SkyyCollections names recipe ids only, no
     input), /craft unchanged. Unique / Rare / Legendary recipes unchanged (each still takes the rarity below). The 0.5.13 tab order rule
     (tier, then cheapest first) and the 0.5.15 ItemLevel key are recomputed from the new costs as before: the cheaper Lanterns move up
     inside their tier (the rule, not a fixed list).
  2. LOOK = THE RECIPE'S METAL: Normal Copper (Copper Bar x2), Unique Copper (Copper Bar x4), Rare Iron (Iron Bar x10), Legendary Thorium
     (Thorium Bar x10) - LAN_METAL, asserted against each recipe's own bar.
     - icon: our own drawn icon (tools/art/make_accessory_icons.py lantern()), drawn at build time with the shared SkyWynn tier ramp as its
       metal (the light-armor / mining sheets' Copper / Iron / Thorium) instead of the rarity metal (iron / gold / rose gold / platinum);
       the gem, glints and Legendary glow stay the rarity's. The generator file is untouched; the other 40 icons are byte-identical.
     - held / worn model texture: each model stays its vanilla lantern (Village / Kweebec / Sandswept / Light Temple); the texture is still
       read from the cached Assets.zip at build time (vanilla-derived: never committed) and now RECOLOURED by tools/skyyart.py (SA.recolor
       with SA.metal_gradient(<metal>) = that metal's vanilla pickaxe head + bar tones) part by part (blockymodel nodes, LAN_LOOK_PARTS);
       the glowing core (Light_On) keeps its vanilla pixels; alpha unchanged everywhere. Same paths
       Items/SkyyAccessories/SkyyAccessories_Lantern_<Rarity>_Texture.png.
  3. Every Assets.zip read of this build (SUI.verify, the sound list, the item / texture reads) uses the CACHED copy (tools/serverjar.py),
     never the installed game file.
  Item ids, qualities, names, saves, bridge keys, config, classes (version texts + the WbRank table): unchanged.

0.5.15 (the base, still true unless 0.5.16 above says otherwise):
Test:  python test_skyyaccessories_0.5.15.py             (harness_kit: -Xverify:all, class compare 0.5.14 -> 0.5.15, the client-sort key)

0.5.15 (2026-10-15) = THE WORKBENCH TAB ORDER, CLIENT SIDE (Skyy 2026-10-15, screenshot of Workbench > Accessories & Bags on a fresh profile:
Workbench Accessory I is the 3rd icon; "sort the accessories by tier. T1 at the top. easiest to craft first." - earlier, 2026-10-13: "since the
tutorial asks you to craft this, id move it to the top. sort them by tier, and per tier,m sort them by easiest to craft.")
  WHAT WE KNOW ABOUT THE NATIVE CLIENT'S ORDER (evidence, 2026-10-15):
    - 0.5.13 / 0.5.14 send the tab's recipes in the wanted order (WbRank TreeSet -> CraftingWindow "craftableRecipes"); the client does NOT
      show that order (Skyy's screenshot) -> the client re-sorts.
    - Vanilla sends every bench category as a fastutil ObjectOpenHashSet (hash order), yet vanilla tabs are not shown in hash order either.
    - The protocol has no order field for a recipe or an item (CraftingRecipe: id, inputs, outputs, primaryOutput, benchRequirement,
      knowledgeRequired, timeSeconds, requiredMemoriesLevel; ItemBase has no order / sort field; ItemQuality has no QualityValue - only its
      index; ItemCategory.order sorts CATEGORIES, not the recipes in a bench tab). The numbers the client knows per output item are
      itemLevel and qualityIndex (plus BenchRequirement.requiredTierLevel per recipe).
    - Every string key the client could sort by was tried against the screenshot (Workbench Accessory I 3rd) on the 47 / 51 tab recipes:
      item id, recipe id, English name, icon path, asset order, the UpdateRecipes / UpdateItems hash-map orders (fastutil + java.util at
      every table size), quality (every index order) then name / id / asset order - only "English name DESCENDING" gives 3rd, and its first
      two (Workbench Accessory III, II) do not match the screenshot. So the client sorts by a NUMBER that TIES on our recipes: all 51 have
      ItemLevel 0 (absent) and only 4 qualities -> the order inside a tie comes from the client's own (unstable) sort, not from the server.
  THE FIX: give every recipe of the tab its own ItemLevel, ascending in exactly the wanted order (0.5.13's ORDER: Workbench Accessory I
  first, then tier = rarity Normal / Unique / Rare / Legendary, inside a tier the cheapest recipe first; the Omni Accessory last):
      ItemLevel = 1 .. 51 (position in the tab). Rarity already rises with the position (asserted), so a client sort by ItemLevel, by
      (rarity, ItemLevel) or by (ItemLevel, rarity), stable or not, all give the same order - no ties left.
  SAFE: ItemLevel is read on the server only by the protocol (Item.toPacket; no other engine caller of getItemLevel in 0.7.2) and by SkyyGear
  GearLevel for GEAR ids only (Skyy_ items are never gear unless a server owner lists them in gear.include) and SkyyMerchants (weapons only).
  Item ids, recipes (inputs, costs, benches, categories), names, qualities, saves, bridge keys, config: unchanged. WbRank (the server order)
  unchanged. Classes: version texts only.
  UNVERIFIED: that the client's key is ItemLevel (it is the only per-item number we can set without changing rarity or a recipe's bench tier
  gate); whether the item tooltip shows the ItemLevel number.

0.5.14 (the base, still true unless 0.5.15 above says otherwise):
Test:  python test_skyyaccessories_0.5.14.py             (harness_kit: -Xverify:all, class compare 0.5.13 -> 0.5.14, the sounds EXECUTED, start twice on a live copy)

0.5.14 (2026-10-14) = SOUND PASS ROUND 2, the SkyyAccessories part (research/Sound-Pass-Plan.md; Skyy 2026-10-14 ~18:30 "do 1. 3. 6. 7. 8.
and 9." - item 6 = sound pass rounds 2-4 + a per-player sound switch). The round 1 recipe (SkyyQuests 0.3.1), generated by tools/soundpass_gen.py:
  1. TWO SOUNDS on the Accessory Bag page, 2D to that player only (category UI):
       equipped   SFX_Drag_Items_Gems                     an accessory went into a free bag slot
       upgraded   SFX_Runebinders_Lattice_Unlock_Local    a better accessory of the same line replaced the old one in place (the
                                                          "upgraded to ..." line - the bag's own upgrade)
     Played from AccSnd.equipped(u, result of AccStore.equipK) right after the move; a refused equip (bag full / same or better
     equipped / retired) and unequipping stay silent. (The bag's slot count is a server setting - there is no per-player bag upgrade.)
  2. AccSnd (the one helper; never throws; a missing id = one WARN; 0.5 s per player per sound) + the PER-PLAYER SWITCH: the bridge key
     settings:sounds:<uuid> (Boolean, SkyyMenu 0.3.25 /settings) FALSE = that player hears no SkyWynn sound; absent / TRUE = play.
  3. SERVER SETUP -> Accessories -> new category "Sounds" (5 rows, all live, KEEP=10): Sounds (master) + per sound on / off + its id
     (check= AccSnd.check). File: Skyy_SkyyAccessories/sounds.properties (written with the defaults when missing).
  4. No saved-data change, no new command, no bridge key written. ROLLBACK to 0.5.13: safe (0.5.13 never reads sounds.properties).

0.5.13 (the base, still true unless 0.5.14 above says otherwise):
       python build_skyyaccessories_0.5.13.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.13.py             (bare JVM -Xverify:all: class compare 0.5.12 -> 0.5.13 = WbRank only, the new
       order on a real CraftingWindow with and without SkyySacks, the 0.5.12 Lantern tracker checks on the new jar, start twice on a live copy)
0.5.13: THE WORKBENCH TAB ORDER (Skyy 2026-10-13: "since the tutorial asks you to craft this, id move it to the top. sort them by tier, and
     per tier,m sort them by easiest to craft."; full notes in tools/accessories_0_5_13_patch.py): Workbench Accessory I first, then
     tier by tier (Normal, Unique, Rare, Legendary = the item's rarity, the Accessory Bag included = Unique), inside a tier the cheapest
     recipe first (inputs expanded to raw materials, each raw material worth 3 ** (material tier - 1)), the Omni Accessory last. Only
     WbRank.rank changes (the order the server sends); items, recipes, saves unchanged.
0.5.12: THE LANTERN HIDE WITHOUT THE WALK (audit 3b; full notes in tools/accessories_0_5_12_patch.py): AccLanternHide removes only the
     recorded helper refs of the store from each viewer's visible set (one list per store per tick) instead of walking every visible
     entity; the old walk stays as the safety net when the store holds unrecorded marked entities. AccLantern.step writes OWNER only when
     the player's entity ref changed. No behaviour change.
0.5.11: THE LANTERN ITEM TEXTURES (client log "Cannot use Blocks/Decorative_Sets/<set>/Lantern_Texture.png as texture for item
     Skyy_Talisman_Lantern_*" x4; full notes in tools/accessories_0_5_11_patch.py): the build copies each vanilla lantern texture from
     Assets.zip into the jar at Common/Items/SkyyAccessories/SkyyAccessories_Lantern_<Rarity>_Texture.png (an item path, never committed,
     no vanilla path overridden) and the Lantern items point there; same model, same pixels. No item texture under Blocks/ (build guard).
0.5.10: THE MINING HELMET LIGHT (Skyy: "make sure that if those mining helmets show a light, it works"; full notes in
     tools/accessories_0_5_10_patch.py): while SkyyGear 0.2.15 posts gear:lamp:<uuid> (1-4 = Lantern Normal..Legendary) the player glows
     exactly like a Lantern of that rarity; with a Lantern in the bag too the stronger wins (never stacked); gone within ~1 s after the
     key goes; ignored while profile:busy. Server Setup -> Accessories -> Lantern: "Mining helmet light" (lantern.helmet, on). Bridge
     acc:lamp = "on" / "off" (SkyyGear's tooltip Lamp line). Nothing saved.
0.5.9: THE NEW ACCESSORY BAG ICON (Skyy 2026-10-08: "Use Option B gem colors", "Yes, the bag icon looks good, commit it"; full notes in
     tools/accessories_0_5_9_patch.py): the Workbench "Accessories & Bags" tab icon = art/accessory-bag-icon/.../SkyyAccessories_Bag_Menu.png
     (original art, committed; was the vanilla Utility_Bag_Seed icon), and the Accessory Bag model's 5 gems follow it (tools/art/make_bags.py
     ACC_GEMS, left to right Health red, Stamina yellow, Mana blue, Regeneration green, Speed cyan). Art only: classes (version constants
     only), every other item, recipes, texts and saved data unchanged.
0.5.8: THE NEW ACCESSORY BAG LOOK (Skyy 2026-10-08: "the accessory bag is a little too over decorated.  but i love the bags.", "as drawn,
     violet. start the bag round"; full notes in tools/accessories_0_5_8_patch.py): tools/art/make_bags.py runs IN MEMORY at build time
     and the Accessory Bag item gets its toned-down model / texture / icon / IconProperties through item(..., visual=). Art only:
     classes (version constants only), every other item, recipes, texts and saved data unchanged.
0.5.7: OUR OWN ACCESSORY ICONS (Skyy 2026-10-07: "all of the items look beautiful. are they deployed in game?", "Amber works."; full
     notes in tools/accessories_0_5_7_patch.py): the build draws the 44 icons with tools/art/make_accessory_icons.py (our own art, at
     build time, nothing vanilla), ships them at Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png and points every
     booster item's Icon at its own (40 line ids + 4 Lantern + the 20 hidden legacy ids at their tier). Art only: models, recipes,
     texts, classes and every other item unchanged.
0.5.6: THE LANTERN RECIPES FOLLOW THE TREE SAP COLLECTION (Skyy 2026-10-05: "add the lantern accessory's crafting recipe to the sap
     collection. so you have to collect a lot to get a legendary lantern"; full notes in tools/acc_0_5_6_patch.py):
     - the four Lantern recipes are KnowledgeRequired; AccKnow (1 s, world thread) keeps exactly those four ids in each player's known
       recipes: while SkyyCollections 0.2.7+ publishes coll:lantern, known = the Lantern recipe ids in coll:recipes:<uuid> (Tree Sap
       tiers, Server Setup rows in SkyyCollections); without it every Lantern stays craftable (0.5.5). Owned Lanterns never change.
     - Hidden lights: most - the row help / config comment now say 1-3 = one light, 4-9 = one light + a ring of 3-8 (the solver's rule).
     - config kit KEEP 10.
     - review fixes: coll:lantern "off" = free (no freeze after a reload hides Tree Sap); 6 s settle after a profile switch; no
       coll:recipes for 10 s = no Lantern known.
0.5.5: LANTERN SMOOTH EDGES (Skyy 2026-10-04: "2, try to smooth the edges"; full notes in tools/acc_0_5_5_patch.py):
     - every hidden light is at most lantern.edge bright (Advanced "Hidden lights: brightest", 96): a weaker light ends its lit area in a
       smaller step (0.00166 x level at the client's cut-off). A reach one such light cannot give gets a RING of lights of the same level
       and height around the light above (AccLanternMark.slot 1..8, AccLantern.ring; at most lantern.lights = Advanced "Hidden lights:
       most", 7, per wearer). Legendary: 95 at 52 up + 5 around at 27.5 blocks - fades smoothly to 0.16 at 48 blocks (0.5.4: a 0.35 step).
       Unique / Rare unchanged. Every 0.5.4 exit path (unequip, death, logout, world change, stop, restart) covers the ring.
     - lantern.height default 64 (0.5.4: 128); AccCfg.migrate055 turns a lantern.height line still at 128 into 64 ONCE (History copy,
       config-changes.log line with Undo, marker comment; other values kept).
0.5.4: THE LANTERN LINE REPLACES NIGHT VISION (Skyy 2026-10-03: "forget night vision, just do the lantern accessory we talked about. that
     just makes you glow like the backpack torch mod. (brighter the higher rarity." + "Range up, brightness capped"; full notes, the tier
     table and the engine proof in tools/acc_0_5_4_patch.py):
     - Lantern Accessory Normal / Unique / Rare / Legendary (Skyy_Talisman_Lantern_Common.._Epic), its own line, crafted at the Workbench
       tab, each tier FROM the tier below. In the Accessory Bag the wearer GLOWS like a torch for everyone (a DynamicLight component on
       the player - the vanilla torch's #ba9 light, never saved); Unique and up add REACH (about 12 / 24 / 48 blocks, a torch ~6) through
       ONE hidden helper entity above the wearer (NonSerialized, Intangible, no model, a 5 s DespawnComponent dead-man switch, our marker)
       with a WHITE light that only its wearer sees (AccLanternHide, the entity tracker's find-visible group; lantern.shareReach shows it
       to everyone), placed as low as the reach allows while eye-level bits stay as bright as torch-lit dust; it only goes into loaded,
       ticking sections between y 1 and 318, within the wearer's view radius. Off at once on unequip / profile switch / death / switch
       off; logout and world change remove it in its own world (AccLanternHelp). Server Setup -> Accessories -> Lantern: on / off, glow
       per rarity, reach per rarity, the highest helper, shared reach. Existing config files are not rewritten (missing keys = defaults).
     - Night Vision is RETIRED: the item stays valid but does nothing, cannot be equipped (Unequip still takes it out), never counts, is
       out of lines / givetier / give / acc:defs and hidden from the creative library; its tooltip says the Lantern replaced it.
     - The "previous tier" rule (Skyy) is checked on every recipe at build time; every line already followed it.
0.5.3: THE NIGHT VISION ACCESSORY (Skyy 2026-10-02: "add a night vision accessory if you can."; full notes and the engine proof in
     tools/acc_0_5_3_patch.py): one item, Skyy_Talisman_NightVision_Rare ("Night Vision Accessory", Rare, admin give only, its own line
     so it stacks with every booster). While it sits in the Accessory Bag, its wearer - and nobody else - gets a light on their own
     character: a DynamicLightUpdate queued on the player's OWN entity viewer (no component, nothing saved), sent by the new system
     AccNightVision in the entity tracker's update group (EntityTrackerSystems.QUEUE_UPDATE_GROUP, after the visible sets are built and
     before SendPackets), decided once a second and at once after a bag change or when the client re-creates the player's entity;
     taken back from that entity when it leaves the bag. Server Setup -> Accessories -> Night Vision: on / off, the light (radius,
     red, green, blue; 255,1,1,1) and a safety re-send (10 s). Existing config files are not rewritten (missing keys = defaults).
0.5.2: THE WORKBENCH TAB "Accessories & Bags" (Skyy 2026-10-01: "make a new tab for accessories, and sacks. list them in the order you
     would craft them. low levels first. with legendries and omnis at the bottom."; full notes in tools/acc_0_5_2_patch.py, engine proof
     in tools/skyywbtab.py): every accessory recipe (Workbench requirement Categories ["Workbench_Crafting"] -> ["Workbench_SkyyAccessories"];
     the pocket Accessory Bag keeps Fieldcraft/Tools and ALSO lists in the tab) and every SkyySacks 0.7.10 bag recipe in one new Workbench
     tab, added at runtime to every Workbench (start() + an asset reload listener; this mod OWNS the tab and its order, SkyySacks carries a
     fallback copy). Order sent by the server: Accessory Bag, Normal bags, then Normal -> Unique -> Rare -> Legendary (stat accessories,
     bench accessories, bags), Omni Accessory, Mythic Omni Bag last (client side UNVERIFIED). Ingredients, outputs and tiers unchanged.
0.5.1: TWO CHANGES (full notes, engine proof and the hidden id list in tools/acc_0_5_1_patch.py):
     - THE STAMINA LINE (Skyy: "double the amount of stamina the stamina accessory gives you, but half the stamina regen boost it
       gives you"; OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina +3 / +6 / +9 / +12 (was +1.5 / +3 / +4.5 / +6) and Stamina Regen
       +2.5 / +5 / +7.5 / +10 % (was +5 / +10 / +15 / +20), Normal..Legendary; tooltips, /accessories lines, the bag page and the
       Server Setup defaults follow the booster table. ONE-TIME UPDATE of a 0.5 config.properties (AccCfg.migrate051, setup() before
       the loader and CfgPub.start; the SkyyGear 0.1.1 migrateStat011 pattern): a boost.Stamina.flat / boost.Stamina.regenPct line that
       still holds the 0.5 numbers gets the 0.5.1 numbers, any other value is kept (INFO line); the old file is first kept as a
       History version (verified before the rewrite - else WARN, untouched, retried next start), one config-changes.log line per
       changed entry (Server Setup -> Changes can undo it); the marker comment "SkyyAccessories 0.5.1 Stamina defaults" makes it
       run once (the 0.5.1 default text carries it).
     - OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"): the 20 legacy booster ids (_Talisman, _Ring,
       _Artifact, the old _Legendary) and the 5 retired bench accessories get "Variant": true and no "Categories" (the engine's item
       library filter, documented in the Item codec - proven at build time); they still load, look, show their tooltip and convert
       as in 0.5. The current items stay listed. No new quality (SkyyVault's HideFromSearch is a quality flag: it would need hidden
       twin qualities and shift every quality index once more).
     - (forced by the 0.4.3 build gate) the Campfire Accessory item text follows SkyyCooking 0.1.3 (Skyy, LOCKED 2026-10-01: campfire
       cooking pays half the Cooking XP): "25% Cooking XP and 75% of your cooking bonus by default" (was 50%); deploy with SkyyCooking 0.1.3.
0.5 notes:
0.5: BOOSTER ACCESSORIES, PARTS 1 AND 2 (Skyy's decisions, OPEN-QUESTIONS LOCKED 2026-09-30; research/Booster-Accessories-Spec.md 6.1
     and 6.2; full notes in tools/acc_0_5_patch.py):
     - ONE booster table (BOOSTERS -> flat 1-D arrays in AccDefs): line, stats, four numbers per stat (Normal..Legendary), item ids,
       looks, source words. Five folded lines: Health, Stamina, Mana, Regeneration, Speed. Part 2: five new lines (admin give only,
       ids Skyy_Talisman_<Key>_T1..T4): Brawler (Strength), Runic (Magical Power), Stonehide (Defense), Razorfang (Crit Chance and
       Crit Damage), Feather (less fall damage, higher jumps).
     - combat stats go to SkyyGear as ONE text per player in gear:extra:<uuid> (SkyyAccessories owns the key: whole numbers, keys
       str mp def cc cd, written only on change, a second writer = back off for that player, removed on leave / shutdown); Feather's
       jump and fall ride the accessories.talismans movement post (fall damage is applied by SkyySkills).
     - the 25 talismans FOLD into those lines: same ids, names "<Rarity> <Line> Accessory", new numbers (Health / Stamina flat, Mana %
       with a floor, Regeneration lower, Speed 2.5..10 %), _Epic = Legendary, the old _Legendary = a legacy id (no recipe, counts as
       Legendary, stored as _Epic); only the best rarity of a line counts; "+stamina" = max Stamina AND a Stamina Regen top-up that
       only flows while vanilla's own refill flows (never while sprinting, gliding or blocking).
     - GEAR RARITIES for every accessory: six Skyy_Acc_* qualities (Fabled / Mythic shipped unused), bench I Normal, II Unique,
       III Rare, IV+ Legendary, the Omni Legendary, the bag item Unique; a world-thread restamp fixes saved stacks.
     - config migration (one atomic write, config.properties.pre-0.5.bak, config-changes.log lines, slots 9 -> 18), a one-time chat
       notice per player (notices.properties), Server Setup rows for every number (boost table, 5 line switches, notice switch).
     - the bag: 60 storage slots (slot0..8 in bags/<key>.properties as before, slot9..59 in bags/<key>.more.properties, so a rollback
       to 0.4.5 hides them instead of deleting them), 18 by default; the page shows 9 rows per page with pagers.
     - /accessories lines (players), /accessories give | givetier (admins), bridges acc:defs + acc:fn:give; the bag page lists the
       active bonus of each line and says when SkyyGear / its combat stats / SkyySkills are missing for a line.
     DO NOT ROLL BACK BELOW 0.5: restamped stacks point at Skyy_Acc_* qualities that 0.4.5 does not ship (stale look, UNVERIFIED).
0.4.5 notes:
0.4.5: THE VANILLA LOOK for the Accessory Bag page (Skyy 2026-09-28: "the new goal for any and all UI added in the game is for them
     to look and feel vanilla"; research/Vanilla-UI-Style-Guide.md; full notes in tools/acc_0_4_5_patch.py). ONLY THE LOOK CHANGED:
     - the page is built from the shared kit tools/skyyui.py when this script runs (SUI.verify() first proves every style value,
       texture and sound against Assets.zip, read-only); the kit id is in the ready log line.
     - the vanilla decorated window (title bar with runes, the gold ornaments, ACCESSORY BAG in the title font), 1210 x 780 (was
       640 x 630): a well with the hint and the live Bonuses line (left-aligned, the vanilla value colour), then two vanilla list
       wells - BAG SLOTS (the slot rows) and the inventory list (up to 6 rows) - with vanilla list rows (row panel, blue status bar,
       40 px item icon, 18 px name + 15 px rarity word in the item's quality colour) and small Secondary UNEQUIP / EQUIP buttons,
       then the result line (the kit's status line: green done, red refused, info blue notes / the Campfire line; AccPage.infoColor
       reads 0.4.4's unchanged result texts).
     - every element id of 0.4.4 (#SkyyAcc is now the window body), the un:<i> / eq:<i> bindings, every text (the same Java
       expressions; b.set, so commas show again - safe() only guards the item ids inside the markup), invIds and the profile-key
       check are 0.4.4's; handleDataEvent and every other class are unchanged. This rebuild compiles the current admin config kit
       tools/skyycfg.py 1.1 (the live 0.4.4 jar was built on 1.0): CfgFile / CfgFn / CfgRows / CfgSaveTask carry 1.1's
       hand-edit table-line checks, reload order and monitor changes (the Talisman bonuses rows + /accessories reload use them).
0.4.4 notes:
0.4.4: ADMIN CONFIG IN GAME (research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; full notes in tools/acc_0_4_4_patch.py):
     - FIRST config file Skyy_SkyyAccessories/config.properties, written on the first start with today's values: slots=9,
       regenEverySeconds=2, bonus.<Family>=<Common..Legendary percents> (the numbers the talisman tooltips print).
     - SkyWynn Menu -> Server Setup -> Accessories (SkyyMenu 0.3) edits them through the kit (tools/skyycfg.py): validated, logged in
       config-changes.log, versioned in config-history/, written back line by line. config:def/fn:SkyyAccessories published LAST in setup().
     - slots limits NEW equips only: accessories already in a higher slot stay, keep counting and can be unequipped (the page hides only
       empty slots above the limit). The bonus table and the regeneration interval apply at once.
     - /accessories reload (skyyaccessories.admin only, groups cleared) re-reads the file after hand edits (logged via=command).
     - Item tooltips keep the built-in numbers (assets); the bag page's Bonuses line shows the live ones.
0.4.3 notes:
0.4.3: the CAMPFIRE accessory is BACK (Skyy 2026-09-24: quick inventory cooking, an emergency cook). Full notes in
     tools/acc_0_4_3_patch.py:
     - Skyy_Accessory_Campfire_T1: recipe back (Bench_Campfire + 4 Copper Bars at a Workbench), equippable, Common, in acc:has:<uuid> and
       acc:fn:has again. Description "Quick inventory cooking: campfire dishes in /craft at 50% Cooking XP and 75% of your cooking
       bonus" (SkyyCooking 0.1.1 cook:fn:campfire does the reduction; SkyySacks 0.7.4's /craft Campfire tab shows + calls it - with
       0.7.3, which still treats it as retired, it unlocks nothing).
     - Omni: covers the Campfire again; recipe = the 11 active top-tier bench accessories (0.4.2: 10).
     - Review fixes: the item text calls 50% / 75% the defaults; the bag page status line shows SkyyCooking's LIVE campfire factors
       while the Campfire accessory or the Omni is equipped (AccStore.campFactors / campLine); the 5 s tick logs one warning per
       distinct live pair that differs from the item text (AccStore.campCheck); the build fails if the SkyyCooking defaults line
       cannot be read.
     - Alchemy Bench T1-T4 and Cooking Bench stay retired exactly as in 0.4.2; every other 0.4.2 behaviour is unchanged.
0.4.2 notes:
0.4.2: RETIRED bench accessories (Skyy: Alchemy + Cooking are table-only; research/Smithing-Smelting-Spec.md section 6; the Campfire
     goes too - its 3 recipes are all cooked food). Full notes in tools/acc_0_4_2_patch.py:
     - Skyy_Accessory_Alchemybench_T1..T4, Skyy_Accessory_Cookingbench_T1, Skyy_Accessory_Campfire_T1 keep their item assets (owned
       copies stay valid items) but have NO recipe, say "(retired)" and why in name + description, and do nothing.
     - Equip refuses them (page line + chat line, the item stays in the inventory); Unequip still takes an equipped copy out.
     - An equipped copy is filtered out of acc:has:<uuid> (AccDefs.benchList) and acc:fn:has (AccStore.has), so it unlocks no /craft
       recipes; rarityOf = 0 (never counts toward accessory power); the page shows it grey as "- retired" / "DOES NOTHING".
     - Omni: recipe = the 10 active top-tier bench accessories (was 13) and it no longer covers the retired three.
     - Every 0.4.1 per-profile behaviour is unchanged.
0.4.1 notes:
0.4.1: per-profile storage (tools/PROFILES-CONTRACT.md) - one accessory bag per SkyyProfiles profile (full notes in
     tools/acc_0_4_1_patch.py):
     - AccStore.pkey(UUID) = the contract helper (bridge "profile:fn:key"; falls back to uuid = profile 1). Bag files
       bags/<pkey>.properties (profile 1 = the existing <uuid>.properties, no migration), BAGS cache keyed by the pkey String,
       each store method resolves the key once (slotsK / saveK), locks stay per player.
     - acc:has:<uuid> / acc:tal:<uuid> stay UUID keys for the ACTIVE profile and are republished when profile:epoch:<uuid> (or the
       active key) changes - checked in the 5 s AccTick and the 1 s AccEffects sync; talisman stats, regen and the Speed movement
       source follow the new profile's bag through the same per-second sync (it reads through pkey).
     - The bag page rebuilds instead of acting when the profile changed since it was drawn. Vanilla inventory untouched.
     - Integration pass: Equip/Unequip refused while profile:busy:<uuid> is set (pending crash recovery) or the player's profile
       state is unknown (SkyyProfiles installed, no profile:epoch:<uuid>); one pkey per click for every store call of that click.
     - Without SkyyProfiles every key is the UUID: behaviour identical to 0.4.
0.4 notes:
0.4: RARITY TIERS + PERCENT LAYER + OMNI (full notes in tools/acc_0_4_patch.py):
     - Talismans Skyy_Talisman_<Family>_<Common|Uncommon|Rare|Epic|Legendary> (Quality = vanilla quality of that name), upgrade recipe =
       previous rarity + materials at a Workbench. Legacy 0.2/0.3 ids <Talisman|Ring|Artifact> keep their assets (no recipe) and count
       as Uncommon/Rare/Epic; Equip stores the modern id, Unequip returns the modern (upgradable) item. Bench accessory rarity by tier
       (T1 Common .. T5+ Legendary). One talisman per family counts (best rarity).
     - Vitality/Endurance/Intelligence = % of the FLAT max Health/Stamina/Mana, Regeneration = % of the FULL current max Health
       every 2 s (deliberate: the Health bar the item text names; a heal is not a max bonus), Speed = %
       through the movement protocol's pct layer. StaticModifier MULTIPLICATIVE was checked in bytecode: it applies after ADDITIVE but
       all multiplicative amounts are SUMMED into one factor (vanilla Meat_Buff 1.05 + ours 1.10 = x2.15), so the % is computed here
       from type max + every other ADDITIVE MAX modifier and posted as ADDITIVE (keys skyyacc_health/stamina/mana, as in 0.2/0.3).
     - Skyy_Accessory_Omni (Legendary, Workbench, all 13 max-tier bench accessories) counts as every bench accessory at max tier:
       acc:has expands it into Skyy_Accessory_<BenchId>_T<maxTier> entries, exactly one entry per bench at the best tier of real +
       Omni (SkyySacks needs no change). Own group "Omni".
     - /accessories (acc, accbag): setPermissionGroups hytale:Adventurer. Bag page shows rarity names in the quality colours.
0.3 notes:
0.3: Speed talismans use the SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py has the full spec; SkyySkills 0.2 Acrobatics runs the
     identical MoveSync code): bridge "move:<uuid>" -> ConcurrentHashMap source -> Map{layer "flat"|"pct", speed, jump, fallDamage}.
     This mod posts ONLY its own source "accessories.talismans" (layer pct, speed = best Speed talisman, removed at 0) and then applies
     the total of ALL sources: baseSpeed = default x clamp((1 + sum flat speed) x (1 + sum pct speed), 0.3, 5); jump height =
     (h0 + sum flat blocks) x (1 + sum pct), jumpForce = sqrt(2 g h), h0 = default jumpForce^2 / 2g, g = 32. Idempotent: two appliers
     agree, so talismans and Acrobatics never fight. The 5-strike back-off only triggers against writers outside the protocol (a new
     target resets it; logged once per player); defaults are restored only for a field that still holds the value the protocol wrote;
     nothing is written while mounted. fallDamage is applied only by the owner of bridge "stat:owner:fallDamage" (SkyySkills) -
     talismans post no fall stat. Non-Skyy mods that write MovementSettings directly are NOT coordinated (they win for the player
     they reset): keep them out of SkyWynn worlds; the known ones are named in the log on the first sync (skyymove.KNOWN_WRITERS).
0.2 notes:
SkyyAccessories 0.2 - build script (derived from 0.1 by tools/acc_0_2_patch.py - edit the patch, not this file)
0.2: STAT TALISMANS (Hypixel SkyBlock style) that work while they sit in the Accessory Bag, bag capacity 6 -> 9 (old bags keep their
     slots), "Talisman bonuses" summary line on the bag page. Items Skyy_Talisman_<Family>_<Talisman|Ring|Artifact>; one per family
     counts (same swap rule as the bench accessories). Effects: AccEffects (EntityTickingSystem on Player, world thread, 1 s per player):
     StaticModifier(MAX, ADDITIVE) keys skyyacc_health / skyyacc_stamina / skyyacc_mana, Regeneration = addStatValue(Health) every 2 s,
     Speed = MovementSettings.baseSpeed = default * (1 + bonus) + update(packetHandler) (EndgameAndQoL AccessoryPassiveSystem /
     RPGLeveling MovementSpeedHelper pattern: baseSpeed only) with a back-off when another mod keeps resetting it. Modifiers are removed
     as soon as the talisman leaves the bag. Bridge: acc:has:<uuid> = bench accessories in the bag (0.1 meaning, SkyySacks reads it),
     acc:tal:<uuid> = talismans in the bag, acc:fn:has = both.
     Review fixes: baseSpeed-only speed (no f*f compounding), unequip undoes exactly the baseSpeed we wrote, equip pre-checks the bag and
     hand-backs fall back to a free bag slot then a logged loss, per-player locks, talismans use the vanilla crystal fragment model.
0.1 notes:
SkyyAccessories 0.1 - build script (javassist via jpype). Accessory bag + bench accessories (Skyy's design 2026-09-23).
Run:   python build_skyyaccessories_0.1.py            -> SkyyAccessories/SkyyAccessories-0.1.jar
       python build_skyyaccessories_0.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Design (pattern copied from TerrariaAddons' AccessoryPouchSharedContainer: per-player container persisted to a file, opened from the
item's Secondary interaction; effects are checked, never "applied"):
 - Item Skyy_Accessory_Bag (Fieldcraft recipe): right-click -> page "SkyyAccBag" (/accessories or /acc also opens it).
   6 slots stored in Skyy_SkyyAccessories/bags/<uuid>.properties (slot0..slot5 = item id). Equip moves the item out of your
   inventory into the bag; Unequip gives it back (if your storage is full the item stays in the bag).
 - Bench accessories Skyy_Accessory_<BenchId>_T<n>: one per bench tier. T1 = the bench item + 4 copper bars at a Workbench;
   T(n+1) = T(n) + exactly the materials the real bench needs to upgrade to that tier (from the bench's TierLevels).
   Only one accessory per bench fits in the bag; equipping a higher tier hands the lower one back.
 - Bridge: "acc:has:<uuid>" -> "id,id" (what is in the bag) republished on every change and for every online player (5s tick);
   "acc:fn:has" -> java.util.function.Function apply(Object[]{UUID, String itemId}) -> Boolean. SkyySacks 0.6.1 reads acc:has to
   add a craft-page tab per bench accessory (recipes filtered by BenchRequirement.requiredTierLevel <= accessory tier).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyySkills 0.2)
import skyycfg as CFG   # 0.4.4: the admin config kit (research/Server-Setup-Spec.md 1.3-1.4, tools/CONFIG-CONTRACT.md)
import skyyui as SUI    # 0.4.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
import skyywbtab as WB  # 0.5.2: the Workbench tab "Accessories & Bags" (one source with SkyySacks 0.7.10; this mod is the OWNER)
import serverjar as _SJ # 0.5.16: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
# 0.5.22: skyyonce (the lifelong bag item of 0.5.20) is not used any more - the bag item is retired
ASSETS_ZIP = _SJ.assets_zip()   # read-only
SUI.verify(assets_zip=ASSETS_ZIP)   # 0.5.16: the cached copy; proves every vanilla value / texture / sound the page uses against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()   # "skyyui <version> <blob12>" - in the ready log line

VERSION = "0.5.24"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
ISS = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"
# 0.2 stat / movement API (verified with reflect.py + TerrariaAddons bytecode, see tools/acc_0_2_patch.py)
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
DST = "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes"
MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
MMG = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MVS = "com.hypixel.hytale.protocol.MovementSettings"
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
QRY = "com.hypixel.hytale.component.query.Query"
CRP = "com.hypixel.hytale.component.ComponentRegistryProxy"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (INV, "getHotbar"), (INV, "getBackpack"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"),
             (IC, "addItemStack"), (IC, "getCapacity"), (OCU, "registerSimple"), (HSV, "SCHEDULED_EXECUTOR"), (UNI, "getPlayers"),
             (PAGE, "rebuild"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
for c, m in ((ESM, "getComponentType"), (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (ESM, "addStatValue"), (ESM, "get"),
             (ESV, "get"), (ESV, "getMax"), (DST, "getHealth"), (DST, "getStamina"), (DST, "getMana"), (SMO, "getAmount"), (MTG, "MAX"),
             (CAL, "ADDITIVE"), (MMG, "getComponentType"), (MMG, "getSettings"), (MMG, "getDefaultSettings"), (MMG, "update"),
             (MVS, "baseSpeed"), (PR, "getPacketHandler"), (PLA, "isWaitingForClientReady"),
             (ETS, "tick"), (ACH, "getReferenceTo"), (CB, "getComponent"), (REF, "isValid"), (CRP, "registerSystem"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)
MV.probe(B, pool)   # 0.3: MovementStates.mounting, MovementSettings.jumpForce, PhysicsConstants.GRAVITY_ACCELERATION, ...
# 0.4: percent layer reads the stat type's base max + the other MAX modifiers; /accessories gets the Adventurer permission group
EST = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
ACM = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((EST, "getAssetMap"), (EST, "getMax"), (ILT, "getAsset"), (ESV, "getModifiers"), (SMO, "getCalculationType"),
             (MOD, "getTarget"), (MTG, "MAX"), (CAL, "ADDITIVE"), (ACM, "setPermissionGroups"), (ACM, "addAliases")):
    B.probe(pool, c, m)
# 0.4.4: /accessories reload (admin sub-command, groups cleared) + the kit's reload op with the admin's name
for c, m in ((ACM, "requirePermission"), (ACM, "addSubCommand"), (ACM, "setPermissionGroups"), (PR, "getUsername"), (PR, "getUuid"),
             (PR, "sendMessage")):
    B.probe(pool, c, m)
# 0.5: the Stamina Regen top-up (research/Booster-Accessories-Spec.md 5.4.1 - every call read in HytaleServer.jar bytecode), the quality
# restamp (the SkyySacks 0.7.7 calls), the admin give (addOrDropItemStack, the SkyyCooking / SkyyExploration call; the target's world
# thread: Store.isInThread + World.execute), /accessories lines (PlayerRef.hasPermission) and the raw command text (SkyyGear /gear give)
RGV = "com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue"
RGN = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating"
RGT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType"
CND = "com.hypixel.hytale.server.core.modules.entity.condition.Condition"
TMR = "com.hypixel.hytale.server.core.modules.time.TimeResource"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
for c, m in ((ESV, "getRegeneratingValues"), (RGV, "getRegenerating"), (RGN, "getRegenType"), (RGN, "getAmount"), (RGN, "getInterval"),
             (RGT, "ADDITIVE"), (CND, "allConditionsMet"), (TMR, "getResourceType"), (TMR, "getNow"), (ST, "getResource"),
             (ESV, "get"), (ESV, "getMax"), (ESM, "addStatValue"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"),
             (IS, "getQuantity"), (ITM, "getQualityIndex"), (IC, "setItemStackForSlot"), (SIC, "addOrDropItemStack"),
             (INV, "getCombinedStorageHotbarBackpack"), (ST, "isInThread"), (REF, "getStore"), (PR, "getReference"),
             (PR, "getWorldUuid"), (PR, "hasPermission"), (PR, "isValid"), (UNI, "getPlayer"), (UNI, "getWorld"), (WLD, "execute"),
             (ACM, "setAllowsExtraArguments"), (CTX, "getInputString"), (MSG, "raw"), (MSG, "color")):
    B.probe(pool, c, m)
# 0.5.1: old ids out of the creative library - the ITEM flag Variant (tools/acc_0_5_1_patch.py B): the asset field, its packet field and
# the categories packet field exist, and the Item codec's own documentation still says what the flags do in the item library
IBASE = "com.hypixel.hytale.protocol.ItemBase"
for c, m in ((ITM, "isVariant"), (ITM, "getCategories"), (IBASE, "variant"), (IBASE, "categories")):
    B.probe(pool, c, m)


def _variant_proof():
    import zipfile as _zf
    cls = _zf.ZipFile(B.SERVER_JAR).read("com/hypixel/hytale/server/core/asset/type/item/config/Item.class")
    for needle in (b"Variant", b"Categories",
                   b"If this item is marked as a variant, then we filter it out of the item library menu by default, unless the player "
                   b"chooses to display variants.",
                   b"A list of categories this item will be shown in on the creative library menu."):
        if needle not in cls:
            raise SystemExit("0.5.1: the Item codec no longer says %r - check how old ids are hidden from the creative library" % needle[:60])
    print("creative library: the Item codec documents Variant (filtered out of the item library by default) and Categories")


_variant_proof()

# 0.5.4 LANTERN - the engine members the glow and the helper use (every one B.probe'd) and the facts they rely on (_lantern_engine_proof
# reads them in HytaleServer.jar bytecode and stops the build when one changed; tools/acc_0_5_4_patch.py has the notes)
DLC = "com.hypixel.hytale.server.core.modules.entity.component.DynamicLight"
PDL = "com.hypixel.hytale.server.core.modules.entity.component.PersistentDynamicLight"
CLT = "com.hypixel.hytale.protocol.ColorLight"
TCO = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
NID = "com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId"
INT_ = "com.hypixel.hytale.server.core.modules.entity.component.Intangible"
DES = "com.hypixel.hytale.server.core.modules.entity.DespawnComponent"
DTH = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"
NSR = "com.hypixel.hytale.component.NonSerialized"
HLD = "com.hypixel.hytale.component.Holder"
CRG = "com.hypixel.hytale.component.ComponentRegistry"
CTY = "com.hypixel.hytale.component.ComponentType"
RTY = "com.hypixel.hytale.component.ResourceType"
ARS = "com.hypixel.hytale.component.AddReason"
RRS = "com.hypixel.hytale.component.RemoveReason"
ESR = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
CSR = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
ARC = "com.hypixel.hytale.component.Archetype"
V3D = "org.joml.Vector3d"
COMP = "com.hypixel.hytale.component.Component"
# the fix round: the reach light is the wearer's own (AccLanternHide edits each viewer's visible set like HideFromNonSpectators)
EVW = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer"
ETR = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems"
CVS = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$CollectVisible"
SGR = "com.hypixel.hytale.component.SystemGroup"
SDP = "com.hypixel.hytale.component.dependency.SystemDependency"
ORD = "com.hypixel.hytale.component.dependency.Order"
HPM = "com.hypixel.hytale.server.core.entity.entities.player.HiddenPlayersManager"
for c, m in ((EVW, "getComponentType"), (EVW, "visible"), (EVW, "viewRadiusBlocks"), (ETR, "FIND_VISIBLE_ENTITIES_GROUP"), (ORD, "AFTER"),
             (HPM, "isPlayerHidden"), (PR, "getHiddenPlayersManager"), (ST, "getEntityCountFor"), (ACH, "getArchetype"), (CB, "getArchetype"),
             ("com.hypixel.hytale.component.system.tick.ArchetypeTickingSystem", "tick"), ("com.hypixel.hytale.component.system.ISystem", "getGroup"),
             ("com.hypixel.hytale.component.system.ISystem", "getDependencies")):
    B.probe(pool, c, m)
for c, m in ((DLC, "getComponentType"), (DLC, "getColorLight"), (DLC, "setColorLight"), (CLT, "radius"), (CLT, "red"), (CLT, "green"),
             (CLT, "blue"), (TCO, "getComponentType"), (TCO, "getPosition"), (TCO, "setPosition"), (NID, "getComponentType"),
             (INT_, "getComponentType"), (DES, "getComponentType"), (DES, "despawnInSeconds"), (DES, "setDespawnTo"),
             (DTH, "getComponentType"), (NSR, "get"), (HLD, "addComponent"), (HLD, "ensureComponent"), (CRG, "newHolder"),
             (CRG, "getNonSerializedComponentType"), (CRG, "getNonTickingComponentType"), (ARS, "SPAWN"), (RRS, "REMOVE"),
             (ESR, "takeNextNetworkId"), (ESR, "getWorld"), (WLD, "getChunkStore"), (CSR, "getChunkSectionReference"), (CSR, "getStore"),
             (ARC, "contains"), (ST, "getArchetype"), (ST, "getRegistry"), (ST, "getExternalData"), (ST, "getResource"),
             (ST, "getComponent"), (CB, "addComponent"), (CB, "tryRemoveComponent"), (CB, "addEntity"), (CB, "tryRemoveEntity"),
             (CB, "getComponent"), (ACH, "getComponent"), (ACH, "getReferenceTo"), (REF, "isValid"), (REF, "getStore"),
             (PR, "getComponentType"), (PR, "getUuid"), (TMR, "getResourceType"), (TMR, "getNow"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (CRP, "registerComponent"), (CRP, "registerSystem")):
    B.probe(pool, c, m)


def _lantern_engine_proof():
    """0.5.4: the HytaleServer.jar facts the glow and the helper rely on (read in bytecode - a changed engine stops this build)"""
    import jpype as _jp
    IPc = _jp.JClass("javassist.bytecode.InstructionPrinter")

    def code(cls, name, desc=None):
        cc = pool.get(cls)
        out = []
        for mi in cc.getClassFile().getMethods():
            if str(mi.getName()) != name or (desc is not None and str(mi.getDescriptor()) != desc):
                continue
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            it = ca.iterator()
            while it.hasNext():
                p = it.next()
                out.append(str(IPc.instructionString(it, p, mi.getConstPool())))
        if not out:
            raise SystemExit("0.5.4: %s.%s is gone - re-check the Lantern (tools/acc_0_5_4_patch.py)" % (cls, name))
        return "\n".join(out)

    def need(cond, what):
        if not cond:
            raise SystemExit("0.5.4: the engine changed - %s; re-check the Lantern (tools/acc_0_5_4_patch.py)" % what)
    em = code("com.hypixel.hytale.server.core.modules.entity.EntityModule", "setup").split("\n")
    i_dl = [k for k, l in enumerate(em) if l.endswith("= Class " + DLC)]
    need(len(i_dl) == 1 and any("registerComponent((Ljava/lang/Class;Ljava/util/function/Supplier;)" in l for l in em[i_dl[0]:i_dl[0] + 6]),
         "DynamicLight is no longer registered WITHOUT a codec (registerComponent(Class, Supplier))")
    i_pd = [k for k, l in enumerate(em) if l.endswith("= Class " + PDL)]
    need(len(i_pd) == 1 and any("PersistentDynamicLight.CODEC" in l for l in em[i_pd[0]:i_pd[0] + 6]),
         "PersistentDynamicLight (the SAVED light) is no longer the one with the codec")
    need("CODEC" not in [str(f.getName()) for f in pool.get(DLC).getDeclaredFields()], "DynamicLight now has a CODEC field (it could be saved)")
    ini = code(DLC, "<init>", "(Lcom/hypixel/hytale/protocol/ColorLight;)V")
    need("iconst_1" in ini and "DynamicLight.isNetworkOutdated" in ini, "new DynamicLight(ColorLight) no longer marks itself for sending")
    scl = code(DLC, "setColorLight")
    need("iconst_1" in scl and "DynamicLight.isNetworkOutdated" in scl, "DynamicLight.setColorLight no longer marks the light for sending")
    dt = code("com.hypixel.hytale.server.core.modules.entity.system.EntitySystems$DynamicLightTracker", "tick")
    need("consumeNetworkOutdated" in dt and "Visible.visibleTo" in dt and "Visible.newlyVisibleTo" in dt and "queueUpdatesFor" in dt,
         "DynamicLightTracker no longer sends a light to every viewer (visibleTo) and to new viewers (newlyVisibleTo)")
    tr = code("com.hypixel.hytale.server.core.modules.entity.dynamiclight.DynamicLightSystems$EntityTrackerRemove", "onComponentRemoved",
              "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/modules/entity/component/DynamicLight;"
              "Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V")
    need("Visible.visibleTo" in tr and "EntityViewer.queueRemove" in tr and "ComponentUpdateType.DynamicLight" in tr,
         "a removed DynamicLight is no longer taken off every viewer")
    hs = code(ARC, "hasSerializableComponents")
    need("getNonSerializedComponentType" in hs and "Archetype.contains" in hs, "NonSerialized no longer makes an archetype unsaveable")
    for cn, mn in (("com.hypixel.hytale.server.core.universe.world.chunk.EntityChunk", "cloneSerializable"),
                   ("com.hypixel.hytale.server.core.universe.world.storage.provider.RocksDbChunkStorageProvider$Saver", "snapshotDirtyEntityReferences")):
        need("hasSerializableComponents" in code(cn, mn), "%s.%s no longer skips entities without saveable components" % (cn, mn))
    ae = code("com.hypixel.hytale.builtin.ambience.systems.AmbientEmitterSystems$EntityRefAdded", "onEntityAdded")
    need(all(x in ae for x in ("ComponentRegistry.newHolder", "TransformComponent.clone", "EntityStore.takeNextNetworkId",
                               "NetworkId.<init>", "Holder.ensureComponent", "getNonSerializedComponentType", "NonSerialized.get",
                               "CommandBuffer.addEntity", "AddReason.SPAWN")),
         "the vanilla helper-entity pattern (ambient emitters: Transform + NetworkId + Intangible + NonSerialized via the CommandBuffer) changed")
    ns = code("com.hypixel.hytale.server.core.modules.entity.system.NetworkSendableSpatialSystem", "<clinit>")
    need("TransformComponent.getComponentType" in ns and "NetworkId.getComponentType" in ns and "Archetype.of" in ns,
         "entities sent to clients are no longer exactly those with a TransformComponent and a NetworkId")
    cv = code("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$CollectVisible", "tick")
    need("EntityViewer.viewRadiusBlocks" in cv and "SpatialStructure.collect" in cv, "visibility is no longer the viewer's radius in blocks")
    # the fix round - THE REACH LIGHT IS THE WEARER'S OWN: each tick ClearEntityViewers empties every viewer's visible set (BEFORE the
    # find-visible group), CollectVisible fills it (in the group), the vanilla HideFromPlayer / HideFromNonSpectators take entries out (in
    # the group, AFTER CollectVisible - AccLanternHide does the same), and only AFTER the group ClearPreviouslyVisible -> EnsureVisibleComponent
    # -> AddToVisible turn what is left into Visible.visibleTo / newlyVisibleTo, the only viewers the light, the moves and the entity go to
    T_ = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$"
    need("EntityViewer.visible" in cv and "Set.addAll" in cv and
         code(T_ + "CollectVisible", "getGroup").count("FIND_VISIBLE_ENTITIES_GROUP") == 1, "CollectVisible no longer fills the visible set in the find-visible group")
    ce = code(T_ + "ClearEntityViewers", "<clinit>")
    need("SystemGroupDependency.<init>" in ce and "Order.BEFORE" in ce and "FIND_VISIBLE_ENTITIES_GROUP" in ce and
         "EntityViewer.visible" in code(T_ + "ClearEntityViewers", "tick") and "Set.clear" in code(T_ + "ClearEntityViewers", "tick"),
         "the visible sets are no longer emptied BEFORE the find-visible group every tick")
    cp_ = code(T_ + "ClearPreviouslyVisible", "<clinit>")
    need("SystemGroupDependency.<init>" in cp_ and "Order.AFTER" in cp_ and "FIND_VISIBLE_ENTITIES_GROUP" in cp_,
         "ClearPreviouslyVisible no longer runs AFTER the find-visible group")
    need("Order.AFTER" in code(T_ + "EnsureVisibleComponent", "<clinit>") and "ClearPreviouslyVisible" in code(T_ + "EnsureVisibleComponent", "<clinit>")
         and "Order.AFTER" in code(T_ + "AddToVisible", "<clinit>") and "EnsureVisibleComponent" in code(T_ + "AddToVisible", "<clinit>"),
         "EnsureVisibleComponent / AddToVisible no longer follow ClearPreviouslyVisible")
    at_ = code(T_ + "AddToVisible", "tick")
    need("EntityViewer.visible" in at_ and "Visible.addViewerParallel" in at_, "AddToVisible no longer turns the visible set into Visible.visibleTo")
    hp_i, hp_t = code(T_ + "HideFromPlayer", "<init>"), code(T_ + "HideFromPlayer", "tick")
    need("Order.AFTER" in hp_i and "EntityTrackerSystems$CollectVisible" in hp_i and "FIND_VISIBLE_ENTITIES_GROUP" in code(T_ + "HideFromPlayer", "getGroup")
         and "EntityViewer.visible" in hp_t and "Iterator.remove" in hp_t and "HiddenPlayersManager.isPlayerHidden" in hp_t,
         "the vanilla HideFromPlayer no longer takes hidden players out of the visible set in the find-visible group after CollectVisible")
    hs_ = code("com.hypixel.hytale.server.core.modules.entity.spectator.SpectatorSystems$HideFromNonSpectators", "tick",
               "(FILcom/hypixel/hytale/component/Store;)V")
    need("Store.getEntityCountFor" in hs_ and "EntityTickingSystem.tick" in hs_,
         "the vanilla HideFromNonSpectators no longer skips a world without spectators (getEntityCountFor, then super.tick)")
    tu_ = code("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate", "tick")
    need("Visible.visibleTo" in tu_ and "Visible.newlyVisibleTo" in tu_ and "PositionUtil.equals" in tu_,
         "a move is no longer sent only to the viewers that see the entity (Visible.visibleTo / newlyVisibleTo)")
    sd_ = code(T_ + "SendPackets", "tick")
    need("EntityViewer.sent" in sd_ and "Set.contains" in sd_ and "EntityUpdates.removed" in sd_,
         "an entity that left a viewer's visible set is no longer removed on that client (SendPackets)")
    need(any(str(k.getSignature()) == "(Lcom/hypixel/hytale/component/dependency/Order;Ljava/lang/Class;)V" for k in pool.get(SDP).getConstructors()),
         "new SystemDependency(Order, Class) is gone")
    lc = code("com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$LODCull", "tick")
    need("BoundingBox" in lc and "getMaximumThickness" in lc, "the LOD cull no longer needs a BoundingBox (a helper could be culled)")
    ts = code("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate", "tick")
    need("getSentTransform" in ts and "PositionUtil.equals" in ts and "queueUpdatesFor" in ts, "a moved entity is no longer re-sent")
    ul = code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "updateLocation")
    need("-32.0" in ul and "ChunkUtil.chunkCoordinate" in ul and "getChunkSectionReference" in ul and "isn't currently loaded" in ul,
         "entities are no longer put into sections by chunkCoordinate (or the below-the-world / unloaded rules changed)")
    need("can't be loaded! Removing!" in code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "handleInvalidChunk"),
         "an entity in a section that cannot load is no longer removed")
    ue = code("com.hypixel.hytale.server.core.modules.entity.system.UpdateLocationSystems", "updateEntityInChunk")
    need("getNonTickingComponentType" in ue and "removeEntity" in ue and "addEntityHolder" in ue,
         "an entity moved into a non-ticking section is no longer parked (removeEntity + addEntityHolder)")
    ds = code("com.hypixel.hytale.server.core.modules.entity.DespawnSystem", "tick")
    need("TimeResource.getNow" in ds and "Instant.isAfter" in ds and "removeEntity" in ds, "DespawnSystem no longer removes an entity after its time")
    dq = code("com.hypixel.hytale.server.core.modules.entity.DespawnSystem", "<init>")
    need("Interactable.getComponentType" in dq and "Query.not" in dq, "DespawnSystem's query is no longer Despawn and not Interactable")
    rs = code("com.hypixel.hytale.server.core.modules.entity.damage.RespawnSystems$OnRespawnSystem", "componentType")
    need("DeathComponent.getComponentType" in rs, "a respawn is no longer the DeathComponent going away")
    ad = code(CB, "addEntity", "(Lcom/hypixel/hytale/component/Holder;Lcom/hypixel/hytale/component/AddReason;)Lcom/hypixel/hytale/component/Ref;")
    need("Ref.<init>((Lcom/hypixel/hytale/component/Store;)V)" in ad, "CommandBuffer.addEntity no longer hands back the (pending) Ref it adds")
    rv = code(REF, "isValid", "()Z")
    need("Ref.index" in rv and "-2147483648" in rv, "Ref.isValid is no longer index != MIN_VALUE")
    for cn in (PR, "com.hypixel.hytale.server.core.modules.entity.component.Intangible", NID, DES, DTH):
        need(COMP in [str(i.getName()) for i in pool.get(cn).getInterfaces()], "%s is no longer an entity component" % cn)
    cu = pool.get("com.hypixel.hytale.math.util.ChunkUtil")
    need(int(cu.getField("HEIGHT").getConstantValue()) == 320 and int(cu.getField("SIZE").getConstantValue()) == 32 and
         int(cu.getField("HEIGHT_SECTIONS").getConstantValue()) == 10, "the world is no longer 320 high in 10 sections of 32")
    need(int(pool.get(CLT).getField("FIXED_BLOCK_SIZE").getConstantValue()) == 4, "ColorLight is no longer 4 bytes")
    print("lantern: engine facts read - DynamicLight has no codec (never saved) and reaches every viewer, removal is sent; NonSerialized "
          "entities are never saved; the ambient-emitter helper pattern; Transform + NetworkId = sent; no BoundingBox = never LOD-culled; "
          "moves re-sent; sections 0-9 x 32 (unloaded / non-ticking sections refuse entities); DespawnSystem; respawn = DeathComponent removed; "
          "the visible set is rebuilt every tick and edited in the find-visible group after CollectVisible (HideFromPlayer / "
          "HideFromNonSpectators), then becomes Visible.visibleTo - the only viewers a light, a move or the entity itself is sent to")


_lantern_engine_proof()

PKG = "com.skyy.accessories"
dfs  = pool.makeClass(PKG + ".AccDefs")
st_  = pool.makeClass(PKG + ".AccStore")
fn   = pool.makeClass(PKG + ".AccFn")
page = pool.makeClass(PKG + ".AccPage", pool.get(PAGE))
fac  = pool.makeClass(PKG + ".AccPageFactory")
cmd  = pool.makeClass(PKG + ".AccCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".AccTick")
eff  = pool.makeClass(PKG + ".AccEffects", pool.get(ETS))
mvs_ = pool.makeClass(PKG + ".MoveSync")   # 0.3: shared movement protocol
pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))
cfg_ = pool.makeClass(PKG + ".AccCfg")                         # 0.4.4: config.properties loader + the kit's hooks
rcmd = pool.makeClass(PKG + ".AccReloadCmd", pool.get(APC))    # 0.4.4: /charms reload (server admins only)
lcmd = pool.makeClass(PKG + ".AccLinesCmd", pool.get(APC))     # 0.5: /charms lines (every player)
gcmd = pool.makeClass(PKG + ".AccGiveCmd", pool.get(APC))      # 0.5: /charms give (server admins only)
tcmd = pool.makeClass(PKG + ".AccGiveTierCmd", pool.get(APC))  # 0.5: /charms givetier (server admins only)
adm  = pool.makeClass(PKG + ".AccAdmin")                         # 0.5: the give helpers (argument text, player lookup, acc:fn:give)
gtk  = pool.makeClass(PKG + ".AccGiveTask")                      # 0.5: one give, run on the TARGET player's world thread
gfn  = pool.makeClass(PKG + ".AccGiveFn")                        # 0.5: bridge acc:fn:give
rtk  = pool.makeClass(PKG + ".AccRestampTask")                   # 0.5: the quality restamp on a player's world thread
note = pool.makeClass(PKG + ".AccNotice")                        # 0.5: the one-time chat notice per player
gear = pool.makeClass(PKG + ".AccGear")                          # 0.5 part 2: gear:extra publisher, bag page notes, bridge clean-up
lmk  = pool.makeClass(PKG + ".AccLanternMark")                   # 0.5.4: Lantern - the marker component on our helper entities
lms  = pool.makeClass(PKG + ".AccLanternMarkSup")                # 0.5.4: Lantern - its Supplier (ComponentRegistryProxy.registerComponent)
lan  = pool.makeClass(PKG + ".AccLantern")                       # 0.5.4: Lantern - the glow + the helper (state + logic)
lsys = pool.makeClass(PKG + ".AccLanternSys", pool.get(ETS))     # 0.5.4: Lantern - the system on every player (glow, helper follow)
lhs  = pool.makeClass(PKG + ".AccLanternHelp", pool.get(ETS))    # 0.5.4: Lantern - the system on our helpers (orphans removed)
lhd  = pool.makeClass(PKG + ".AccLanternHide", pool.get(ETS))    # 0.5.4: Lantern - the system on every viewer (others' helpers unseen)
kn   = pool.makeClass(PKG + ".AccKnow")                          # 0.5.6: the Lantern recipe knowledge follows SkyyCollections (Tree Sap)
ast_ = pool.makeClass(PKG + ".AccStarter")                       # 0.5.17: the starter Void Charms (one per profile, once)
# 0.5.18: craft from the bag + auto-equip (tools/accessories_0_5_18_patch.py)
C8_EES = "com.hypixel.hytale.component.system.EntityEventSystem"
C8_EVT = "com.hypixel.hytale.component.system.EcsEvent"
C8_CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
C8_MQ = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
C8_CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
C8_CRM = "com.hypixel.hytale.builtin.crafting.component.CraftingManager"
C8_BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
C8_CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
C8_PRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre"
C8_POST = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"
C8_ENS = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
acr_ = pool.makeClass(PKG + ".AccCraft")                         # 0.5.18: the Craft view's recipes, the one craft operation, auto-equip
aat_ = pool.makeClass(PKG + ".AccAutoTask")                      # 0.5.18: auto-equip after a bench / /craft craft (world-thread task)
apre = pool.makeClass(PKG + ".AccAutoPre", pool.get(C8_EES))     # 0.5.18: CraftRecipeEvent$Pre -> AccAutoTask
apst = pool.makeClass(PKG + ".AccAutoPost", pool.get(C8_EES))    # 0.5.18: CraftRecipeEvent$Post -> AccAutoTask (timed crafts)
bfn_ = pool.makeClass(PKG + ".AccBagFn")                         # 0.5.19: bridge acc:fn:bag (SkyySacks' benches + /craft use the bag)
apw_ = pool.makeClass(PKG + ".AccPower")                         # 0.5.22: Accessory Power (AP sum, the 15 Powers, the pick, the stat doors)
apf_ = pool.makeClass(PKG + ".AccPowerFn")                       # 0.5.22: bridge acc:fn:power (get / set - SkyyWardrobe loadouts)
apc_ = pool.makeClass(PKG + ".AccPowerCmd", pool.get(APC))       # 0.5.22: /charms power [name] (every player)
aho_ = pool.makeClass(PKG + ".AccHubOpen")                       # 0.5.22: the Character hub's Void Charms tab (hub:tab:character:accessories)
# 0.5.22: the kit 1.7 hub bar (HubBar.page17 rows 1 + 2, subTab, route, put / removeAll - tools/HUBS-CONTRACT.md 'Kit 1.7')
HUBB = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)
VC_HUB, VC_TAB, VC_LABEL, VC_ORDER, VC_CMD = "character", "accessories", "Void Charms", 60, "charms"
for _c, _m in (("com.hypixel.hytale.server.core.ui.ItemGridSlot", "setName"), ("com.hypixel.hytale.server.core.ui.ItemGridSlot", "setDescription"),
               ("com.hypixel.hytale.server.core.ui.ItemGridSlot", "setActivatable"), ("com.hypixel.hytale.server.core.ui.ItemGridSlot", "setItemIncompatible"),
               (PAGE, "sendUpdate"), (PAGE, "close"), (UEB, "addEventBinding"), (BT, "SlotClicking"), (UNI, "getPlayer"), (PR, "getReference"),
               (REF, "getStore"), (PLA, "getPageManager"), (IC, "removeItemStackFromSlot"), (INV, "getUtility"), (INV, "getTools"),
               ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "getCustomPage")):   # 0.5.23: isOpen
    B.probe(pool, _c, _m)
assert [(r[0], r[1], r[2]) for r in SUI.HUB_TABS if r[1] == VC_TAB] == [(VC_HUB, VC_TAB, VC_ORDER)], "0.5.22: the contract tab"
# ================= 0.5.14 SOUND PASS ROUND 2: AccSnd (pasted by tools/accessories_0_5_14_patch.py from tools/soundpass_gen.py - research/Sound-Pass-Plan.md) =================
# Vanilla sound event ids played BY ID, 2D to that player only (category UI); never throws; 0.5 s per player per sound; the per-player
# switch settings:sounds:<uuid> (Boolean FALSE on the bridge = silent; SkyyMenu 0.3.25 /settings); Skyy_SkyyAccessories/sounds.properties.
import zipfile as _sndzf, jpype as _sndjp
_SNDZ = ASSETS_ZIP   # 0.5.16: the cached copy (read-only)
SOUND_IDS = set(os.path.basename(_n)[:-5] for _n in _sndzf.ZipFile(_SNDZ).namelist() if _n.startswith("Server/Audio/SoundEvents/") and _n.endswith(".json"))
SND_SOUNDS = [["equip", "EQUIP", "Charm equipped", "SFX_Drag_Items_Gems"], ["upgrade", "UPGRADE", "Charm upgraded", "SFX_Runebinders_Lattice_Unlock_Local"]]
for _s in SND_SOUNDS:
    assert _s[3] in SOUND_IDS, "0.5.14: sound event %s is not in Assets.zip" % _s[3]
_SND_PKG = (PKG).rstrip(".")
_SND_FIELDS = [
    "public static volatile boolean ON = true;",
    "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong MUTED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong WARNS = new java.util.concurrent.atomic.AtomicLong();",
    "public static final long GAP_MS = 500L;",
    "public static final String MUTE_KEY = \"settings:sounds:\";",
    "public static java.nio.file.Path FILE;",
    "public static volatile boolean S_EQUIP = true;",
    "public static volatile String S_EQUIP_ID = \"SFX_Drag_Items_Gems\";",
    "public static volatile boolean S_UPGRADE = true;",
    "public static volatile String S_UPGRADE_ID = \"SFX_Runebinders_Lattice_Unlock_Local\";",
    "public static final String DEFAULT_TEXT = \"# SkyyAccessories sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Void Charms -> Sounds,\\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\\nsounds.enabled=true\\n# Charm equipped: A charm went into a free Void Charms slot.\\nsound.equip=true\\nsound.equip.id=SFX_Drag_Items_Gems\\n# Charm upgraded: A better charm of the same line replaced the old one in Void Charms.\\nsound.upgrade=true\\nsound.upgrade.id=SFX_Runebinders_Lattice_Unlock_Local\\n\";",
]
_SND_METHODS = [
    r'''
public static void warn(String msg) {
  WARNS.incrementAndGet();
  try { com.hypixel.hytale.logger.HytaleLogger.get("SkyyAccessories").at(java.util.logging.Level.WARNING).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}''',
    r'''
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}''',
    r'''
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Coins_Land).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}''',
    r'''
public static String check(String key, String value) {
  return err(value);
}''',
    r'''
public static boolean word(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return d;
}''',
    r'''
public static String id(int w) {
  if (!ON) return null;
  boolean on = false;
  String v = null;
  if (w == 0) { on = S_EQUIP; v = S_EQUIP_ID; }
  if (w == 1) { on = S_UPGRADE; v = S_UPGRADE_ID; }
  if (!on || v == null) return null;
  v = v.trim();
  return v.length() == 0 ? null : v;
}''',
    r'''
public static java.util.Map bridge() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    return o instanceof java.util.Map ? (java.util.Map) o : null;
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.Map b = bridge();
    if (b == null) return false;
    Object o = b.get(MUTE_KEY + u.toString());
    return (o instanceof Boolean) && !((Boolean) o).booleanValue();
  } catch (Throwable t) { return false; }
}''',
    r'''
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}''',
    r'''
public static com.hypixel.hytale.server.core.universe.PlayerRef ref(java.util.UUID u) {
  if (u == null) return null;
  try {
    com.hypixel.hytale.server.core.universe.Universe uni = com.hypixel.hytale.server.core.universe.Universe.get();
    return uni == null ? null : uni.getPlayer(u);
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean playTo(com.hypixel.hytale.server.core.universe.PlayerRef pr, int w) {
  if (pr == null) return false;
  String id = id(w);
  if (id == null) return false;
  try {
    if (!pr.isValid()) return false;
    java.util.UUID u = pr.getUuid();
    if (muted(u)) { MUTED.incrementAndGet(); return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(u) + "|" + w, System.currentTimeMillis())) return false;
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return true;
  } catch (Throwable t) {
    if (WARNED.putIfAbsent("!play", Boolean.TRUE) == null) warn("could not play a sound (logged once): " + t);
    return false;
  }
}''',
    r'''
public static boolean play(java.util.UUID u, int w) {
  if (u == null || id(w) == null) return false;
  return playTo(ref(u), w);
}''',
    r'''
public static boolean ok(java.util.UUID u, String res, int w) {
  if (res == null || !res.startsWith("+")) return false;
  return play(u, w);
}''',
    r'''
public static boolean equipped(java.util.UUID u, String res) {
  if (u == null || res == null) return false;
  return play(u, res.length() == 0 ? 0 : 1);
}''',
    r'''
public static String text() {
  int n = 0;
  if (S_EQUIP && S_EQUIP_ID != null && S_EQUIP_ID.trim().length() > 0) n++;
  if (S_UPGRADE && S_UPGRADE_ID != null && S_UPGRADE_ID.trim().length() > 0) n++;
  return "sounds " + (ON ? "on" : "off") + " (" + n + " of 2)";
}''',
    r'''
public static String load(java.nio.file.Path dir) {
  if (dir == null) return text();
  FILE = dir.resolve("sounds.properties");
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("sounds.properties.tmp");
      java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ON = word(p.getProperty("sounds.enabled"), true);
    S_EQUIP = word(p.getProperty("sound.equip"), true);
    S_EQUIP_ID = p.getProperty("sound.equip.id", "SFX_Drag_Items_Gems").trim();
    S_UPGRADE = word(p.getProperty("sound.upgrade"), true);
    S_UPGRADE_ID = p.getProperty("sound.upgrade.id", "SFX_Runebinders_Lattice_Unlock_Local").trim();
  } catch (Throwable t) { warn("could not read sounds.properties (the sounds keep their defaults): " + t); }
  return text();
}''',
]
_snd_cls = pool.makeClass(_SND_PKG + ".AccSnd")
for _src in _SND_FIELDS:
    _snd_cls.addField(_sndjp.JClass("javassist.CtField").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
for _src in _SND_METHODS:
    _snd_cls.addMethod(_sndjp.JClass("javassist.CtNewMethod").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
_snd_cls.writeFile(OUT)
print("AccSnd: 2 sound(s), every default id is in Assets.zip")

# (benchId, bench item id, display name, tiers, [upgrade materials to reach T2, T3, ...])
BENCHES = [
    ("Workbench",      "Bench_WorkBench", "Workbench",      3, [[("Ingredient_Bar_Copper", 30), ("Ingredient_Bar_Iron", 20), ("Ingredient_Fabric_Scrap_Linen", 20)],
                                                               [("Ingredient_Bar_Thorium", 30), ("Ingredient_Bar_Cobalt", 20), ("Ingredient_Leather_Heavy", 30), ("Ingredient_Fabric_Scrap_Shadoweave", 50), ("Ingredient_Fire_Essence", 25)]]),
    ("Armor_Bench",    "Bench_Armour",    "Armor Bench",    3, [[("Ingredient_Bar_Copper", 20), ("Ingredient_Bone_Fragment", 20), ("Ingredient_Leather_Medium", 20), ("Wood_Azure_Trunk", 100)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fabric_Scrap_Shadoweave", 40), ("Ingredient_Chitin_Sturdy", 40), ("Ingredient_Voidheart", 3)]]),
    ("Weapon_Bench",   "Bench_Weapon",    "Weapon Bench",   3, [[("Ingredient_Bar_Iron", 20), ("Ingredient_Leather_Light", 30), ("Ingredient_Fabric_Scrap_Linen", 30), ("Ingredient_Sac_Venom", 15)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fire_Essence", 20), ("Ingredient_Ice_Essence", 40), ("Ingredient_Void_Essence", 100)]]),
    ("Alchemybench",   "Bench_Alchemy",   "Alchemy Bench",  4, [[("Ingredient_Bar_Silver", 5), ("Ingredient_Bar_Gold", 10), ("Ingredient_Sac_Venom", 10), ("Rock_Gem_Emerald", 1)],
                                                               [("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 20), ("Ingredient_Chitin_Sturdy", 20), ("Rock_Gem_Zephyr", 1)],
                                                               [("Ingredient_Bar_Silver", 20), ("Ingredient_Bar_Gold", 40), ("Ingredient_Fabric_Scrap_Shadoweave", 30), ("Rock_Gem_Sapphire", 1)]]),
    ("Farmingbench",   "Bench_Farming",   "Farming Bench",  7, [[("Ingredient_Life_Essence", 50), ("Plant_Crop_Wheat_Item", 5), ("Plant_Crop_Lettuce_Item", 5), ("Wood_Softwood_Trunk", 5)],
                                                               [("Ingredient_Life_Essence_Concentrated", 1), ("Plant_Crop_Carrot_Item", 10), ("Plant_Crop_Corn_Item", 10), ("Wood_Lightwood_Trunk", 10)],
                                                               [("Ingredient_Life_Essence_Concentrated", 2), ("Plant_Crop_Cauliflower_Item", 20), ("Plant_Crop_Turnip_Item", 20), ("Wood_Hardwood_Trunk", 20)],
                                                               [("Ingredient_Life_Essence_Concentrated", 3), ("Plant_Crop_Aubergine_Item", 30), ("Plant_Crop_Pumpkin_Item", 30), ("Wood_Drywood_Trunk", 30)],
                                                               [("Ingredient_Life_Essence_Concentrated", 4), ("Plant_Crop_Tomato_Item", 40), ("Plant_Crop_Chilli_Item", 40), ("Wood_Darkwood_Trunk", 40)],
                                                               [("Ingredient_Life_Essence_Concentrated", 5), ("Plant_Crop_Cotton_Item", 50), ("Plant_Crop_Rice_Item", 50), ("Wood_Redwood_Trunk", 50)]]),
    ("Furnace",        "Bench_Furnace",   "Furnace",        2, [[("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 5), ("Ingredient_Bar_Thorium", 5), ("Ingredient_Bar_Cobalt", 5)]]),
    ("Tannery",        "Bench_Tannery",   "Tannery",        2, [[("Ingredient_Leather_Light", 5), ("Ingredient_Leather_Medium", 5), ("Ingredient_Leather_Heavy", 5), ("Ingredient_Chitin_Sturdy", 5)]]),
    ("Arcanebench",    "Bench_Arcane",    "Arcane Bench",   1, []),
    ("Cookingbench",   "Bench_Cooking",   "Cooking Bench",  1, []),
    ("Furniture_Bench","Bench_Furniture", "Furniture Bench",1, []),
    ("Loombench",      "Bench_Loom",      "Loom",           1, []),
    ("Salvagebench",   "Bench_Salvage",   "Salvage Bench",  1, []),
    ("Campfire",       "Bench_Campfire",  "Campfire",       1, []),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
# 0.4.2 RETIRED bench accessories (Smithing-Smelting spec section 6). Their rows stay in BENCHES so the item assets are still generated
# (owned copies stay valid items), but they get no recipe, Equip refuses them, acc:has / acc:fn:has leave them out, the Omni does not
# cover them and they never count for rarity/power. AccDefs.retiredWhy / retiredChat name these two ids literally - keep them in sync.
# 0.4.3: the Campfire is NOT retired any more (Skyy 2026-09-24: quick inventory cooking at 50% Cooking XP and 75% of the cooking
# bonus - SkyyCooking 0.1.1 cook:fn:campfire, called by SkyySacks' /craft page). It is an ordinary ACTIVE bench accessory again.
RETIRED = ["Alchemybench", "Cookingbench"]
assert RETIRED == ["Alchemybench", "Cookingbench"], "AccDefs.retiredWhy / retiredChat and RETIRED_DESC name these literally"
ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]
assert all(any(b[0] == r for b in BENCHES) for r in RETIRED), RETIRED
assert len(ACTIVE) == len(BENCHES) - len(RETIRED) == 11, [b[0] for b in ACTIVE]
assert [b[3] for b in ACTIVE if b[0] == "Campfire"] == [1], "0.4.3: the Campfire must be an active single-tier bench"
RETIRED_NAMES = [[b[2] for b in BENCHES if b[0] == r][0] for r in RETIRED]
RETIRED_MAX = [[b[3] for b in BENCHES if b[0] == r][0] for r in RETIRED]   # tier count per retired bench (pretty: numeral only if > 1)
assert RETIRED_MAX == [4, 1], RETIRED_MAX
# 0.4.3 Campfire accessory description (Skyy's call, orchestrator wording). The two numbers are SkyyCooking's defaults
# campfire.xpFactor / campfire.buffFactor (cook:fn:campfire applies the real, configurable factors) - checked against the newest
# SkyyCooking build script when it is present, so the tooltip cannot drift from those defaults.
# 0.4.3 review fix: a server can change the real factors in cooking.properties, so the text calls them the defaults and points at the
# Accessory Bag page, whose status line shows the LIVE factors (AccStore.campLine); AccStore.campCheck logs a mismatch once.
CAMP_XP_PCT, CAMP_BUFF_PCT = 25, 75   # 0.5.1: SkyyCooking 0.1.3 halves the campfire XP share (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01)
CAMPFIRE_DESC = ("Quick inventory cooking: campfire dishes in /craft at %d%% Cooking XP and %d%% of your cooking bonus by default (your "
                 "Void Charms page shows this server's numbers). Put it in your Void Charms and /craft cooks the Campfire recipes "
                 "straight from your inventory - an emergency cook; a Cooking Bench gives the full bonus and XP.") % (CAMP_XP_PCT, CAMP_BUFF_PCT)
assert CAMPFIRE_DESC.startswith("Quick inventory cooking: campfire dishes in /craft at 25% Cooking XP and 75% of your cooking bonus by default"), CAMPFIRE_DESC
def _camp_defaults_check():
    import re, glob
    def _v(p):
        m = re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyCooking", "build_skyycooking_*.py")), key=_v)
    if not found:
        print("note: no SkyyCooking build script next to this mod - Campfire description numbers not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    m = re.search(r"^CAMP_BUFF_DEF, CAMP_XP_DEF = ([0-9.]+), ([0-9.]+)", txt, re.M)
    if not m:   # 0.4.3 review fix: SkyyCooking IS here but changed shape - fail instead of silently skipping the check
        raise SystemExit("0.4.3: %s has no 'CAMP_BUFF_DEF, CAMP_XP_DEF = <buff>, <xp>' line any more - find SkyyCooking's campfire "
                         "defaults, update CAMP_*_PCT and this check (tools/acc_0_4_3_patch.py)" % os.path.basename(found[-1]))
    # 0.4.3 review fix: the bag page / log read the LIVE factors from cook:fn:campfactors - the SkyyCooking build must still publish it
    if 'b.put("cook:fn:campfactors"' not in txt or "Double buffFactor, Double xpFactor, Boolean enabled" not in txt:
        raise SystemExit("0.4.3: %s no longer publishes cook:fn:campfactors -> Object[]{Double buffFactor, Double xpFactor, Boolean "
                         "enabled} - update AccStore.campFactors and this check (tools/acc_0_4_3_patch.py)" % os.path.basename(found[-1]))
    buff, xp = int(round(float(m.group(1)) * 100)), int(round(float(m.group(2)) * 100))
    if (buff, xp) != (CAMP_BUFF_PCT, CAMP_XP_PCT):
        raise SystemExit("0.4.3: %s defaults are buff %d%% / XP %d%% but the Campfire accessory text says %d%% / %d%% - update CAMP_*_PCT"
                         % (os.path.basename(found[-1]), buff, xp, CAMP_BUFF_PCT, CAMP_XP_PCT))
    print("campfire accessory text matches %s defaults (XP %d%%, bonus %d%%)" % (os.path.basename(found[-1]), xp, buff))
_camp_defaults_check()
BAG = "Skyy_Accessory_Bag"
OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni"); 0.5: Legendary (crafted, never Mythic)
# ---- 0.5.3 NIGHT VISION, RETIRED in 0.5.4 (tools/acc_0_5_4_patch.py; Skyy 2026-10-03: "forget night vision, just do the lantern"):
# the id stays a valid item (owned copies load, look and read), but like the 0.4.2 bench accessories it does nothing, Equip refuses it,
# Unequip takes it out, it never counts, and it is out of lines / givetier / give / acc:defs and the creative library
NV_ID = "Skyy_Talisman_NightVision_Rare"
NV_ADMIN = "NightVision"                    # the old /charms givetier name (now answered with "retired - use Lantern")
NV_LINE = "Night Vision"
NV_TIER = 3                                 # its id word (Rare): the frame keeps the Rare quality, rarityOf is 0 (retired)
NV_LOOK = "Ingredient_Lightning_Essence"    # the vanilla item whose model, texture and icon it copies (unchanged)
NV_WHY = "Retired - the Lantern Accessory replaced it - craft one in the Craft tab of Void Charms"   # 0.5.21: crafted in the bag only
NV_CHAT = ("The Night Vision Accessory is retired: the Lantern Accessory replaced it (craft one in the Craft tab of your Void Charms, /charms lines shows "
           "it). This accessory does nothing any more and cannot be equipped. If one is still in your Void Charms, Unequip takes it out.")
NV_ROW = "retired - take it out"            # the bag page row while one is still in the bag (its slot row says "- retired")
NV_GIVE = "Night Vision is retired - the Lantern replaced it: /charms givetier <player> Lantern <rarity>"
assert all(ord(_c) < 128 for _t in (NV_WHY, NV_CHAT, NV_ROW, NV_GIVE) for _c in _t) and not any(_c in NV_WHY for _c in ",:()")
# ---- 0.5.4 THE LANTERN LINE (tools/acc_0_5_4_patch.py): four rarities of its own line, crafted from the rarity below. Not a booster-table
# row (those carry stat numbers): it gives no stat, it lights the wearer (a DynamicLight component) and, from Unique up, a hidden helper
# entity above them. Word ids (the folded lines' Common / Uncommon / Rare / Epic) so the shared Workbench tab rank files each one into its
# rarity tier; the stat rules give them their rarity (tierOf), group T:Lantern (one per bag, a higher one swaps a lower one out), and
# bestTiers skips them (no booster family).
LAN_FAM = "Lantern"                         # the family key in the ids
LAN_ADMIN = "Lantern"                       # config / commands / acc:defs (/charms givetier <player> Lantern Rare)
LAN_LINE = "Lantern"                        # what players see: "<Rarity> Lantern Accessory", the bag page row "Lantern"
LAN_IDS = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_Lantern_Epic"]
LAN_SRC = "Craft"                           # acc:defs source word of every rarity
# the look of each rarity: a vanilla lantern's block model + texture + icon (the vanilla Weapon_Deployable_Slowness_Totem carries a block
# model on a plain item the same way); names Lantern / Kweebec Lantern / Sandswept Lantern / Light Temple Lantern
LAN_LOOKS = ["Deco_Lantern", "Furniture_Kweebec_Lantern", "Furniture_Desert_Lantern", "Furniture_Temple_Light_Lantern"]
# the recipes at the Workbench tab: [Normal inputs, Unique extra, Rare extra, Legendary extra] - each upgrade also takes the rarity below
LAN_RECIPES = [
    [("Furniture_Crude_Torch", 4), ("Ingredient_Bar_Copper", 2)],   # 0.5.16: no Deco_Lantern (Skyy 2026-10-15)
    [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Bar_Copper", 4), ("Ingredient_Tree_Sap", 5)],
    [("Rock_Gem_Topaz", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Fire_Essence", 5)],
    [("Rock_Gem_Topaz", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Fire_Essence", 15)],
]
LAN_FLAVOUR = "It never needs oil, and it never goes out."
# THE LIGHT. The vanilla torch players craft (Furniture_Crude_Torch "Crude Torch") and its wall form carry BlockType Light {Radius 0,
# Color "#ba9"}: a "#RGB" colour is one hex digit per channel (0-15, ColorParseUtil.hexStringToColorLightDirect; the harness runs the
# engine's parser on it), so the torch = levels 11 / 10 / 9. _torch_proof below reads both items from Assets.zip.
TORCH_ITEMS = ["Furniture_Crude_Torch", "Wood_Torch_Wall"]
TORCH_HEX = "#ba9"
TORCH_RGB = (11, 10, 9)
LAN_TORCH = 11                              # the torch's level (its brightest channel)
LAN_SIG_R = 1                               # our lights carry radius byte 1: max(channel, 1) = channel for channels >= 1 (no visible change)
LAN_VIS = 0.05                              # "lit" = at least 5% light (walls at 15%): the reach is measured at the wearer's feet level
LAN_PZ = 3.0                                # the wearer's own particles: up to 3 blocks above the feet
LAN_PD = 0.3                                # the glow at its brightest for particles (dust at the feet, 0.3 blocks from the light)
LAN_MINH = 5                                # a helper with less room than this above the feet is not used
LAN_TOP, LAN_BOTTOM = 318.0, 1.0            # inside the world (ChunkUtil.HEIGHT 320, sections 0-9 x 32 - proven in _lantern_engine_proof)
LAN_DESPAWN = 5.0                           # the helper's DespawnComponent: removed 5 s after we last refreshed it (refreshed every tick)
LAN_EPS = 1.0e-6                            # height margin: (feet + 123) - feet can be 122.99999999999999 (review finding 4)
LAN_VIEW_MARGIN = 4                         # the helper stays this far inside the wearer's view radius (CollectVisible's radius)
LAN_MOVE_DIV, LAN_MOVE_MIN, LAN_MOVE_MAX = 50.0, 0.1, 1.5   # moved when off its spot by height / 50 blocks, 0.1 - 1.5 (finding 3)
LAN_RARITIES = ["Normal", "Unique", "Rare", "Legendary"]
LAN_SWITCH = "line.Lantern"
LAN_SHARE_KEY = "lantern.shareReach"        # fix round: off = the reach light is the wearer's own (AccLanternHide); on = everyone sees it
# 0.5.5 (tools/acc_0_5_5_patch.py): + lantern.edge (the brightest a hidden light may be) and lantern.lights (the most hidden lights per
# wearer); lantern.height 128 -> 64 (Skyy 2026-10-04: "2, try to smooth the edges")
LAN_KEYS = (["lantern.glow.%s" % _r for _r in LAN_RARITIES] + ["lantern.reach.%s" % _r for _r in LAN_RARITIES] + ["lantern.height",
            "lantern.edge", "lantern.lights"])
LAN_FIELDS = ["LAN_GLOW1", "LAN_GLOW2", "LAN_GLOW3", "LAN_GLOW4", "LAN_REACH1", "LAN_REACH2", "LAN_REACH3", "LAN_REACH4", "LAN_HEIGHT",
              "LAN_EDGE", "LAN_LIGHTS"]
LAN_DEF = [11, 11, 11, 11, 10, 18, 32, 64, 64, 96, 8]   # 0.5.18: reach 6 / 12 / 24 / 48 -> 10 / 18 / 32 / 64, lights 7 -> 8 (Skyy 2026-10-15)
LAN_DEF_055 = [11, 11, 11, 11, 6, 12, 24, 48, 64, 96, 7]   # 0.5.5 - 0.5.17 (migrate0518 rewrites lines still holding these)
LAN_MIN = [0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 1]
LAN_MAX = [15, 15, 15, 15, 64, 64, 64, 64, 160, 255, 9]
assert len(LAN_KEYS) == len(LAN_FIELDS) == len(LAN_DEF) == len(LAN_MIN) == len(LAN_MAX) == 11
LAN_RING_MAX = 8                            # 0.5.5: at most 8 ring lights around the light above (lantern.lights max 9)
assert LAN_MAX[10] == LAN_RING_MAX + 1
# 0.5.5: the one-time lantern.height update (AccCfg.migrate055; the 0.5.1 migrate051 rules) - its marker is a doc comment (no '='), in
# the default text and in every updated file; looked for in comment lines only
M55_KEY, M55_OLD, M55_NEW = "lantern.height", "128", str(LAN_DEF[8])
M55_MARK_ID = "SkyyAccessories 0.5.5 Lantern defaults"
M55_MARK = ("# %s (Skyy 2026-10-04, smooth the edges): the hidden lights go at most 64 blocks up (0.5.4: 128) and are "
            "softer." % M55_MARK_ID)
M55_WHO = "SkyyAccessories 0.5.5"
assert M55_NEW == "64" and all(32 <= ord(_c) < 127 for _c in M55_MARK) and "=" not in M55_MARK and M55_MARK.startswith("# ")
# 0.5.18: the one-time Lantern reach update (AccCfg.migrate0518; the migrate055 rules, several keys) - its marker is a doc comment too
M518_IDX = [4, 5, 6, 7, 10]                                   # lantern.reach.Normal .. Legendary, lantern.lights
M518_KEYS = [LAN_KEYS[_i] for _i in M518_IDX]
M518_OLD = [str(LAN_DEF_055[_i]) for _i in M518_IDX]
M518_NEW = [str(LAN_DEF[_i]) for _i in M518_IDX]
M518_MARK_ID = "SkyyAccessories 0.5.18 Lantern reach"
M518_MARK = ("# %s (Skyy 2026-10-15, light a bigger area): reach 10 / 18 / 32 / 64 blocks (0.5.5: 6 / 12 / 24 / 48), up to 8 hidden "
             "lights." % M518_MARK_ID)
M518_WHO = "SkyyAccessories 0.5.18"
assert M518_KEYS == ["lantern.reach.Normal", "lantern.reach.Unique", "lantern.reach.Rare", "lantern.reach.Legendary", "lantern.lights"]
assert (M518_OLD, M518_NEW) == (["6", "12", "24", "48", "7"], ["10", "18", "32", "64", "8"]), (M518_OLD, M518_NEW)
assert all(32 <= ord(_c) < 127 for _c in M518_MARK) and "=" not in M518_MARK and M518_MARK.startswith("# ") and M55_MARK_ID not in M518_MARK
assert [_d for _i, _d in enumerate(LAN_DEF) if _i not in M518_IDX] == [_d for _i, _d in enumerate(LAN_DEF_055) if _i not in M518_IDX]
assert all(_lo <= _d <= _hi for _lo, _d, _hi in zip(LAN_MIN, LAN_DEF, LAN_MAX)) and LAN_DEF[:4] == [LAN_TORCH] * 4
LAN_ON_OFF = "switched off"
# the default file's Lantern part (a fresh install; an existing file is never rewritten - a missing key = its default). No '=' or key-colon
# in the comments: the config kit uncomments '#key=value' template lines.
LAN_CONFIG_LINES = [
    "# Lantern Accessory (0.5.18): while it sits in a player's Void Charms, that player glows like a torch (everyone sees it), and",
    "# hidden lights above them that only they see light farther - around them it stays about as bright as their glow. Set",
    "# line.Lantern to false to switch it off for everyone. lantern.glow.<rarity> is the light level on the wearer, 0-15 (11 is a torch,",
    "# 15 the brightest vanilla light, 0 no glow). lantern.reach.<rarity> is how many blocks around the wearer are lit, 0-64 (a torch",
    "# lights about 6). lantern.height is the highest a hidden light may go above the wearer, 8-160 blocks (they sit as low as the reach",
    "# allows). lantern.edge is the brightest a hidden light may be, 8-255: lower gives a softer far edge and needs more lights.",
    "# lantern.lights is the most hidden lights per wearer, 1-9: 1-3 give one light above the wearer (as in 0.5.4; a ring needs 3",
    "# more), 4-9 give that light + a ring of 3-8 around it. lantern.shareReach true shows the hidden lights to everyone near the wearer too",
    "# (their bits near them can glow brightly).",
    M55_MARK,
    M518_MARK,
    "%s=true" % LAN_SWITCH] + ["%s=%d" % kv for kv in zip(LAN_KEYS, LAN_DEF)] + ["%s=false" % LAN_SHARE_KEY]
# the Server Setup rows (category "lantern"; tools/CONFIG-CONTRACT.md row tuple)
LAN_ROWS = [
    (LAN_SWITCH, "Lantern line", "lantern", "bool", "true", "", "", "", "", "live",
     "Off = Lanterns light nothing for anyone; every Lantern light goes out within a second.",
     "field:AccDefs.LINE_LANTERN@config.properties:%s" % LAN_SWITCH)] + [
    (LAN_KEYS[_i], "%s: glow" % LAN_RARITIES[_i], "lantern", "int", str(LAN_DEF[_i]), str(LAN_MIN[_i]), str(LAN_MAX[_i]), "step=1", "",
     "live", "Light level on the wearer. 11 = a torch, 15 = the brightest vanilla light, 0 = none.",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[_i], LAN_KEYS[_i])) for _i in range(4)] + [
    (LAN_KEYS[4 + _i], "%s: reach" % LAN_RARITIES[_i], "lantern", "int", str(LAN_DEF[4 + _i]), str(LAN_MIN[4 + _i]), str(LAN_MAX[4 + _i]),
     "step=1", "blocks", "live", "Blocks lit around the wearer (a torch = 6); a hidden light only they see adds the rest.",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[4 + _i], LAN_KEYS[4 + _i])) for _i in range(4)] + [
    (LAN_KEYS[8], "Hidden light: highest", "lantern", "int", str(LAN_DEF[8]), str(LAN_MIN[8]), str(LAN_MAX[8]), "step=1", "blocks",
     "live,adv", "They sit as low as the reach allows, never higher than this (or the wearer's view distance).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[8], LAN_KEYS[8])),
    (LAN_KEYS[9], "Hidden lights: brightest", "lantern", "int", str(LAN_DEF[9]), str(LAN_MIN[9]), str(LAN_MAX[9]), "step=1", "",
     "live,adv", "Lower = a softer far edge; long reaches then use more hidden lights. 255 = one big light (0.5.4).",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[9], LAN_KEYS[9])),
    (LAN_KEYS[10], "Hidden lights: most", "lantern", "int", str(LAN_DEF[10]), str(LAN_MIN[10]), str(LAN_MAX[10]), "step=1", "",
     "live,adv", "1-3 = one light above the wearer; 4-9 = that light + a ring of 3-8 lights around it.",
     "field:AccDefs.%s@config.properties:%s" % (LAN_FIELDS[10], LAN_KEYS[10])),
    (LAN_SHARE_KEY, "Others see the reach light", "lantern", "bool", "false", "", "", "", "", "live,adv",
     "On = players near a wearer see the hidden light too (their bits near it can glow brightly).",
     "field:AccDefs.LAN_SHARE@config.properties:%s" % LAN_SHARE_KEY)]
assert all(ord(_c) < 128 for _t in LAN_CONFIG_LINES + [LAN_FLAVOUR] for _c in _t)
assert not any("=" in _l for _l in LAN_CONFIG_LINES if _l.startswith("#")), "no template-looking comment lines"
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in LAN_ROWS), [_r[0] for _r in LAN_ROWS if len(_r[1]) > 40 or len(_r[10]) > 100]
assert len(LAN_ROWS) == 13 and LAN_CONFIG_LINES[-1] == "lantern.shareReach=false" and M55_MARK in LAN_CONFIG_LINES
assert LAN_CONFIG_LINES.index(M518_MARK) == LAN_CONFIG_LINES.index(M55_MARK) + 1 < LAN_CONFIG_LINES.index("lantern.reach.Normal=10")

# 0.5.10: THE MINING HELMET LIGHT (tools/accessories_0_5_10_patch.py) - lantern.helmet: SkyyGear's gear:lamp:<uuid> (1-4) lights the wearer
# like a Lantern of that rarity (the stronger of helmet / bag Lantern wins). Independent of line.Lantern. A missing key = on.
LAN_HELMET_KEY = "lantern.helmet"
LAN_HELMET_LINES = [
    "# Mining helmet light (0.5.10): while a player wears an active SkyyGear mining helmet, they glow like a Lantern of the helmet's",
    "# strength (Copper Normal, Iron and Thorium Unique, Cobalt and Adamantite Rare, Mithril and Onyxium Legendary); with a Lantern in",
    "# the Void Charms too, the stronger one lights them (never both). Set lantern.helmet to false to switch helmet lights off.",
    "%s=true" % LAN_HELMET_KEY]
LAN_HELMET_ROW = (LAN_HELMET_KEY, "Mining helmet light", "lantern", "bool", "true", "", "", "", "", "live",
                  "Off = SkyyGear mining helmets light nothing (Lanterns unchanged). Gone within a second.",
                  "field:AccDefs.LAN_HELMET@config.properties:%s" % LAN_HELMET_KEY)
assert all(ord(_c) < 128 for _t in LAN_HELMET_LINES for _c in _t)
assert not any("=" in _l for _l in LAN_HELMET_LINES if _l.startswith("#"))
assert len(LAN_HELMET_ROW[1]) <= 40 and len(LAN_HELMET_ROW[10]) <= 100
# 0.5.17: THE STARTER ACCESSORY BAG (tools/accessories_0_5_17_patch.py) - starter.bag: every profile gets ONE Accessory Bag item once. A
# missing key = on (the 0.5.10 lantern.helmet rule: an existing file keeps its bytes, the kit writes the line the first time it is edited).
STARTER_KEY = "starter.bag"
STARTER_LINES = [
    "# Starter Void Charms (0.5.17): every profile gets ONE Void Charms in its inventory, once - a new profile when it starts, an",
    "# older profile at its next login. A profile that already holds a bag item counts as given. A full inventory is tried again",
    "# every minute. Set starter.bag to false to give no bags (switching it back on later still gives them).",
    "%s=true" % STARTER_KEY]
STARTER_ROW = (STARTER_KEY, "Starter Void Charms", "bag", "bool", "true", "", "", "", "", "live",
               "Every profile gets one Void Charms once: new ones at the start, older ones at the next login.",
               "field:AccDefs.STARTER@config.properties:%s" % STARTER_KEY)
STARTER_GIVE = ("[Void Charms] Your old Accessory " "Bag item is retired - your accessories are safe in Void Charms: open it from the SkyWynn Menu "
                "(Character > Void Charms) or with /charms.")   # 0.5.22: AccStarter removes the retired bag item (this is its one-time line)
STARTER_FULL = ("[Void Charms] Your inventory is full, so your free Void Charms could not be given. Make room - it is tried again "
                "every minute.")
assert all(ord(_c) < 128 for _t in STARTER_LINES + [STARTER_GIVE, STARTER_FULL] for _c in _t)
assert not any("=" in _l for _l in STARTER_LINES if _l.startswith("#"))
assert len(STARTER_ROW[1]) <= 40 and len(STARTER_ROW[10]) <= 100
# 0.5.18: CRAFT FROM THE BAG + AUTO-EQUIP (tools/accessories_0_5_18_patch.py) - two switches, a missing key = on (the starter.bag rule)
CRAFT_KEY, AUTO_KEY = "craft.bag", "craft.autoEquip"
CRAFT_LINES = [
    "# Craft in Void Charms (0.5.18): the Void Charms page has a Craft tab with every accessory recipe. Crafting there needs no bench;",
    "# materials come from the inventory, then the Void, then Void Charms itself. Set craft.bag to false to switch the tab off.",
    "%s=true" % CRAFT_KEY,
    "# Auto-equip (0.5.18): an accessory a player crafts (Void Charms page, bench or /craft) goes straight into Void Charms when it fits - a",
    "# new line, or better than the best of its line. Otherwise it stays in the inventory. Set craft.autoEquip to false to stop it.",
    "%s=true" % AUTO_KEY]
CRAFT_ROW = (CRAFT_KEY, "Craft in Void Charms", "bag", "bool", "true", "", "", "", "", "live",
             "The Void Charms Craft tab - the only place accessories are crafted (off = no accessory crafting).",   # 0.5.21
             "field:AccDefs.CRAFT@config.properties:%s" % CRAFT_KEY)
AUTO_ROW = (AUTO_KEY, "Auto-equip crafted accessories", "bag", "bool", "true", "", "", "", "", "live",
            "A crafted accessory goes into Void Charms when it is a new line or better than the one in it.",
            "field:AccDefs.AUTO@config.properties:%s" % AUTO_KEY)
assert all(ord(_c) < 128 for _t in CRAFT_LINES for _c in _t)
assert not any("=" in _l for _l in CRAFT_LINES if _l.startswith("#"))
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in (CRAFT_ROW, AUTO_ROW))
# 0.5.20: THE LIFELONG ACCESSORY BAG (tools/accessories_0_5_20_patch.py) - one switch, a missing key = on (the starter.bag rule)
LIFE_KEY = "lifelong.bag"
LIFE_LINES = [
    "# Void Charms stays with you (0.5.20): the bag item can't be dropped, stored in a container or sold, one per profile (extra copies",
    "# are removed - the accessories live with the profile, never in the item) and /accbag brings it back. Set it to false for the old rules.",
    "%s=true" % LIFE_KEY]
LIFE_ROW = (LIFE_KEY, "Void Charms stays with you", "bag", "bool", "true", "", "", "", "", "live",
            "Never dropped, stored or sold; one per profile (extras removed); /accbag brings it back.",
            "field:AccDefs.LIFELONG@config.properties:%s" % LIFE_KEY)
assert all(ord(_c) < 128 for _t in LIFE_LINES for _c in _t)
assert not any("=" in _l for _l in LIFE_LINES if _l.startswith("#"))
assert len(LIFE_ROW[1]) <= 40 and len(LIFE_ROW[10]) <= 100


# ---- the light model (research/NightVision-Glare-Research.md 1.3 / 1.4; the Java twins in AccDefs: lanLight, lanMaxLevel, lanReach,
# lanSolve - same arithmetic, same iteration counts, so the build table below and the running server agree to the last bit)
def lan_light(level, d):
    """one channel's light at distance d (blocks) from a light of this level: 0.8 C (1 - 0.1 d / C)^1.5, C = level / 15, zero past the
    client's cut-off 0.635 x level and the shader's own zero 10 C"""
    import math as _m
    if level <= 0:
        return 0.0
    c = level / 15.0
    if d < 0.0:
        d = 0.0
    if d >= 0.635 * level or d >= 10.0 * c:
        return 0.0
    x = 1.0 - 0.1 * d / c
    return 0.8 * c * x * _m.sqrt(x)


def lan_maxlevel(dist, cap):
    """the highest level 0-255 whose light at dist is not above cap (the light only grows with the level)"""
    lo, hi = 0, 255
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if lan_light(mid, dist) <= cap:
            lo = mid
        else:
            hi = mid - 1
    return lo


def lan_reach(level, h):
    """how far from the wearer (blocks, at their feet level) a light of this level h blocks above the feet still lights (>= LAN_VIS)"""
    import math as _m
    if lan_light(level, h) < LAN_VIS:
        return 0.0
    lo, hi = 0.0, 400.0
    for _i in range(50):
        m = (lo + hi) * 0.5
        if lan_light(level, _m.sqrt(h * h + m * m)) >= LAN_VIS:
            lo = m
        else:
            hi = m
    return lo


def lan_cap(glow):
    """the brightest the helper may make anything near the wearer: the wearer's own glow at its brightest (a torch when no glow)"""
    return lan_light(glow if glow > 0 else LAN_TORCH, LAN_PD)


# 0.5.5: cos(pi / M) for a ring of M lights (M 3..8) as literals, so the Java AccDefs.LAN_COS holds the very same doubles
import math as _math55
LAN_COS = [1.0, 1.0, 1.0] + [_math55.cos(_math55.pi / _m) for _m in range(3, LAN_RING_MAX + 1)]


def lan_ring_reach(level, h, m, rho):
    """0.5.5: how far the ground at the wearer's feet level is lit (>= LAN_VIS) with no dark gap, from the wearer outward in 0.25-block
    steps, by a light of this level h blocks above the wearer + m more at h, rho blocks out (angles 2 pi k / m): the worse of the walk
    toward a ring light (cos 1) and between two (cos pi / m) - the nearest light decides (same level: the nearest is the brightest).
    The Java AccDefs.lanRingReach (same arithmetic, same order)"""
    import math as _m
    hh = h * h
    worst = 400.0
    for c in (1.0, LAN_COS[m]):
        i = 0
        while i < 1600:
            x = i * 0.25
            d1 = _m.sqrt(x * x + hh)
            d2 = _m.sqrt(x * x + rho * rho - 2.0 * x * rho * c + hh)
            if lan_light(level, d1 if d1 < d2 else d2) < LAN_VIS:
                break
            i += 1
        r = 0.0 if i == 0 else (i - 1) * 0.25
        if r < worst:
            worst = r
    return worst


def lan_solve5(glow, reach, hmax, emax, nmax):
    """0.5.5: (height, level, reach reached, ring lights, ring radius in half blocks) for one rarity. First ONE light, as 0.5.4 but never
    brighter than emax: the LOWEST height whose cap-limited level reaches `reach`. Else the best of those (h0, l0) + a ring of m = 3 ..
    nmax - 1 lights (at most LAN_RING_MAX) of that level and height: the smallest m, then the smallest radius (half blocks up to 2 x
    reach) whose lan_ring_reach reaches `reach`; the best reach found when nothing does; (0, 0, the glow's own reach, 0, 0) when the glow
    alone is enough. The Java AccDefs.lanSolve"""
    own = lan_reach(glow, 0.0)
    if reach <= own + 0.5:
        return 0, 0, own, 0, 0
    cap = lan_cap(glow)
    best = (0, 0, own, 0, 0)
    for h in range(LAN_MINH, hmax + 1):
        lv = lan_maxlevel(h - LAN_PZ, cap)
        if lv > emax:
            lv = emax
        if lv <= 0:
            continue
        r = lan_reach(lv, float(h))
        if r > best[2] + 1e-9:
            best = (h, lv, r, 0, 0)
        if r >= reach:
            return h, lv, r, 0, 0
    h0, l0 = best[0], best[1]
    if h0 <= 0:
        return best
    for m in range(3, min(nmax - 1, LAN_RING_MAX) + 1):
        for p2 in range(1, 2 * reach + 1):
            r = lan_ring_reach(l0, float(h0), m, p2 * 0.5)
            if r > best[2] + 1e-9:
                best = (h0, l0, r, m, p2)
            if r >= reach:
                return h0, l0, r, m, p2
    return best


def lan_solve(glow, reach, hmax):
    """the 0.5.4 single-light solve (no level limit, one light): (height, level, reach reached)"""
    return lan_solve5(glow, reach, hmax, 255, 1)[:3]


def lan_key(level):
    """our GLOW as one int: radius byte LAN_SIG_R, then the torch tint at that level (red = level, green / blue = 10 / 11 and 9 / 11 of
    it, rounded) - the Java AccDefs.lanKey (the light ON the player: near the player every channel is fully lit, so the tint is the
    vanilla torch's warm fall-off)"""
    r = 1 if level < 1 else (255 if level > 255 else level)
    g, b = max(1, (r * 10 + 5) // 11), max(1, (r * 9 + 5) // 11)
    return (LAN_SIG_R << 24) | (r << 16) | (g << 8) | b


def lan_hkey(level):
    """the HELPER's light as one int: radius byte LAN_SIG_R, then red = green = blue = the level - the Java AccDefs.lanHKey. White because
    the client fades every channel on its own (LightCluster getChannelLightNEW(distance, Color.r / .g / .b): zero at 10 x channel / 15
    blocks): a torch-tinted helper 123 blocks up would light the ground with red only (review finding 1)"""
    lv = 1 if level < 1 else (255 if level > 255 else level)
    return (LAN_SIG_R << 24) | (lv << 16) | (lv << 8) | lv


def lan_rgb(key, d):
    """the client's light of each channel at d blocks from a light with this key - what the ground under a helper gets: per channel
    E = max(channel, radius byte), the light skipped past 0.635 x the brightest E, then the shader's getChannelLightNEW(0.1 d, E / 15) =
    0.8 C max(0, 1 - 0.1 d / C)^1.5 for EACH channel on its own"""
    rad = (key >> 24) & 255
    chans = [max((key >> s) & 255, rad) for s in (16, 8, 0)]
    if d >= 0.635 * max(chans):
        return (0.0, 0.0, 0.0)
    out = []
    for e in chans:
        c = e / 15.0
        x = 1.0 - 0.1 * d / c if c > 0.0 else 0.0
        out.append(0.8 * c * x * (x ** 0.5) if x > 0.0 else 0.0)
    return tuple(out)


LAN_TABLE5 = [None] + [lan_solve5(LAN_DEF[_t - 1], LAN_DEF[3 + _t], LAN_DEF[8], LAN_DEF[9], LAN_DEF[10]) for _t in range(1, 5)]
LAN_TABLE = [None] + [_x[:3] for _x in LAN_TABLE5[1:]]       # (height, level, reach) as in 0.5.4
LAN_RING = [None] + [_x[3:] for _x in LAN_TABLE5[1:]]        # 0.5.5: (ring lights, ring radius in half blocks)
# 0.5.18: the bigger reaches (Skyy 2026-10-15) - every rarity now has a hidden light (Normal's 10 blocks need more than the glow's ~6)
assert [(_h, _l) for _h, _l, _r in LAN_TABLE[1:]] == [(10, 24), (25, 50), (52, 95), (52, 95)], LAN_TABLE
assert LAN_RING[1:] == [(0, 0), (0, 0), (3, 7), (7, 90)], LAN_RING
assert [round(_r, 1) for _h, _l, _r in LAN_TABLE[1:]] == [10.0, 18.3, 32.0, 64.0], LAN_TABLE
assert all(_r >= LAN_DEF[3 + _t] - 1e-9 for _t, (_h, _l, _r) in enumerate(LAN_TABLE[1:], 1)), "every default reach is reached in full"
assert all(_l <= LAN_DEF[9] and _h <= LAN_DEF[8] for _h, _l, _r in LAN_TABLE[1:]) and all(1 + _m <= LAN_DEF[10] for _m, _p in LAN_RING[1:])
# why lantern.lights 8: with 0.5.5's 7 the Legendary ring stops short of 64 (1 + 6 lights), the same height / edge with 8 reach it
assert round(lan_solve5(LAN_DEF[3], 64, LAN_DEF[8], LAN_DEF[9], 7)[2], 1) == 61.0 and LAN_TABLE5[4][3] == 7
# the 0.5.5 defaults still give the 0.5.5 table (only the defaults changed, not the light model)
assert [lan_solve5(LAN_DEF_055[_t - 1], LAN_DEF_055[3 + _t], LAN_DEF_055[8], LAN_DEF_055[9], LAN_DEF_055[10])[:2] + lan_solve5(
    LAN_DEF_055[_t - 1], LAN_DEF_055[3 + _t], LAN_DEF_055[8], LAN_DEF_055[9], LAN_DEF_055[10])[3:] for _t in range(1, 5)] == [
    (0, 0, 0, 0), (14, 31, 0, 0), (38, 72, 0, 0), (52, 95, 5, 55)]
# 0.5.4's table is still what lantern.edge 255 + lantern.lights 1 + lantern.height 128 give (0.5.4's reaches)
assert [lan_solve(LAN_DEF_055[_t - 1], LAN_DEF_055[3 + _t], 128)[:2] for _t in range(1, 5)] == [(0, 0), (14, 31), (38, 72), (123, 208)]
# the step at the edge (world brightness = 3 x the light at the cut-off 0.635 x level): 0.5.4's Legendary 0.34, now 0.16
assert 3.0 * lan_light(208, 0.635 * 208 - 1e-9) > 0.34 and 3.0 * lan_light(LAN_TABLE[4][1], 0.635 * LAN_TABLE[4][1] - 1e-9) < 0.17
assert all(lan_light(_l, _h - LAN_PZ) <= lan_cap(LAN_TORCH) for _h, _l, _r in LAN_TABLE[1:]), "the brightness cap holds"   # 0.5.18: Normal too
assert lan_key(LAN_TORCH) == (1 << 24) | (11 << 16) | (10 << 8) | 9, "the default glow is the torch's 11 / 10 / 9"
# finding 1: the ground under every default helper (straight below, and at the reach's edge) gets the same light on red, green and blue;
# the old torch tint gave Legendary ground green 0.04 / blue 0 against red 0.42 (a red disc)
for _h, _l, _r in LAN_TABLE[1:]:   # 0.5.18: Normal has a helper too
    for _d in (float(_h), min((_h * _h + (_r * 0.98) ** 2) ** 0.5, 0.98 * 0.635 * _l)):   # 0.5.5: a ring row's reach is not one light's
        _w = lan_rgb(lan_hkey(_l), _d)
        assert _w[0] > 0.0 and _w[0] == _w[1] == _w[2], ("the helper light is not white on the ground", _h, _l, _d, _w)
_old = lan_rgb(lan_key(208), 123.0)
assert _old[0] > 0.4 and _old[1] < 0.1 * _old[0] and _old[2] == 0.0, ("the torch-tinted far light would be red", _old)
# the reach a rarity SHOWS: the glow's own reach when there is no helper (the glow alone may light more than a small row), else the
# row when it is reached, else what is reached (the Java AccDefs.lanShown)
LAN_SHOWN = [0] + [int(round(LAN_TABLE[_t][2])) if LAN_TABLE[_t][0] <= 0 else
                   (LAN_DEF[3 + _t] if LAN_TABLE[_t][2] >= LAN_DEF[3 + _t] else int(round(LAN_TABLE[_t][2]))) for _t in range(1, 5)]
assert LAN_SHOWN == [0, 10, 18, 32, 64], LAN_SHOWN   # 0.5.18
print("lantern: tier table (glow, helper level at height -> reach in blocks, a torch ~%.1f): %s" % (lan_reach(LAN_TORCH, 0.0), " | ".join(
    "%s glow %d%s%s -> %.1f" % (LAN_RARITIES[_t - 1], LAN_DEF[_t - 1], (" + light %d at %d up" % (LAN_TABLE[_t][1], LAN_TABLE[_t][0]))
                                if LAN_TABLE[_t][0] else "", (" + %d around at %.1f blocks" % (LAN_RING[_t][0], LAN_RING[_t][1] * 0.5))
                                if LAN_RING[_t][0] else "", LAN_TABLE[_t][2]) for _t in range(1, 5))))
CAP = 60          # 0.5: bag STORAGE slots (Skyy 2026-09-30: "bag 18 slots to start, up to 60"); AccStore.CAP, the page, un:<i>
MAIN_SLOTS = 9    # 0.5: slot0..slot8 stay in bags/<key>.properties - the file 0.4.x reads and rewrites whole - and slot9..slot59 go
                  # into bags/<key>.more.properties, which 0.4.x never opens: a rollback hides the extra slots, it cannot delete them
SLOTS_DEF = 18    # 0.5: config row slots default (1..CAP); it limits NEW equips only, as in 0.4.4
PAGE_ROWS = 9     # 0.5: bag page rows per page - the bag slots and the accessories in the inventory, each with the kit pager
BONUS_MAX = 12    # 0.5: the Bonuses well: two columns of 6 short lines
REGEN_EVERY = 2
REGEN_MAX = 30
assert MAIN_SLOTS == 9 and 1 <= SLOTS_DEF <= CAP == 60 and PAGE_ROWS == 9 and BONUS_MAX == 12

# ---- BOOSTER TABLE START (SkyyAccessories/test_skyyaccessories_0.5.py execs this block: plain Python - no kit, no JVM, no files)
# 0.5 rarity (Skyy 2026-09-30: "they are all accessories. but they come in the same rarity tiers as weapons and armor"; spec 1.2 / 5.2).
# ID words and display rarities are SEPARATE: the id word "Epic" means Legendary on screen, and "Legendary" ending an id is a legacy word.
ID_WORD = ["", "Common", "Uncommon", "Rare", "Epic"]            # tier 1..4: parse and build ids ONLY (the Workbench ladder)
LEGACY_WORDS = [("Talisman", 2), ("Ring", 3), ("Artifact", 4), ("Legendary", 4)]   # old id tails -> tier; modernOf -> the ID_WORD id
DISPLAY = ["", "Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic"]         # rarity 1..6 = everything players see
ACC_AP = [0, 10, 13, 16, 19, 22, 25]   # Accessory Power by rarity (spec 1.3): a build constant in acc:defs only - no setting, not shown
MAX_LINE_RARITY = 4                    # a line stops at Legendary; Fabled / Mythic are rare finds for later (spec 4.1)
SOURCE_WORDS = ("Craft", "Drop", "Chest", "Combine", "Boss")   # placeholder source words for the later loot pass (spec 2.3)
# THE BOOSTER TABLE (spec 2, 5.4): one row per line. Everything else - the AccDefs arrays, config entries, Server Setup rows, the
# effect tick, tooltips, item assets, /accessories lines, acc:defs and the harness - comes from it.
# (family key = item ids, admin name = config / commands / acc:defs, line name = what players see,
#  look: crystal colour + Legendary icon item (every rarity the colour's crystal fragment model; icons fragments / small cluster /
#        large cluster / that item) OR None + [4 items] (each rarity copies that vanilla item's model and icon, spec 5.6),
#  stats [(stat, kind, [Normal, Unique, Rare, Legendary])], source words per rarity, flavour line,
#  recipes [Normal inputs, Unique extra, Rare extra, Legendary extra] - each upgrade also takes the rarity below, at a Workbench -
#        or None (no recipe: admin give only until the loot pass, Skyy's decision 5),
#  id style "word" = Skyy_Talisman_<Key>_<Common|Uncommon|Rare|Epic> (the folded lines, their legacy ids kept) or "T" =
#        Skyy_Talisman_<Key>_T1..T4 (the new lines, spec 5.3))
SRC_FOLDED = ["Craft", "Craft+Drop", "Craft+Chest", "Craft+Boss"]
BOOSTERS = [
    ("Vitality", "Health", "Health", "Red", "Rock_Gem_Ruby",
     [("flat", "maxHealth", [6, 12, 18, 24])], SRC_FOLDED, "A warm pulse that steadies the heart.", [
        [("Ingredient_Crystal_Red", 2), ("Ingredient_Life_Essence", 5), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Red", 3), ("Ingredient_Life_Essence", 10), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Ruby", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Life_Essence", 30)],
        [("Rock_Gem_Ruby", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Life_Essence_Concentrated", 2)],
     ], "word"),
    ("Endurance", "Stamina", "Stamina", "Yellow", "Rock_Gem_Topaz",
     [("flat", "maxStamina", [3, 6, 9, 12]), ("regenPct", "staminaRegen", [2.5, 5, 7.5, 10])], SRC_FOLDED,   # 0.5.1: Skyy
     "It hums faster the harder you breathe.", [
        [("Ingredient_Crystal_Yellow", 2), ("Ingredient_Leather_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Leather_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Topaz", 1), ("Ingredient_Leather_Medium", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Topaz", 3), ("Ingredient_Leather_Heavy", 15), ("Ingredient_Bar_Thorium", 10)],
     ], "word"),
    ("Intelligence", "Mana", "Mana", "Blue", "Rock_Gem_Sapphire",
     [("pct", "manaPct", [6, 12, 18, 24]), ("floor", "manaFloor", [1, 2, 3, 4])], SRC_FOLDED,
     "Cold to the touch, and full of quiet thoughts.", [
        [("Ingredient_Crystal_Blue", 2), ("Ingredient_Fabric_Scrap_Linen", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Blue", 3), ("Ingredient_Fabric_Scrap_Linen", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Sapphire", 1), ("Ingredient_Fabric_Scrap_Silk", 10), ("Ingredient_Bar_Silver", 5)],
        [("Rock_Gem_Sapphire", 3), ("Ingredient_Bolt_Cindercloth", 5), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    ("Regeneration", "Regeneration", "Regeneration", "Green", "Rock_Gem_Emerald",
     [("pct", "healPct", [0.25, 0.5, 0.75, 1.0])], SRC_FOLDED, "Moss grows back on it overnight.", [
        [("Ingredient_Crystal_Green", 2), ("Ingredient_Life_Essence", 10), ("Ingredient_Tree_Sap", 3)],
        [("Ingredient_Crystal_Green", 3), ("Ingredient_Life_Essence", 20), ("Ingredient_Tree_Sap", 5)],
        [("Rock_Gem_Emerald", 1), ("Ingredient_Life_Essence", 50), ("Ingredient_Bar_Gold", 5)],
        [("Rock_Gem_Emerald", 3), ("Ingredient_Life_Essence_Concentrated", 3), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    ("Speed", "Speed", "Speed", "Cyan", "Rock_Gem_Zephyr",
     [("pct", "speedPct", [2.5, 5, 7.5, 10])], SRC_FOLDED, "The wind always seems to be at your back.", [
        [("Ingredient_Crystal_Cyan", 2), ("Ingredient_Feathers_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Cyan", 3), ("Ingredient_Feathers_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Zephyr", 1), ("Ingredient_Feathers_Blue", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Zephyr", 3), ("Ingredient_Lightning_Essence", 10), ("Ingredient_Bar_Cobalt", 10)],
     ], "word"),
    # ---- part 2 (spec 2.3, 2.4): no recipes, ids _T1.._T4
    ("Strength", "Strength", "Brawler", None,
     ["Ingredient_Bone_Fragment", "Ingredient_Sinue_Cindersinue", "Ingredient_Fire_Essence", "Ingredient_Voidheart"],
     [("flat", "str", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Scuffed wraps from a hundred fights.", None, "T"),
    ("MagicPower", "MagicPower", "Runic", "Purple", "Rock_Gem_Voidstone",
     [("flat", "mp", [3, 6, 9, 12])], ["Chest", "Combine", "Craft", "Boss"], "Faint runes crawl across it when you cast.", None, "T"),
    ("Defense", "Defense", "Stonehide", "White", "Rock_Crystal_Iridescent_Large",
     [("flat", "def", [3, 6, 9, 12])], ["Drop", "Combine", "Craft", "Boss"], "Heavy as a boulder, and just as stubborn.", None, "T"),
    ("Crit", "Crit", "Razorfang", "Pink", "Rock_Crystal_Iridescent_Medium",
     [("chancePct", "cc", [2, 4, 6, 8]), ("damagePct", "cd", [4, 8, 12, 16])], ["Chest", "Combine", "Craft", "Boss"],
     "Its edge always finds the gap in the armor.", None, "T"),
    ("Feather", "Feather", "Feather", None,
     ["Ingredient_Feathers_Light", "Ingredient_Feathers_Blue", "Ingredient_Ice_Essence", "Ingredient_Motes_Light"],
     [("fallPct", "fallPct", [10, 20, 30, 40]), ("jumpPct", "jumpPct", [5, 10, 15, 20])], ["Craft", "Craft", "Chest", "Chest"],
     "Lighter than it has any right to be.", None, "T"),
]
# THE STAT ALLOWLIST (spec 1.4; Skyy's decision 6: "stats that do nothing yet must NEVER be on a booster"): kind -> (config unit,
# whole numbers only, cap, what applies it in game). A row using any other kind stops the build. Never dmg, element damage, tdmg,
# spd or stam through gear:extra, or a key SkyyGear marks "later" (it accepts them and does nothing - a booster would lie).
STAT_KINDS = {
    "maxHealth":    ("flat", False, 1000, "stat map key skyyacc_health (StaticModifier MAX, ADDITIVE)"),
    "maxStamina":   ("flat", False, 1000, "stat map key skyyacc_stamina (StaticModifier MAX, ADDITIVE)"),
    "staminaRegen": ("pct",  False, 100,  "the Stamina Regen top-up: addStatValue(Stamina) while vanilla's own refill runs (AccEffects.staminaRegen)"),
    "manaPct":      ("pct",  False, 100,  "stat map key skyyacc_mana (MAX, ADDITIVE): percent of the flat Mana, never less than manaFloor"),
    "manaFloor":    ("flat", False, 1000, "the least the Mana line adds (with manaPct in the same line)"),
    "healPct":      ("pct",  False, 100,  "addStatValue(Health) every regenEverySeconds, percent of max Health"),
    "speedPct":     ("pct",  False, 100,  "movement protocol source accessories.talismans, layer pct, speed"),
    # part 2: SkyyGear 0.1 (live) reads gear:extra:<uuid> on every hit (VERIFIED: GearStats.totals(..., withExtra = true) in the
    # offence and Defense handlers); SkyyGear floors each part, so these take whole numbers only
    "str":          ("flat", True,  1000, "gear:extra key str - SkyyGear: +1% damage per point (melee, arrows, thrown weapons, staff melee)"),
    "mp":           ("flat", True,  1000, "gear:extra key mp - SkyyGear: +1% spell damage per point"),
    "def":          ("flat", True,  1000, "gear:extra key def - SkyyGear: mob and player hits x 100 / (100 + Defense)"),
    "cc":           ("pct",  True,  100,  "gear:extra key cc - SkyyGear: Crit Chance in percent (base 0)"),
    "cd":           ("pct",  True,  100,  "gear:extra key cd - SkyyGear: Crit Damage in percent (rides with cc on one line)"),
    "fallPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, fallDamage (pct layer, negated) - applied by SkyySkills"),
    "jumpPct":      ("pct",  False, 100,  "movement protocol source accessories.talismans, jump (pct layer) - applied by MoveSync.sync"),
}
# the gear:extra keys (spec 5.4): kind -> SkyyGear stat key; the ONLY keys SkyyAccessories may write (lsteal joins in wave 2)
GEAR_ALLOW = ("str", "mp", "def", "cc", "cd")
GEAR_KEYS = sorted(GEAR_ALLOW)                  # the text lists them in this order: "cc:8,cd:16,def:12,mp:12,str:12"
STAT_GEAR = {"str": "str", "mp": "mp", "def": "def", "cc": "cc", "cd": "cd"}
GEAR_NEVER = ("dmg", "tdmg", "spd", "stam", "fEarth", "fFire", "fWater", "fAir", "fThunder", "lsteal")
# kinds that only ride along with another kind of the same line (one tooltip template, one bag-page part with it)
RIDERS = {"manaFloor": "manaPct", "cd": "cc", "jumpPct": "fallPct", "staminaRegen": "maxStamina"}
ENTRIES = []      # config entries "<Admin>.<stat>" in table order: (key, line index, kind, [Normal, Unique, Rare, Legendary])
for _li, _b in enumerate(BOOSTERS):
    for _st, _kind, _vals in _b[5]:
        ENTRIES.append(("%s.%s" % (_b[1], _st), _li, _kind, list(_vals)))
E = dict((_e[0], _i) for _i, _e in enumerate(ENTRIES))
KIND_E = dict((_e[2], _i) for _i, _e in enumerate(ENTRIES))
LI = dict((_b[1], _i) for _i, _b in enumerate(BOOSTERS))


def booster_id(b, t):
    """the item id of rarity t (1..4) of table row b (its id style)"""
    return "Skyy_Talisman_%s_%s" % (b[0], ID_WORD[t]) if b[9] == "word" else "Skyy_Talisman_%s_T%d" % (b[0], t)


LINE_IDS = [booster_id(_b, _t) for _b in BOOSTERS for _t in range(1, 5)]   # [line * 4 + tier - 1]
LINE_SRC = [_b[6][_t - 1] for _b in BOOSTERS for _t in range(1, 5)]
BOOST_DEF = [",".join("%g" % _v for _v in _e[3]) for _e in ENTRIES]
FOLDED = [_b for _b in BOOSTERS if _b[9] == "word"]      # the 0.4.x lines: word ids, legacy ids, Workbench recipes
E_GEAR = [STAT_GEAR.get(_e[2], "") for _e in ENTRIES]    # per entry: its gear:extra key or ""
COMBAT_LINES = [_b[2] for _li, _b in enumerate(BOOSTERS) if any(E_GEAR[_i] for _i, _e in enumerate(ENTRIES) if _e[1] == _li)]


def _table_checks():
    """the table rules (spec 6.1 / 6.2 build checks); the harness runs them again"""
    import re as _re
    fams, admins, names, kinds = [b[0] for b in BOOSTERS], [b[1] for b in BOOSTERS], [b[2] for b in BOOSTERS], []
    for lst, what in ((fams, "family key"), (admins, "admin name"), (names, "line name")):
        assert len(set(lst)) == len(lst), "duplicate %s: %s" % (what, lst)
    words = [w for w in ID_WORD[1:]] + [w for w, _t in LEGACY_WORDS]
    for b in BOOSTERS:
        fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
        assert _re.match(r"^[A-Z][A-Za-z]+$", fam) and not any(fam.endswith(w) for w in words), "family key %r: CamelCase, no _, " \
            "not ending in an id word or legacy word" % fam
        assert _re.match(r"^[A-Z][A-Za-z]+$", adm) and _re.match(r"^[A-Z][A-Za-z]+$", line), (adm, line)
        assert len(src) == MAX_LINE_RARITY and all(all(w in SOURCE_WORDS for w in x.split("+")) for x in src), (fam, src)
        assert style in ("word", "T"), (fam, style)
        if style == "word":
            assert recipes is not None and len(recipes) == MAX_LINE_RARITY, (fam, "a folded line keeps its 4 Workbench steps")
        else:
            assert recipes is None, (fam, "new lines have no recipe (Skyy: acquisition later - admin give only)")
        if crystal is None:
            assert isinstance(gem, list) and len(gem) == MAX_LINE_RARITY and len(set(gem)) == 4, (fam, "4 look items, one per rarity")
        else:
            assert _re.match(r"^[A-Z][a-z]+$", crystal) and isinstance(gem, str), (fam, crystal, gem)
        assert flavour and "." in flavour and all(ord(ch) < 128 for ch in flavour), flavour
        for st, kind, vals in stats:
            assert kind in STAT_KINDS, "%s uses the stat kind %r, which is not in the allowlist STAT_KINDS (spec 1.4)" % (fam, kind)
            unit, whole, cap, _how = STAT_KINDS[kind]
            assert _re.match(r"^[a-z][A-Za-z]*$", st), st
            assert len(vals) == MAX_LINE_RARITY, "%s.%s needs exactly 4 numbers (Normal..Legendary): %r" % (adm, st, vals)
            for v in vals:
                assert 0 <= v <= cap and round(v, 2) == v and (not whole or v == int(v)), (adm, st, v)
            assert list(vals) == sorted(vals) and vals[0] > 0, "%s.%s must grow with the rarity: %r" % (adm, st, vals)
            kinds.append(kind)
        ks = [k for _s, k, _v in stats]
        for rider, main in RIDERS.items():
            assert (rider in ks) <= (main in ks), "%s goes with %s in one line" % (rider, main)
        assert len([k for k in ks if k not in RIDERS]) == 1, "%s: exactly one main stat (the rest ride along): %s" % (adm, ks)
    assert len(set(kinds)) == len(kinds), "one line per stat kind (spec 1.1: one line per stat)"
    assert len(set(LINE_IDS)) == len(LINE_IDS) == 4 * len(BOOSTERS), "two rarities share an id"
    assert len(set(e[0] for e in ENTRIES)) == len(ENTRIES)
    assert ACC_AP[1:5] == [10, 13, 16, 19] and all(10 <= a <= 25 for a in ACC_AP[1:]), ACC_AP   # locked +10 to +25 (locks 111-113)
    assert DISPLAY[1:5] == ["Normal", "Unique", "Rare", "Legendary"] and MAX_LINE_RARITY == 4
    # part 2: gear:extra - only the allowlist, whole numbers, never a key SkyyGear keeps for weapons / armor or "later"
    for k, g in STAT_GEAR.items():
        assert g in GEAR_ALLOW and g not in GEAR_NEVER and STAT_KINDS[k][1], "gear:extra key %r is outside str mp def cc cd" % g
    assert set(GEAR_ALLOW) == set(STAT_GEAR.values()) and not set(GEAR_ALLOW) & set(GEAR_NEVER)
    assert all(g == "" or g in GEAR_ALLOW for g in E_GEAR)
    # part 2 ids: _T1.._T4, never the bench prefix, never ending in a legacy word (modernOf would rebuild them)
    for b in BOOSTERS:
        if b[9] != "T":
            continue
        for t in range(1, 5):
            i = booster_id(b, t)
            assert i.startswith("Skyy_Talisman_") and not i.startswith("Skyy_Accessory_") and i.endswith("_T%d" % t), i
            assert not any(i.endswith("_" + w) for w, _t in LEGACY_WORDS), i
    assert len(BOOSTERS) + 2 <= BONUS_MAX, "the Bonuses well holds one row per line + 2 notes (%d lines)" % len(BOOSTERS)


_table_checks()
# ---- BOOSTER TABLE END
assert [_b[0] for _b in BOOSTERS] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Strength", "MagicPower",
                                     "Defense", "Crit", "Feather"], "the five folded lines + the five part 2 lines"
assert [_b[0] for _b in FOLDED] == ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed"]
assert BOOST_DEF == ["6,12,18,24", "3,6,9,12", "2.5,5,7.5,10", "6,12,18,24", "1,2,3,4", "0.25,0.5,0.75,1", "2.5,5,7.5,10",
                     "3,6,9,12", "3,6,9,12", "3,6,9,12", "2,4,6,8", "4,8,12,16", "10,20,30,40", "5,10,15,20"], BOOST_DEF
assert [_e[0] for _e in ENTRIES][7:] == ["Strength.flat", "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct",
                                         "Feather.fallPct", "Feather.jumpPct"], "the spec 5.8 part 2 entry names"
assert COMBAT_LINES == ["Brawler", "Runic", "Stonehide", "Razorfang"], COMBAT_LINES
# the numbers are exact float32 values (the loader computes (float) of the parsed text; the jar literals are "%.4ff")
import struct as _struct
def _f32(x):
    return _struct.unpack("<f", _struct.pack("<f", x))[0]   # menu-pattern-ok (a struct format, not a page text)
assert all(_f32(v) == v for _e in ENTRIES for v in _e[3]), "a booster default is not exact in float32"
# the rarity look: frame art = SkyyGear's Skyy_Gear_* table (tooltip + arrow texture quality, slot texture quality, drop particle);
# colours = the kit's rarity palette (the same hexes as SkyyGear / SkyySacks); the six quality assets Skyy_Acc_<Rarity>
QUAL_IDS = [""] + ["Skyy_Acc_" + _r for _r in DISPLAY[1:]]
QUAL_ART = {"Normal": ("Common", "Common", "Drop_Common"), "Unique": ("Legendary", "Legendary", "Drop_Legendary"),
            "Rare": ("Epic", "Epic", "Drop_Epic"), "Legendary": ("Rare", "Rare", "Drop_Rare"),
            "Fabled": ("Common", "Developer", "Drop_Legendary"), "Mythic": ("Epic", "Epic", "Drop_Epic")}
RARITY_COLORS = ["#ffffff"] + [SUI.RARITY[_r] for _r in DISPLAY[1:]]
BENCH_RARITY = [0, 1, 2, 3, 4, 4, 4, 4]   # bench tier I Normal, II Unique, III Rare, IV and up Legendary (crafted: stops at Legendary)


def _gear_art_check():
    """SkyyAccessories ships its own qualities (every Skyy mod works alone), but the look must match SkyyGear's ladder"""
    import re as _re, glob as _glob
    def _v(p):
        m = _re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(_glob.glob(os.path.join(HERE, "..", "SkyyGear", "build_skyygear_*.py")), key=_v)
    if not found:
        print("note: no SkyyGear build script next to this mod - the Skyy_Acc_* frame art is not cross-checked")
        return
    txt = open(found[-1], encoding="utf8", errors="replace").read()
    rows = _re.findall(r'^\s*\("(\w+)", "(\w+)", "(#[0-9A-Fa-f]{6})", "#[0-9A-Fa-f]{6}", "(\w+)", "(\w+)", "(\w+)"\),', txt, _re.M)
    got = dict((nm, (col.lower(), (tt, sl, pt))) for _rid, nm, col, tt, sl, pt in rows)
    for r in DISPLAY[1:]:
        if r not in got:
            raise SystemExit("0.5: %s has no %s row in its RARITIES table - update _gear_art_check" % (os.path.basename(found[-1]), r))
        if got[r][1] != QUAL_ART[r] or got[r][0] != SUI.RARITY[r].lower():
            raise SystemExit("0.5: the %s look differs from %s (%r vs %r) - update QUAL_ART" % (r, os.path.basename(found[-1]), got[r], (SUI.RARITY[r], QUAL_ART[r])))
    print("rarity look matches %s (%s)" % (os.path.basename(found[-1]), ", ".join(DISPLAY[1:])))


_gear_art_check()

# ---- the Python mirror of the Java id rules (AccDefs.tailTier / tierOf / familyOf / isLegacy / modernOf / rarityOf) + the fold checks
def py_family(iid):
    tail = iid[len("Skyy_Talisman_"):]
    k = tail.rfind("_")
    return tail[:k] if k > 0 else tail
def py_tail_tier(iid):
    w = iid[iid.rfind("_") + 1:]
    return int(w[1:]) if len(w) >= 2 and w[0] == "T" and w[1:].isdigit() else -1
def py_tier(iid):
    if py_tail_tier(iid) > 0:
        return py_tail_tier(iid)
    for r in range(len(ID_WORD) - 1, 0, -1):
        if iid.endswith("_" + ID_WORD[r]):
            return r
    for w, t in LEGACY_WORDS:
        if iid.endswith("_" + w):
            return t
    return 1
def py_legacy(iid):
    return py_tail_tier(iid) <= 0 and any(iid.endswith("_" + w) for w, _t in LEGACY_WORDS)
def py_modern(iid):
    return "Skyy_Talisman_%s_%s" % (py_family(iid), ID_WORD[py_tier(iid)]) if py_legacy(iid) else iid
def old_tier(iid):   # SkyyAccessories 0.4.5 AccDefs.tierOf on talisman ids (Common 1 .. Legendary 5; Talisman 2, Ring 3, Artifact 4)
    for r, w in ((5, "Legendary"), (4, "Epic"), (3, "Rare"), (2, "Uncommon"), (1, "Common")):
        if iid.endswith("_" + w):
            return r
    return {"Artifact": 4, "Ring": 3, "Talisman": 2}.get(iid[iid.rfind("_") + 1:], 1)
OLD_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w in ("Common", "Uncommon", "Rare", "Epic", "Legendary")]
LEGACY_IDS = ["Skyy_Talisman_%s_%s" % (_b[0], _w) for _b in FOLDED for _w, _t in LEGACY_WORDS]
FOLDED_IDS = [booster_id(_b, _t) for _b in FOLDED for _t in range(1, 5)]
NEW_IDS = [booster_id(_b, _t) for _b in BOOSTERS if _b[9] == "T" for _t in range(1, 5)]
assert len(OLD_IDS) == 25 and len(LEGACY_IDS) == 20 and set(FOLDED_IDS) < set(OLD_IDS) and len(NEW_IDS) == 20
assert not set(NEW_IDS) & set(OLD_IDS + LEGACY_IDS) and sorted(FOLDED_IDS + NEW_IDS) == sorted(LINE_IDS)
for _li, _b in enumerate(BOOSTERS):
    for _t in range(1, 5):
        _i = LINE_IDS[_li * 4 + _t - 1]
        assert py_tier(_i) == _t and py_family(_i) == _b[0] and not py_legacy(_i) and py_modern(_i) == _i, _i
        assert (py_tail_tier(_i) == _t) == (_b[9] == "T"), _i       # part 2: the _T<n> tail parses first
    if _b[9] != "word":
        continue
    for _w, _t in LEGACY_WORDS:
        _i = "Skyy_Talisman_%s_%s" % (_b[0], _w)
        assert py_legacy(_i) and py_tier(_i) == _t and py_family(_i) == _b[0] and py_modern(_i) == LINE_IDS[_li * 4 + _t - 1], _i
assert py_modern("Skyy_Talisman_Vitality_Legendary") == "Skyy_Talisman_Vitality_Epic"
assert py_tier("Skyy_Talisman_Crit_T4") == 4 and py_family("Skyy_Talisman_MagicPower_T2") == "MagicPower"
# the equip swap order (AccStore.equipK: a higher tier of the same line swaps in, equal or lower is refused) is 0.4.5's for every pair
# of the 40 old ids of a line, except that the old fifth id (_Legendary) now TIES with the other tier-4 ids (_Epic and _Artifact)
_sgn = lambda x: (x > 0) - (x < 0)
for _b in FOLDED:
    _ids = sorted(set(i for i in OLD_IDS + LEGACY_IDS if py_family(i) == _b[0]))   # the 5 + 3 ids 0.4.5 knew (_Legendary is in both lists)

    assert len(_ids) == 8, _ids
    for _a in _ids:
        for _c in _ids:
            _o, _n = _sgn(old_tier(_a) - old_tier(_c)), _sgn(py_tier(_a) - py_tier(_c))
            if _o != _n:
                assert _n == 0 and "_Legendary" in (_a[-10:], _c[-10:]) and 4 in (old_tier(_a), old_tier(_c)), (_a, _c, _o, _n)

# ---- 0.5 CONFIG (the defaults file = the kit's DEFAULTS; AccCfg.migrate appends the lines from "notice.boosters" on to a 0.4.x file)
# 0.5.3: the Night Vision id through the booster table's id rules (the Python mirror of AccDefs.tierOf / familyOf / isLegacy / modernOf)
assert NV_ID == "Skyy_Talisman_%s_%s" % (NV_ADMIN, ID_WORD[NV_TIER]) and DISPLAY[NV_TIER] == "Rare", NV_ID
assert py_tier(NV_ID) == NV_TIER and py_family(NV_ID) == NV_ADMIN and py_tail_tier(NV_ID) == -1 and not py_legacy(NV_ID) and py_modern(NV_ID) == NV_ID
assert NV_ADMIN not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] and NV_LINE not in [_b[2] for _b in BOOSTERS]
assert NV_ID not in LINE_IDS + OLD_IDS + LEGACY_IDS and not NV_ID.startswith("Skyy_Accessory_")
# 0.5.4: the Lantern ids = the id words of each rarity, their own family (never a booster family / legacy / bench id)
assert LAN_IDS == ["Skyy_Talisman_%s_%s" % (LAN_FAM, ID_WORD[_t]) for _t in range(1, 5)], LAN_IDS
assert all(py_tier(_i) == _t + 1 and py_family(_i) == LAN_FAM and py_tail_tier(_i) == -1 and not py_legacy(_i) and py_modern(_i) == _i
           for _t, _i in enumerate(LAN_IDS))
assert LAN_FAM not in [_b[0] for _b in BOOSTERS] + [_b[1] for _b in BOOSTERS] + [NV_ADMIN] and LAN_LINE not in [_b[2] for _b in BOOSTERS]
assert not set(LAN_IDS) & set(LINE_IDS + OLD_IDS + LEGACY_IDS + [NV_ID])
# groups of new keys: (comment lines, [(key, value), ...]) - the migration writes a group's comments before its first missing key
# 0.5.1 STAMINA (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01: double the max Stamina, half the Stamina Regen). AccCfg.migrate051 rewrites a
# boost.Stamina.flat / boost.Stamina.regenPct line that still holds these 0.5 numbers (the SkyyGear 0.1.1 migrateStat011 rules)
M51_OLD = [("Stamina.flat", "1.5,3,4.5,6"), ("Stamina.regenPct", "5,10,15,20")]
M51_KEYS = [_k for _k, _o in M51_OLD]
M51_NEW = [BOOST_DEF[E[_k]] for _k in M51_KEYS]
assert M51_NEW == ["3,6,9,12", "2.5,5,7.5,10"] and all(_k in E for _k in M51_KEYS), M51_NEW
# the marker (in the 0.5.1 default text and in every updated file): a doc comment with spaces and no '=', so the kit never takes it for
# a "#key=value" template line; migrate051 looks for M51_MARK_ID in comment lines only
M51_MARK_ID = "SkyyAccessories 0.5.1 Stamina defaults"
M51_MARK = ("# %s (Skyy, OPEN-QUESTIONS LOCKED 2026-10-01): max Stamina doubled to 3,6,9,12 and Stamina Regen halved "
            "to 2.5,5,7.5,10 (0.5: 1.5,3,4.5,6 and 5,10,15,20)." % M51_MARK_ID)
# the name on the update's config-changes.log lines and its History version: a fixed literal (SkyyGear 0.1.1 review finding 5)
M51_WHO = "SkyyAccessories 0.5.1"
assert all(32 <= ord(_c) < 127 for _c in M51_MARK) and "=" not in M51_MARK and M51_MARK.startswith("# ")
ADD_GROUPS = [
    (["# Tell players once, in chat, about the 0.5 accessory change (only players who had accessories before 0.5): true or false."],
     [("notice.boosters", "true")]),
    (["# Line switches: false = the line stays in the bag, counts for nothing and the Void Charms page says it is switched off."],
     [("line.%s" % _b[1], "true") for _b in BOOSTERS]),
    (["# Send the combat stats of the %s accessories to SkyyGear (true or false; false = they add nothing)." % ", ".join(COMBAT_LINES)],
     [("combatToGear", "true")]),
    (["# Booster numbers: four numbers for Normal,Unique,Rare,Legendary (no minus sign, up to 2 decimals). The entry name gives the",
      "# unit: flat = added to your maximum (Strength, MagicPower, Defense: whole points), pct = percent (Mana: of your Mana;",
      "# Regeneration: of max Health healed every regenEverySeconds; Speed: faster movement), chancePct / damagePct = whole percent",
      "# Crit Chance / Crit Damage, regenPct = percent faster Stamina refill, floor = the least the Mana line adds, fallPct = percent",
      "# less fall damage (written without a minus), jumpPct = percent higher jumps. The item tooltips print the built-in numbers;",
      "# the Void Charms page and /charms lines show the ones below.", M51_MARK],
     [("boost." + _e[0], BOOST_DEF[_i]) for _i, _e in enumerate(ENTRIES)]),
]
CONFIG_TEXT = "\n".join([
    "# SkyyAccessories settings. Change them in game: SkyWynn Menu -> Server Setup -> Void Charms, or edit this file",
    "# and run /charms reload (server admins: skyyaccessories.admin). Every change is logged in config-changes.log.",
    "#",
    "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP,
    "# keep counting and can still be unequipped - only a newly equipped accessory needs a free slot within the limit.",
    "slots=%d" % SLOTS_DEF,
    "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX,
    "regenEverySeconds=%d" % REGEN_EVERY,
] + [ln for _notes, _keys in ADD_GROUPS for ln in _notes + ["%s=%s" % kv for kv in _keys]] + LAN_CONFIG_LINES + LAN_HELMET_LINES + CRAFT_LINES + [""])   # 0.5.22: STARTER_LINES + LIFE_LINES gone (the bag item is retired)   # 0.5.4: + the Lantern (0.5.3's Night Vision part is gone)
assert all(ord(ch) < 128 for ch in CONFIG_TEXT), "config text must stay ASCII"
# the 0.4.x lines the migration handles (spec 5.1): bonus.<family> with its untouched default and where an EDITED list goes ("" = its
# unit changed, it is dropped and logged); the 0.4.4 / 0.4.5 default comment lines it rewrites ("" = removed)
OLD_BONUS = [("Vitality", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Health.flat by hand"),
             ("Endurance", "2,4,6,8,10", "", "its unit changed from percent to flat - set boost.Stamina.flat by hand"),
             ("Intelligence", "2,4,6,8,10", "Mana.pct", ""),
             ("Regeneration", "0.5,1,1.5,2,3", "Regeneration.pct", ""),
             ("Speed", "2,4,6,8,10", "Speed.pct", "")]
assert all(c == "" or c in E for _f, _d, c, _n in OLD_BONUS)
OLD_COMMENTS = [
    ("# Accessory bag slots every player can fill, 1-9. Lowering it deletes nothing: accessories already in a higher slot stay,",
     "# Accessory bag slots every player can fill, 1-%d. Lowering it deletes nothing: accessories already in a higher slot stay," % CAP),
    ("# How often the Regeneration talisman heals, in seconds (1-30).", "# How often the Regeneration Accessory heals, in seconds (1-%d)." % REGEN_MAX),
    ("# Talisman bonuses in percent for Common,Uncommon,Rare,Epic,Legendary (0-100 each, up to 2 decimals), one line per family.", ""),
    ("# Vitality / Endurance / Intelligence = percent of your flat max Health / Stamina / Mana, Regeneration = percent of max Health", ""),
    ("# healed every regenEverySeconds, Speed = percent movement speed. The item tooltips keep printing the built-in numbers", ""),
    ("# (2,4,6,8,10, Regeneration 0.5,1,1.5,2,3); the Void Charms page shows the ones below.", ""),
]
ADD_KEY = [k for _g, (_n, _ks) in enumerate(ADD_GROUPS) for k, _v in _ks]
ADD_VAL = [v for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, v in _ks]
ADD_GROUP = [_g for _g, (_n, _ks) in enumerate(ADD_GROUPS) for _k, _v in _ks]
GROUP_NOTE = ["\n".join(_n) for _n, _ks in ADD_GROUPS]
MIG_NOTICE = ("[Void Charms] Your talismans are now accessories: Health, Stamina, Mana, Regeneration and Speed Accessory, in the gear "
              "rarities Normal, Unique, Rare and Legendary, with new numbers. Stamina now also refills faster. /charms lines "
              "shows every line.")   # spec 5.1 (the one place where the old word "talismans" reaches a player: it names what they had)


def jlit(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def jstrs(xs):
    return ", ".join(jlit(x) for x in xs)
def JX(src):
    return src.replace("@PKG@", PKG)
def jfloats(vals, scale=1.0):
    return ", ".join("%.4ff" % (v * scale) for v in [0] + list(vals))
# 0.5: Java written with @TOKEN@ class names (no f-string brace doubling in the new code)
_TOK = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "MSG": MSG, "PLA": PLA, "INV": INV, "IC": IC, "IS": IS,
        "IST": IST, "ISS": ISS, "ESM": ESM, "ESV": ESV, "DST": DST, "MOD": MOD, "SMO": SMO, "MTG": MTG, "CAL": CAL, "CB": CB,
        "ACH": ACH, "QRY": QRY, "CTX": CTX, "EVD": EVD, "BT": BT, "UCB": UCB, "UEB": UEB, "RGV": RGV, "RGN": RGN, "RGT": RGT,
        "CND": CND, "TMR": TMR, "SIC": SIC, "ITM": ITM, "EST": EST}
def JT(src):
    out = src
    for _k, _v in _TOK.items():
        out = out.replace("@%s@" % _k, _v)
    assert "@" not in out, "unresolved @TOKEN@ in: " + out[:160]
    return out
def JM(cls, src):
    cls.addMethod(CtNewMethod.make(JT(src), cls))
# 0.5.4: the Lantern class tokens (@DLC@ ...); JT() resolves the others
_LANT = {"DLC": DLC, "CLT": CLT, "TCO": TCO, "NID": NID, "INT": INT_, "DES": DES, "DTH": DTH, "NSR": NSR, "HLD": HLD, "CRG": CRG,
         "CTY": CTY, "RTY": RTY, "ARS": ARS, "RRS": RRS, "ESR": ESR, "CSR": CSR, "ARC": ARC, "V3D": V3D,
         "EVW": EVW, "ETR": ETR, "CVS": CVS, "SGR": SGR, "SDP": SDP, "ORD": ORD, "HPM": HPM}   # + the fix round's AccLanternHide


def LANJ(src):
    for _k, _v in _LANT.items():
        src = src.replace("@%s@" % _k, _v)
    return src
def JF(cls, src):
    cls.addField(CtField.make(JT(src), cls))

# ================= AccDefs =================
bench_ids = ", ".join('"%s"' % b[0] for b in ACTIVE)     # 0.4.2: ACTIVE benches only (the Omni's synthetic grants)
bench_names = ", ".join('"%s"' % b[2] for b in ACTIVE)
assert '"Campfire"' in bench_ids and '"Alchemybench"' not in bench_ids and '"Cookingbench"' not in bench_ids, bench_ids   # 0.4.3
dfs.addField(CtField.make('public static final String BAG = "%s";' % BAG, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_IDS = new String[] { %s };' % bench_ids, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_NAMES = new String[] { %s };' % bench_names, dfs))
# 0.5: THE BOOSTER TABLE as flat 1-D arrays (javassist compiles no [][]): per line (FAMILIES order), per line x 4 + tier - 1, per entry
dfs.addField(CtField.make('public static final String[] FAMILIES = new String[] { %s };' % jstrs(b[0] for b in BOOSTERS), dfs))   # family keys (item ids only)
dfs.addField(CtField.make('public static final String[] LINE_ADMIN = new String[] { %s };' % jstrs(b[1] for b in BOOSTERS), dfs))   # config, commands, acc:defs
dfs.addField(CtField.make('public static final String[] LINE_NAME = new String[] { %s };' % jstrs(b[2] for b in BOOSTERS), dfs))    # "<Rarity> <Line> Accessory"
dfs.addField(CtField.make('public static final String[] LINE_IDS = new String[] { %s };' % jstrs(LINE_IDS), dfs))
dfs.addField(CtField.make('public static final String[] LINE_SRC = new String[] { %s };' % jstrs(LINE_SRC), dfs))
dfs.addField(CtField.make('public static final String[] ID_WORD = new String[] { %s };' % jstrs(ID_WORD), dfs))   # ids only (tier 1..4)
dfs.addField(CtField.make('public static final String[] LEGACY_WORD = new String[] { %s };' % jstrs(w for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final int[] LEGACY_TIER = new int[] { %s };' % ", ".join(str(t) for w, t in LEGACY_WORDS), dfs))
dfs.addField(CtField.make('public static final String[] DISPLAY = new String[] { %s };' % jstrs(DISPLAY), dfs))   # rarity 1..6
dfs.addField(CtField.make('public static final String[] RARITY_COLOR = new String[] { %s };' % jstrs(RARITY_COLORS), dfs))   # kit colours
dfs.addField(CtField.make('public static final int[] AP = new int[] { %s };' % ", ".join(str(a) for a in ACC_AP), dfs))
dfs.addField(CtField.make('public static final String[] E_KEYS = new String[] { %s };' % jstrs(e[0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_LINE = new int[] { %s };' % ", ".join(str(e[1]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final String[] E_UNIT = new String[] { %s };' % jstrs(STAT_KINDS[e[2]][0] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int[] E_WHOLE = new int[] { %s };' % ", ".join("1" if STAT_KINDS[e[2]][1] else "0" for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final float[] E_CAP = new float[] { %s };' % ", ".join("%d.0f" % STAT_KINDS[e[2]][2] for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static final int BONUS_MAX = %d;' % BONUS_MAX, dfs))
# the live numbers [entry * 5 + tier] (tier 0 = no accessory = 0), in the config unit (Speed / Regeneration in percent); AccCfg.load swaps it
dfs.addField(CtField.make('public static volatile float[] BOOST = new float[] { %s };' % ", ".join(jfloats(e[3]) for e in ENTRIES), dfs))
dfs.addField(CtField.make('public static volatile int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))   # 0.4.4: config row regenEverySeconds (kit field:)
for _b in BOOSTERS:   # 0.5: the line switches (kit field: rows line.<Admin>, live kill switches, on by default - Skyy's decision 6)
    dfs.addField(CtField.make('public static volatile boolean LINE_%s = true;' % _b[1].upper(), dfs))
dfs.addField(CtField.make('public static volatile boolean NOTICE = true;', dfs))   # 0.5: config row notice.boosters
# 0.5 part 2: the gear:extra key of each entry ("" = not a combat stat), the allowlist in text order, config row combatToGear, and the
# entries of the movement parts (-1 = no such entry)
dfs.addField(CtField.make('public static final String[] E_GEAR = new String[] { %s };' % jstrs(E_GEAR), dfs))
dfs.addField(CtField.make('public static final String[] GEAR_KEYS = new String[] { %s };' % jstrs(GEAR_KEYS), dfs))
dfs.addField(CtField.make('public static volatile boolean COMBAT_TO_GEAR = true;', dfs))
dfs.addField(CtField.make('public static final int E_SPEED = %d;' % KIND_E.get("speedPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_JUMP = %d;' % KIND_E.get("jumpPct", -1), dfs))
dfs.addField(CtField.make('public static final int E_FALL = %d;' % KIND_E.get("fallPct", -1), dfs))
dfs.addField(CtField.make('public static final String OMNI = "%s";' % OMNI, dfs))
dfs.addField(CtField.make('public static final int[] BENCH_MAX = new int[] { %s };' % ", ".join(str(b[3]) for b in ACTIVE), dfs))
# 0.4.2: retired bench ids + display names (same index) and the grey used for them on the bag page
dfs.addField(CtField.make('public static final String[] RETIRED = new String[] { %s };' % ", ".join('"%s"' % r for r in RETIRED), dfs))
dfs.addField(CtField.make('public static final String[] RETIRED_NAMES = new String[] { %s };' % ", ".join('"%s"' % n for n in RETIRED_NAMES), dfs))
dfs.addField(CtField.make('public static final int[] RETIRED_MAX = new int[] { %s };' % ", ".join(str(m) for m in RETIRED_MAX), dfs))
dfs.addField(CtField.make('public static final String RETIRED_COLOR = "#8a97a3";', dfs))
# 0.5.3 NIGHT VISION, RETIRED in 0.5.4: its id and texts (isRetired, retiredWhy / retiredChat, pretty, the bag row, the give refusal)
dfs.addField(CtField.make('public static final String NV_ID = "%s";' % NV_ID, dfs))
dfs.addField(CtField.make('public static final String NV_ADMIN = "%s";' % NV_ADMIN, dfs))
dfs.addField(CtField.make('public static final String NV_LINE = "%s";' % NV_LINE, dfs))
dfs.addField(CtField.make("public static final String NV_WHY = %s;" % jlit(NV_WHY), dfs))
dfs.addField(CtField.make("public static final String NV_CHAT = %s;" % jlit(NV_CHAT), dfs))
dfs.addField(CtField.make("public static final String NV_ROW = %s;" % jlit(NV_ROW), dfs))
dfs.addField(CtField.make("public static final String NV_GIVE = %s;" % jlit(NV_GIVE), dfs))
JM(dfs, r"""
public static boolean isNv(String id) {
  return NV_ID.equals(id);
}""")
JM(dfs, r"""
public static boolean hasNv(String[] s) {
  if (s == null) return false;
  for (int i = 0; i < s.length; i++) if (NV_ID.equals(s[i])) return true;
  return false;
}""")
# the old /accessories givetier names (NightVision, Night_Vision, Night-Vision, NV) - answered with the retirement
JM(dfs, r"""
public static boolean isNvName(String w) {
  if (w == null) return false;
  String x = w.trim();
  return x.equalsIgnoreCase(NV_ADMIN) || x.equalsIgnoreCase("Night_Vision") || x.equalsIgnoreCase("Night-Vision") || x.equalsIgnoreCase("NV");
}""")
# 0.5.4 THE LANTERN: ids, names, the live settings (the kit's field: rows), the tier table (lanTable: rebuilt when a setting changed), the
# light model and our light's int key (radius byte LAN_SIG_R + the torch tint). Compiled before every caller (javassist: method order).
dfs.addField(CtField.make('public static final String LAN_FAM = "%s";' % LAN_FAM, dfs))
dfs.addField(CtField.make('public static final String LAN_ADMIN = "%s";' % LAN_ADMIN, dfs))
dfs.addField(CtField.make('public static final String LAN_LINE = "%s";' % LAN_LINE, dfs))
dfs.addField(CtField.make('public static final String LAN_SRC = "%s";' % LAN_SRC, dfs))
dfs.addField(CtField.make('public static final String[] LAN_IDS = new String[] { %s };' % ", ".join('"%s"' % _i for _i in LAN_IDS), dfs))
dfs.addField(CtField.make('public static final int LAN_TORCH = %d;' % LAN_TORCH, dfs))
dfs.addField(CtField.make('public static final int LAN_SIG_R = %d;' % LAN_SIG_R, dfs))
dfs.addField(CtField.make('public static final double LAN_VIS = %r;' % LAN_VIS, dfs))
dfs.addField(CtField.make('public static final double LAN_PZ = %r;' % LAN_PZ, dfs))
dfs.addField(CtField.make('public static final double LAN_PD = %r;' % LAN_PD, dfs))
dfs.addField(CtField.make('public static final int LAN_MINH = %d;' % LAN_MINH, dfs))
dfs.addField(CtField.make('public static final int[] LAN_DEF = new int[] { %s };' % ", ".join(str(_x) for _x in LAN_DEF), dfs))
dfs.addField(CtField.make('public static volatile boolean LINE_LANTERN = true;', dfs))   # config row line.Lantern
dfs.addField(CtField.make('public static volatile boolean LAN_SHARE = false;', dfs))     # config row lantern.shareReach (fix round)
dfs.addField(CtField.make('public static volatile boolean LAN_HELMET = true;', dfs))     # 0.5.10: config row lantern.helmet (mining helmet light)
dfs.addField(CtField.make('public static volatile boolean STARTER = true;', dfs))        # 0.5.17: config row starter.bag (the starter Void Charms)
dfs.addField(CtField.make('public static volatile boolean CRAFT = true;', dfs))          # 0.5.18: config row craft.bag (the Craft tab of the bag page)
dfs.addField(CtField.make('public static volatile boolean AUTO = true;', dfs))           # 0.5.18: config row craft.autoEquip (crafted accessories into the bag)
dfs.addField(CtField.make('public static volatile boolean LIFELONG = true;', dfs))       # 0.5.20: config row lifelong.bag (the lifelong Void Charms)
dfs.addField(CtField.make('public static final double LAN_EPS = %r;' % LAN_EPS, dfs))
dfs.addField(CtField.make('public static final int LAN_VIEW_MARGIN = %d;' % LAN_VIEW_MARGIN, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_DIV = %r;' % LAN_MOVE_DIV, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_MIN = %r;' % LAN_MOVE_MIN, dfs))
dfs.addField(CtField.make('public static final double LAN_MOVE_MAX = %r;' % LAN_MOVE_MAX, dfs))
for _nf, _nd in zip(LAN_FIELDS, LAN_DEF):
    dfs.addField(CtField.make('public static volatile int %s = %d;' % (_nf, _nd), dfs))      # config rows lantern.*
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_H = new int[5];', dfs))      # per rarity: the helper's height (0 = none)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_L = new int[5];', dfs))      # per rarity: the helper's light level
dfs.addField(CtField.make('public static volatile float[] LAN_TAB_R = new float[5];', dfs))  # per rarity: the reach it reaches (blocks)
dfs.addField(CtField.make('public static volatile String LAN_SIG = "";', dfs))                # the settings the table was built from
dfs.addField(CtField.make('public static volatile int LAN_EPOCH = 0;', dfs))                  # +1 per rebuild (players decide again)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_M = new int[5];', dfs))      # 0.5.5: per rarity: ring lights (0 = one light)
dfs.addField(CtField.make('public static volatile int[] LAN_TAB_P = new int[5];', dfs))      # 0.5.5: per rarity: the ring radius, half blocks
dfs.addField(CtField.make('public static final int LAN_RING_MAX = %d;' % LAN_RING_MAX, dfs))
dfs.addField(CtField.make('public static final double[] LAN_COS = new double[] { %s };' % ", ".join(repr(_c) for _c in LAN_COS), dfs))
JM(dfs, r"""
public static double lanLight(int level, double dist) {
  if (level <= 0) return 0.0;
  double c = (double) level / 15.0;
  double d = dist < 0.0 ? 0.0 : dist;
  if (d >= 0.635 * (double) level || d >= 10.0 * c) return 0.0;
  double x = 1.0 - 0.1 * d / c;
  return 0.8 * c * x * Math.sqrt(x);
}""")
JM(dfs, r"""
public static int lanMaxLevel(double dist, double cap) {
  int lo = 0;
  int hi = 255;
  while (lo < hi) {
    int mid = (lo + hi + 1) / 2;
    if (lanLight(mid, dist) <= cap) lo = mid; else hi = mid - 1;
  }
  return lo;
}""")
JM(dfs, r"""
public static double lanReach(int level, double h) {
  if (lanLight(level, h) < LAN_VIS) return 0.0;
  double lo = 0.0;
  double hi = 400.0;
  for (int i = 0; i < 50; i++) {
    double m = (lo + hi) * 0.5;
    if (lanLight(level, Math.sqrt(h * h + m * m)) >= LAN_VIS) lo = m; else hi = m;
  }
  return lo;
}""")
# 0.5.5: the ring's lit reach (the Python lan_ring_reach: same arithmetic, same order, the same cos literals)
JM(dfs, r"""
public static double lanRingReach(int level, double h, int m, double rho) {
  double hh = h * h;
  double worst = 400.0;
  for (int k = 0; k < 2; k++) {
    double c = k == 0 ? 1.0 : LAN_COS[m];
    int i = 0;
    while (i < 1600) {
      double x = (double) i * 0.25;
      double d1 = Math.sqrt(x * x + hh);
      double d2 = Math.sqrt(x * x + rho * rho - 2.0 * x * rho * c + hh);
      if (lanLight(level, d1 < d2 ? d1 : d2) < LAN_VIS) break;
      i++;
    }
    double r = i == 0 ? 0.0 : (double) (i - 1) * 0.25;
    if (r < worst) worst = r;
  }
  return worst;
}""")
JM(dfs, r"""
public static int lanGlow(int t) {
  switch (t) {
    case 1: return LAN_GLOW1;
    case 2: return LAN_GLOW2;
    case 3: return LAN_GLOW3;
    case 4: return LAN_GLOW4;
    default: return 0;
  }
}""")
JM(dfs, r"""
public static int lanReachOf(int t) {
  switch (t) {
    case 1: return LAN_REACH1;
    case 2: return LAN_REACH2;
    case 3: return LAN_REACH3;
    case 4: return LAN_REACH4;
    default: return 0;
  }
}""")
JM(dfs, r"""
public static double lanCap(int t) {
  int g = lanGlow(t);
  return lanLight(g > 0 ? g : LAN_TORCH, LAN_PD);
}""")
# one rarity's hidden lights (the Python lan_solve5): ONE light first - the LOWEST height (5 .. lantern.height) whose cap-limited level,
# never above lantern.edge, reaches the reach row; else the best of those + a ring of m (3 .. lantern.lights - 1, at most LAN_RING_MAX)
# lights of that level and height, the smallest m and then the smallest radius (half blocks) that reaches it; the best reach when nothing
# does; none when the glow alone reaches it. out = { height, level } in hh / ll, the reach in rr, the ring in mm / pp (0.5.5)
JM(dfs, r"""
public static void lanSolve(int t, int[] hh, int[] ll, float[] rr, int[] mm, int[] pp) {
  int g = lanGlow(t);
  double own = lanReach(g, 0.0);
  int want = lanReachOf(t);
  hh[t] = 0;
  ll[t] = 0;
  rr[t] = (float) own;
  mm[t] = 0;
  pp[t] = 0;
  if ((double) want <= own + 0.5) return;
  double cap = lanCap(t);
  int hmax = LAN_HEIGHT;
  int emax = LAN_EDGE;
  double best = own;
  for (int h = LAN_MINH; h <= hmax; h++) {
    int lv = lanMaxLevel((double) h - LAN_PZ, cap);
    if (lv > emax) lv = emax;
    if (lv <= 0) continue;
    double r = lanReach(lv, (double) h);
    if (r > best + 0.000000001) { best = r; hh[t] = h; ll[t] = lv; rr[t] = (float) r; }
    if (r >= (double) want) { hh[t] = h; ll[t] = lv; rr[t] = (float) r; return; }
  }
  int h0 = hh[t];
  int l0 = ll[t];
  if (h0 <= 0) return;
  int mmax = LAN_LIGHTS - 1;
  if (mmax > LAN_RING_MAX) mmax = LAN_RING_MAX;
  for (int m = 3; m <= mmax; m++) {
    for (int p2 = 1; p2 <= 2 * want; p2++) {
      double r = lanRingReach(l0, (double) h0, m, (double) p2 * 0.5);
      if (r > best + 0.000000001) { best = r; rr[t] = (float) r; mm[t] = m; pp[t] = p2; }
      if (r >= (double) want) { rr[t] = (float) r; mm[t] = m; pp[t] = p2; return; }
    }
  }
}""")
JM(dfs, r"""
public static synchronized void lanTable() {
  String sig = LAN_GLOW1 + "," + LAN_GLOW2 + "," + LAN_GLOW3 + "," + LAN_GLOW4 + "," + LAN_REACH1 + "," + LAN_REACH2 + "," + LAN_REACH3 + "," + LAN_REACH4 + "," + LAN_HEIGHT + "," + LAN_EDGE + "," + LAN_LIGHTS;
  if (sig.equals(LAN_SIG)) return;
  int[] hh = new int[5];
  int[] ll = new int[5];
  float[] rr = new float[5];
  int[] mm = new int[5];
  int[] pp = new int[5];
  for (int t = 1; t <= 4; t++) lanSolve(t, hh, ll, rr, mm, pp);
  LAN_TAB_M = mm;
  LAN_TAB_P = pp;
  LAN_TAB_H = hh;
  LAN_TAB_L = ll;
  LAN_TAB_R = rr;
  LAN_SIG = sig;
  LAN_EPOCH = LAN_EPOCH + 1;
}""")
JM(dfs, r"""
public static int lanKey(int level) {
  int r = level < 1 ? 1 : (level > 255 ? 255 : level);
  int g = (r * 10 + 5) / 11;
  int b = (r * 9 + 5) / 11;
  if (g < 1) g = 1;
  if (b < 1) b = 1;
  return (LAN_SIG_R << 24) | (r << 16) | (g << 8) | b;
}""")
# the helper's light: WHITE (red = green = blue = the level) - the client fades each channel on its own, a torch tint would reach the ground
# red only (review finding 1); the glow on the player keeps the torch tint (lanKey)
JM(dfs, r"""
public static int lanHKey(int level) {
  int l = level < 1 ? 1 : (level > 255 ? 255 : level);
  return (LAN_SIG_R << 24) | (l << 16) | (l << 8) | l;
}""")
JM(dfs, LANJ(r"""
public static @CLT@ lanColor(int k) {
  return new @CLT@((byte) (k >>> 24), (byte) (k >>> 16), (byte) (k >>> 8), (byte) k);
}"""))
JM(dfs, LANJ(r"""
public static int lanKeyOf(@CLT@ c) {
  if (c == null) return 0;
  return ((c.radius & 255) << 24) | ((c.red & 255) << 16) | ((c.green & 255) << 8) | (c.blue & 255);
}"""))
# OUR light (radius byte LAN_SIG_R + the exact torch tint of its red level): another mod's or the builder tool's light never matches
JM(dfs, LANJ(r"""
public static boolean lanOurs(@CLT@ c) {
  if (c == null || (c.radius & 255) != LAN_SIG_R || (c.red & 255) < 1) return false;
  return lanKeyOf(c) == lanKey(c.red & 255);
}"""))
# the reach a rarity shows (bag page, /accessories lines): what the glow alone lights when there is no helper (a reach row below the glow's
# own ~6 blocks no longer reads "about 0 blocks"), else the reach row when it is reached, else what is reached (rounded)
JM(dfs, r"""
public static int lanShown(int t) {
  if (t < 1 || t > 4) return 0;
  lanTable();
  float r = LAN_TAB_R[t];
  if (LAN_TAB_H[t] <= 0) return Math.round(r);
  int want = lanReachOf(t);
  if (r >= (float) want) return want;
  return Math.round(r);
}""")
JM(dfs, r"""
public static String lanGlowText(int t) {
  int g = lanGlow(t);
  if (g <= 0) return "no glow";
  if (g == LAN_TORCH) return "glows like a torch";
  return "glows at light " + g + " (a torch is " + LAN_TORCH + ")";
}""")
JM(dfs, r"""
public static String lanText(int t) {
  if (t < 1 || t > 4) return "";
  lanTable();
  return lanGlowText(t) + ", lights about " + lanShown(t) + " blocks around you";
}""")
# the bag page row (short: one 422 px line at 16 px): "glows like a torch" (no helper) / "torch glow, lights about 48 blocks"
JM(dfs, r"""
public static String lanRow(int t) {
  if (t < 1 || t > 4) return "";
  lanTable();
  int g = lanGlow(t);
  if (LAN_TAB_H[t] <= 0) {
    if (g <= 0) return "no light";
    if (g == LAN_TORCH) return "glows like a torch";
    return "glows at light " + g;
  }
  String gs = "";
  if (g == LAN_TORCH) gs = "torch glow, ";
  else if (g > 0) gs = "glow " + g + ", ";
  return gs + "lights about " + lanShown(t) + " blocks";
}""")
dfs.addMethod(CtNewMethod.make("""
public static boolean isAccessory(String id) {
  if (id == null) return false;
  if (id.startsWith("Skyy_Talisman_")) return true;
  return id.startsWith("Skyy_Accessory_") && !id.equals(BAG);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isTalisman(String id) {
  return id != null && id.startsWith("Skyy_Talisman_") && id.length() > "Skyy_Talisman_".length();
}""", dfs))
# "Skyy_Talisman_Vitality_Ring" -> "Vitality"
dfs.addMethod(CtNewMethod.make("""
public static String familyOf(String id) {
  if (!isTalisman(id)) return null;
  String tail = id.substring("Skyy_Talisman_".length());
  int k = tail.lastIndexOf('_');
  return k > 0 ? tail.substring(0, k) : tail;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static int familyIndex(String fam) {
  if (fam == null) return -1;
  for (int i = 0; i < FAMILIES.length; i++) if (FAMILIES[i].equals(fam)) return i;
  return -1;
}""", dfs))
# "Skyy_Accessory_Workbench_T2" -> "Workbench" ; ids without _T<n> -> whole tail
dfs.addMethod(CtNewMethod.make("""
public static String benchOf(String id) {
  if (!isAccessory(id) || isTalisman(id)) return null;
  String tail = id.substring("Skyy_Accessory_".length());
  int t = tail.lastIndexOf("_T");
  if (t > 0) {
    boolean digits = t + 2 < tail.length();
    for (int i = t + 2; i < tail.length(); i++) if (!Character.isDigit(tail.charAt(i))) digits = false;
    if (digits) return tail.substring(0, t);
  }
  return tail;
}""", dfs))
# 0.4.2: a retired bench accessory (Alchemy Bench T1-T4, Cooking Bench; 0.4.3: no longer the Campfire): kept as an item, does nothing
dfs.addMethod(CtNewMethod.make("""
public static boolean isRetired(String id) {
  if (NV_ID.equals(id)) return true;   // 0.5.4: Night Vision - replaced by the Lantern
  if (id == null || isTalisman(id) || OMNI.equals(id)) return false;
  String b = benchOf(id);
  if (b == null) return false;
  for (int i = 0; i < RETIRED.length; i++) if (RETIRED[i].equalsIgnoreCase(b)) return true;
  return false;
}""", dfs))
# 0.4.2: Equip refusal on the page (one line, no commas / colons / parentheses) and the longer chat explanation
dfs.addMethod(CtNewMethod.make("""
public static String retiredWhy(String id) {
  if (NV_ID.equals(id)) return NV_WHY;   // 0.5.4
  String b = benchOf(id);
  if ("Alchemybench".equalsIgnoreCase(b)) return "Retired - brew at a real Alchemy Bench now - it takes ingredients from your Magic Bags";
  if ("Cookingbench".equalsIgnoreCase(b)) return "Retired - cook at a real Cooking Bench now - it takes ingredients from your Magic Bags";
  return "Retired - this accessory does nothing any more";   // 0.4.3: the Campfire is active again - no retired id reaches this
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String retiredChat(String id) {
  if (NV_ID.equals(id)) return NV_CHAT;   // 0.5.4
  String b = benchOf(id);
  String tail = " This accessory does nothing any more and cannot be equipped. If one is still in your Void Charms, Unequip takes it out.";
  if ("Alchemybench".equalsIgnoreCase(b)) return "The Alchemy Bench accessory is retired: Alchemy is a skill now. Brew at a real Alchemy Bench - it takes ingredients straight from your Magic Bags." + tail;
  if ("Cookingbench".equalsIgnoreCase(b)) return "The Cooking Bench accessory is retired: Cooking is a skill now. Cook at a real Cooking Bench - it takes ingredients straight from your Magic Bags." + tail;
  return "This accessory is retired." + tail;   // 0.4.3: the Campfire is active again - no retired id reaches this
}""", dfs))
# 0.5: the tier of a "_T<digits>" tail (the part 2 line ids Skyy_Talisman_<Key>_T1..T4), else -1
JM(dfs, r"""
public static int tailTier(String id) {
  if (!isTalisman(id)) return -1;
  int k = id.lastIndexOf('_');
  if (k < 0 || k + 2 >= id.length() + 1) return -1;
  String w = id.substring(k + 1);
  if (w.length() < 2 || w.charAt(0) != 'T') return -1;
  for (int i = 1; i < w.length(); i++) if (!Character.isDigit(w.charAt(i))) return -1;
  try { return Integer.parseInt(w.substring(1)); } catch (Throwable e) { return -1; }
}""")
# 0.5 tier 1..4 of a stat accessory: a _T<n> tail, then the id words Common..Epic, then the legacy words (Talisman 2, Ring 3, Artifact 4,
# Legendary 4 - the old fifth id folds into Legendary); bench accessories keep their _T<n>
JM(dfs, r"""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isTalisman(id)) {
    int tt = tailTier(id);
    if (tt > 0) return tt;
    for (int r = ID_WORD.length - 1; r >= 1; r--) if (id.endsWith("_" + ID_WORD[r])) return r;
    for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return LEGACY_TIER[j];
    return 1;
  }
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""")
# 0.4 / 0.5: an old stat accessory id (0.2/0.3 Talisman / Ring / Artifact, and 0.4's fifth id _Legendary): asset kept, no recipe
JM(dfs, r"""
public static boolean isLegacy(String id) {
  if (!isTalisman(id) || tailTier(id) > 0) return false;
  for (int j = 0; j < LEGACY_WORD.length; j++) if (id.endsWith("_" + LEGACY_WORD[j])) return true;
  return false;
}""")
# "Skyy_Talisman_Vitality_Ring" -> "..._Rare", "Skyy_Talisman_Vitality_Legendary" -> "..._Epic" (Legendary); every other id unchanged
JM(dfs, r"""
public static String modernOf(String id) {
  if (!isLegacy(id)) return id;
  String f = familyOf(id);
  int t = tierOf(id);
  if (f == null || t < 1 || t >= ID_WORD.length) return id;
  return "Skyy_Talisman_" + f + "_" + ID_WORD[t];
}""")
# 0.5 rarity 1..4 (Normal..Legendary, the gear ladder) of every accessory: stat accessories by tier, bench I Normal, II Unique,
# III Rare, IV and up Legendary, the Omni Legendary (crafted: never above Legendary); 5 / 6 (Fabled / Mythic) are for the rare finds
JM(dfs, r"""
public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isRetired(id)) return 0;   // 0.4.2: retired - never counts (future accessory power reads rarityOf)
  if (OMNI.equals(id)) return 4;
  int t = tierOf(id);
  if (t < 1) t = 1;
  if (t > 4) t = 4;
  return t;
}""")
JM(dfs, r"""
public static String rarityName(String id) {
  if (isRetired(id)) return "Does nothing";   // 0.4.2: the page's rarity column for a retired accessory
  return DISPLAY[rarityOf(id)];
}""")
dfs.addMethod(CtNewMethod.make("""
public static String rarityColor(String id) {
  if (isRetired(id)) return RETIRED_COLOR;   // 0.4.2
  return RARITY_COLOR[rarityOf(id)];
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean hasOmni(String[] s) {
  if (s == null) return false;
  for (int i = 0; i < s.length; i++) if (OMNI.equals(s[i])) return true;
  return false;
}""", dfs))
# one-per-group key used by AccStore.equip: bench id for bench accessories, "T:<family>" for talismans
dfs.addMethod(CtNewMethod.make("""
public static String groupOf(String id) {
  if (isTalisman(id)) return "T:" + familyOf(id);
  return benchOf(id);
}""", dfs))
# 0.5.4 the Lantern: one of its four ids (a word id of family Lantern), the best rarity in a bag (0 = none), the givetier names
JM(dfs, r"""
public static boolean isLantern(String id) {
  return isTalisman(id) && LAN_FAM.equals(familyOf(id)) && !isLegacy(id) && tailTier(id) <= 0;
}""")
JM(dfs, r"""
public static boolean isLanternId(String id) {
  if (id == null) return false;
  for (int i = 0; i < LAN_IDS.length; i++) if (LAN_IDS[i].equals(id)) return true;
  return false;
}""")
JM(dfs, r"""
public static int lanBest(String[] s) {
  int best = 0;
  if (s == null) return 0;
  for (int i = 0; i < s.length; i++) {
    if (!isLantern(s[i])) continue;
    int t = tierOf(s[i]);
    if (t > 4) t = 4;
    if (t > best) best = t;
  }
  return best;
}""")
JM(dfs, r"""
public static boolean isLanName(String w) {
  if (w == null) return false;
  String x = w.trim();
  return x.equalsIgnoreCase(LAN_ADMIN) || x.equalsIgnoreCase("Lanterns");
}""")
# highest tier per line (index = FAMILIES) among the bag slots - ONLY THE HIGHEST RARITY OF A LINE COUNTS (a duplicate that slipped in
# through stashK changes nothing: the maximum is taken)
dfs.addMethod(CtNewMethod.make("""
public static int[] bestTiers(String[] s) {
  int[] out = new int[FAMILIES.length];
  if (s == null) return out;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (!isTalisman(id)) continue;
    int f = familyIndex(familyOf(id));
    if (f < 0) continue;
    int t = tierOf(id);
    if (t > 4) t = 4;   // 0.5: Normal..Legendary
    if (t > out[f]) out[f] = t;
  }
  return out;
}""", dfs))
# 0.5: the Java of AccDefs.statParts (per line, the short texts of its stats at one tier, live numbers) and AccDefs.lineOn, generated
# from the booster table when this script runs (a new stat kind needs its text here and a tooltip in TIPS)
def _stat_code():
    TXT = {   # kind -> Java expression of one part ((v) = the number); manaFloor rides along with manaPct
        "maxHealth": '"+" + numText(v) + " max Health"',
        "maxStamina": '"+" + numText(v) + " max Stamina"',
        "staminaRegen": '"+" + numText(v) + "% Stamina Regen"',
        "healPct": '"Heals " + numText(v) + "% max Health every " + REGEN_EVERY + " s"',
        "speedPct": '"+" + numText(v) + "% Speed"',
        "str": '"+" + numText(v) + " Strength"',                  # part 2
        "mp": '"+" + numText(v) + " Magical Power"',
        "def": '"+" + numText(v) + " Defense"',
    }
    PAIRS = {   # part 2: two stats of one line on ONE part (the rider is left out when its number is 0)
        "cc": ("cd", '"+" + numText(a) + "% Crit Chance"', '"+" + numText(r) + "% Crit Damage"'),
        "fallPct": ("jumpPct", '"-" + numText(a) + "% fall damage"', '"+" + numText(r) + "% jump height"'),
    }
    lines = []
    for li, bo in enumerate(BOOSTERS):
        body = []
        ks = dict((kd, E[bo[1] + "." + st]) for st, kd, _v in bo[5])
        for st, kd, _v in bo[5]:
            e = str(E[bo[1] + "." + st])
            if kd in ("manaFloor", "cd", "jumpPct"):
                continue
            if kd in PAIRS:
                rk, ta, tr = PAIRS[kd]
                rx = ("b[" + str(ks[rk]) + " * 5 + t]") if rk in ks else "0.0f"
                body.append("    float a" + e + " = b[" + e + " * 5 + t];\n    float r" + e + " = " + rx + ";\n    String p" + e + " = \"\";\n"
                            "    if (a" + e + " > 0.0f) p" + e + " = " + ta.replace("(a)", "(a" + e + ")") + ";\n"
                            "    if (r" + e + " > 0.0f) p" + e + " = p" + e + " + (p" + e + ".length() > 0 ? \", \" : \"\") + " +
                            tr.replace("(r)", "(r" + e + ")") + ";\n    if (p" + e + ".length() > 0) out.add(p" + e + ");")
                continue
            if kd == "manaPct":
                fl = ks.get("manaFloor")
                fx = ("b[" + str(fl) + " * 5 + t]") if fl is not None else "0.0f"
                body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    float f" + e + " = " + fx + ";\n    if (v" + e + " > 0.0f || f" + e +
                            " > 0.0f) out.add(\"+\" + numText(v" + e + ") + \"% max Mana\" + (f" + e + " > 0.0f ? \" (at least +\" + numText(f" + e +
                            ") + \")\" : \"\"));")
                continue
            assert kd in TXT, "0.5: no text for the stat kind %s - add it to _stat_code (and to TIPS)" % kd
            body.append("    float v" + e + " = b[" + e + " * 5 + t];\n    if (v" + e + " > 0.0f) out.add(" + TXT[kd].replace("(v)", "(v" + e + ")") + ");")
        lines.append("  if (li == " + str(li) + ") {\n" + "\n".join(body) + "\n  }")
    return ("public static String[] statParts(int li, int t) {\n  java.util.ArrayList out = new java.util.ArrayList();\n"
            "  float[] b = BOOST;\n  if (t < 1 || t > 4) return new String[0];\n" + "\n".join(lines) +
            "\n  return (String[]) out.toArray(new String[0]);\n}")
STAT_JAVA = _stat_code()
LINEON_JAVA = ("public static boolean lineOn(int li) {\n  switch (li) {\n" +
               "".join("    case %d: return LINE_%s;\n" % (i, b[1].upper()) for i, b in enumerate(BOOSTERS)) +
               "    default: return false;\n  }\n}")
# 0.5: 24.0 -> "24", 1.5 -> "1.5", 0.25 -> "0.25" (up to 2 decimals, values are >= 0)
JM(dfs, r"""
public static String numText(float v) {
  long c = Math.round((double) v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""")
# 0.5: is a line switched on (config rows line.<Admin>; generated from the table)
JM(dfs, LINEON_JAVA)
# 0.5: line index of an admin name, a family key (the old names Vitality / Endurance / Intelligence as aliases) or a line name; -1 = none
JM(dfs, r"""
public static int lineOf(String name) {
  if (name == null) return -1;
  String n = name.trim();
  for (int i = 0; i < FAMILIES.length; i++) {
    if (LINE_ADMIN[i].equalsIgnoreCase(n) || FAMILIES[i].equalsIgnoreCase(n) || LINE_NAME[i].equalsIgnoreCase(n)) return i;
  }
  return -1;
}""")
# 0.5: rarity word or number -> tier 1..4 (Normal, Unique, Rare, Legendary or 1-4); -1 = not a line rarity
JM(dfs, r"""
public static int rarityIndex(String w) {
  if (w == null) return -1;
  String x = w.trim();
  for (int t = 1; t <= 4; t++) if (DISPLAY[t].equalsIgnoreCase(x) || String.valueOf(t).equals(x)) return t;
  return -1;
}""")
JM(dfs, r"""
public static String idOf(int li, int t) {
  if (li < 0 || li >= FAMILIES.length || t < 1 || t > 4) return null;
  return LINE_IDS[li * 4 + t - 1];
}""")
JM(dfs, r"""
public static boolean isBoosterId(String id) {
  if (id == null) return false;
  for (int i = 0; i < LINE_IDS.length; i++) if (LINE_IDS[i].equals(id)) return true;
  return false;
}""")
# 0.5: the short texts of one line's stats at one tier, with the live numbers (generated from the booster table)
JM(dfs, STAT_JAVA)
# 0.5: the Bonuses well - one key / value row per line with its best accessory in the bag (key = the line name, value = its stats at
# that rarity with the live numbers, or "switched off"), up to BONUS_MAX rows: [key0, value0, key1, value1, ...], "" = an empty row.
# (AccGear.pageRows adds the SkyyGear / SkyySkills notes in the free rows.)
JM(dfs, r"""
public static String[] bonusRows(String[] s) {
  String[] out = new String[BONUS_MAX * 2];
  for (int i = 0; i < out.length; i++) out[i] = "";
  int[] best = bestTiers(s);
  int n = 0;
  for (int li = 0; li < FAMILIES.length; li++) {
    if (best[li] <= 0 || n >= BONUS_MAX) continue;
    out[n * 2] = LINE_NAME[li];
    if (!lineOn(li)) { out[n * 2 + 1] = "switched off"; n++; continue; }
    String[] p = statParts(li, best[li]);
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(", "); sb.append(p[k]); }
    out[n * 2 + 1] = sb.length() > 0 ? sb.toString() : "nothing (its numbers are 0 on this server)";
    n++;
  }
  int lt = lanBest(s);   // 0.5.4: the Lantern - its own line, after the booster lines
  if (lt > 0 && n < BONUS_MAX) {
    out[n * 2] = LAN_LINE;
    out[n * 2 + 1] = LINE_LANTERN ? lanRow(lt) : "switched off";
    n++;
  }
  if (hasNv(s) && n < BONUS_MAX) {   // 0.5.4: a retired Night Vision still in the bag
    out[n * 2] = NV_LINE;
    out[n * 2 + 1] = NV_ROW;
    n++;
  }
  return out;
}""")
JM(dfs, r"""
public static String bonusText(String[] s) {
  String[] l = bonusRows(s);
  if (l[0].length() > 0) return "Bonuses - your best accessory of each line counts";
  return hasOmni(s) ? "Bonuses - no stat accessories yet - the Omni counts as every bench accessory" : "Bonuses - none yet - put accessories in Void Charms";
}""")
# 0.5 part 2: the tiers that COUNT right now (bestTiers with the switched-off lines at 0) - the effect tick, the gear:extra text, the notes
JM(dfs, r"""
public static int[] activeTiers(String[] s) {
  int[] best = bestTiers(s);
  for (int li = 0; li < best.length; li++) if (!lineOn(li)) best[li] = 0;
  return best;
}""")
# 0.5 part 2: does line li at tier t send anything to SkyyGear (a gear:extra entry above 0) / have a fall-damage part above 0?
JM(dfs, r"""
public static boolean sendsGear(int li, int t) {
  if (t < 1 || t > 4) return false;
  for (int e = 0; e < E_GEAR.length; e++) if (E_LINE[e] == li && E_GEAR[e].length() > 0 && BOOST[e * 5 + t] >= 1.0f) return true;
  return false;
}""")
JM(dfs, r"""
public static boolean hasFall(int li, int t) {
  return E_FALL >= 0 && E_LINE[E_FALL] == li && t >= 1 && t <= 4 && BOOST[E_FALL * 5 + t] > 0.0f;
}""")
dfs.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (NV_ID.equals(id)) return NV_LINE + " Accessory - retired";   // 0.5.4: replaced by the Lantern
  if (isLantern(id)) {   // 0.5.4: "<Rarity> Lantern Accessory"
    int lr = rarityOf(id);
    return lr >= 1 && lr < DISPLAY.length ? DISPLAY[lr] + " " + LAN_LINE + " Accessory" : LAN_LINE + " Accessory";
  }
  if (isTalisman(id)) {   // 0.5: "<Rarity> <Line> Accessory" - never the family key or the old word (a legacy id shows its rarity's name)
    int r = rarityOf(id);
    int li = familyIndex(familyOf(id));
    String ln = li >= 0 ? LINE_NAME[li] + " Accessory" : "Accessory";
    return r >= 1 && r < DISPLAY.length ? DISPLAY[r] + " " + ln : ln;
  }
  if (OMNI.equals(id)) return "Omni Accessory";
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;
  if (isRetired(id)) {   // 0.4.2 (BENCH_NAMES holds only the active benches); no parentheses in inline page text; numeral only for multi-tier benches
    for (int j = 0; j < RETIRED.length; j++) if (RETIRED[j].equalsIgnoreCase(b)) return RETIRED_NAMES[j] + (RETIRED_MAX[j] > 1 ? " " + roman(tierOf(id)) : "") + " - retired";
  }
  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_MAX[i] > 1 ? BENCH_NAMES[i] + " " + roman(tierOf(id)) : BENCH_NAMES[i];
  return b.replace('_', ' ') + " " + roman(tierOf(id));
}""", dfs))

# 0.5: what the bag's "same or better ... already equipped" refusal names
JM(dfs, r"""
public static String lineLabel(String id) {
  if (NV_ID.equals(id)) return NV_LINE + " Accessory";   // 0.5.3 (0.5.4: retired - Equip answers with retiredWhy first)
  if (isLantern(id)) return LAN_LINE + " Accessory";   // 0.5.4
  if (isTalisman(id)) {
    int li = familyIndex(familyOf(id));
    return li >= 0 ? LINE_NAME[li] + " Accessory" : "accessory of that line";
  }
  return OMNI.equals(id) ? "Omni accessory" : "bench accessory";
}""")
# 0.5 bridge acc:defs (spec 5.9): every rarity of every line as name:key:tier:itemId:rarity:ap:sources, records joined by ","
JM(dfs, r"""
public static String defsText() {
  StringBuilder sb = new StringBuilder();
  for (int li = 0; li < FAMILIES.length; li++) {
    for (int t = 1; t <= 4; t++) {
      if (sb.length() > 0) sb.append(',');
      sb.append(LINE_ADMIN[li]).append(':').append(FAMILIES[li]).append(':').append(t).append(':').append(LINE_IDS[li * 4 + t - 1]);
      sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LINE_SRC[li * 4 + t - 1]);
    }
  }
  for (int t = 1; t <= 4; t++) {   // 0.5.4: the Lantern - one record per rarity (0.5.3's Night Vision record is gone)
    if (sb.length() > 0) sb.append(',');
    sb.append(LAN_ADMIN).append(':').append(LAN_FAM).append(':').append(t).append(':').append(LAN_IDS[t - 1]);
    sb.append(':').append(DISPLAY[t]).append(':').append(AP[t]).append(':').append(LAN_SRC);
  }
  return sb.toString();
}""")
# 0.5 /accessories lines: one chat line per line (its four rarities with the live numbers); ids = the admin's extra id line
JM(dfs, r"""
public static String[] linesText(boolean ids) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int li = 0; li < FAMILIES.length; li++) {
    StringBuilder sb = new StringBuilder();
    sb.append(LINE_NAME[li]).append(" Accessory (").append(LINE_ADMIN[li]).append(")");
    if (!lineOn(li)) sb.append(" - SWITCHED OFF on this server");
    sb.append(": ");
    for (int t = 1; t <= 4; t++) {
      if (t > 1) sb.append(" | ");
      sb.append(DISPLAY[t]).append(' ');
      String[] p = statParts(li, t);
      if (p.length == 0) sb.append("nothing");
      for (int k = 0; k < p.length; k++) { if (k > 0) sb.append(" and "); sb.append(p[k]); }
    }
    out.add(sb.toString());
    if (ids) {
      StringBuilder ib = new StringBuilder("    ids: ");
      for (int t = 1; t <= 4; t++) { if (t > 1) ib.append(" / "); ib.append(LINE_IDS[li * 4 + t - 1]); }
      out.add(ib.toString());
    }
  }
  StringBuilder nb = new StringBuilder();   // 0.5.4: the Lantern - its four rarities (0.5.3's Night Vision line is gone: retired)
  nb.append(LAN_LINE).append(" Accessory (").append(LAN_ADMIN).append(")");
  if (!LINE_LANTERN) nb.append(" - SWITCHED OFF on this server");
  nb.append(": ");
  for (int t = 1; t <= 4; t++) {
    if (t > 1) nb.append(" | ");
    nb.append(DISPLAY[t]).append(' ').append(lanText(t));
  }
  nb.append(LAN_SHARE ? " - everyone sees the glow and the far light" : " - everyone sees your glow, only you see the far light");
  out.add(nb.toString());
  if (ids) {
    StringBuilder lb = new StringBuilder("    ids: ");
    for (int t = 1; t <= 4; t++) { if (t > 1) lb.append(" / "); lb.append(LAN_IDS[t - 1]); }
    out.add(lb.toString());
  }
  return (String[]) out.toArray(new String[0]);
}""")
# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id, at the best tier (a bench id -> max tier
# reduction, the same one SkyySacks' accessories() parser does). Real bench accessories first (slot order; the stored id of the best
# tier is kept as-is), then - when the Omni is in the bag - every bench at BENCH_MAX: a bench not listed yet is appended as the
# synthetic "Skyy_Accessory_<BenchId>_T<maxTier>", a listed bench whose real tier is lower is replaced IN PLACE by that synthetic id
# (review fix: a plain string-containment dedupe published a real Workbench_T2 AND the synthetic Workbench_T3, so SkyyMenu's
# "N bench accessories" count read 14 instead of 13). The Omni id itself is not listed, so acc:has keeps its 0.1 meaning.
# keys = bench id of out[k] (same index), best[k] = its tier; at most s.length + BENCH_IDS.length entries.
# 0.4.2: a retired bench accessory is skipped (an equipped old copy unlocks nothing), and BENCH_IDS holds only the ACTIVE benches, so
# the Omni does not grant the retired ones either.
dfs.addMethod(CtNewMethod.make("""
public static java.util.ArrayList benchList(String[] s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == null) return out;
  java.util.ArrayList keys = new java.util.ArrayList();
  int[] best = new int[s.length + BENCH_IDS.length];
  boolean omni = false;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (id == null || isTalisman(id) || !isAccessory(id)) continue;
    if (OMNI.equals(id)) { omni = true; continue; }
    String bn = benchOf(id);
    if (bn == null) continue;
    if (isRetired(id)) continue;   // 0.4.2
    int t = tierOf(id);
    int k = keys.indexOf(bn);
    if (k < 0) { keys.add(bn); out.add(id); best[out.size() - 1] = t; }
    else if (t > best[k]) { out.set(k, id); best[k] = t; }
  }
  if (omni) {
    for (int j = 0; j < BENCH_IDS.length; j++) {
      String syn = "Skyy_Accessory_" + BENCH_IDS[j] + "_T" + BENCH_MAX[j];
      int k2 = keys.indexOf(BENCH_IDS[j]);
      if (k2 < 0) { keys.add(BENCH_IDS[j]); out.add(syn); best[out.size() - 1] = BENCH_MAX[j]; }
      else if (BENCH_MAX[j] > best[k2]) { out.set(k2, syn); best[k2] = BENCH_MAX[j]; }
    }
  }
  return out;
}""", dfs))

# ================= AccStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
st_.addField(CtField.make("public static final int MAIN = %d;" % MAIN_SLOTS, st_))   # 0.5: slot0..MAIN-1 in <key>.properties, the rest in <key>.more.properties
# 0.4.4: CAP stays the STORAGE size (0.5: 60 - the page, the un:<i> buttons); SLOTS = this server's limit for NEW equips (config row
# slots, kit field:, default 18). Accessories already in a slot >= SLOTS stay, keep counting and can be unequipped.
st_.addField(CtField.make("public static volatile int SLOTS = %d;" % SLOTS_DEF, st_))
# 0.5: bag files that could not be READ at load (path text -> reason): never overwritten afterwards, so a read error cannot wipe a bag
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADFILE = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static boolean RESTAMP_WARNED = false;", st_))
# 0.4.1: BAGS is keyed by the profile storage key (pkey String, PROFILES-CONTRACT rule 2), not the UUID
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", st_))
# 0.2 effect state (world thread writes, 5 s tick prunes offline players): CLOCK uuid -> float[]{secondsSinceSync, regenSeconds},
# SPEED uuid -> 0.3: MoveSync applier state float[]{lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed, targetJump, warned} (0.2: own speed state)
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SPEED = new java.util.concurrent.ConcurrentHashMap();", st_))
# 0.5.4: uuid -> the bag changed since the Lantern last looked (save, join, profile switch): AccLantern.step decides on the next world tick
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LPOKE = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", st_))
# 0.4.1 PROFILES-CONTRACT storage key helper (verbatim from tools/PROFILES-CONTRACT.md): active profile's key, uuid = profile 1
st_.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", st_))
# 0.4.1 rule 3: EPOCH uuid -> profile:epoch:<uuid> seen at the last publish, PUBKEY uuid -> pkey the last publish used (pruned like PUBLISHED)
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object epochOf(java.util.UUID u) {
  try { return bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { return null; }
}""", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object lock(java.util.UUID u) {
  Object o = LOCKS.get(u);
  if (o != null) return o;
  Object n = new Object();
  o = LOCKS.putIfAbsent(u, n);
  return o == null ? n : o;
}""", st_))
# 0.5: slots from..to-1 of one bag file (a missing file = empty slots); a file that cannot be read is remembered in BADFILE
JM(st_, r"""
public static void readInto(String[] s, java.nio.file.Path f, int from, int to) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    for (int i = from; i < to && i < s.length; i++) {
      String v = p.getProperty("slot" + i);
      if (v != null && v.trim().length() > 0) s[i] = v.trim();
    }
  } catch (Throwable t) {
    BADFILE.put(f.toString(), String.valueOf(t));
    warn("could not load bag file " + f + " - it is left as it is and not overwritten until the server restarts: " + t);
  }
}""")
# 0.4.1: the bag of storage key k; 0.5: slot0..8 from bags/<k>.properties (0.4.x's file, same format), slot9..59 from bags/<k>.more.properties
JM(st_, r"""
public static String[] slotsK(java.util.UUID u, String k) {
  String[] s = (String[]) BAGS.get(k);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(k);
    if (s != null) return s;
    s = new String[CAP];
    readInto(s, DIR.resolve(k + ".properties"), 0, MAIN);
    readInto(s, DIR.resolve(k + ".more.properties"), MAIN, CAP);
    BAGS.put(k, s);
    return s;
  }
}""")
# 0.5: true when a file of bag k could not be read at load: the page then moves nothing into or out of that bag (a move could not be
# saved, and an item put in would be lost at the next restart)
JM(st_, r"""
public static boolean isBad(String k) {
  if (DIR == null || k == null) return false;
  return BADFILE.containsKey(DIR.resolve(k + ".properties").toString()) || BADFILE.containsKey(DIR.resolve(k + ".more.properties").toString());
}""")
# 0.5: writes slots from..to-1 into one bag file (tmp + move). The main file is always written (0.4.5's format and comment); the second
# file only when it holds something or already exists (then it may become empty - it is never deleted). A BADFILE is never written.
JM(st_, r"""
public static void writeSlots(String[] s, String name, int from, int to, boolean always) throws java.io.IOException {
  java.nio.file.Path f = DIR.resolve(name);
  if (BADFILE.containsKey(f.toString())) { warn("bag file " + f + " could not be read at load, so it is not overwritten (restart after fixing or removing it)"); return; }
  java.util.Properties p = new java.util.Properties();
  boolean any = false;
  for (int i = from; i < to && i < s.length; i++) if (s[i] != null) { p.setProperty("slot" + i, s[i]); any = true; }
  if (!any && !always && !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path tmp = DIR.resolve(name + ".tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, from == 0 ? "SkyyAccessories bag" : "SkyyAccessories bag - slots 10 to 60 (0.5 and later)"); } finally { out.close(); }
  java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}""")
# 0.4.1: the bag of the player's ACTIVE profile
st_.addMethod(CtNewMethod.make("""
public static String[] slots(java.util.UUID u) {
  return slotsK(u, pkey(u));
}""", st_))
# copy of the bag for readers (talisman tick, page build) - never the live array
st_.addMethod(CtNewMethod.make("""
public static String[] snapshot(java.util.UUID u) {
  String[] s = slots(u);
  String[] c = new String[s.length];
  synchronized (lock(u)) { System.arraycopy(s, 0, c, 0, s.length); }
  return c;
}""", st_))
# acc:has keeps its 0.1 meaning (bench accessories only - SkyySacks 0.6.1 parses every id there as Skyy_Accessory_<Bench>_T<n>, so a
# talisman id made a bogus "itality Talisman I" craft tab); talismans go to acc:tal:<uuid>; acc:fn:has still answers for both.
# 0.4: acc:has = AccDefs.benchList (one entry per bench at its best tier, the Omni counting as every bench at max tier); acc:tal lists modern ids (legacy
# Talisman/Ring/Artifact published as their Uncommon/Rare/Epic id)
st_.addMethod(CtNewMethod.make(f"""
public static void publish(java.util.UUID u) {{
  Object ep = epochOf(u);   // 0.4.1: read BEFORE the key, so a later switch always looks newer
  synchronized (lock(u)) {{
    String k = pkey(u);
    String[] s = slotsK(u, k);
    StringBuilder acc = new StringBuilder();
    StringBuilder tal = new StringBuilder();
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || !{PKG}.AccDefs.isTalisman(s[i]) || {PKG}.AccDefs.isRetired(s[i])) continue;   // 0.5.4: not a retired one
      if (tal.length() > 0) tal.append(',');
      tal.append({PKG}.AccDefs.modernOf(s[i]));
    }}
    java.util.ArrayList bl = {PKG}.AccDefs.benchList(s);
    for (int i = 0; i < bl.size(); i++) {{
      if (acc.length() > 0) acc.append(',');
      acc.append((String) bl.get(i));
    }}
    bridge().put("acc:has:" + u.toString(), acc.toString());
    bridge().put("acc:tal:" + u.toString(), tal.toString());
    PUBLISHED.put(u, Boolean.TRUE);
    if (ep == null) EPOCH.remove(u); else EPOCH.put(u, ep);
    PUBKEY.put(u, k);
    LPOKE.put(u, Boolean.TRUE);   // 0.5.4: the Lantern looks at this bag on the next world tick
  }}
}}""", st_))
# 0.4.1: saves the bag of storage key k (the key the caller resolved once), then republishes the active profile; 0.5: two files
st_.addMethod(CtNewMethod.make("""
public static void saveK(java.util.UUID u, String k) {
  synchronized (lock(u)) {
    try {
      String[] s = slotsK(u, k);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      writeSlots(s, k + ".properties", 0, MAIN, true);
      writeSlots(s, k + ".more.properties", MAIN, CAP, false);
    } catch (Throwable t) { warn("could not save bag " + k + " for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  saveK(u, pkey(u));
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static boolean has(java.util.UUID u, String id) {{
  if (u == null || id == null) return false;
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: acc:fn:has never answers true for a retired accessory
  synchronized (lock(u)) {{
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (id.equals(s[i]) || id.equals({PKG}.AccDefs.modernOf(s[i]))) return true;
    }}
    if (id.startsWith("Skyy_Accessory_") && {PKG}.AccDefs.benchList(s).contains(id)) return true;   // 0.4: Omni = every bench at max tier
    return false;
  }}
}}""", st_))
# 0.4.4: the number of slots a NEW accessory may go into (SLOTS clamped to 1..the bag's length); = s.length with the default 9
st_.addMethod(CtNewMethod.make("""
public static int capOf(String[] s) {
  int c = SLOTS;
  if (c < 1) c = 1;
  if (s != null && c > s.length) c = s.length;
  return c;
}""", st_))
# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory
st_.addMethod(CtNewMethod.make(f"""
public static boolean canEquipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: never equipped (the page refuses first, with the reason)
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    boolean same = false;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return false;   // 0.5: an equal or better one anywhere in the line = refused
      same = true;
    }}
    if (same) return true;   // 0.5: every slot of the line is lower - the lowest is swapped out
    int cap = capOf(s);   // 0.4.4: a free slot below this server's limit (an in-place upgrade above is still fine)
    for (int i = 0; i < cap; i++) if (s[i] == null) return true;
    return false;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean canEquip(java.util.UUID u, String id) {
  return canEquipK(u, pkey(u), id);
}""", st_))
# equips id; returns the item id that was displaced (same group, lower tier) or "" when a free slot was used, or null when the bag is full / an equal or better one is in
st_.addMethod(CtNewMethod.make(f"""
public static String equipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return null;   // 0.4.2
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    int low = -1;
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || g == null || !g.equals({PKG}.AccDefs.groupOf(s[i]))) continue;
      if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;   // 0.5: an equal or better one anywhere in the line = refused
      if (low < 0 || {PKG}.AccDefs.tierOf(s[i]) < {PKG}.AccDefs.tierOf(s[low])) low = i;
    }}
    if (low >= 0) {{ String old = s[low]; s[low] = id; saveK(u, k); return old; }}   // 0.5: the lowest slot of the line
    int cap = capOf(s);   // 0.4.4: new accessories only go below this server's limit (canEquipK asks the same)
    for (int i = 0; i < cap; i++) if (s[i] == null) {{ s[i] = id; saveK(u, k); return ""; }}
    return null;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String equip(java.util.UUID u, String id) {
  return equipK(u, pkey(u), id);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequipK(java.util.UUID u, String k, int idx) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length || s[idx] == null) return null;
    String id = s[idx]; s[idx] = null; saveK(u, k); return id;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequip(java.util.UUID u, int idx) {
  return unequipK(u, pkey(u), idx);
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void putK(java.util.UUID u, String k, int idx, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    if (idx < 0 || idx >= s.length) return;
    s[idx] = id; saveK(u, k);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void put(java.util.UUID u, int idx, String id) {
  putK(u, pkey(u), idx, id);
}""", st_))
# last resort so an item can never vanish: first free slot, ignoring the one-per-group rule (bestTiers and SkyySacks use the best tier)
st_.addMethod(CtNewMethod.make("""
public static boolean stashK(java.util.UUID u, String k, String id) {
  synchronized (lock(u)) {
    String[] s = slotsK(u, k);
    for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; saveK(u, k); return true; }
    return false;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean stash(java.util.UUID u, String id) {
  return stashK(u, pkey(u), id);
}""", st_))
# 0.5.19 (acc:fn:bag): the accessories in bag k ("id,id,..."; retired ones left out), for SkyySacks' bench display + /craft counts
st_.addMethod(CtNewMethod.make(f"""
public static String listK(java.util.UUID u, String k) {{
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || {PKG}.AccDefs.isRetired(s[i])) continue;
      if (sb.length() > 0) sb.append(',');
      sb.append(s[i]);
    }}
    return sb.toString();
  }}
}}""", st_))
# 0.5.19: empty ONE slot holding exactly id (the Unequip path: saved at once + republished); returns that slot, -1 = none there
st_.addMethod(CtNewMethod.make(f"""
public static int takeK(java.util.UUID u, String k, String id) {{
  if (id == null || {PKG}.AccDefs.isRetired(id)) return -1;
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] != null && s[i].equals(id)) {{ s[i] = null; saveK(u, k); return i; }}
    }}
    return -1;
  }}
}}""", st_))
# 0.5.19: put id back - refused (false) while any accessory of its line is in the bag (never two of one line, never a swap: the caller keeps
# the item), or for an id that is not one of our accessories (review fix A3); slot `at` when it is still free AND below this server's limit,
# else the first free slot below that limit
st_.addMethod(CtNewMethod.make(f"""
public static boolean putBackK(java.util.UUID u, String k, String id, int at) {{
  if (id == null || !id.startsWith("Skyy_") || {PKG}.AccDefs.isRetired(id) || {PKG}.AccDefs.groupOf(id) == null) return false;   // review fix A3: our accessories only
  synchronized (lock(u)) {{
    String[] s = slotsK(u, k);
    String g = {PKG}.AccDefs.groupOf(id);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (s[i].equals(id)) return false;
      if (g != null && g.equals({PKG}.AccDefs.groupOf(s[i]))) return false;
    }}
    int slot = -1;
    int cap = capOf(s);
    if (at >= 0 && at < cap && s[at] == null) slot = at;   // review fix A3: never above this server's limit
    for (int i = 0; slot < 0 && i < cap; i++) if (s[i] == null) slot = i;
    if (slot < 0) return false;
    s[slot] = id;
    saveK(u, k);
    return true;
  }}
}}""", st_))
# Integration pass (semantics rule 5): null = item moves between the live inventory and this player's bag are safe right now, else the
# reason shown on the page. profile:busy:<uuid> = the live inventory may not belong to the active profile (pending crash recovery at
# join; a switch runs inside one world-thread task, so the page handler never sees that one). SkyyProfiles installed but no
# profile:epoch:<uuid> for an online player = its players file is unreadable and pkey fell back to profile 1's key (or the join work
# has not run yet): moving items now could carry them from one profile to another. Without SkyyProfiles both keys are absent -> null.
st_.addMethod(CtNewMethod.make("""
public static String moveBlock(java.util.UUID u) {
  try {
    java.util.Map b = bridge();
    String us = u.toString();
    if (b.get("profile:busy:" + us) != null) return "your profile is still loading - try again in a moment";
    if (b.get("profile:fn:key") != null && b.get("profile:epoch:" + us) == null) return "your profile is not loaded - try again in a moment - tell an admin if this stays";
  } catch (Throwable t) { }
  return null;
}""", st_))
# 0.4.1 PROFILES-CONTRACT rule 3: republish acc:has / acc:tal when profile:epoch:<uuid> changed since the last publish, or the active
# key is not the one published (either write order inside SkyyProfiles). Only after the first publish (0.4 timing kept). Without
# SkyyProfiles the epoch is absent on both sides -> false after one lookup. Called by publishOnline (5 s) and AccEffects (1 s).
st_.addMethod(CtNewMethod.make("""
public static boolean checkEpoch(java.util.UUID u) {
  if (u == null || !PUBLISHED.containsKey(u)) return false;
  Object ep = epochOf(u);
  Object last = EPOCH.get(u);
  boolean changed = (ep == null) ? (last != null) : !ep.equals(last);
  if (!changed) {
    if (ep == null) return false;
    Object pk = PUBKEY.get(u);
    if (pk == null || pk.equals(pkey(u))) return false;
  }
  publish(u);
  return true;
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
      else checkEpoch(u);   // 0.4.1: profile switch -> republish
    }}
    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);
    CLOCK.keySet().retainAll(online);
    SPEED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", st_))

# 0.5: the accessories (Skyy_Talisman_* / Skyy_Accessory_*, the bag item too) in storage + hotbar + backpack, by count
JM(st_, r"""
public static int accCount(@IC@[] conts) {
  int n = 0;
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id != null && (id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 RESTAMP (spec 5.2, the SkyySacks 0.7.7 pattern): a saved stack keeps the quality index it was saved with, so every accessory stack
# (and the bag item) whose index differs from its item's gets withQuality(item index) - id and count unchanged (asserted per stack, and
# the accessory count before and after is compared). World thread only (AccRestampTask); returns the stacks changed.
JM(st_, r"""
public static int restamp(@INV@ inv) {
  if (inv == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  int before = accCount(conts);
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !(id.startsWith("Skyy_Talisman_") || id.startsWith("Skyy_Accessory_"))) continue;
      @ITM@ item = it.getItem();
      if (item == null) continue;
      int want = item.getQualityIndex();
      if (it.getQualityIndex() == want) continue;
      @IS@ nw = it.withQuality(want);
      if (nw == null || !id.equals(nw.getItemId()) || nw.getQuantity() != it.getQuantity()) {
        if (!RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp skipped " + id + ": withQuality changed the id or the count (logged once)"); }
        continue;
      }
      cont.setItemStackForSlot(s, nw);
      n++;
    }
  }
  int after = accCount(conts);
  if (after != before && !RESTAMP_WARNED) { RESTAMP_WARNED = true; warn("restamp: the accessory count changed from " + before + " to " + after + " (logged once)"); }
  return n;
}""")
# 0.5: how many of item id are in storage + hotbar + backpack (the give counts before and after)
JM(st_, r"""
public static int countOf(@INV@ inv, String id) {
  if (inv == null || id == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n = n + it.getQuantity();
    }
  }
  return n;
}""")
# 0.5 (part 1 review finding 1): the give arithmetic - got = the count after minus before (never below 0), handed out = got + dropped;
# c[3] = 1 when that is not the n asked for (a stack merged elsewhere, a full inventory that could not drop, ...)
JM(st_, r"""
public static int[] giveCount(int before, int after, int dropped, int n) {
  int got = after - before;
  if (got < 0) got = 0;
  int d = dropped < 0 ? 0 : dropped;
  int ok = got + d;
  return new int[] { ok, got, d, ok != n ? 1 : 0 };
}""")
# 0.5 give (spec 5.9): n copies of id, one at a time (MaxStack 1), storage first and the rest dropped at the player's feet
# (addOrDropItemStack, vanilla's giveOutput call), counted before and after. ONLY on that player's world thread (Store.isInThread);
# returns { handed out, now in the inventory, dropped } or null when the player / store / thread is not right.
JM(st_, r"""
public static int[] deliver(@PR@ pr, String id, int n) {
  if (pr == null || id == null || n < 1) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @ST@ st = r.getStore();
  if (st == null || !st.isInThread()) return null;
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null || p.getInventory() == null) return null;
  @INV@ inv = p.getInventory();
  int before = countOf(inv, id);
  int dropped = 0;
  for (int i = 0; i < n; i++) {
    if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) dropped++;   // true = dropped
  }
  int[] c = giveCount(before, countOf(inv, id), dropped, n);
  if (c[3] != 0) warn("give of " + n + " x " + id + " to " + pr.getUsername() + ": " + c[1] + " arrived in the inventory and " + c[2] + " were dropped at their feet (" + c[0] + " handed out)");
  return new int[] { c[0], c[1], c[2] };
}""")
# 0.4.3 review fix: SkyyCooking's LIVE Campfire accessory factors. The item text can only carry the defaults (CAMP_*_PCT), but a server
# can change campfire.xpFactor / campfire.buffFactor in cooking.properties (+ /cookadmin reload). SkyyCooking 0.1.1 publishes them as
# cook:fn:campfactors = Function, apply(anything) -> Object[]{ Double buffFactor, Double xpFactor, Boolean enabled } (live, any thread,
# no I/O). campFactors() -> {xpFactor, buffFactor, enabled 1/0} or null (SkyyCooking absent, or the key missing / changed shape).
st_.addField(CtField.make('public static volatile String CF_SEEN = "";', st_))   # campCheck: last state logged (tick thread only)
st_.addField(CtField.make("public static final double CAMP_XP_TEXT = %s;" % repr(CAMP_XP_PCT / 100.0), st_))
st_.addField(CtField.make("public static final double CAMP_BUFF_TEXT = %s;" % repr(CAMP_BUFF_PCT / 100.0), st_))
st_.addField(CtField.make('public static final String CAMPFIRE_ID = "Skyy_Accessory_Campfire_T1";', st_))
st_.addMethod(CtNewMethod.make("""
public static double[] campFactors() {
  try {
    Object f = bridge().get("cook:fn:campfactors");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply((Object) null);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    if (a.length < 3 || !(a[0] instanceof Number) || !(a[1] instanceof Number) || !(a[2] instanceof Boolean)) return null;
    double bv = ((Number) a[0]).doubleValue();
    double xv = ((Number) a[1]).doubleValue();
    if (!(xv >= 0.0 && xv <= 1.0 && bv >= 0.0 && bv <= 1.0)) return null;
    return new double[] { xv, bv, ((Boolean) a[2]).booleanValue() ? 1.0 : 0.0 };
  } catch (Throwable t) { return null; }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String campPct(double v) {
  long c = Math.round(v * 1000.0);
  if (c % 10L == 0L) return String.valueOf(c / 10L) + "%";
  return String.valueOf(c / 10L) + "." + String.valueOf(c % 10L) + "%";
}""", st_))
# 5 s tick (AccTick, scheduler thread): one WARNING per distinct state - live factors that differ from the item text, graded cooking
# turned off, or SkyyCooking running (cook:fn:campfire) without a readable cook:fn:campfactors. Silent while the live factors match
# the text or SkyyCooking (0.1.1+) is absent. Checking every 5 s also catches /cookadmin reload.
st_.addMethod(CtNewMethod.make("""
public static void campCheck() {
  try {
    if (bridge().get("cook:fn:campfire") == null) return;
    double[] f = campFactors();
    String seen = "unreadable";
    if (f != null && f[2] < 0.5) seen = "off";
    else if (f != null) seen = (Math.abs(f[0] - CAMP_XP_TEXT) < 0.0005 && Math.abs(f[1] - CAMP_BUFF_TEXT) < 0.0005) ? "default" : campPct(f[0]) + " " + campPct(f[1]);
    if (seen.equals(CF_SEEN)) return;
    CF_SEEN = seen;
    if (seen.equals("default")) return;
    if (f == null) warn("SkyyCooking runs (cook:fn:campfire), but its live Campfire accessory factors could not be read (cook:fn:campfactors missing or changed shape - expected Object[]{Double buffFactor, Double xpFactor, Boolean enabled}). The Campfire Accessory item text shows the defaults " + campPct(CAMP_XP_TEXT) + " Cooking XP / " + campPct(CAMP_BUFF_TEXT) + " of the cooking bonus and the Void Charms page cannot show this server's numbers.");
    else if (seen.equals("off")) warn("graded cooking is off in cooking.properties (enabled=false): the Campfire accessory cooks plain dishes with no Cooking XP, but its item text says " + campPct(CAMP_XP_TEXT) + " Cooking XP / " + campPct(CAMP_BUFF_TEXT) + " of the cooking bonus. The Void Charms page says it is off.");
    else warn("cooking.properties sets the Campfire accessory to " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of the cooking bonus (campfire.xpFactor / campfire.buffFactor), but the Campfire Accessory item text says the defaults " + campPct(CAMP_XP_TEXT) + " / " + campPct(CAMP_BUFF_TEXT) + ". The Void Charms page shows the live numbers; the item text only changes with a SkyyAccessories rebuild (CAMP_XP_PCT / CAMP_BUFF_PCT).");
  } catch (Throwable t) { }
}""", st_))
# Accessory Bag page status line while the Campfire accessory or the Omni is equipped ("" otherwise, or when the factors cannot be read)
st_.addMethod(CtNewMethod.make("""
public static String campLine(String[] s) {
  try {
    boolean on = false;
    if (s != null) for (int i = 0; i < s.length; i++) if (CAMPFIRE_ID.equals(s[i]) || com.skyy.accessories.AccDefs.OMNI.equals(s[i])) on = true;
    if (!on) return "";
    if (bridge().get("cook:fn:campfire") == null) return "Campfire quick cook - SkyyCooking is not running - plain dishes and no Cooking XP";
    double[] f = campFactors();
    if (f == null) return "";
    if (f[2] < 0.5) return "Campfire quick cook - graded cooking is off on this server - plain dishes and no Cooking XP";
    return "Campfire quick cook on this server - " + campPct(f[0]) + " Cooking XP and " + campPct(f[1]) + " of your cooking bonus";
  } catch (Throwable t) { return ""; }
}""", st_))

# ================= 0.5.22 ACCESSORY POWER (tools/accessories_0_5_22_patch.py; research/Accessory-Power-Spec.md; Skyy 2026-10-16 "pick a power.
# unlike hypixle we start with 5 combat. and the 4 gathering." + the popups: bench accessories give AP by rarity, free switch with a 5 s wait,
# the Combat 15 Powers now with the combat 'Fortune' renamed Jackpot). THE POWER TABLE: (id, name, group 0 combat / 1 Combat 15 / 2 gathering,
# [(stat, value per 100 Accessory Power)]) - stat keys: hp def str cc cd mp mana (whole points; cc / cd percent), spd (% speed), bp.<skill> /
# swing.<skill> (% Breaking Power / Speed), dd.<skill> (Fortune: 100 = one extra drop; mining / foraging / farming), fspd.fishing /
# dd.fishing / treasure.fishing (% Fishing Speed / Double Catch / Treasure). Minus = a debuff (Combat 15: SkyyGear-Plan locks 92-109).
PW_TABLE = [
    ("Tank", "Tank", 0, [("hp", 12), ("def", 6)]),
    ("Balance", "Balance", 0, [("hp", 5), ("def", 3), ("str", 3), ("cc", 1), ("cd", 3), ("mana", 2), ("spd", 1)]),
    ("Slayer", "Slayer", 0, [("hp", 2), ("def", 1), ("str", 7), ("cd", 10)]),
    ("Lucky", "Lucky", 0, [("hp", 4), ("def", 2), ("cc", 5), ("cd", 3)]),
    ("Magical", "Magical", 0, [("hp", 4), ("def", 1), ("mp", 7), ("mana", 4)]),
    ("Fortress", "Fortress", 1, [("hp", 20), ("def", 10)]),
    ("Harmony", "Harmony", 1, [("hp", 8), ("def", 5), ("str", 5), ("cc", 2), ("cd", 5), ("mana", 3), ("spd", 2)]),
    ("GlassCannon", "Glass Cannon", 1, [("hp", -4), ("def", -2), ("str", 12), ("cc", 3), ("cd", 16)]),
    ("Blitz", "Blitz", 1, [("hp", -3), ("def", -2), ("str", 3), ("cc", 3), ("spd", 4)]),
    ("Arcane", "Arcane", 1, [("hp", 3), ("def", -2), ("str", -2), ("mp", 12), ("mana", 6)]),
    ("Jackpot", "Jackpot", 1, [("hp", -3), ("def", -2), ("str", 2), ("cc", 9), ("cd", 6)]),
    ("Mining", "Mining", 2, [("bp.mining", 14), ("swing.mining", 9), ("dd.mining", 6)]),
    ("Foraging", "Foraging", 2, [("bp.foraging", 9), ("swing.foraging", 14), ("dd.foraging", 6)]),
    ("Farming", "Farming", 2, [("bp.farming", 3), ("swing.farming", 10), ("dd.farming", 9)]),
    ("Fishing", "Fishing", 2, [("fspd.fishing", 8), ("dd.fishing", 2), ("treasure.fishing", 1)]),
]
PW_GROUPS = ["Combat", "Combat 15", "Gathering"]
PW_START_DEF = "Balance"
PW_STARTERS = [_p[0] for _p in PW_TABLE if _p[2] != 1]              # a start Power is never a locked Combat 15 one
PW_CKEYS = ["hp", "def", "str", "cc", "cd", "mp", "mana", "spd"]     # AccPower.tick's combat array (AccEffects reads it by these indexes)
PW_GEARK = ["def", "str", "cc", "cd", "mp"]                          # -> the gear:extra text (SkyyGear's own keys)
# stat key -> (kind: 0 whole combat, 1 one-decimal combat %, 2 one-decimal gathering %, 3 whole Fortune; short label; % shown; reader)
# reader: "" = always (this mod applies it), "skills" = SkyySkills running (skill:fn:level), else the bridge flag that must be TRUE
def pw_stat(k):
    if k in ("hp", "def", "str", "mp", "mana"):
        return (0, {"hp": "HP", "def": "Def", "str": "Str", "mp": "Magic", "mana": "Mana"}[k], False, "")
    if k in ("cc", "cd"):
        return (0, {"cc": "Crit", "cd": "Crit Dmg"}[k], True, "")   # short: a Power row holds 7 stats on one 600 px line
    if k == "spd":
        return (1, "Speed", True, "")
    sk, _d, sl = k.partition(".")
    if sk == "bp":
        return (2, "Breaking Power", True, "skill:bonus:reads:bp")
    if sk == "swing":
        return (2, "Breaking Speed", True, "skill:bonus:reads:swing")
    if sk == "dd" and sl != "fishing":
        return (3, sl.capitalize() + " Fortune", False, "skills")
    if sl == "fishing":
        return (2, {"fspd": "Fishing Speed", "dd": "Double Catch", "treasure": "Treasure"}[sk], True, "skill:bonus:reads:fish")
    raise SystemExit("0.5.22: unknown Power stat %r" % k)
PW_E = [(_i, _k, _v) for _i, _p in enumerate(PW_TABLE) for _k, _v in _p[3]]   # one entry per Power stat (config pw.<Power>.<stat>)
assert len(PW_TABLE) == 15 and [_p[0] for _p in PW_TABLE if _p[2] == 0] == ["Tank", "Balance", "Slayer", "Lucky", "Magical"]
assert [_p[1] for _p in PW_TABLE if _p[2] == 1] == ["Fortress", "Harmony", "Glass Cannon", "Blitz", "Arcane", "Jackpot"], "Fortune -> Jackpot"
assert [_p[0] for _p in PW_TABLE if _p[2] == 2] == ["Mining", "Foraging", "Farming", "Fishing"]
assert all(_k in PW_CKEYS or pw_stat(_k)[0] >= 2 for _i, _k, _v in PW_E) and PW_START_DEF in PW_STARTERS
assert all(-100 <= _v <= 100 and _v != 0 for _i, _k, _v in PW_E) and len(set((_i, _k) for _i, _k, _v in PW_E)) == len(PW_E)
assert all(set(PW_GEARK) <= set(PW_CKEYS) for _ in [0]) and all(" " not in _p[0] for _p in PW_TABLE)
PW_AP_DEF = [10, 13, 16, 19, 22, 25]           # spec 1 (locks 111-113: +10 to +25); = ACC_AP[1:]
assert PW_AP_DEF == ACC_AP[1:], "0.5.22: the live AP table starts from the 0.5 constant"
PW_DEFS = {"power.enabled": "true", "power.ap": ",".join(str(_a) for _a in PW_AP_DEF), "power.bench": "full", "power.base": "100",
           "power.curve": "0.6", "power.guard": "20", "power.wait": "5", "power.start": PW_START_DEF, "power.unlock": "15"}
# the build-time twin of AccPower.mult / valueAt (spec 2 / 2.3: x0.74 at 60 AP, x1.73 at 250, x2.12 at 350, x4.44 at 1,200)
def pw_mult(ap, base=100, curve=0.6, guard=20.0):
    return 0.0 if ap <= 0 else min(guard, (float(ap) / base) ** curve)
assert [round(pw_mult(_a), 2) for _a in (60, 250, 350, 1200)] == [0.74, 1.73, 2.12, 4.44], "spec 2: the curve"
# the Omni = the sum of the 11 active top-tier bench accessories (spec 1: 143 at the defaults)
PW_OMNI_DEF = sum(ACC_AP[min(_b[3], 4)] for _b in ACTIVE)
assert PW_OMNI_DEF == 143 and len(ACTIVE) == 11, (PW_OMNI_DEF, len(ACTIVE))
# the spec 2.3 table at 350 AP (late bag) for two Powers, rounded like the Java (combat whole numbers)
assert [int(round(_v * pw_mult(350))) for _k, _v in PW_TABLE[0][3]] == [25, 13] and [int(round(_v * pw_mult(350))) for _k, _v in PW_TABLE[2][3]] == [4, 2, 15, 21]
# drop-only lines (spec 5.2): drop-up = no CRAFT row until one is in the bag, then its upgrades (Q4 default); drop = never in CRAFT (none yet)
DROP_UP = ["Strength", "MagicPower", "Defense", "Crit", "Feather"]
DROP_ONLY = []
assert sorted(DROP_UP) == sorted(_b[0] for _b in BOOSTERS if _b[9] == "T"), "the five part 2 lines drop at their first rarity"
# their upgrade costs (Unique, Rare, Legendary - each also takes the rarity below, like every other ladder; checked against Assets.zip at
# the asset step): the line's own look items + the metal of that tier
DROP_UP_RECIPES = {
    "Strength": [[("Ingredient_Bone_Fragment", 10), ("Ingredient_Bar_Copper", 4)],
                 [("Ingredient_Sinue_Cindersinue", 5), ("Ingredient_Bar_Iron", 10)],
                 [("Ingredient_Fire_Essence", 10), ("Ingredient_Voidheart", 1), ("Ingredient_Bar_Thorium", 10)]],
    "MagicPower": [[("Ingredient_Crystal_Purple", 3), ("Ingredient_Bar_Copper", 4)],
                   [("Rock_Gem_Voidstone", 1), ("Ingredient_Crystal_Purple", 5), ("Ingredient_Bar_Silver", 5)],
                   [("Rock_Gem_Voidstone", 3), ("Ingredient_Bar_Cobalt", 10)]],
    "Defense": [[("Ingredient_Crystal_White", 3), ("Ingredient_Bar_Copper", 4)],
                [("Ingredient_Crystal_White", 5), ("Ingredient_Bar_Iron", 10)],
                [("Rock_Gem_Diamond", 3), ("Ingredient_Bar_Thorium", 10)]],
    "Crit": [[("Ingredient_Crystal_Pink", 3), ("Ingredient_Bar_Copper", 4)],
             [("Ingredient_Crystal_Pink", 5), ("Ingredient_Bar_Iron", 10)],
             [("Rock_Gem_Ruby", 2), ("Ingredient_Crystal_Pink", 10), ("Ingredient_Bar_Thorium", 10)]],
    "Feather": [[("Ingredient_Feathers_Light", 10), ("Ingredient_Bar_Copper", 4)],
                [("Ingredient_Feathers_Blue", 10), ("Ingredient_Bar_Iron", 10)],
                [("Ingredient_Ice_Essence", 10), ("Ingredient_Motes_Light", 5), ("Ingredient_Bar_Thorium", 10)]],
}
assert sorted(DROP_UP_RECIPES) == sorted(DROP_UP) and all(len(_r) == 3 for _r in DROP_UP_RECIPES.values())
# power.properties (Server Setup -> Accessories -> Accessory Power; a missing file is written once with these lines)
PW_LINES = [
    "# SkyyAccessories - Accessory Power (0.5.22). Change it in game: SkyWynn Menu -> Server Setup -> Void Charms -> Accessory Power,",
    "# or edit this file and press Reload there (or /charms reload). Every accessory in Void Charms adds Accessory Power (AP) by its rarity -",
    "# only the best of each line counts. Each player picks ONE Power; its stats are the pw. numbers (per 100 AP) x (AP / power.base) ^ power.curve,",
    "# at most x power.guard.",
    "power.enabled=true",
    "# AP per rarity: Normal,Unique,Rare,Legendary,Fabled,Mythic (six whole numbers 0-100).",
    "power.ap=" + PW_DEFS["power.ap"],
    "# Bench accessories give AP: full, half or none.",
    "power.bench=full",
    "# The AP that gives x1 (1-1000), the curve exponent (0.1-1.0) and the most the multiplier can reach (1-100).",
    "power.base=100",
    "power.curve=0.6",
    "power.guard=20",
    "# Seconds between two Power switches (0-3600).",
    "power.wait=5",
    "# The Power a profile starts on: one of " + ", ".join(PW_STARTERS) + ".",
    "power.start=" + PW_START_DEF,
    "# The Combat level that unlocks the Combat 15 Powers (0-100).",
    "power.unlock=15",
    "# false: the Power is hidden (nobody can pick it; a player on it goes back to power.start).",
] + ["power.show.%s=true" % _p[0] for _p in PW_TABLE] + [
    "# Each Power's stats per 100 AP (a minus is a debuff, -100 to 100): hp / def / str / mp / mana whole points, cc / cd percent, spd % speed,",
    "# bp.<skill> % Breaking Power, swing.<skill> % Breaking Speed, dd.<skill> Fortune (100 is one extra drop), fspd / dd / treasure .fishing percent.",
] + ["pw.%s.%s=%g" % (PW_TABLE[_i][0], _k, _v) for _i, _k, _v in PW_E] + [""]
PW_TEXT = "\n".join(PW_LINES)
assert all(ord(_c) < 128 for _c in PW_TEXT) and not any("=" in _l for _l in PW_LINES if _l.startswith("#"))
PW_ROWS = [
    ("power.enabled", "Accessory Power on", "power", "bool", "true", "", "", "", "", "live",
     "Off = no Power stats (Accessory Power is still shown).", "field:AccPower.ON@Skyy_SkyyAccessories/power.properties:power.enabled"),
    ("power.ap", "AP per rarity", "power", "text", PW_DEFS["power.ap"], "", "40", "", "", "live",
     "Six whole numbers 0-100: Normal, Unique, Rare, Legendary, Fabled, Mythic.",
     "field:AccPower.AP_TEXT@Skyy_SkyyAccessories/power.properties:power.ap;check=AccPower.checkAp;after=AccPower.afterAp"),
    ("power.bench", "Bench accessories give AP", "power", "choice", "full", "", "", "full|Full,half|Half,none|None", "", "live",
     "Bench accessories add AP by their rarity like the others: full, half or none.",
     "field:AccPower.BENCH@Skyy_SkyyAccessories/power.properties:power.bench"),
    ("power.base", "AP for x1", "power", "int", "100", "1", "1000", "step=1", "", "live,adv",
     "The Accessory Power that gives the Power's numbers exactly (x1).", "field:AccPower.BASE@Skyy_SkyyAccessories/power.properties:power.base"),
    ("power.curve", "Power curve exponent", "power", "dec", "0.6", "0.1", "1", "step=0.05", "", "live,adv",
     "0.6 = double the AP, about 1.5x the stats. 1 = straight line.", "field:AccPower.CURVE@Skyy_SkyyAccessories/power.properties:power.curve"),
    ("power.guard", "Power multiplier guard", "power", "dec", "20", "1", "100", "step=1", "x", "live,adv",
     "The most the multiplier can reach (a sanity cap).", "field:AccPower.GUARD@Skyy_SkyyAccessories/power.properties:power.guard"),
    ("power.wait", "Wait between Power switches", "power", "int", "5", "0", "3600", "step=1", "s", "live",
     "Switching is free; this many seconds must pass between two switches.", "field:AccPower.WAIT@Skyy_SkyyAccessories/power.properties:power.wait"),
    ("power.start", "Starting Power", "power", "choice", PW_START_DEF, "", "", ",".join("%s|%s" % (_p[0], _p[1]) for _p in PW_TABLE if _p[2] != 1),
     "", "live", "The Power of a profile that never picked one.", "field:AccPower.START@Skyy_SkyyAccessories/power.properties:power.start"),
    ("power.unlock", "Combat level for Combat 15 Powers", "power", "int", "15", "0", "100", "step=1", "", "live",
     "Fortress, Harmony, Glass Cannon, Blitz, Arcane and Jackpot unlock at this Combat level.",
     "field:AccPower.UNLOCK@Skyy_SkyyAccessories/power.properties:power.unlock"),
    ("pw", "Power stats per 100 AP", "power", "table", "", "-100", "100", "dec;none;Per 100 AP", "", "live,danger",
     "Each Power's stats per 100 Accessory Power. A minus is a debuff.", "reload@Skyy_SkyyAccessories/power.properties:pw.;check=AccPower.checkStat"),
] + [("power.show.%s" % _p[0], "%s Power" % _p[1], "power", "bool", "true", "", "", "", "", "live,adv",
      "Off = hidden: nobody can pick it (a player on it goes back to the starting Power).",
      "field:AccPower.ON_%s@Skyy_SkyyAccessories/power.properties:power.show.%s" % (_p[0].upper(), _p[0])) for _p in PW_TABLE]
assert all(len(_r[1]) <= 40 and len(_r[10]) <= 100 for _r in PW_ROWS), [_r[0] for _r in PW_ROWS if len(_r[1]) > 40 or len(_r[10]) > 100]
# the Java tables (flat 1-D arrays; javassist compiles no [][])
def _pwj(xs):
    return ", ".join(jlit(x) for x in xs)
JF(apw_, "public static java.nio.file.Path FILE;")    # Skyy_SkyyAccessories/power.properties
JF(apw_, "public static java.nio.file.Path DIR;")     # Skyy_SkyyAccessories/power (one file per profile storage key)
JF(apw_, "public static volatile boolean ON = true;")
JF(apw_, "public static volatile String AP_TEXT = %s;" % jlit(PW_DEFS["power.ap"]))
JF(apw_, "public static volatile int[] AP = new int[] { 0, %s };" % PW_DEFS["power.ap"])
JF(apw_, 'public static volatile String BENCH = "full";')
JF(apw_, "public static volatile int BASE = 100;")
JF(apw_, "public static volatile double CURVE = 0.6;")
JF(apw_, "public static volatile double GUARD = 20.0;")
JF(apw_, "public static volatile int WAIT = 5;")
JF(apw_, "public static volatile String START = %s;" % jlit(PW_START_DEF))
JF(apw_, "public static volatile int UNLOCK = 15;")
for _p in PW_TABLE:
    JF(apw_, "public static volatile boolean ON_%s = true;" % _p[0].upper())
JF(apw_, "public static final String[] PW_ID = new String[] { %s };" % _pwj(_p[0] for _p in PW_TABLE))
JF(apw_, "public static final String[] PW_NAME = new String[] { %s };" % _pwj(_p[1] for _p in PW_TABLE))
JF(apw_, "public static final int[] PW_GRP = new int[] { %s };" % ", ".join(str(_p[2]) for _p in PW_TABLE))
JF(apw_, "public static final String[] GROUPS = new String[] { %s };" % _pwj(PW_GROUPS))
JF(apw_, "public static final int[] E_PW = new int[] { %s };" % ", ".join(str(_i) for _i, _k, _v in PW_E))
JF(apw_, "public static final String[] E_KEY = new String[] { %s };" % _pwj(_k for _i, _k, _v in PW_E))
JF(apw_, "public static final double[] E_DEF = new double[] { %s };" % ", ".join("%r" % float(_v) for _i, _k, _v in PW_E))
JF(apw_, "public static final int[] E_KIND = new int[] { %s };" % ", ".join(str(pw_stat(_k)[0]) for _i, _k, _v in PW_E))
JF(apw_, "public static final String[] E_LABEL = new String[] { %s };" % _pwj(pw_stat(_k)[1] for _i, _k, _v in PW_E))
JF(apw_, "public static final int[] E_PCT = new int[] { %s };" % ", ".join("1" if pw_stat(_k)[2] else "0" for _i, _k, _v in PW_E))
JF(apw_, "public static final String[] E_NEED = new String[] { %s };" % _pwj(pw_stat(_k)[3] for _i, _k, _v in PW_E))
JF(apw_, "public static final int[] E_C = new int[] { %s };" % ", ".join(str(PW_CKEYS.index(_k)) if _k in PW_CKEYS else "-1" for _i, _k, _v in PW_E))
JF(apw_, "public static volatile double[] E_VAL = new double[] { %s };" % ", ".join("%r" % float(_v) for _i, _k, _v in PW_E))
JF(apw_, "public static final String[] C_KEYS = new String[] { %s };" % _pwj(PW_CKEYS))
JF(apw_, "public static final String[] DROP_UP = new String[] { %s };" % _pwj(DROP_UP))
JF(apw_, "public static final String[] DROP_ONLY = new String[] { %s };" % (_pwj(DROP_ONLY) if DROP_ONLY else ""))
JF(apw_, 'public static final String SRC = "accessories";')   # our skill:bonus source (spec 4)
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap PICK = new java.util.concurrent.ConcurrentHashMap();")   # pkey -> String[]{id, ms}
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap BADP = new java.util.concurrent.ConcurrentHashMap();")   # pkey -> unreadable file warned
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap LV = new java.util.concurrent.ConcurrentHashMap();")     # uuid -> long[]{Combat level, ms}
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap LASTB = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> our skill:bonus map
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap LASTP = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> our acc:power text
JF(apw_, "public static final java.util.concurrent.ConcurrentHashMap LASTC = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> double[] combat
JF(apw_, "public static boolean F_LOAD = false;")
JF(apw_, "public static volatile long PICKS = 0L;")
JF(apw_, "public static final String DEFAULT_TEXT = %s;" % jlit(PW_TEXT))
JM(apw_, r"""
public static void info(String msg) {
  try { if (@PKG@.AccStore.LOG != null) @PKG@.AccStore.LOG.at(java.util.logging.Level.INFO).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""")
JM(apw_, "public static boolean powerOn(int i) {\n  switch (i) {\n" + "".join("    case %d: return ON_%s;\n" % (_i, _p[0].upper()) for _i, _p in enumerate(PW_TABLE))
     + "    default: return false;\n  }\n}")
JM(apw_, "public static void setOn(int i, boolean v) {\n  switch (i) {\n" + "".join("    case %d: ON_%s = v; break;\n" % (_i, _p[0].upper()) for _i, _p in enumerate(PW_TABLE))
     + "    default: break;\n  }\n}")
# "glass cannon" / "GlassCannon" / "glass_cannon" -> its index (-1 = none)
JM(apw_, r"""
public static String norm(String s) {
  if (s == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (Character.isLetterOrDigit(c)) b.append(Character.toLowerCase(c));
  }
  return b.toString();
}""")
JM(apw_, r"""
public static int index(String name) {
  String n = norm(name);
  if (n.length() == 0) return -1;
  for (int i = 0; i < PW_ID.length; i++) if (norm(PW_ID[i]).equals(n) || norm(PW_NAME[i]).equals(n)) return i;
  return -1;
}""")
JM(apw_, r"""
public static String nameOf(int i) {
  return i >= 0 && i < PW_NAME.length ? PW_NAME[i] : "none";
}""")
# power.ap: six whole numbers 0-100 -> { 0, Normal .. Mythic } or null
JM(apw_, r"""
public static int[] parseAp(String t) {
  if (t == null) return null;
  String[] p = t.split(",", -1);
  if (p.length != 6) return null;
  int[] out = new int[7];
  for (int i = 0; i < 6; i++) {
    String x = p[i].trim();
    if (x.length() == 0 || x.length() > 3) return null;
    for (int j = 0; j < x.length(); j++) if (!Character.isDigit(x.charAt(j))) return null;
    int v = Integer.parseInt(x);
    if (v > 100) return null;
    out[i + 1] = v;
  }
  return out;
}""")
JM(apw_, r"""
public static String checkAp(String key, String value) {
  if (parseAp(value) == null) return "Needs six whole numbers from 0 to 100 for Normal, Unique, Rare, Legendary, Fabled and Mythic, like 10,13,16,19,22,25.";
  return null;
}""")
JM(apw_, r"""
public static void afterAp(String key) {
  int[] a = parseAp(AP_TEXT);
  if (a != null) AP = a;
}""")
JM(apw_, r"""
public static int entryOf(String en) {
  if (en == null) return -1;
  for (int e = 0; e < E_KEY.length; e++) if ((PW_ID[E_PW[e]] + "." + E_KEY[e]).equals(en)) return e;
  return -1;
}""")
# check= hook of the pw table: key = pw[<Power>.<stat>], value = the canonical text, null = a removal
JM(apw_, r"""
public static String checkStat(String key, String value) {
  String en = key == null ? "" : key;
  int a = en.indexOf('[');
  int b = en.lastIndexOf(']');
  if (a >= 0 && b > a) en = en.substring(a + 1, b);
  int e = entryOf(en);
  if (e < 0) return "Unknown entry - the entries are <Power>.<stat> like Tank.hp or Mining.dd.mining (see power.properties).";
  if (value == null) return "The " + en + " line stays - set it to " + E_DEF[e] + " for the built-in number.";
  double v = 0.0;
  try { v = Double.parseDouble(value.trim()); } catch (Throwable t) { return "Needs one number from -100 to 100."; }
  if (Double.isNaN(v) || v < -100.0 || v > 100.0) return "Needs one number from -100 to 100.";
  return null;
}""")
JM(apw_, r"""
public static boolean bool(String v, boolean def) {
  if (v == null) return def;
  String x = v.trim().toLowerCase();
  if (x.equals("true") || x.equals("on") || x.equals("yes") || x.equals("1")) return true;
  if (x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0")) return false;
  return def;
}""")
JM(apw_, r"""
public static double dec(String v, double def, double lo, double hi) {
  if (v == null) return def;
  double d = def;
  try { d = Double.parseDouble(v.trim()); } catch (Throwable t) { return def; }
  if (Double.isNaN(d) || Double.isInfinite(d)) return def;
  if (d < lo) return lo;
  if (d > hi) return hi;
  return d;
}""")
# load power.properties (a missing file is written once with the built-in lines); the loader clamps like the kit validates
JM(apw_, r"""
public static String load() {
  java.util.Properties p = new java.util.Properties();
  try {
    if (FILE != null && !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
      info("wrote the first power.properties with the built-in Accessory Power settings: " + FILE);
    }
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    if (!F_LOAD) { F_LOAD = true; @PKG@.AccStore.warn("power.properties could not be read - the current Accessory Power settings stay: " + t); }
    return "power.properties could not be read";
  }
  ON = bool(p.getProperty("power.enabled"), true);
  String at = p.getProperty("power.ap");
  int[] a = parseAp(at);
  if (a != null) { AP = a; AP_TEXT = at.trim(); }
  else { AP = parseAp("@APDEF@"); AP_TEXT = "@APDEF@"; if (at != null) @PKG@.AccStore.warn("power.properties: power.ap=" + at.trim() + " is not six whole numbers 0-100 - the built-in @APDEF@ is used"); }
  String bn = p.getProperty("power.bench", "full").trim().toLowerCase();
  BENCH = (bn.equals("half") || bn.equals("none")) ? bn : "full";
  BASE = (int) dec(p.getProperty("power.base"), 100.0, 1.0, 1000.0);
  CURVE = dec(p.getProperty("power.curve"), 0.6, 0.1, 1.0);
  GUARD = dec(p.getProperty("power.guard"), 20.0, 1.0, 100.0);
  WAIT = (int) dec(p.getProperty("power.wait"), 5.0, 0.0, 3600.0);
  UNLOCK = (int) dec(p.getProperty("power.unlock"), 15.0, 0.0, 100.0);
  String sp = p.getProperty("power.start", "@STARTDEF@").trim();
  int si = index(sp);
  START = (si >= 0 && PW_GRP[si] != 1) ? PW_ID[si] : "@STARTDEF@";
  for (int i = 0; i < PW_ID.length; i++) setOn(i, bool(p.getProperty("power.show." + PW_ID[i]), true));
  double[] v = new double[E_DEF.length];
  int custom = 0;
  for (int e = 0; e < v.length; e++) {
    v[e] = dec(p.getProperty("pw." + PW_ID[E_PW[e]] + "." + E_KEY[e]), E_DEF[e], -100.0, 100.0);
    if (v[e] != E_DEF[e]) custom++;
  }
  E_VAL = v;
  StringBuilder off = new StringBuilder();
  for (int i = 0; i < PW_ID.length; i++) if (!powerOn(i)) off.append(off.length() > 0 ? ", " : "").append(PW_NAME[i]);
  return "Accessory Power " + (ON ? "on" : "OFF") + " (AP " + AP_TEXT + ", benches " + BENCH + ", x1 at " + BASE + " AP, curve " + CURVE + ", guard x" + GUARD
    + ", " + WAIT + " s between switches, start " + START + ", Combat 15 at Combat " + UNLOCK + (custom > 0 ? ", " + custom + " custom Power numbers" : "")
    + (off.length() > 0 ? ", hidden: " + off.toString() : "") + ")";
}""".replace("@APDEF@", PW_DEFS["power.ap"]).replace("@STARTDEF@", PW_START_DEF))
# ---- the AP sum (spec 1)
JM(apw_, r"""
public static boolean activeBench(String b) {
  if (b == null) return false;
  for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) if (@PKG@.AccDefs.BENCH_IDS[i].equals(b)) return true;
  return false;
}""")
JM(apw_, r"""
public static int apBench(int ap) {
  if ("none".equals(BENCH)) return 0;
  if ("half".equals(BENCH)) return ap / 2;
  return ap;
}""")
JM(apw_, r"""
public static int rar(int t) {
  return t < 1 ? 1 : (t > 4 ? 4 : t);
}""")
# the Omni = what the active top-tier bench accessories it is made from would give (spec 1: 143 at the defaults)
JM(apw_, r"""
public static int omniAp() {
  int[] a = AP;
  int t = 0;
  for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) t = t + apBench(a[rar(@PKG@.AccDefs.BENCH_MAX[i])]);
  return t;
}""")
# the AP one accessory gives on its own (0 = none): retired / not ours / a switched-off line 0; a bench accessory next to the Omni 0;
# the Omni itself 0 here (apOf adds omniAp once)
JM(apw_, r"""
public static int apRaw(String id, boolean omni) {
  if (id == null || !@PKG@.AccDefs.isAccessory(id) || @PKG@.AccDefs.isRetired(id)) return 0;
  String m = @PKG@.AccDefs.modernOf(id);
  if (@PKG@.AccDefs.OMNI.equals(m)) return 0;
  int[] a = AP;
  int r = @PKG@.AccDefs.rarityOf(m);
  if (r < 1 || r >= a.length) return 0;
  if (@PKG@.AccDefs.isTalisman(m)) {
    if (@PKG@.AccDefs.isLantern(m)) return @PKG@.AccDefs.LINE_LANTERN ? a[r] : 0;
    int li = @PKG@.AccDefs.familyIndex(@PKG@.AccDefs.familyOf(m));
    if (li < 0 || !@PKG@.AccDefs.lineOn(li)) return 0;
    return a[r];
  }
  if (omni || !activeBench(@PKG@.AccDefs.benchOf(m))) return 0;
  return apBench(a[r]);
}""")
JM(apw_, r"""
public static int apOf(String[] s) {
  if (s == null) return 0;
  boolean omni = @PKG@.AccDefs.hasOmni(s);
  java.util.HashMap best = new java.util.HashMap();
  for (int i = 0; i < s.length; i++) {
    int a = apRaw(s[i], omni);
    if (a <= 0) continue;
    String g = @PKG@.AccDefs.groupOf(@PKG@.AccDefs.modernOf(s[i]));
    if (g == null) continue;
    Integer o = (Integer) best.get(g);
    if (o == null || o.intValue() < a) best.put(g, Integer.valueOf(a));
  }
  int t = 0;
  java.util.Iterator it = best.values().iterator();
  while (it.hasNext()) t = t + ((Integer) it.next()).intValue();
  if (omni) t = t + omniAp();
  return t;
}""")
# what one accessory IN THE BAG adds (the hover text): >= 0 its AP, -1 a better one of its line is in the bag, -2 a bench accessory the Omni
# already covers, -3 its line is switched off, -4 retired
JM(apw_, r"""
public static int apOne(String[] s, String id) {
  if (id == null) return 0;
  if (@PKG@.AccDefs.isRetired(id)) return -4;
  String m = @PKG@.AccDefs.modernOf(id);
  if (@PKG@.AccDefs.OMNI.equals(m)) return omniAp();
  boolean omni = @PKG@.AccDefs.hasOmni(s);
  if (!@PKG@.AccDefs.isTalisman(m) && omni && activeBench(@PKG@.AccDefs.benchOf(m))) return -2;
  int a = apRaw(id, omni);
  if (a <= 0) return @PKG@.AccDefs.isTalisman(m) ? -3 : 0;
  String g = @PKG@.AccDefs.groupOf(m);
  int r = @PKG@.AccDefs.rarityOf(m);
  for (int j = 0; s != null && j < s.length; j++) {
    if (s[j] == null || @PKG@.AccDefs.isRetired(s[j])) continue;
    String x = @PKG@.AccDefs.modernOf(s[j]);
    if (g != null && g.equals(@PKG@.AccDefs.groupOf(x)) && @PKG@.AccDefs.rarityOf(x) > r) return -1;
  }
  return a;
}""")
# what an accessory NOT in the bag would add on its own (the inventory grid's hover text)
JM(apw_, r"""
public static int apIf(String id) {
  if (id == null || @PKG@.AccDefs.isRetired(id)) return 0;
  if (@PKG@.AccDefs.OMNI.equals(@PKG@.AccDefs.modernOf(id))) return omniAp();
  return apRaw(id, false);
}""")
JM(apw_, r"""
public static double mult(int ap) {
  if (ap <= 0) return 0.0;
  int base = BASE < 1 ? 1 : BASE;
  double m = Math.pow((double) ap / (double) base, CURVE);
  if (m > GUARD) m = GUARD;
  return m;
}""")
JM(apw_, r"""
public static String oneDec(double v) {
  long c = Math.round(Math.abs(v) * 10.0);
  String t = (c % 10L == 0L) ? String.valueOf(c / 10L) : String.valueOf(c / 10L) + "." + String.valueOf(c % 10L);
  return (v < 0.0 && c != 0L) ? "-" + t : t;
}""")
# one Power stat at multiplier m, rounded like it is applied: whole numbers (SkyyGear floors gear:extra; Fortune points), else 1 decimal
JM(apw_, r"""
public static double valueAt(int e, double m) {
  double v = E_VAL[e] * m;
  int k = E_KIND[e];
  if (k == 0 || k == 3) return (double) Math.round(v);
  return (double) Math.round(v * 10.0) / 10.0;
}""")
# ---- who reads what (spec 4 "show only what works")
JM(apw_, r"""
public static boolean reader(String need) {
  if (need == null || need.length() == 0) return true;
  try {
    java.util.Map b = @PKG@.AccStore.bridge();
    if (need.equals("skills")) return b.get("skill:fn:level") instanceof java.util.function.Function;
    return Boolean.TRUE.equals(b.get(need));
  } catch (Throwable t) { return false; }
}""")
JM(apw_, r"""
public static boolean works(int e) {
  return e >= 0 && e < E_NEED.length && reader(E_NEED[e]);
}""")
# a Power is listed / pickable while it is switched on and at least one of its stats has a reader and a number
JM(apw_, r"""
public static boolean visible(int i) {
  if (i < 0 || i >= PW_ID.length || !powerOn(i)) return false;
  double[] v = E_VAL;
  for (int e = 0; e < E_PW.length; e++) if (E_PW[e] == i && v[e] != 0.0 && works(e)) return true;
  return false;
}""")
# the Combat level (SkyySkills skill:fn:level "Combat" = the current class skill), cached 5 s; -1 = unknown (SkyySkills not running)
JM(apw_, r"""
public static int level(java.util.UUID u) {
  if (u == null) return -1;
  long now = System.currentTimeMillis();
  long[] c = (long[]) LV.get(u);
  if (c != null && now - c[1] < 5000L && now >= c[1]) return (int) c[0];
  int lv = -1;
  try {
    Object f = @PKG@.AccStore.bridge().get("skill:fn:level");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Combat" });
      if (r instanceof Number) lv = ((Number) r).intValue();
    }
  } catch (Throwable t) { lv = -1; }
  LV.put(u, new long[] { (long) lv, now });
  return lv;
}""")
# null = this player may pick Power i, else why not
JM(apw_, r"""
public static String lockOf(java.util.UUID u, int i) {
  if (i < 0 || i >= PW_GRP.length || PW_GRP[i] != 1 || UNLOCK <= 0) return null;
  int lv = level(u);
  if (lv < 0) return "needs SkyySkills (your Combat level)";
  if (lv < UNLOCK) return "unlocks at Combat " + UNLOCK + " (you are Combat " + lv + ")";
  return null;
}""")
# ---- the pick, per profile storage key (PROFILES-CONTRACT: power/<pkey>.properties power= / switched=)
JM(apw_, r"""
public static java.nio.file.Path fileOf(String k) {
  if (DIR == null || k == null || k.length() == 0 || k.indexOf('/') >= 0 || k.indexOf('\\') >= 0 || k.indexOf("..") >= 0) return null;
  return DIR.resolve(k + ".properties");
}""")
JM(apw_, r"""
public static String[] readPick(String k) {
  if (k == null) return new String[] { "", "0" };
  String[] c = (String[]) PICK.get(k);
  if (c != null) return c;
  String[] r = new String[] { "", "0" };
  java.nio.file.Path f = fileOf(k);
  try {
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      r[0] = p.getProperty("power", "").trim();
      r[1] = p.getProperty("switched", "0").trim();
    }
  } catch (Throwable t) {
    if (BADP.putIfAbsent(k, Boolean.TRUE) == null) @PKG@.AccStore.warn("power: " + f + " could not be read - that profile uses the starting Power until it is picked again: " + t);
  }
  PICK.put(k, r);
  return r;
}""")
JM(apw_, r"""
public static long msOf(String[] p) {
  try { return Long.parseLong(p[1]); } catch (Throwable t) { return 0L; }
}""")
JM(apw_, r"""
public static boolean writePick(String k, String id, long now) {
  java.nio.file.Path f = fileOf(k);
  if (f == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("power", id);
    p.setProperty("switched", String.valueOf(now));
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyAccessories 0.5.22 - the Accessory Power this profile picked (Void Charms > Power)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    PICK.put(k, new String[] { id, String.valueOf(now) });
    BADP.remove(k);
    return true;
  } catch (Throwable t) { @PKG@.AccStore.warn("power: could not save " + f + ": " + t); return false; }
}""")
# the Power that works for this player now: the pick if it is visible and unlocked, else power.start, else the first one that works
JM(apw_, r"""
public static int effIndex(java.util.UUID u, String k) {
  int i = index(readPick(k)[0]);
  if (i >= 0 && visible(i) && lockOf(u, i) == null) return i;
  int s = index(START);
  if (s >= 0 && visible(s) && lockOf(u, s) == null) return s;
  for (int j = 0; j < PW_ID.length; j++) if (visible(j) && lockOf(u, j) == null) return j;
  return -1;
}""")
JM(apw_, r"""
public static long waitLeft(String k, long now) {
  long w = (long) WAIT * 1000L;
  if (w <= 0L) return 0L;
  long ms = msOf(readPick(k));
  if (ms <= 0L) return 0L;
  if (ms > now) return w;
  long left = ms + w - now;
  return left > 0L ? left : 0L;
}""")
JM(apw_, r"""
public static String clean(String s) {
  if (s == null) return "";
  String t = s.trim();
  if (t.length() > 24) t = t.substring(0, 24);
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < t.length(); i++) { char c = t.charAt(i); if (Character.isLetterOrDigit(c) || c == ' ') b.append(c); }
  return b.toString();
}""")
JM(apw_, r"""
public static String listText(java.util.UUID u) {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < PW_ID.length; i++) {
    if (!visible(i)) continue;
    if (b.length() > 0) b.append(", ");
    b.append(PW_NAME[i]);
    if (lockOf(u, i) != null) b.append(" (Combat ").append(UNLOCK).append(")");
  }
  return b.length() == 0 ? "no Power is switched on here" : "Powers: " + b.toString();
}""")
# THE PICK (world thread: the Power view, /charms power, acc:fn:power set); wait = the switch wait applies (not for loadouts)
JM(apw_, r"""
public static String pick(java.util.UUID u, String k, String name, long now, boolean wait) {
  if (u == null || k == null) return "your player could not be read";
  if (!ON) return "Accessory Powers are switched off on this server";
  String blk = @PKG@.AccStore.moveBlock(u);
  if (blk != null) return blk;
  int i = index(name);
  if (i < 0 || !visible(i)) return "there is no Power called " + clean(name) + " here - " + listText(u);
  String lock = lockOf(u, i);
  if (lock != null) return PW_NAME[i] + " is locked - it " + lock;
  if (effIndex(u, k) == i) return PW_NAME[i] + " is already your Power";
  if (wait) {
    long left = waitLeft(k, now);
    if (left > 0L) return "wait " + ((left + 999L) / 1000L) + " s before you switch your Power again";
  }
  if (!writePick(k, PW_ID[i], now)) return "your Power could not be saved - tell an admin (server log)";
  PICKS = PICKS + 1L;
  return "Power is now " + PW_NAME[i] + " - your stats follow within a second";
}""")
# "+11 HP, +6 Def, +6 Str, +2% Crit Chance ..." of Power i at multiplier m (only the stats that work here)
JM(apw_, r"""
public static String statText(int i, double m) {
  StringBuilder b = new StringBuilder();
  for (int e = 0; e < E_PW.length; e++) {
    if (E_PW[e] != i || !works(e)) continue;
    double v = valueAt(e, m);
    if (v == 0.0) continue;
    if (b.length() > 0) b.append(", ");
    b.append(v > 0.0 ? "+" : "").append(E_KIND[e] == 0 || E_KIND[e] == 3 ? String.valueOf((long) v) : oneDec(v));
    b.append(E_PCT[e] == 1 ? "% " : " ").append(E_LABEL[e]);
  }
  return b.length() == 0 ? "nothing yet - put accessories in Void Charms for Accessory Power" : b.toString();
}""")
JM(apw_, r"""
public static String multText(double m) {
  long c = Math.round(m * 100.0);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""")
# ---- the doors (spec 4): skill:bonus:<uuid> source "accessories" (replaced whole, removed when empty), acc:power:<uuid>
JM(apw_, r"""
public static void publishBonus(java.util.UUID u, java.util.HashMap want) {
  if (u == null) return;
  String key = "skill:bonus:" + u.toString();
  java.util.Map b = @PKG@.AccStore.bridge();
  Object last = LASTB.get(u);
  Object o = b.get(key);
  if (want == null || want.isEmpty()) {
    if (last != null) {
      if (o instanceof java.util.Map) ((java.util.Map) o).remove(SRC, last);
      LASTB.remove(u);
    }
    return;
  }
  if (last != null && last.equals(want) && o instanceof java.util.Map && ((java.util.Map) o).get(SRC) == last) return;
  java.util.Map m = null;
  if (o instanceof java.util.Map) m = (java.util.Map) o;
  else { m = new java.util.concurrent.ConcurrentHashMap(); b.put(key, m); }
  java.util.Map v = java.util.Collections.unmodifiableMap(new java.util.HashMap(want));
  m.put(SRC, v);
  LASTB.put(u, v);
}""")
JM(apw_, r"""
public static void publishTag(java.util.UUID u, String tag) {
  String key = "acc:power:" + u.toString();
  Object last = LASTP.get(u);
  if (tag.equals(last)) return;
  @PKG@.AccStore.bridge().put(key, tag);
  LASTP.put(u, tag);
}""")
# THE TICK (AccEffects, the player's world thread, once a second): publishes the gathering stats + acc:power and returns the combat sums
# { hp, def, str, cc, cd, mp, mana, spd } for AccEffects to apply. profile:busy: the gathering source goes and null comes back - AccEffects then
# changes no Health / Mana / Stamina modifier, no movement and no gear:extra text that second (critic: no previous profile's numbers)
JM(apw_, r"""
public static double[] tick(java.util.UUID u, String[] s) {
  double[] c = new double[C_KEYS.length];
  if (u == null) return c;
  if (@PKG@.AccStore.moveBlock(u) != null) {   // the live player may not be the active profile's: AccEffects writes no stat this second
    publishBonus(u, null);
    return null;
  }
  String k = @PKG@.AccStore.pkey(u);
  int ap = apOf(s);
  int i = effIndex(u, k);
  publishTag(u, (ON ? (i >= 0 ? PW_ID[i] : "None") : "Off") + "|" + ap);
  java.util.HashMap g = new java.util.HashMap();
  if (ON && i >= 0) {
    double m = mult(ap);
    for (int e = 0; e < E_PW.length; e++) {
      if (E_PW[e] != i) continue;
      double v = valueAt(e, m);
      if (v == 0.0) continue;
      if (E_C[e] >= 0) c[E_C[e]] = c[E_C[e]] + v;
      else if (works(e)) g.put(E_KEY[e], Double.valueOf(v / 100.0));
    }
  }
  publishBonus(u, g);
  LASTC.put(u, c);
  return c;
}""")
JM(apw_, r"""
public static String owner(Object k) {
  String s = String.valueOf(k);
  return s.length() >= 36 ? s.substring(0, 36) : s;
}""")
# AccTick (every 5 s): players who left lose our skill:bonus source and acc:power; their caches go
JM(apw_, r"""
public static void prune(java.util.Set online) {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = new java.util.ArrayList(LASTB.keySet()).iterator();
  while (it.hasNext()) { java.util.UUID u = (java.util.UUID) it.next(); if (!online.contains(u)) publishBonus(u, null); }
  it = new java.util.ArrayList(LASTP.entrySet()).iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online.contains(e.getKey())) continue;
    b.remove("acc:power:" + e.getKey().toString(), e.getValue());
    LASTP.remove(e.getKey());
  }
  LASTC.keySet().retainAll(online);
  LV.keySet().retainAll(online);
  java.util.HashSet on = new java.util.HashSet();
  java.util.Iterator oi = online.iterator();
  while (oi.hasNext()) on.add(String.valueOf(oi.next()));
  it = PICK.keySet().iterator();
  while (it.hasNext()) if (!on.contains(owner(it.next()))) it.remove();
  it = BADP.keySet().iterator();
  while (it.hasNext()) if (!on.contains(owner(it.next()))) it.remove();
}""")
JM(apw_, r"""
public static void shutdownAll() {
  prune(new java.util.HashSet());
}""")
# ---- drop-only lines (spec 5.2): line key "T:<family>" (AccDefs.groupOf)
JM(apw_, r"""
public static boolean dropUp(String g) {
  if (g == null || !g.startsWith("T:")) return false;
  String f = g.substring(2);
  for (int i = 0; i < DROP_UP.length; i++) if (DROP_UP[i].equals(f)) return true;
  return false;
}""")
JM(apw_, r"""
public static boolean dropOnly(String g) {
  if (g == null || !g.startsWith("T:")) return false;
  String f = g.substring(2);
  for (int i = 0; i < DROP_ONLY.length; i++) if (DROP_ONLY[i].equals(f)) return true;
  return false;
}""")
JM(apw_, r"""
public static String dropText(String id) {
  String g = @PKG@.AccDefs.groupOf(@PKG@.AccDefs.modernOf(id));
  if (dropUp(g)) return "Drop only - upgrade it in Craft while it is in Void Charms";
  if (dropOnly(g)) return "Drop only - cannot be upgraded";
  return "";
}""")

# ================= 0.5.22 AccPowerFn: bridge acc:fn:power (spec 3 'Loadouts'; SkyyWardrobe saves the Power with a loadout)
# apply(Object[]{"get", UUID}) -> String the Power id that works now ("" = none); apply(Object[]{"set", UUID, String id or name}) -> String
# the result ("Power is now ..." = done; no switch wait for a loadout). World thread for "set" (it writes the profile's file).
# mode 1 = once:item:Skyy_Accessory_Bag (tools/skyyonce.py rule 6, read by SkyyIslands 0.5.17+ kitSkip): always TRUE - the retired bag item
# never goes into a starter kit / island reset chest (0.5.20 published it while the item was lifelong; without it the default kit would
# hand the retired item out again)
apf_.addInterface(pool.get("java.util.function.Function"))
JF(apf_, "public int mode = 0;")
apf_.addConstructor(CtNewConstructor.make("public AccPowerFn() { }", apf_))
apf_.addConstructor(CtNewConstructor.make("public AccPowerFn(int m) { this.mode = m; }", apf_))
JM(apf_, r"""
public Object apply(Object arg) {
  if (this.mode == 1) return Boolean.TRUE;
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof String) || !(a[1] instanceof java.util.UUID)) return null;
    java.util.UUID u = (java.util.UUID) a[1];
    String k = @PKG@.AccStore.pkey(u);
    if ("get".equals(a[0])) {
      int i = @PKG@.AccPower.effIndex(u, k);
      return i >= 0 ? @PKG@.AccPower.PW_ID[i] : "";
    }
    if ("set".equals(a[0]) && a.length > 2 && a[2] instanceof String) return @PKG@.AccPower.pick(u, k, (String) a[2], System.currentTimeMillis(), false);
    return null;
  } catch (Throwable t) { @PKG@.AccStore.warn("acc:fn:power failed: " + t); return null; }
}""")
print("0.5.22 Accessory Power: %d Powers (%s), %d stat entries, AP %s, Omni %d AP, drop-up lines %s" % (
    len(PW_TABLE), ", ".join(_p[1] for _p in PW_TABLE), len(PW_E), PW_DEFS["power.ap"], PW_OMNI_DEF, ", ".join(DROP_UP)))

# ================= AccCfg (0.4.4; 0.5: booster entries, line switches, notice switch, the one-time 0.5 migration) =================
cfg_.addField(CtField.make("public static java.nio.file.Path FILE;", cfg_))
cfg_.addField(CtField.make("public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT), cfg_))
cfg_.addField(CtField.make("public static final String[] BOOST_DEF = new String[] { %s };" % jstrs(BOOST_DEF), cfg_))   # index = AccDefs.E_KEYS
cfg_.addField(CtField.make('public static volatile String TIP_SEEN = "";', cfg_))   # the last "differs from the tooltips" text logged
# 0.5 migration data (spec 5.1)
cfg_.addField(CtField.make("public static final String[] OLD_FAM = new String[] { %s };" % jstrs(o[0] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_DEF = new String[] { %s };" % jstrs(o[1] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_CARRY = new String[] { %s };" % jstrs(o[2] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_WHY = new String[] { %s };" % jstrs(o[3] for o in OLD_BONUS), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_KEY = new String[] { %s };" % jstrs(ADD_KEY), cfg_))
cfg_.addField(CtField.make("public static final String[] ADD_VAL = new String[] { %s };" % jstrs(ADD_VAL), cfg_))
cfg_.addField(CtField.make("public static final int[] ADD_GROUP = new int[] { %s };" % ", ".join(str(g) for g in ADD_GROUP), cfg_))
cfg_.addField(CtField.make("public static final String[] GROUP_NOTE = new String[] { %s };" % jstrs(GROUP_NOTE), cfg_))
cfg_.addField(CtField.make("public static final String[] OLD_COMMENT = new String[] { %s };" % jstrs(o for o, n in OLD_COMMENTS), cfg_))
cfg_.addField(CtField.make("public static final String[] NEW_COMMENT = new String[] { %s };" % jstrs(n for o, n in OLD_COMMENTS), cfg_))
# 0.5.4 the Lantern: the switch and the keys with their bounds; defaults in AccDefs.LAN_DEF (0.5.3's Night Vision keys are ignored)
cfg_.addField(CtField.make('public static final String LAN_SWITCH = "%s";' % LAN_SWITCH, cfg_))
cfg_.addField(CtField.make('public static final String LAN_SHARE_KEY = "%s";' % LAN_SHARE_KEY, cfg_))   # fix round
cfg_.addField(CtField.make('public static final String LAN_HELMET_KEY = "%s";' % LAN_HELMET_KEY, cfg_))   # 0.5.10
cfg_.addField(CtField.make('public static final String STARTER_KEY = "%s";' % STARTER_KEY, cfg_))   # 0.5.17
cfg_.addField(CtField.make('public static final String CRAFT_KEY = "%s";' % CRAFT_KEY, cfg_))   # 0.5.18
cfg_.addField(CtField.make('public static final String AUTO_KEY = "%s";' % AUTO_KEY, cfg_))     # 0.5.18
cfg_.addField(CtField.make('public static final String LIFE_KEY = "%s";' % LIFE_KEY, cfg_))     # 0.5.20
cfg_.addField(CtField.make("public static final String[] LAN_KEYS = new String[] { %s };" % jstrs(LAN_KEYS), cfg_))
cfg_.addField(CtField.make("public static final int[] LAN_MIN = new int[] { %s };" % ", ".join(str(_x) for _x in LAN_MIN), cfg_))
cfg_.addField(CtField.make("public static final int[] LAN_MAX = new int[] { %s };" % ", ".join(str(_x) for _x in LAN_MAX), cfg_))
for _src in [
r"""
public static void info(String msg) {
  try { if (@PKG@.AccStore.LOG != null) @PKG@.AccStore.LOG.at(java.util.logging.Level.INFO).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""",
r"""
public static void writeDefaults() {
  try {
    if (FILE == null || java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    info("wrote the first config.properties with the built-in settings: " + FILE);
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write the default config.properties: " + t); }
}""",
r"""
public static double num(String t) {
  if (t == null) return -1.0;
  String x = t.trim();
  if (x.length() == 0 || x.length() > 12) return -1.0;
  int dot = -1;
  for (int i = 0; i < x.length(); i++) {
    char c = x.charAt(i);
    if (c == '.') {
      if (dot >= 0 || i == 0 || i == x.length() - 1) return -1.0;
      dot = i;
    } else if (c < '0' || c > '9') return -1.0;
  }
  if (dot >= 0 && x.length() - dot - 1 > 2) return -1.0;
  try { return Double.parseDouble(x); } catch (Throwable e) { return -1.0; }
}""",
# "6,12,18,24" -> n numbers (n = 4 for a booster entry, 5 for a 0.4.x bonus list), or null when it is not exactly n numbers >= 0
r"""
public static double[] parseN(String v, int n) {
  if (v == null) return null;
  String[] p = v.split(",", -1);
  if (p.length != n) return null;
  double[] out = new double[n];
  for (int i = 0; i < n; i++) {
    double x = num(p[i]);
    if (x < 0.0) return null;
    out[i] = x;
  }
  return out;
}""",
r"""
public static boolean sameRow(double[] a, double[] b) {
  if (a == null || b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) if (Math.abs(a[i] - b[i]) > 0.0000001) return false;
  return true;
}""",
r"""
public static String dtext(double v) {
  long c = Math.round(v * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  if (c % 10L == 0L) return String.valueOf(c / 100L) + "." + String.valueOf((c % 100L) / 10L);
  String f = String.valueOf(c % 100L);
  if (f.length() < 2) f = "0" + f;
  return String.valueOf(c / 100L) + "." + f;
}""",
r"""
public static String rowText(double[] r) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < r.length; i++) { if (i > 0) sb.append(','); sb.append(dtext(r[i])); }
  return sb.toString();
}""",
r"""
public static int intIn(String v, int def, int lo, int hi, String key) {
  if (v == null) return def;
  int n = def;
  try { n = Integer.parseInt(v.trim()); }
  catch (Throwable t) { @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not a whole number - " + def + " is used"); return def; }
  if (n < lo) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is below " + lo + " - " + lo + " is used"); return lo; }
  if (n > hi) { @PKG@.AccStore.warn("config.properties: " + key + "=" + n + " is above " + hi + " - " + hi + " is used"); return hi; }
  return n;
}""",
r"""
public static boolean boolIn(String v, boolean def, String key) {
  if (v == null) return def;
  String x = v.trim().toLowerCase();
  if (x.equals("true") || x.equals("on") || x.equals("yes") || x.equals("1")) return true;
  if (x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0")) return false;
  @PKG@.AccStore.warn("config.properties: " + key + "=" + v.trim() + " is not true or false - " + (def ? "true" : "false") + " is used");
  return def;
}""",
r"""
public static int entryIndex(String en) {
  if (en == null) return -1;
  for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) if (@PKG@.AccDefs.E_KEYS[i].equals(en)) return i;
  return -1;
}""",
# one booster entry from the file: 4 numbers, capped at the entry's cap, whole numbers where the entry needs them (the loader clamps like
# the kit validates; a line that is not 4 numbers falls back to the built-in numbers)
r"""
public static double[] boostIn(String v, int e) {
  double[] d = parseN(BOOST_DEF[e], 4);
  if (v == null) return d;
  String k = "boost." + @PKG@.AccDefs.E_KEYS[e];
  double[] r = parseN(v, 4);
  if (r == null) {
    @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " is not 4 numbers like " + BOOST_DEF[e] + " (Normal,Unique,Rare,Legendary; 0 or more, at most 2 decimals, no minus sign) - the built-in numbers are used");
    return d;
  }
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  boolean cl = false;
  boolean wh = false;
  for (int t = 0; t < 4; t++) {
    if (r[t] > cap) { r[t] = cap; cl = true; }
    if (@PKG@.AccDefs.E_WHOLE[e] == 1 && r[t] != Math.floor(r[t])) { r[t] = Math.floor(r[t]); wh = true; }
  }
  if (cl) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " has a number above " + dtext(cap) + " - " + dtext(cap) + " is used there");
  if (wh) @PKG@.AccStore.warn("config.properties: " + k + "=" + v.trim() + " takes whole numbers only - the decimals are dropped");
  return r;
}""",
r"""
public static String oneLine(String t) {
  if (t == null) return "";
  return t.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ');
}""",
# the key of one physical .properties line (null for a comment or a blank line)
r"""
public static String keyOf(String ln) {
  if (ln == null) return null;
  int i = 0;
  while (i < ln.length() && (ln.charAt(i) == ' ' || ln.charAt(i) == '\t' || ln.charAt(i) == '\f')) i++;
  if (i >= ln.length()) return null;
  char c0 = ln.charAt(i);
  if (c0 == '#' || c0 == '!') return null;
  int j = i;
  while (j < ln.length()) {
    char c = ln.charAt(j);
    if (c == '=' || c == ':' || c == ' ' || c == '\t' || c == '\f') break;
    j++;
  }
  return ln.substring(i, j);
}""",
# a value line that continues on the next physical line (an odd number of backslashes at the end)
r"""
public static boolean contLine(String ln) {
  int n = 0;
  for (int i = ln.length() - 1; i >= 0 && ln.charAt(i) == '\\'; i--) n++;
  return n % 2 == 1;
}""",
# the migration's change-log lines, in the kit's config-changes.log format (who migration-0.5, uuid -, via migrate) + one INFO line each
r"""
public static void logMig(java.util.ArrayList logs) {
  StringBuilder sb = new StringBuilder();
  String now = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").format(java.time.LocalDateTime.now());
  for (int i = 0; i < logs.size(); i++) {
    String[] e = (String[]) logs.get(i);
    sb.append(now).append('\t').append("migration-0.5").append('\t').append('-').append('\t').append("migrate").append('\t');
    sb.append(oneLine(e[0])).append('\t').append(oneLine(e[1])).append('\t').append(oneLine(e[2])).append('\t').append(oneLine(e[3])).append('\n');
    info("config " + oneLine(e[0]) + " " + oneLine(e[1]) + " -> " + oneLine(e[2]) + " by migration-0.5 (migrate)" + ("ok".equals(e[3]) ? "" : " [" + e[3] + "]"));
  }
  try {
    java.nio.file.Path lf = FILE.resolveSibling("config-changes.log");
    java.nio.file.Files.write(lf, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.AccStore.warn("could not write config-changes.log for the 0.5 update: " + t); }
}""",
# THE ONE-TIME 0.5 MIGRATION (spec 5.1). setup() -> load(true) -> here, BEFORE CfgPub.start. Runs only when the file has a bonus. line
# and no boost. line (a file with neither just gets the missing 0.5 keys); afterwards there is no bonus. line, so it never runs again.
# One atomic write; the old file is copied once to config.properties.pre-0.5.bak; every changed / carried / dropped / added value is
# logged. Returns "" when nothing was done, else the summary for the ready log line.
r"""
public static String migrate() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return "";
    byte[] raw = java.nio.file.Files.readAllBytes(FILE);
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(raw));
    boolean hasBonus = false;
    boolean hasBoost = false;
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String pk = (String) it.next();
      if (pk.startsWith("bonus.")) hasBonus = true;
      if (pk.startsWith("boost.")) hasBoost = true;
    }
    // 0.5 part 2: mig = the 0.4.x -> 0.5 update (bonus. lines and no boost. line). A file that already has boost. lines (a server
    // that ran part 1) only gets the 0.5 keys it misses appended: no slots change, no removal, no .bak (nothing is lost).
    boolean mig = hasBonus && !hasBoost;
    String text = new String(raw, "ISO-8859-1");
    String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    String body = text;
    if (body.endsWith("\r\n")) body = body.substring(0, body.length() - 2);
    else if (body.endsWith("\n")) body = body.substring(0, body.length() - 1);
    String[] lines = body.length() == 0 ? new String[0] : body.split("\r?\n", -1);
    java.util.ArrayList logs = new java.util.ArrayList();
    java.util.HashMap carried = new java.util.HashMap();
    for (int f = 0; mig && f < OLD_FAM.length; f++) {
      String key = "bonus." + OLD_FAM[f];
      String ov = p.getProperty(key);
      if (ov == null) continue;
      String o = ov.trim();
      double[] r = parseN(o, 5);
      if (r != null && sameRow(r, parseN(OLD_DEF[f], 5))) { logs.add(new String[] { key, o, "(removed - the 0.5 default applies)", "done" }); continue; }
      if (OLD_CARRY[f].length() == 0) { logs.add(new String[] { key, o, "(dropped - " + OLD_WHY[f] + ")", "invalid" }); continue; }
      if (r == null) { logs.add(new String[] { key, o, "(dropped - not 5 numbers, so the 0.5 default applies)", "invalid" }); continue; }
      int e = entryIndex(OLD_CARRY[f]);
      double[] c = new double[] { r[0], r[1], r[2], r[4] };
      String note = "";
      for (int t = 0; t < 4; t++) {
        if (e >= 0 && c[t] > (double) @PKG@.AccDefs.E_CAP[e]) { c[t] = (double) @PKG@.AccDefs.E_CAP[e]; note = ", capped at " + dtext(c[t]); }
      }
      String cv = rowText(c);
      carried.put(OLD_CARRY[f], cv);
      logs.add(new String[] { key, o, "boost." + OLD_CARRY[f] + "=" + cv + " (the 1st, 2nd, 3rd and 5th number - the 4th, " + dtext(r[3]) + ", is dropped" + note + ")", "done" });
    }
    String sv = p.getProperty("slots");
    boolean bump = mig && sv != null && sv.trim().equals("9");
    boolean bumped = false;
    StringBuilder out = new StringBuilder();
    boolean contDrop = false;
    boolean contKeep = false;
    for (int i = 0; i < lines.length; i++) {
      String ln = lines[i];
      if (contDrop) { contDrop = contLine(ln); continue; }
      if (contKeep) { contKeep = contLine(ln); out.append(ln).append(nl); continue; }
      String k = keyOf(ln);
      if (mig && k != null && k.startsWith("bonus.")) { contDrop = contLine(ln); continue; }
      if (bump && "slots".equals(k) && !contLine(ln)) { out.append("slots=@SLOTS@").append(nl); bumped = true; continue; }
      if (mig && k == null) {
        int oc = -1;
        for (int j = 0; j < OLD_COMMENT.length; j++) if (OLD_COMMENT[j].equals(ln)) oc = j;
        if (oc >= 0) { if (NEW_COMMENT[oc].length() > 0) out.append(NEW_COMMENT[oc]).append(nl); continue; }
      }
      if (k != null) contKeep = contLine(ln);
      out.append(ln).append(nl);
    }
    if (bumped) logs.add(0, new String[] { "slots", "9", "@SLOTS@", "ok" });
    StringBuilder add = new StringBuilder();
    int lastGroup = -1;
    for (int a = 0; a < ADD_KEY.length; a++) {
      if (p.getProperty(ADD_KEY[a]) != null) continue;
      String v = ADD_VAL[a];
      if (ADD_KEY[a].startsWith("boost.")) {
        String cv2 = (String) carried.get(ADD_KEY[a].substring(6));
        if (cv2 != null) v = cv2;
        logs.add(new String[] { "boost[" + ADD_KEY[a].substring(6) + "]", "(none)", v, "done" });
      } else logs.add(new String[] { ADD_KEY[a], "(none)", v, "done" });
      if (ADD_GROUP[a] != lastGroup) {
        lastGroup = ADD_GROUP[a];
        String[] nt = GROUP_NOTE[lastGroup].split("\n");
        for (int j = 0; j < nt.length; j++) add.append(nt[j]).append(nl);
      }
      add.append(ADD_KEY[a]).append('=').append(v).append(nl);
    }
    if (logs.size() == 0) return "";
    String result = out.toString();
    if (add.length() > 0) result = result + "# ---- added by SkyyAccessories 0.5 (booster accessories) ----" + nl + add.toString();
    java.nio.file.Path bak = FILE.resolveSibling(FILE.getFileName().toString() + ".pre-0.5.bak");
    if (!hasBoost && !java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0])) java.nio.file.Files.copy(FILE, bak, new java.nio.file.CopyOption[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp-0.5");
    java.io.FileOutputStream fo = new java.io.FileOutputStream(tmp.toFile());
    try { fo.write(result.getBytes("ISO-8859-1")); fo.flush(); fo.getFD().sync(); } finally { fo.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    logMig(logs);
    if (hasBoost) return "config.properties: " + logs.size() + " missing 0.5 settings added (config-changes.log)";
    return "config.properties updated to 0.5 (" + logs.size() + " changes in config-changes.log, the old file kept as config.properties.pre-0.5.bak)";
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to 0.5 - it stays as it is, and the built-in 0.5 numbers apply where it has none: " + t);
    return "config.properties could not be updated to 0.5 (see the warning)";
  }
}""",
# the mod's loader: setup() (first = true: writes the 0.5 default file or migrates a 0.4.x one, first) and the kit's RELOAD after every
# save / hand edit
r"""
public static String load(boolean first) {
  String mig = "";
  if (first) { writeDefaults(); mig = migrate(); }
  java.util.Properties p = new java.util.Properties();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) {
    if (!first) {
      @PKG@.AccStore.warn("config.properties could not be read - the current settings stay: " + t);
      return "config.properties could not be read - the current settings stay";
    }
    @PKG@.AccStore.warn("config.properties could not be read - the built-in settings are used: " + t);
    p = new java.util.Properties();
  }
  int sl = intIn(p.getProperty("slots"), @SLOTS@, 1, @CAP@, "slots");
  int rg = intIn(p.getProperty("regenEverySeconds"), @REGEN@, 1, @RMAX@, "regenEverySeconds");
  float[] bo = new float[@NE@ * 5];
  StringBuilder bt = new StringBuilder();
  for (int e = 0; e < @NE@; e++) {
    double[] r = boostIn(p.getProperty("boost." + @PKG@.AccDefs.E_KEYS[e]), e);
    bo[e * 5] = 0.0f;
    for (int t = 0; t < 4; t++) bo[e * 5 + t + 1] = (float) r[t];
    if (!sameRow(r, parseN(BOOST_DEF[e], 4))) bt.append(", ").append(@PKG@.AccDefs.E_KEYS[e]).append(' ').append(rowText(r));
  }
  boolean[] on = new boolean[@NL@];
  StringBuilder off = new StringBuilder();
  for (int li = 0; li < @NL@; li++) {
    on[li] = boolIn(p.getProperty("line." + @PKG@.AccDefs.LINE_ADMIN[li]), true, "line." + @PKG@.AccDefs.LINE_ADMIN[li]);
    if (!on[li]) off.append(", ").append(@PKG@.AccDefs.LINE_ADMIN[li]);
  }
  boolean nt = boolIn(p.getProperty("notice.boosters"), true, "notice.boosters");
  boolean cg = boolIn(p.getProperty("combatToGear"), true, "combatToGear");   // 0.5 part 2
  boolean lanOn = boolIn(p.getProperty(LAN_SWITCH), true, LAN_SWITCH);   // 0.5.4: the Lantern - the switch and its numbers (a missing key = its default)
  boolean lanShare = boolIn(p.getProperty(LAN_SHARE_KEY), false, LAN_SHARE_KEY);   // the fix round: the reach light shown to everyone (off)
  boolean lanHelmet = boolIn(p.getProperty(LAN_HELMET_KEY), true, LAN_HELMET_KEY);   // 0.5.10: the mining helmet light (on)
  boolean starter = boolIn(p.getProperty(STARTER_KEY), true, STARTER_KEY);   // 0.5.17: the starter Void Charms (on)
  boolean craftOn = boolIn(p.getProperty(CRAFT_KEY), true, CRAFT_KEY);   // 0.5.18: the Craft tab of the bag page (on)
  boolean autoOn = boolIn(p.getProperty(AUTO_KEY), true, AUTO_KEY);      // 0.5.18: crafted accessories into the bag (on)
  boolean lifeOn = boolIn(p.getProperty(LIFE_KEY), true, LIFE_KEY);      // 0.5.20: the lifelong Void Charms (on)
  int[] lanv = new int[LAN_KEYS.length];
  for (int q = 0; q < LAN_KEYS.length; q++) lanv[q] = intIn(p.getProperty(LAN_KEYS[q]), @PKG@.AccDefs.LAN_DEF[q], LAN_MIN[q], LAN_MAX[q], LAN_KEYS[q]);
  @PKG@.AccStore.SLOTS = sl;
  @PKG@.AccDefs.REGEN_EVERY = rg;
  @PKG@.AccDefs.BOOST = bo;
@SETLINES@
  @PKG@.AccDefs.NOTICE = nt;
  @PKG@.AccDefs.COMBAT_TO_GEAR = cg;
  @PKG@.AccDefs.LINE_LANTERN = lanOn;   // 0.5.4
  @PKG@.AccDefs.LAN_SHARE = lanShare;
  @PKG@.AccDefs.LAN_HELMET = lanHelmet;   // 0.5.10
  @PKG@.AccDefs.STARTER = starter;   // 0.5.17
  @PKG@.AccDefs.CRAFT = craftOn;   // 0.5.18
  @PKG@.AccDefs.AUTO = autoOn;     // 0.5.18
  @PKG@.AccDefs.LIFELONG = lifeOn;   // 0.5.20
@SETLAN@
  StringBuilder tip = new StringBuilder();
  if (rg != @REGEN@) tip.append(", Regeneration every ").append(rg).append(" s");
  tip.append(bt.toString());
  String ts = "";
  if (tip.length() > 0) ts = tip.substring(2);
  if (!ts.equals(TIP_SEEN)) {
    TIP_SEEN = ts;
    if (ts.length() > 0) info("this server's booster numbers differ from what the item tooltips print (built-in numbers - the Void Charms page and /charms lines show the live ones): " + ts);
  }
  String bs = "built-in";
  if (bt.length() > 0) bs = "custom (" + bt.substring(2) + ")";
  String res = "config " + sl + " charm slots, Regeneration every " + rg + " s, booster numbers " + bs;
  if (off.length() > 0) res = res + ", lines switched off: " + off.substring(2);
  if (!nt) res = res + ", the 0.5 notice is off";
  if (!cg) res = res + ", combat stats are not sent to SkyyGear (combatToGear=false)";
  if (!lanOn) res = res + ", Lantern switched off";   // 0.5.4
  if (lanShare) res = res + ", Lantern reach light shown to everyone";
  if (!lanHelmet) res = res + ", mining helmet light switched off";   // 0.5.10
  if (!starter) res = res + ", starter Void Charms switched off";   // 0.5.17
  if (!craftOn) res = res + ", the Void Charms Craft tab switched off";   // 0.5.18
  if (!autoOn) res = res + ", auto-equip of crafted accessories switched off";   // 0.5.18
  StringBuilder lc = new StringBuilder();
  for (int q = 0; q < LAN_KEYS.length; q++) if (lanv[q] != @PKG@.AccDefs.LAN_DEF[q]) lc.append(lc.length() > 0 ? ", " : "").append(LAN_KEYS[q]).append('=').append(lanv[q]);
  if (lc.length() > 0) res = res + ", Lantern numbers custom (" + lc.toString() + ")";
  if (mig.length() > 0) res = res + "; " + mig;
  return res;
}""",
r"""
public static String reload() {
  String r = load(false) + "; " + @PKG@.AccPower.load();   // 0.5.22: + power.properties (the pw table, Accessory Power)
  info("config.properties applied: " + r);
  return r;
}""",
# check= hook of the boost table: key = boost[<entry>], value = the canonical text, null = a removal
r"""
public static String checkBoost(String key, String value) {
  String en = key == null ? "" : key;
  int a = en.indexOf('[');
  int b = en.lastIndexOf(']');
  if (a >= 0 && b > a) en = en.substring(a + 1, b);
  int e = entryIndex(en);
  if (e < 0) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < @PKG@.AccDefs.E_KEYS.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.E_KEYS[i]); }
    return "Unknown entry. The booster entries are: " + sb.toString() + ".";
  }
  if (value == null) return "The " + en + " line stays - set it to " + BOOST_DEF[e] + " to go back to the built-in numbers.";
  double[] r = parseN(value, 4);
  if (r == null) return "Needs 4 numbers for Normal,Unique,Rare,Legendary like " + BOOST_DEF[e] + " (no minus sign, up to 2 decimals).";
  double cap = (double) @PKG@.AccDefs.E_CAP[e];
  for (int t = 0; t < 4; t++) if (r[t] > cap) return "Each number must be from 0 to " + dtext(cap) + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  if (@PKG@.AccDefs.E_WHOLE[e] == 1) {
    for (int t = 0; t < 4; t++) if (r[t] != Math.floor(r[t])) return "Whole numbers only for " + en + " - " + @PKG@.AccDefs.DISPLAY[t + 1] + " is " + dtext(r[t]) + ".";
  }
  return null;
}""",
]:
    _src = JX(_src).replace("@CAP@", str(CAP)).replace("@SLOTS@", str(SLOTS_DEF)).replace("@REGEN@", str(REGEN_EVERY)) \
        .replace("@RMAX@", str(REGEN_MAX)).replace("@NE@", str(len(ENTRIES))).replace("@NL@", str(len(BOOSTERS))) \
        .replace("@SETLINES@", "\n".join("  %s.AccDefs.LINE_%s = on[%d];" % (PKG, b[1].upper(), i) for i, b in enumerate(BOOSTERS))) \
        .replace("@SETLAN@", "\n".join("  %s.AccDefs.%s = lanv[%d];" % (PKG, f, i) for i, f in enumerate(LAN_FIELDS)))   # 0.5.4
    assert "@" not in _src.replace("@PKG@", ""), _src[:80]
    cfg_.addMethod(CtNewMethod.make(_src, cfg_))

# ================= the admin config kit (0.4.4; research/Server-Setup-Spec.md 4.14, tools/CONFIG-CONTRACT.md; 0.5 rows: spec 5.8) =================
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind) - row key = file key (spec 7: the file key never changes)
CFG_CATS = [("bag", "Void Charms"), ("power", "Accessory Power"), ("boosters", "Boosters"), ("lantern", "Lantern")]   # 0.5.22: + Accessory Power   # 0.5.4: Lantern (0.5.3's Night Vision is retired)
CFG_ROWS = [
    ("slots", "Charm slots", "bag", "int", str(SLOTS_DEF), "1", str(CAP), "step=1", "", "new,danger",
     "Lowering it deletes nothing: accessories already in higher slots stay and count until taken out.",
     "field:AccStore.SLOTS@config.properties:slots;confirm=down"),
    ("notice.boosters", "Tell players about the accessory change", "bag", "bool", "true", "", "", "", "", "live",
     "One chat line, once, for each player who had accessories before 0.5.",
     "field:AccDefs.NOTICE@config.properties:notice.boosters"),
    ("regenEverySeconds", "Regeneration heals every", "boosters", "int", str(REGEN_EVERY), "1", str(REGEN_MAX), "step=1", "s", "live,adv",
     "How often the Regeneration Accessory heals. Its item tooltip keeps saying %d seconds." % REGEN_EVERY,
     "field:AccDefs.REGEN_EVERY@config.properties:regenEverySeconds"),
    ("boost", "Booster numbers", "boosters", "table", "", "", "60", "text;type;Normal..Legendary", "", "live,danger",
     "Four numbers, Normal to Legendary. The entry name gives the unit. Fall is written without a minus.",
     "reload@config.properties:boost.;check=AccCfg.checkBoost"),
    ("combatToGear", "Send combat stats to SkyyGear", "boosters", "bool", "true", "", "", "", "", "live",
     "Off = %s add nothing (SkyyGear applies their stats)." % " and ".join(
         [", ".join(COMBAT_LINES[:-1]), COMBAT_LINES[-1]] if len(COMBAT_LINES) > 1 else COMBAT_LINES),
     "field:AccDefs.COMBAT_TO_GEAR@config.properties:combatToGear"),
] + [("line.%s" % _b[1], "%s line" % _b[2], "boosters", "bool", "true", "", "", "", "", "live",
      "Off = the line stays in Void Charms, counts for nothing and the Void Charms page says switched off.",
      "field:AccDefs.LINE_%s@config.properties:line.%s" % (_b[1].upper(), _b[1])) for _b in BOOSTERS] + LAN_ROWS + [LAN_HELMET_ROW] + [CRAFT_ROW, AUTO_ROW] + PW_ROWS   # 0.5.22: the bag item is retired (starter.bag / lifelong.bag rows gone: their keys are read and ignored) + Accessory Power   # 0.5.20: + lifelong.bag; 0.5.4: + the Lantern; 0.5.10: + the mining helmet light; 0.5.17: + the starter bag; 0.5.18: + craft / auto-equip
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS), [_r[0] for _r in CFG_ROWS if len(_r[10]) > 100]
CFG_NOTE = "Item tooltips show the built-in numbers - the Void Charms page shows this server's."
# 0.5.14 sound pass round 2: Server Setup -> Accessories -> Sounds (Skyy_SkyyAccessories/sounds.properties)
CFG_CATS = CFG_CATS + [("sounds", "Sounds")]
CFG_ROWS = CFG_ROWS + [('sounds.enabled', 'Sounds', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'Off = SkyyAccessories plays no sound at all. Players can also mute every sound in /settings.', 'field:AccSnd.ON@Skyy_SkyyAccessories/sounds.properties:sounds.enabled'), ('sound.equip', 'Charm equipped sound', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'A charm went into a free Void Charms slot. Off = silent.', 'field:AccSnd.S_EQUIP@Skyy_SkyyAccessories/sounds.properties:sound.equip'), ('sound.equip.id', 'Charm equipped sound id', 'sounds', 'text', 'SFX_Drag_Items_Gems', '', '120', '', '', 'live', 'A vanilla sound event id (try it with /soundtest). Empty = no sound.', 'field:AccSnd.S_EQUIP_ID@Skyy_SkyyAccessories/sounds.properties:sound.equip.id;check=AccSnd.check'), ('sound.upgrade', 'Charm upgraded sound', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'A better charm of the same line replaced the old one in Void Charms. Off = silent.', 'field:AccSnd.S_UPGRADE@Skyy_SkyyAccessories/sounds.properties:sound.upgrade'), ('sound.upgrade.id', 'Charm upgraded sound id', 'sounds', 'text', 'SFX_Runebinders_Lattice_Unlock_Local', '', '120', '', '', 'live', 'A vanilla sound event id (try it with /soundtest). Empty = no sound.', 'field:AccSnd.S_UPGRADE_ID@Skyy_SkyyAccessories/sounds.properties:sound.upgrade.id;check=AccSnd.check')]
kit = CFG.emit(pool, PKG, MOD="SkyyAccessories", TITLE="Void Charms", VERSION=VERSION, NODE="skyyaccessories.admin", CATS=CFG_CATS,
               ROWS=CFG_ROWS, FILES=["Skyy_SkyyAccessories/config.properties", "Skyy_SkyyAccessories/sounds.properties", "Skyy_SkyyAccessories/power.properties"], NOTE=CFG_NOTE, RELOAD="AccCfg.reload", KEEP=10,
               DEFAULTS={"config.properties": CONFIG_TEXT, "power.properties": PW_TEXT, "sounds.properties": '# SkyyAccessories sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Void Charms -> Sounds,\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\nsounds.enabled=true\n# Charm equipped: A charm went into a free Void Charms slot.\nsound.equip=true\nsound.equip.id=SFX_Drag_Items_Gems\n# Charm upgraded: A better charm of the same line replaced the old one in Void Charms.\nsound.upgrade=true\nsound.upgrade.id=SFX_Runebinders_Lattice_Unlock_Local\n'})

# ================= 0.5.1: the one-time Stamina defaults update (AccCfg.migrate051; the SkyyGear 0.1.1 migrateStat011 pattern) =================
# compiled after CFG.emit: it uses the kit's own parser (CfgFile), History (CfgHist), change log (CfgLog) and atomic write (CfgRows)
cfg_.addField(CtField.make("public static final String[] M51_KEY = new String[] { %s };" % jstrs(M51_KEYS), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_OLD = new String[] { %s };" % jstrs(_o for _k, _o in M51_OLD), cfg_))
cfg_.addField(CtField.make("public static final String[] M51_NEW = new String[] { %s };" % jstrs(M51_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK = %s;" % jlit(M51_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M51_MARK_ID = %s;" % jlit(M51_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M51_WHO = %s;" % jlit(M51_WHO), cfg_))
for _src in [
# a key exactly as java.util.Properties / the loader read it (case-sensitive) -> the M51_KEY index, -1 = none
r"""
public static int m51Idx(String k) {
  if (k == null || !k.startsWith("boost.")) return -1;
  for (int i = 0; i < M51_KEY.length; i++) if (("boost." + M51_KEY[i]).equals(k)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.key / value / end). null = the 0.5.1 marker
# is already in a comment line (nothing to do); an empty array = no boost. line at all (a 0.4.x file: the 0.5 migration appends the
# 0.5.1 numbers with the marker). Else { new text, "boost.Stamina.flat 1.5,3,4.5,6 -> 3,6,9,12, ...", String[] kept notes,
# String[] { entry, old, new }* }. A key whose LAST live entry (the one Properties keeps) is a one-line entry holding the 0.5 numbers
# (as 4 numbers) is updated: every one-line entry of it that holds them gets the 0.5.1 text (value text only: key, separator and CR
# stay). Anything else is kept: a custom value (noted unless it already is the 0.5.1 default), a continued entry (noted), a missing
# line (silent). The marker goes on its own line right above the first boost.Stamina entry, else above the first boost. entry - the
# start of a logical line, so nothing continues into it. Every line is scanned from the start of a logical line.
r"""
public static Object[] m51Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = M51_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int firstStam = -1;
  int firstBoost = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M51_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    if (firstBoost < 0 && key != null && key.startsWith("boost.")) firstBoost = k;
    int m = m51Idx(key);
    if (m >= 0) {
      if (firstStam < 0) firstStam = k;
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  if (firstBoost < 0) return new Object[0];
  int at = firstStam >= 0 ? firstStam : firstBoost;
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && sameRow(parseN(eff[i], 4), parseN(M51_OLD[i], 4))) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append("boost.").append(M51_KEY[i]).append(' ').append(oneLine(eff[i])).append(" -> ").append(M51_NEW[i]);
      rows.add(M51_KEY[i]);
      rows.add(eff[i]);
      rows.add(M51_NEW[i]);
    } else if (multi[i] || !sameRow(parseN(eff[i], 4), parseN(M51_NEW[i], 4))) {
      kept.add("boost." + M51_KEY[i] + "=" + oneLine(eff[i]) + " kept (custom) - the 0.5.1 default is " + M51_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == at) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M51_MARK + (crm ? "\r" : ""));
    }
    int m2 = m51Idx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && sameRow(parseN(@PKG@.CfgFile.value(l, k).trim(), 4), parseN(M51_OLD[m2], 4))) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M51_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M51_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""",
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): History + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyAccessories)
r"""
public static void m51Kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.AccStore.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors, so the update checks that config-history really holds a copy with exactly these bytes (the
# new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log (SkyyGear review finding 3)
r"""
public static boolean m51Saved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's table format (CfgLog.add without its per-line INFO): time, name, uuid, via, key, old, new,
# status - the key is the table row key + [entry], so Server Setup -> Changes undoes it with a tset back to the old value
r"""
public static String m51Log(String e, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M51_WHO + "\t-\tupdate\tboost[" + @PKG@.CfgRows.oneLine(e) + "]\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), BEFORE load(true) (the loader, the 0.5 migration) and CfgPub.start: the file before this update becomes a History version
# (KEEP 10 since 0.5.6, verified by m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one
# change-log line per updated entry, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; " ("" = nothing
# done: no file, no boost. line yet, marker already there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate051() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m51Update(new String(old, "ISO-8859-1"));
    if (r == null || r.length == 0) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M51_WHO, "before the 0.5.1 Stamina defaults update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.1 Stamina defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(m51Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.1 Stamina defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no Stamina line still had its 0.5 numbers - nothing changed (0.5.1 Stamina marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.1 Stamina defaults (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))

# ================= 0.5.5: the one-time lantern.height update (AccCfg.migrate055; the migrate051 pattern and its kit helpers) =================
cfg_.addField(CtField.make("public static final String M55_KEY = %s;" % jlit(M55_KEY), cfg_))
cfg_.addField(CtField.make("public static final String M55_OLD = %s;" % jlit(M55_OLD), cfg_))
cfg_.addField(CtField.make("public static final String M55_NEW = %s;" % jlit(M55_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M55_MARK = %s;" % jlit(M55_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M55_MARK_ID = %s;" % jlit(M55_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M55_WHO = %s;" % jlit(M55_WHO), cfg_))
for _src in [
# the value as the loader reads an int (trimmed, Integer.parseInt) equals this number
r"""
public static boolean m55Is(String v, String want) {
  if (v == null) return false;
  try { return Integer.parseInt(v.trim()) == Integer.parseInt(want); } catch (Throwable t) { return false; }
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile). null = the 0.5.5 marker is already in a
# comment line. Else { new text, "lantern.height 128 -> 64" or "", String[] kept notes, String[] { key, old, new } or empty }. The LAST
# live lantern.height entry (the one Properties keeps) decides: a one-line entry holding 128 -> every one-line entry holding 128 gets 64
# (value text only: key, separator and CR stay); anything else is kept (a custom value is noted unless it already is 64). The marker goes
# on its own line right above the first lantern.height entry, or at the end of a file without one (the file's own line ending).
r"""
public static Object[] m55Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int first = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M55_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (M55_KEY.equals(@PKG@.CfgFile.key(s))) {
      if (first < 0) first = k;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  boolean mig = eff != null && !multi && m55Is(eff, M55_OLD);
  String chg = "";
  String[] rows = new String[0];
  java.util.ArrayList kept = new java.util.ArrayList();
  if (mig) {
    chg = M55_KEY + " " + oneLine(eff) + " -> " + M55_NEW;
    rows = new String[] { M55_KEY, eff, M55_NEW };
  } else if (eff != null && (multi || !m55Is(eff, M55_NEW))) {
    kept.add(M55_KEY + "=" + oneLine(eff) + " kept (custom) - the 0.5.5 default is " + M55_NEW);
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M55_MARK + nl : text + nl + M55_MARK;
    return new Object[] { out0, chg, (String[]) kept.toArray(new String[0]), rows };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M55_MARK + (crm ? "\r" : ""));
    }
    if (mig && e2 == k && M55_KEY.equals(@PKG@.CfgFile.key(s2)) && m55Is(@PKG@.CfgFile.value(l, k).trim(), M55_OLD)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M55_NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M55_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, (String[]) kept.toArray(new String[0]), rows };
}""",
# one config-changes.log line in the kit's format: time, name, uuid, via, key, old, new, status - a scalar row, so Server Setup -> Changes
# undoes it with a set back to the old value
r"""
public static String m55Log(String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M55_WHO + "\t-\tupdate\t" + M55_KEY + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), after migrate051 and BEFORE load(true) / CfgPub.start: the file before this update becomes a History version (verified by
# m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line when the value
# changed, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; " ("" = nothing done: no file, the marker is
# there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate055() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m55Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M55_WHO, "before the 0.5.5 Lantern defaults update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.5 Lantern defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    if (rows.length == 3) {
      @PKG@.CfgLog.enqueue(m55Log(rows[1], rows[2]));
      @PKG@.CfgLog.flush();
    }
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.5 Lantern default: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: no lantern.height line held the old 128 - nothing changed (0.5.5 Lantern marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.5 Lantern defaults (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))

# ================= 0.5.18: the one-time Lantern reach update (AccCfg.migrate0518; the migrate055 rules for several keys, its kit helpers) =================
cfg_.addField(CtField.make("public static final String[] M518_KEY = new String[] { %s };" % jstrs(M518_KEYS), cfg_))
cfg_.addField(CtField.make("public static final String[] M518_OLD = new String[] { %s };" % jstrs(M518_OLD), cfg_))
cfg_.addField(CtField.make("public static final String[] M518_NEW = new String[] { %s };" % jstrs(M518_NEW), cfg_))
cfg_.addField(CtField.make("public static final String M518_MARK = %s;" % jlit(M518_MARK), cfg_))
cfg_.addField(CtField.make("public static final String M518_MARK_ID = %s;" % jlit(M518_MARK_ID), cfg_))
cfg_.addField(CtField.make("public static final String M518_WHO = %s;" % jlit(M518_WHO), cfg_))
for _src in [
# a key exactly as java.util.Properties / the loader read it -> the M518_KEY index, -1 = none
r"""
public static int m518Idx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < M518_KEY.length; i++) if (M518_KEY[i].equals(k)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile). null = the 0.5.18 marker is already in a
# comment line. Else { new text, "lantern.reach.Normal 6 -> 10, ..." or "", String[] kept notes, String[] { key, old, new }* }. Per key the
# LAST live entry (the one Properties keeps) decides: a one-line entry holding the 0.5.5 default -> every one-line entry of that key holding
# it gets the new default (value text only: key, separator and CR stay); anything else is kept (a custom value is noted unless it already
# is the new default); a missing key stays missing (the loader's default is the new one). The marker goes on its own line right above the
# first entry of any of the keys, or at the end of a file without one (the file's own line ending).
r"""
public static Object[] m518Update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = M518_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(M518_MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int m = m518Idx(@PKG@.CfgFile.key(s));
    if (m >= 0) {
      if (first < 0) first = k;
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && m55Is(eff[i], M518_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(M518_KEY[i]).append(' ').append(oneLine(eff[i])).append(" -> ").append(M518_NEW[i]);
      rows.add(M518_KEY[i]);
      rows.add(eff[i]);
      rows.add(M518_NEW[i]);
    } else if (multi[i] || !m55Is(eff[i], M518_NEW[i])) {
      kept.add(M518_KEY[i] + "=" + oneLine(eff[i]) + " kept (custom) - the 0.5.18 default is " + M518_NEW[i]);
    }
  }
  String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
  if (first < 0) {
    String out0 = (text.length() == 0 || text.endsWith("\n")) ? text + M518_MARK + nl : text + nl + M518_MARK;
    return new Object[] { out0, chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (k == first) {
      boolean crm = raw[k].endsWith("\r") || (k == raw.length - 1 && text.indexOf("\r\n") >= 0);
      out.add(M518_MARK + (crm ? "\r" : ""));
    }
    int m2 = m518Idx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && m55Is(@PKG@.CfgFile.value(l, k).trim(), M518_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + M518_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  StringBuilder sb = new StringBuilder(text.length() + M518_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""",
# one config-changes.log line in the kit's format (a scalar row: Server Setup -> Changes undoes it with a set back to the old value)
r"""
public static String m518Log(String key, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + M518_WHO + "\t-\tupdate\t" + key + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + n + "\tok";
}""",
# setup(), after migrate051 + migrate055 and BEFORE load(true) / CfgPub.start: History copy first (verified by m51Saved), then the kit's
# atomicWrite, one change-log line per changed key, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by "; "
# ("" = nothing done: no file, the marker is there, or a failure - WARN, file untouched, the next start tries again)
r"""
public static synchronized String migrate0518() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = m518Update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    m51Kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), M518_WHO, "before the 0.5.18 Lantern reach update");
    if (!m51Saved(old)) {
      @PKG@.AccStore.warn("config.properties NOT updated to the 0.5.18 Lantern reach: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(m518Log(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.5.18 Lantern reach: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no Lantern reach / lights line still held its 0.5.5 default - nothing changed (0.5.18 Lantern marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append("; ").append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.AccStore.warn("could not update config.properties to the 0.5.18 Lantern reach (the file is used as it is): " + t);
    return "";
  }
}""",
]:
    cfg_.addMethod(CtNewMethod.make(JX(_src), cfg_))

# ================= 0.5 part 2: AccGear - combat stats to SkyyGear (gear:extra:<uuid>), the bag page notes, bridge clean-up =================
# SkyyGear 0.1 (live) / 0.1.1 / 0.1.2 read gear:extra:<uuid> as ONE String ("str:40,cc:10": GearStats.extra -> parseExtra, whole numbers,
# unknown keys skipped) and add it to the totals of every hit (GearStats.totals(..., withExtra = true) in the offence and Defense
# handlers). No other mod writes the key (every build script in this repo checked), so SkyyAccessories OWNS it (spec 5.4, "one
# gear:extra writer" in 4.2): the text is written only when it changes; removed when it becomes empty, for every player who left
# (AccTick, every 5 s) and on shutdown - always with Map.remove(key, ourText), so a text another mod wrote is never removed. A text we
# did not write is overwritten with one WARN per player; when it changes again within 5 s after that overwrite (a second writer) or
# is not a String at all (another format), writing stops for that player until they rejoin or switch profile (profile:epoch changes),
# with one more WARN - two writers never fight every second. Bridge values are java.lang types only.
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> our text in the bridge
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap AT = new java.util.concurrent.ConcurrentHashMap();")      # uuid -> Long ms of our overwrite of a foreign text
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap STOP = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> the profile epoch we stopped at
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> the overwrite WARN was logged
JF(gear, "public static final java.util.concurrent.ConcurrentHashMap MOVED = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> we have a movement entry
JF(gear, 'public static final String SOURCE = "accessories.talismans";')   # our movement protocol source (tools/skyymove.py)
JF(gear, 'public static final String OWNER_FALL = "stat:owner:fallDamage";')   # SkyySkills claims it: it applies every source's fall damage
JM(gear, r"""
public static String keyOf(java.util.UUID u) {
  return "gear:extra:" + u.toString();
}""")
JM(gear, r"""
public static String clip(Object o) {
  String t = String.valueOf(o);
  return t.length() > 80 ? t.substring(0, 80) + "..." : t;
}""")
JM(gear, r"""
public static Object epochMark(java.util.UUID u) {
  Object ep = @PKG@.AccStore.epochOf(u);
  if (ep == null) return "-";
  return ep;
}""")
# the text for one bag: best = AccDefs.activeTiers (switched-off lines 0); every gear:extra entry of the line's best rarity, floored to a
# whole number (SkyyGear floors each part anyway), summed per key, keys in GEAR_KEYS order, zero parts left out; "" = nothing to send
JM(gear, r"""
public static String textOf(int[] best) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR || best == null) return "";
  String[] gk = @PKG@.AccDefs.GEAR_KEYS;
  long[] sum = new long[gk.length];
  float[] bo = @PKG@.AccDefs.BOOST;
  for (int e = 0; e < @PKG@.AccDefs.E_GEAR.length; e++) {
    String g = @PKG@.AccDefs.E_GEAR[e];
    if (g.length() == 0) continue;
    int li = @PKG@.AccDefs.E_LINE[e];
    int t = li >= 0 && li < best.length ? best[li] : 0;
    if (t < 1 || t > 4) continue;
    int gi = -1;
    for (int k = 0; k < gk.length; k++) if (gk[k].equals(g)) gi = k;
    if (gi < 0) continue;
    double v = Math.floor((double) bo[e * 5 + t]);
    if (v > 0.0) sum[gi] = sum[gi] + (long) v;
  }
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < gk.length; k++) {
    if (sum[k] <= 0L) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(gk[k]).append(':').append(sum[k]);
  }
  return sb.toString();
}""")
# 0.5.22: the text for one bag + the Power's combat sums c = AccPower.tick (def, str, cc, cd, mp at C_KEYS indexes 1..5): the lines as
# textOf (combatToGear) plus the Power (power.enabled), summed per key, signed (a Combat 15 debuff can take a key below 0; SkyyGear 0.2+
# parses negative parts) but never below -50 (an admin's -100 per 100 AP x the guard must not reach Defense -100), zero parts left out
JM(gear, r"""
public static String textOf2(int[] best, double[] c) {
  String[] gk = @PKG@.AccDefs.GEAR_KEYS;
  long[] sum = new long[gk.length];
  if (@PKG@.AccDefs.COMBAT_TO_GEAR && best != null) {
    float[] bo = @PKG@.AccDefs.BOOST;
    for (int e = 0; e < @PKG@.AccDefs.E_GEAR.length; e++) {
      String g = @PKG@.AccDefs.E_GEAR[e];
      if (g.length() == 0) continue;
      int li = @PKG@.AccDefs.E_LINE[e];
      int t = li >= 0 && li < best.length ? best[li] : 0;
      if (t < 1 || t > 4) continue;
      for (int k = 0; k < gk.length; k++) if (gk[k].equals(g)) { double v = Math.floor((double) bo[e * 5 + t]); if (v > 0.0) sum[k] = sum[k] + (long) v; }
    }
  }
  if (c != null) {
    for (int q = 0; q < @PKG@.AccPower.C_KEYS.length && q < c.length; q++) {
      for (int k = 0; k < gk.length; k++) if (gk[k].equals(@PKG@.AccPower.C_KEYS[q])) sum[k] = sum[k] + Math.round(c[q]);
    }
  }
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < gk.length; k++) {
    if (sum[k] < -50L) sum[k] = -50L;   // a debuff never goes below -50 (SkyyGear: hits x 100 / (100 + Defense) must stay positive)
    if (sum[k] == 0L) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(gk[k]).append(':').append(sum[k]);
  }
  return sb.toString();
}""")
# publish one player's text (any thread: the bridge is a ConcurrentHashMap; the tick calls it on the world thread once a second).
# Returns 0 nothing written, 1 written, 2 removed, 3 a foreign text overwritten, 4 writing stopped for this player.
JM(gear, r"""
public static int publish(java.util.UUID u, String name, String text, long now) {
  if (u == null) return 0;
  String key = keyOf(u);
  java.util.Map b = @PKG@.AccStore.bridge();
  Object st = STOP.get(u);
  if (st != null) {
    if (st.equals(epochMark(u))) return 0;
    STOP.remove(u);
    AT.remove(u);
    WARNED.remove(u);
    @PKG@.AccCfg.info("gear:extra for " + name + ": the profile switched - SkyyAccessories writes it again");
  }
  String tx = text == null ? "" : text;
  Object cur = b.get(key);
  String last = (String) LAST.get(u);
  if (cur != null && !(cur instanceof String)) {
    STOP.put(u, epochMark(u));
    LAST.remove(u);
    @PKG@.AccStore.warn(key + " (" + name + ") holds a " + cur.getClass().getName() + ", not a text - another mod's format, so SkyyAccessories leaves it alone and sends no accessory combat stats for this player until they rejoin or switch profile");
    return 4;
  }
  boolean foreign = cur != null && (last == null || !last.equals(cur));
  if (foreign) {
    Long at = (Long) AT.get(u);
    if (at != null && now - at.longValue() < 5000L) {
      STOP.put(u, epochMark(u));
      LAST.remove(u);
      AT.remove(u);
      @PKG@.AccStore.warn(key + " (" + name + ") changed again within 5 s after SkyyAccessories wrote it (now: " + clip(cur) + ") - a second writer; SkyyAccessories stops writing it for this player until they rejoin or switch profile");
      return 4;
    }
    if (tx.length() == 0) { LAST.remove(u); return 0; }   // nothing of ours to send: the other text stays
    if (!WARNED.containsKey(u)) {
      WARNED.put(u, Boolean.TRUE);
      @PKG@.AccStore.warn(key + " (" + name + ") held a text SkyyAccessories did not write (" + clip(cur) + ") - SkyyAccessories is the only writer of this key and replaces it");
    }
    b.put(key, tx);
    LAST.put(u, tx);
    AT.put(u, Long.valueOf(now));
    return 3;
  }
  if (tx.length() == 0) {
    LAST.remove(u);
    if (cur != null) { b.remove(key, cur); return 2; }
    return 0;
  }
  if (tx.equals(cur)) { LAST.put(u, tx); return 0; }
  b.put(key, tx);
  LAST.put(u, tx);
  return 1;
}""")
# our movement entry for one player (the protocol's own remove: MoveSync.post with all zeros does exactly this)
JM(gear, r"""
public static void dropMove(java.util.UUID u) {
  try {
    Object o = @PKG@.AccStore.bridge().get("move:" + u.toString());
    if (o instanceof java.util.Map) ((java.util.Map) o).remove(SOURCE);
  } catch (Throwable t) { }
}""")
# every player who left (AccTick, every 5 s, any thread): our gear:extra text and movement entry go, the per-player state is forgotten
JM(gear, r"""
public static void prune(java.util.Set online) {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (online.contains(e.getKey())) continue;
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
    it.remove();
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) {
    java.util.UUID mu = (java.util.UUID) mi.next();
    if (online.contains(mu)) continue;
    dropMove(mu);
    mi.remove();
  }
  AT.keySet().retainAll(online);
  STOP.keySet().retainAll(online);
  WARNED.keySet().retainAll(online);
}""")
# plugin shutdown: every text we wrote and every movement entry of ours leaves the bridge (the bridge outlives a plugin reload)
JM(gear, r"""
public static void shutdownAll() {
  java.util.Map b = @PKG@.AccStore.bridge();
  java.util.Iterator it = LAST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    b.remove(keyOf((java.util.UUID) e.getKey()), e.getValue());
  }
  java.util.Iterator mi = MOVED.keySet().iterator();
  while (mi.hasNext()) dropMove((java.util.UUID) mi.next());
  LAST.clear();
  MOVED.clear();
  AT.clear();
  STOP.clear();
  WARNED.clear();
}""")
# SkyyGear running = its bridge functions are there (gear:fn:stats, gear:gates - SkyyGear 0.1 setup); its combat stats switch = the
# kit's config:fn:SkyyGear "get" of part.stats (a java.lang call; tools/CONFIG-CONTRACT.md: never throws, never touches the world).
# Unknown (no config function, an odd answer) counts as on.
JM(gear, r"""
public static boolean gearRunning() {
  java.util.Map b = @PKG@.AccStore.bridge();
  return b.get("gear:fn:stats") instanceof java.util.function.Function || b.get("gear:gates") != null;
}""")
JM(gear, r"""
public static boolean gearStatsOn() {
  try {
    Object f = @PKG@.AccStore.bridge().get("config:fn:SkyyGear");
    if (!(f instanceof java.util.function.Function)) return true;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "get", "part.stats" });
    if (!(r instanceof String)) return true;
    String x = ((String) r).trim().toLowerCase();
    return !(x.equals("false") || x.equals("off") || x.equals("no") || x.equals("0"));
  } catch (Throwable t) { return true; }
}""")
JM(gear, r"""
public static boolean fallOwned() {
  return @PKG@.AccStore.bridge().get(OWNER_FALL) != null;
}""")
# why the combat lines do nothing for this player right now ("" = they work): the bag page's "Combat stats" note
JM(gear, r"""
public static String combatNote(java.util.UUID u) {
  if (!@PKG@.AccDefs.COMBAT_TO_GEAR) return "not sent - switched off in Server Setup";
  if (!gearRunning()) return "need SkyyGear, which is not running";
  if (!gearStatsOn()) return "off in SkyyGear (Gear stats in combat)";
  if (u != null && STOP.containsKey(u)) return "paused - another mod writes them (server log)";
  return "";
}""")
# the Bonuses well of the bag page: AccDefs.bonusRows + the notes in the free rows (a combat line that sends nothing, Feather's fall part
# without a fall-damage owner) - [key0, value0, ...], BONUS_MAX rows
JM(gear, r"""
public static String[] pageRows(String[] s, java.util.UUID u) {
  String[] r = @PKG@.AccDefs.bonusRows(s);
  int max = @PKG@.AccDefs.BONUS_MAX;
  int n = 0;
  while (n < max && r[n * 2].length() > 0) n++;
  int[] best = @PKG@.AccDefs.activeTiers(s);
  boolean gear = false;
  boolean fall = false;
  for (int li = 0; li < best.length; li++) {
    if (best[li] <= 0) continue;
    if (@PKG@.AccDefs.sendsGear(li, best[li])) gear = true;
    if (@PKG@.AccDefs.hasFall(li, best[li])) fall = true;
  }
  if (gear && n < max) {
    String cn = combatNote(u);
    if (cn.length() > 0) { r[n * 2] = "Combat stats"; r[n * 2 + 1] = cn; n++; }
  }
  if (fall && n < max && !fallOwned()) { r[n * 2] = "Fall damage"; r[n * 2 + 1] = "needs SkyySkills, which is not running"; n++; }
  return r;
}""")

# ================= AccFn (bridge function acc:fn:has) =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public AccFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    return Boolean.valueOf({PKG}.AccStore.has((java.util.UUID) a[0], String.valueOf(a[1])));
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", fn))

# ================= 0.5.19 AccBagFn (bridge function acc:fn:bag; tools/accessories_0_5_19_patch.py docstring) =================
bfn_.addInterface(pool.get("java.util.function.Function"))
bfn_.addConstructor(CtNewConstructor.make("public AccBagFn() { }", bfn_))
bfn_.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof String) || !(a[1] instanceof java.util.UUID) || !(a[2] instanceof String)) return null;
    String op = (String) a[0];
    java.util.UUID u = (java.util.UUID) a[1];
    String k = (String) a[2];
    if ({PKG}.AccStore.DIR == null || !k.equals({PKG}.AccStore.pkey(u))) return null;
    if ({PKG}.AccStore.isBad(k) || {PKG}.AccStore.moveBlock(u) != null) return null;
    if (op.equals("list")) return {PKG}.AccStore.listK(u, k);
    if (a.length < 4 || !(a[3] instanceof String)) return null;
    String id = (String) a[3];
    if (op.equals("take")) return Integer.valueOf({PKG}.AccStore.takeK(u, k, id));
    if (op.equals("put")) {{
      int at = (a.length > 4 && a[4] instanceof Integer) ? ((Integer) a[4]).intValue() : -1;
      return Boolean.valueOf({PKG}.AccStore.putBackK(u, k, id, at));
    }}
    return null;
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("acc:fn:bag failed: " + t); return null; }}
}}""", bfn_))

# ================= AccPage =================
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String[] invIds;", page))
page.addField(CtField.make("public String key;", page))   # 0.4.1: profile storage key the page was built for
page.addField(CtField.make("public int slotPage;", page))   # 0.5: the bag slot pager (clamped in build())
page.addField(CtField.make("public int invPage;", page))    # 0.5: the inventory list pager (clamped in build())
page.addField(CtField.make("public int mode;", page))       # 0.5.18: 0 = the Bag view, 1 = the Craft view (the tabs)
page.addField(CtField.make("public int craftPage;", page))  # 0.5.18: the Craft view's pager (clamped in buildCraft())
page.addField(CtField.make("public String[] craftIds;", page))   # 0.5.18: the recipe id of every Craft row as last drawn (cr:<index>)
page.addField(CtField.make("public int craftSub;", page))   # 0.5.21: the Craft view's sub tab (AccCraft.SUB_NAMES index, clamped in buildCraft())
page.addField(CtField.make("public int filt;", page))       # 0.5.22: the BAG view's filter (0 All, 1 Combat, 2 Gathering, 3 Benches)
page.addField(CtField.make('public String sel = "";', page))   # 0.5.22: the selected accessory: "b:<id>" in the bag, "i:<id>" in the inventory
page.addField(CtField.make("public String[] bagIds;", page))   # 0.5.22: the bag grid's cells as last drawn (SlotIndex -> id)
page.addField(CtField.make("public int cells;", page))      # 0.5.22: grid cells drawn (the stuck-tooltip guard empties them)
page.addConstructor(CtNewConstructor.make(f"""
public AccPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
# accessory item ids carried in storage/hotbar/backpack (distinct)
page.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList old = new java.util.ArrayList();   // 0.4.2: retired accessories, appended after the usable ones
  {INV} inv = p.getInventory();
  if (inv == null) return out;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (!{PKG}.AccDefs.isAccessory(id)) continue;
      if ({PKG}.AccDefs.isRetired(id)) {{ if (!old.contains(id)) old.add(id); }}
      else if (!out.contains(id)) out.add(id);
    }}
  }}
  out.addAll(old);   // 0.4.2: so they never push a usable accessory out of the Equip rows
  return out;
}}""", page))
# remove one of item id from any inventory section; true when removed
page.addMethod(CtNewMethod.make(f"""
public static boolean takeOne({PLA} p, String id) {{
  {INV} inv = p.getInventory();
  if (inv == null) return false;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      {ISS} tx = cont.removeItemStackFromSlot(s, 1);
      if (tx != null && tx.succeeded()) return true;
    }}
  }}
  return false;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static boolean giveOne({PLA} p, String id) {{
  try {{
    {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    tx = p.getInventory().getHotbar().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    {IC} bp = p.getInventory().getBackpack();
    if (bp == null) return false;
    tx = bp.addItemStack(new {IS}(id, 1));
    return tx != null && tx.succeeded();
  }} catch (Throwable t) {{ return false; }}
}}""", page))
# ================= 0.5.18 AccCraft: CRAFT FROM THE BAG + AUTO-EQUIP (tools/accessories_0_5_18_patch.py; Skyy 2026-10-15 "allow crafting from
# the accessory bag, and make crafted accessory's auto equip.") - the Craft view's recipe list + rows, the ONE craft operation (world thread,
# inside the page click), the crafts.log journal, and the auto-equip of accessories crafted anywhere (AccAutoPre / AccAutoPost -> AccAutoTask)
_C8 = {"CRR": C8_CRR, "MQ": C8_MQ, "CIC": C8_CIC, "CRM": C8_CRM, "BRQ": C8_BRQ, "CRE": C8_CRE, "PRE": C8_PRE, "POST": C8_POST,
       "ENS": C8_ENS, "EES": C8_EES, "EVT": C8_EVT, "ARC": ARC}
def CJ(src):
    for _k, _v in _C8.items():
        src = src.replace("@%s@" % _k, _v)
    return JT(src)
def CM(cls, src):
    cls.addMethod(CtNewMethod.make(CJ(src), cls))
def CF(cls, src):
    cls.addField(CtField.make(CJ(src), cls))
for _c, _m in ((C8_CRR, "getAssetMap"), (C8_CRR, "getInput"), (C8_CRR, "getPrimaryOutput"), (C8_CRR, "isKnowledgeRequired"),
               (C8_CRR, "getBenchRequirement"), (C8_CRR, "getTimeSeconds"), (C8_MQ, "getResourceTypeId"), (C8_MQ, "getItemId"),
               (C8_MQ, "getQuantity"), (C8_CIC, "canRemoveMaterials"), (C8_CIC, "removeMaterials"), (IC, "countRemovableMaterial"),
               (IC, "getMatchingResourceType"), (C8_CRM, "getInputMaterials"), (C8_BRQ, "categories"), (C8_CRE, "getCraftedRecipe"),
               (C8_CRE, "getQuantity"), (C8_CRE, "isCancelled"), (ST, "invoke"), (ST, "getExternalData"), (C8_ENS, "getWorld"),
               (C8_EES, "handle"), (ITM, "getItemLevel"), (ITM, "getTranslationKey"), (ITM, "getMaxStack"), (ITM, "isVariant"),
               (IS, "getMetadata"), (PLA, "getPlayerConfigData"), (PLA, "markNeedsSave"), (ARC, "empty"),
               ("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData", "getKnownRecipes"),
               ("com.hypixel.hytale.server.core.modules.i18n.I18nModule", "getMessage")):
    B.probe(pool, _c, _m)
C8_GREEN, C8_GREY = SUI.STATUS["+"], SUI.COLOR["rowSub"]
C8_ROWS = 9                                   # the Craft view: recipes per page (0.5.21: unused - the list scrolls)
# 0.5.21: ACCESSORY RECIPES LIVE IN THE BAG (tools/accessories_0_5_21_patch.py): every accessory recipe's BenchRequirement is this bench id +
# category (no block is that bench: no Workbench tab, pocket crafting or SkyySacks list shows them); AccCraft.ours() reads the category
BAGCRAFT_ID = BAGCRAFT_CAT = "SkyyAccessoryBag"
# the Craft view's SUB TABS (Skyy 10-16 "add sub tabs. like benches. then split the accessory's up by combat and gathering. (we will add more
# splits/submenus/filters as need"): (name, tab id). C9_FAM_SUB = stat-line family -> tab index; a family not listed -> C9_FAM_DEFAULT; every
# bench accessory and the Omni -> tab 0. A new tab / line = one row here.
C9_SUBS = [("Benches", "SkyyAccSt0"), ("Combat", "SkyyAccSt1"), ("Gathering", "SkyyAccSt2")]
C9_FAM_SUB = [("Vitality", 1), ("Endurance", 1), ("Intelligence", 1), ("Regeneration", 1), ("Speed", 1), ("Lantern", 2)]
C9_FAM_DEFAULT = 1
assert all(_t == "SkyyAccSt%d" % _i for _i, (_n, _t) in enumerate(C9_SUBS)) and all(0 < _s < len(C9_SUBS) for _f, _s in C9_FAM_SUB)
C8_TEXTS = {
    "OFF": "crafting in Void Charms is switched off on this server",
    "AUTO_IN": "[Void Charms] %s went straight into your Void Charms.",
    "AUTO_OUT": "[Void Charms] %s stays in your inventory - %s.",
}
CF(acr_, 'public static final String TAB = "%s";' % BAGCRAFT_CAT)   # 0.5.21: the bag's own category (was the Workbench tab's)
CF(acr_, "public static final int ROWS = %d;" % C8_ROWS)
CF(acr_, 'public static final String GREEN = "%s";' % C8_GREEN)
CF(acr_, 'public static final String GREY = "%s";' % C8_GREY)
CF(acr_, 'public static final String INCOL = "%s";' % SUI.STATUS["+"])
CF(acr_, 'public static final String OUTCOL = "%s";' % SUI.STATUS_INFO["gold"])
# SELF = uuid -> TRUE while the bag page fires its own craft events (both hooks ignore them: the page puts its result away itself);
# PENDING = "<uuid>|<item id>" -> Long time of a Pre whose task has not run yet (its Post is then skipped: one task per craft)
CF(acr_, "public static final java.util.concurrent.ConcurrentHashMap SELF = new java.util.concurrent.ConcurrentHashMap();")
CF(acr_, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")
CF(acr_, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
CF(acr_, "public static volatile java.util.ArrayList LIST = null;")
CF(acr_, "public static volatile int LISTN = -1;")
CF(acr_, "public static java.nio.file.Path LOGF;")
CF(acr_, "public static volatile long CRAFTED = 0L;")
CF(acr_, "public static volatile long AUTOED = 0L;")
CF(acr_, "public static boolean JWARN = false;")
CF(acr_, "public static boolean FAILED = false;")
# 0.5.21: the sub tabs + the line table (built from LIST, rebuilt when LIST is a new object)
CF(acr_, "public static final String[] SUB_NAMES = new String[] { %s };" % ", ".join('"%s"' % _n for _n, _t in C9_SUBS))
CF(acr_, "public static final String[] SUB_FAM = new String[] { %s };" % ", ".join('"%s"' % _f for _f, _s in C9_FAM_SUB))
CF(acr_, "public static final int[] SUB_OF = new int[] { %s };" % ", ".join(str(_s) for _f, _s in C9_FAM_SUB))
CF(acr_, "public static final int SUB_DEFAULT = %d;" % C9_FAM_DEFAULT)
CF(acr_, "public static volatile java.util.ArrayList LINES = null;")
CF(acr_, "public static volatile Object LINESRC = null;")
for _src in [
# ---- names: the translated en-US text of a key (the SkyySacks 0.8.8 lookup), the item's own name, a resource type's name
r"""
public static String tr(String key) {
  if (key == null) return null;
  try {
    com.hypixel.hytale.server.core.modules.i18n.I18nModule m = com.hypixel.hytale.server.core.modules.i18n.I18nModule.get();
    if (m == null) return null;
    String n = m.getMessage("en-US", key);
    if ((n == null || n.length() == 0) && key.startsWith("server.")) n = m.getMessage("en-US", key.substring(7));
    if (n == null) return null;
    n = n.trim();
    if (n.length() == 0 || (n.indexOf('.') > 0 && n.indexOf(' ') < 0)) return null;
    return n;
  } catch (Throwable t) { return null; }
}""",
r"""
public static String dname(String id) {
  if (id == null) return null;
  Object c = NAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) n = tr(((@ITM@) o).getTranslationKey());
  } catch (Throwable t) { n = null; }
  if (n != null && NAMES.size() < 4096) NAMES.put(id, n);
  return n;
}""",
r"""
public static String rtName(String rt) {
  if (rt == null) return "?";
  String n = tr("server.resourceType." + rt + ".name");
  return n == null ? rt.replace('_', ' ') : n;
}""",
# the result's real name (its item name, e.g. "Workbench Accessory II"); the bag's short name when the item has no translation
r"""
public static String accName(String id) {
  String n = dname(id);
  return n != null ? n : @PKG@.AccDefs.pretty(id);
}""",
# an ingredient: accessories by the bag's short name (the Omni's eleven fit), other items by their item name
r"""
public static String shortName(String id) {
  if (id == null) return "?";
  if (@PKG@.AccDefs.isAccessory(id)) return @PKG@.AccDefs.pretty(id);
  String n = dname(id);
  return n != null ? n : id.replace('_', ' ');
}""",
r"""
public static String matName(@MQ@ q) {
  if (q == null) return "?";
  if (q.getItemId() != null) return shortName(q.getItemId());
  return rtName(q.getResourceTypeId());
}""",
# ---- the list: every recipe of this mod's Workbench tab whose result is a current accessory, sorted like the tab (ItemLevel, then id)
r"""
public static int level(String id) {
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) return ((@ITM@) o).getItemLevel();
  } catch (Throwable t) { }
  return 0;
}""",
r"""
public static String outId(@CRR@ r) {
  if (r == null) return null;
  @MQ@ po = r.getPrimaryOutput();
  return po == null ? null : po.getItemId();
}""",
r"""
public static boolean ours(@CRR@ r) {
  String id = outId(r);
  if (id == null || !@PKG@.AccDefs.isAccessory(id) || @PKG@.AccDefs.isRetired(id)) return false;
  @MQ@[] in = r.getInput();
  if (in == null || in.length == 0) return false;
  @BRQ@[] br = r.getBenchRequirement();
  if (br == null) return false;
  boolean tab = false;
  for (int i = 0; i < br.length && !tab; i++) {
    if (br[i] == null || br[i].categories == null) continue;
    for (int j = 0; j < br[i].categories.length; j++) if (TAB.equals(br[i].categories[j])) tab = true;
  }
  if (!tab) return false;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (!(o instanceof @ITM@) || ((@ITM@) o).isVariant()) return false;
  } catch (Throwable t) { return false; }
  return true;
}""",
r"""
public static boolean before(Object a, Object b) {
  String x = outId((@CRR@) a);
  String y = outId((@CRR@) b);
  int lx = level(x);
  int ly = level(y);
  if (lx != ly) return lx < ly;
  return x.compareTo(y) < 0;
}""",
# built once and again only when the recipe table changed size (asset reloads); null-safe
r"""
public static synchronized java.util.ArrayList recipes() {
  java.util.Map m = null;
  try { m = @CRR@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) return new java.util.ArrayList();
  int n = m.size();
  if (LIST != null && n == LISTN) return LIST;
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @CRR@)) continue;
    if (ours((@CRR@) o)) out.add(o);
  }
  for (int i = 1; i < out.size(); i++) {
    Object x = out.get(i);
    int j = i - 1;
    while (j >= 0 && before(x, out.get(j))) { out.set(j + 1, out.get(j)); j--; }
    out.set(j + 1, x);
  }
  LIST = out;
  LISTN = n;
  return out;
}""",
# a knowledge recipe (the four Lanterns: SkyyCollections' Tree Sap collection - AccKnow keeps the known set) is crafted only when known
r"""
public static boolean known(@PLA@ p, @CRR@ r) {
  if (r == null) return false;
  if (!r.isKnowledgeRequired()) return true;
  try {
    java.util.Set ks = p.getPlayerConfigData().getKnownRecipes();
    if (ks == null) return false;
    String id = outId(r);
    return ks.contains(id) || ks.contains(r.getId());
  } catch (Throwable t) { return false; }
}""",
r"""
public static String lockText(String id) {
  if (@PKG@.AccDefs.isLantern(id)) return "collect Tree Sap to unlock it (Collections)";
  return "you have not unlocked this recipe yet";
}""",
# ---- SkyySacks' Void (the bridge the Bazaar uses: world thread, plain java types; nothing when SkyySacks is absent)
r"""
public static java.util.function.Function fn(String key) {
  try {
    Object o = @PKG@.AccStore.bridge().get(key);
    if (o instanceof java.util.function.Function) return (java.util.function.Function) o;
  } catch (Throwable t) { }
  return null;
}""",
# count (n < 0) / take / put / commit of one item id; the answer as a long (0 when the bridge is missing or fails; count -1 = paused)
r"""
public static long vcall(String key, java.util.UUID u, String id, long n) {
  java.util.function.Function f = fn(key);
  if (f == null || u == null || id == null) return 0L;
  try {
    Object r = n < 0L ? f.apply(new Object[] { u, id }) : f.apply(new Object[] { u, id, Long.valueOf(n) });
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { }
  return 0L;
}""",
r"""
public static java.util.Map vall(java.util.UUID u) {
  java.util.function.Function f = fn("sacks:fn:all");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    if (r instanceof java.util.Map) return (java.util.Map) r;
  } catch (Throwable t) { }
  return null;
}""",
# ---- the COPIES the engine counts and chooses from (CombinedItemContainer: inventory, then Void, then bag)
r"""
public static boolean plain(@IS@ it) {
  try {
    org.bson.BsonDocument md = it.getMetadata();
    return md == null || md.isEmpty();
  } catch (Throwable t) { return false; }
}""",
# the inventory (backpack, storage, hotbar - the order CraftingManager pays from) as a copy of its PLAIN stacks:
# { SimpleItemContainer copy, ItemContainer[] real, int[] container index (-1 = not copied), short[] real slot, int[] quantity, String[] id }
r"""
public static Object[] invCopy(@INV@ inv) {
  @IC@[] cs = new @IC@[] { inv.getBackpack(), inv.getStorage(), inv.getHotbar() };
  int n = 0;
  for (int c = 0; c < cs.length; c++) if (cs[c] != null) n += cs[c].getCapacity();
  if (n < 1) n = 1;
  @SIC@ copy = new @SIC@((short) n);
  int[] ci = new int[n];
  short[] si = new short[n];
  int[] q0 = new int[n];
  String[] ids = new String[n];
  for (int i = 0; i < n; i++) ci[i] = -1;
  int at = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      int here = at;
      at++;
      if (it == null || it.isEmpty() || it.getItemId() == null) continue;
      if (!plain(it)) continue;
      copy.setItemStackForSlot((short) here, new @IS@(it.getItemId(), it.getQuantity()));
      ci[here] = c;
      si[here] = s;
      q0[here] = it.getQuantity();
      ids[here] = it.getItemId();
    }
  }
  return new Object[] { copy, cs, ci, si, q0, ids };
}""",
r"""
public static int maxStack(String id) {
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) {
      int m = ((@ITM@) o).getMaxStack();
      return m < 1 ? 1 : m;
    }
  } catch (Throwable t) { }
  return 1;
}""",
r"""
public static boolean hasType(String id, String rt) {
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    return (o instanceof @ITM@) && @IC@.getMatchingResourceType((@ITM@) o, rt) != null;
  } catch (Throwable t) { return false; }
}""",
r"""
public static void addWant(java.util.LinkedHashMap want, String id, long add, long cap) {
  if (id == null || add <= 0L || cap <= 0L) return;
  Long v = (Long) want.get(id);
  long nv = (v == null ? 0L : v.longValue()) + add;
  if (nv > cap) nv = cap;
  want.put(id, Long.valueOf(nv));
}""",
# the Void's part: per input up to what one craft needs (an item id: sacks:fn:count; a resource type: every Void item of that type from
# sacks:fn:all). { SimpleItemContainer copy, String[] id per slot, Boolean paused }
r"""
public static Object[] voidCopy(java.util.UUID u, @MQ@[] in) {
  java.util.LinkedHashMap want = new java.util.LinkedHashMap();
  boolean paused = false;
  java.util.Map all = null;
  boolean allRead = false;
  for (int i = 0; in != null && i < in.length; i++) {
    @MQ@ q = in[i];
    if (q == null) continue;
    long need = (long) q.getQuantity();
    String id = q.getItemId();
    if (id != null) {
      long c = vcall("sacks:fn:count", u, id, -1L);
      if (c < 0L) { paused = true; continue; }
      addWant(want, id, need, c);
      continue;
    }
    String rt = q.getResourceTypeId();
    if (rt == null) continue;
    if (!allRead) { all = vall(u); allRead = true; }
    if (all == null) continue;
    java.util.Iterator it = all.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String vid = String.valueOf(e.getKey());
      long v = (e.getValue() instanceof Number) ? ((Number) e.getValue()).longValue() : 0L;
      if (v <= 0L || !hasType(vid, rt)) continue;
      addWant(want, vid, need, v);
    }
  }
  int slots = 1;
  java.util.Iterator wi = want.entrySet().iterator();
  while (wi.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) wi.next();
    long v = ((Long) e.getValue()).longValue();
    long ms = (long) maxStack((String) e.getKey());
    slots += (int) ((v + ms - 1L) / ms);
  }
  if (slots > 4000) slots = 4000;
  @SIC@ copy = new @SIC@((short) slots);
  String[] ids = new String[slots];
  int at = 0;
  wi = want.entrySet().iterator();
  while (wi.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) wi.next();
    String id = (String) e.getKey();
    long v = ((Long) e.getValue()).longValue();
    int ms = maxStack(id);
    while (v > 0L && at < slots) {
      int put = v > (long) ms ? ms : (int) v;
      copy.setItemStackForSlot((short) at, new @IS@(id, put));
      ids[at] = id;
      at++;
      v -= (long) put;
    }
  }
  return new Object[] { copy, ids, paused ? Boolean.TRUE : Boolean.FALSE };
}""",
# a copy of bag k (the AccStore.snapshot pattern: one call inside the lock)
r"""
public static String[] bagSnap(java.util.UUID u, String k) {
  String[] s = @PKG@.AccStore.slotsK(u, k);
  String[] c = new String[s.length];
  synchronized (@PKG@.AccStore.lock(u)) { System.arraycopy(s, 0, c, 0, s.length); }
  return c;
}""",
# the bag's part: every equipped accessory that is an ingredient of this recipe (its current id). { copy, int[] bag slot, String[] stored id }
r"""
public static Object[] bagCopy(java.util.UUID u, String k, @MQ@[] in) {
  String[] s = bagSnap(u, k);
  boolean[] use = new boolean[s.length];
  int n = 0;
  for (int i = 0; i < s.length; i++) {
    if (s[i] == null) continue;
    String m = @PKG@.AccDefs.modernOf(s[i]);
    if (m == null) continue;
    for (int j = 0; in != null && j < in.length && !use[i]; j++) if (in[j] != null && m.equals(in[j].getItemId())) use[i] = true;
    if (use[i]) n++;
  }
  int cap = n < 1 ? 1 : n;
  @SIC@ copy = new @SIC@((short) cap);
  int[] idx = new int[cap];
  String[] st = new String[cap];
  for (int i = 0; i < cap; i++) idx[i] = -1;
  int at = 0;
  for (int i = 0; i < s.length; i++) {
    if (!use[i]) continue;
    copy.setItemStackForSlot((short) at, new @IS@(@PKG@.AccDefs.modernOf(s[i]), 1));
    idx[at] = i;
    st[at] = s[i];
    at++;
  }
  return new Object[] { copy, idx, st };
}""",
# { CombinedItemContainer(inventory copy, Void copy, bag copy), the three copies }
r"""
public static Object[] plan(java.util.UUID u, String k, @PLA@ p, @CRR@ r) {
  Object[] ic = invCopy(p.getInventory());
  Object[] vc = voidCopy(u, r.getInput());
  Object[] bc = bagCopy(u, k, r.getInput());
  @CIC@ comb = new @CIC@(new @IC@[] { (@IC@) ic[0], (@IC@) vc[0], (@IC@) bc[0] });
  return new Object[] { comb, ic, vc, bc };
}""",
r"""
public static int[] qty(@SIC@ c) {
  short cap = c.getCapacity();
  int[] q = new int[cap];
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    q[s] = (it == null || it.isEmpty()) ? 0 : it.getQuantity();
  }
  return q;
}""",
r"""
public static String haveText(long v) {
  return v > 9999L ? "9999+" : String.valueOf(v);
}""",
# ONE ROW of the Craft view: { item id, name, "RARITY - status", the rarity colour, "Name have/need, ...", ingredient colour }
r"""
public static String[] row(java.util.UUID u, String k, @PLA@ p, @CRR@ r) {
  String out = outId(r);
  String[] res = new String[] { out, accName(out), "", @PKG@.AccDefs.rarityColor(out), "", GREY };
  String rar = @PKG@.AccDefs.rarityName(out).toUpperCase();
  try {
    @MQ@[] in = r.getInput();
    boolean kn = p != null && known(p, r);
    @CIC@ comb = null;
    if (p != null && p.getInventory() != null && u != null && k != null) comb = (@CIC@) plan(u, k, p, r)[0];
    StringBuilder sb = new StringBuilder();
    for (int i = 0; in != null && i < in.length; i++) {
      if (in[i] == null) continue;
      long have = comb == null ? 0L : (long) comb.countRemovableMaterial(in[i]);
      if (have > (long) in[i].getQuantity()) have = (long) in[i].getQuantity();   // enough = "need/need" (the Void part is only mirrored up to one craft)
      if (sb.length() > 0) sb.append(", ");
      sb.append(matName(in[i])).append(' ').append(haveText(have)).append('/').append(in[i].getQuantity());
    }
    boolean ok = kn && comb != null && comb.canRemoveMaterials(@CRM@.getInputMaterials(r, 1));
    res[2] = rar + " - " + (!kn ? "LOCKED" : (ok ? "CAN CRAFT" : "NEEDS MATERIALS"));
    res[4] = (!kn ? "Locked - " + lockText(out) + ". " : "") + sb.toString();
    if (ok) res[5] = GREEN;
  } catch (Throwable t) {
    res[2] = rar;
    res[4] = "the materials could not be read: " + t;
  }
  return res;
}""",
# ---- the journal Skyy_SkyyAccessories/crafts.log (append + flush to the OS - a JVM crash keeps it; no fsync: it runs on the world thread
# 2-3 times a craft and the inventory itself is only saved on the engine's cycle; over 1 MB it becomes crafts.old.log)
r"""
public static synchronized void journal(String line) {
  if (LOGF == null) return;
  try {
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(LOGF, new java.nio.file.LinkOption[0]) && java.nio.file.Files.size(LOGF) > 1048576L)
      java.nio.file.Files.move(LOGF, LOGF.resolveSibling("crafts.old.log"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    java.io.FileOutputStream out = new java.io.FileOutputStream(LOGF.toFile(), true);
    try {
      out.write((java.time.Instant.now().toString() + " " + line + "\n").getBytes("UTF-8"));
      out.flush();
    } finally { out.close(); }
  } catch (Throwable t) {
    if (!JWARN) { JWARN = true; @PKG@.AccStore.warn("could not write the craft journal " + LOGF + " (logged once): " + t); }
  }
}""",
r"""
public static String who(@PR@ pr, java.util.UUID u, String k) {
  String n = "?";
  try { if (pr != null) n = pr.getUsername(); } catch (Throwable t) { }
  return n + " " + u + " " + k;
}""",
# CraftRecipeEvent$Pre / $Post on the crafter exactly as CraftingManager.craftItem fires them (store.invoke(ref, new Pre(recipe, 1)));
# Pre: true = go on (cancelled or a throw = refused); Post: always true. No store (the bare harness) = no listeners = true.
r"""
public static boolean fire(@ST@ st, @REF@ ref, java.util.UUID u, @CRR@ r, boolean post) {
  if (st == null || ref == null) return true;
  boolean ok = true;
  SELF.put(u, Boolean.TRUE);
  try {
    if (post) {
      @POST@ e = new @POST@(r, 1);
      st.invoke(ref, e);
    } else {
      @PRE@ e2 = new @PRE@(r, 1);
      st.invoke(ref, e2);
      ok = !e2.isCancelled();
    }
  } catch (Throwable t) {
    @PKG@.AccStore.warn("bag craft: CraftRecipeEvent " + (post ? "Post failed" : "Pre failed - the craft was refused") + ": " + t);
    ok = post;
  }
  SELF.remove(u);
  return ok;
}""",
# why the bag does not take put (canEquipK said no): the same / a better one of its line, else no free slot
r"""
public static String why(java.util.UUID u, String k, String put) {
  String[] s = bagSnap(u, k);
  String g = @PKG@.AccDefs.groupOf(put);
  int t = @PKG@.AccDefs.tierOf(put);
  for (int i = 0; i < s.length; i++) {
    if (s[i] == null || g == null || !g.equals(@PKG@.AccDefs.groupOf(s[i]))) continue;
    int ti = @PKG@.AccDefs.tierOf(s[i]);
    if (ti >= t) return "your Void Charms already have " + (ti == t ? "the same " : "a better ") + @PKG@.AccDefs.lineLabel(put);
  }
  return "your Void Charms has no free slot";
}""",
# the Equip button's giveBack: 0 = back in the inventory, 1 = kept in a free bag slot, 2 = lost (logged with the uuid + journal)
r"""
public static int back(@PLA@ p, java.util.UUID u, String k, String id) {
  if (@PKG@.AccPage.giveOne(p, id)) return 0;
  if (@PKG@.AccStore.stashK(u, k, id)) return 1;
  @PKG@.AccStore.warn("ITEM LOST - could not return " + id + " to player " + u + " (inventory and Void Charms full), give it back by hand");
  journal("LOST " + u + " " + k + " " + id + " (inventory and bag full)");
  return 2;
}""",
# fix round 2: would equipK(put) displace an accessory that then has nowhere to go? true = safe (nothing displaced, a free bag slot for
# stashK, or room in storage / hotbar / backpack for giveOne). A bag craft whose materials freed no slot (all from the Void or partial
# stacks) with a full inventory AND a full bag would otherwise destroy the upgraded-out one (back() -> LOST). false = no auto-equip.
r"""
public static boolean swapSafe(@PLA@ p, java.util.UUID u, String k, String put) {
  String[] s = bagSnap(u, k);
  String g = @PKG@.AccDefs.groupOf(put);
  if (g == null) return true;
  int low = -1;
  boolean free = false;
  for (int i = 0; i < s.length; i++) {
    if (s[i] == null) { free = true; continue; }
    if (!g.equals(@PKG@.AccDefs.groupOf(s[i]))) continue;
    if (low < 0 || @PKG@.AccDefs.tierOf(s[i]) < @PKG@.AccDefs.tierOf(s[low])) low = i;
  }
  if (low < 0 || free) return true;
  try {
    @IS@ x = new @IS@(@PKG@.AccDefs.modernOf(s[low]), 1);
    @INV@ inv = p.getInventory();
    if (inv.getStorage().canAddItemStack(x)) return true;
    if (inv.getHotbar().canAddItemStack(x)) return true;
    @IC@ bp = inv.getBackpack();
    return bp != null && bp.canAddItemStack(x);
  } catch (Throwable t) { return false; }
}""",
# one item into storage / hotbar / backpack, counted before and after (1 = it arrived)
r"""
public static int addInv(@INV@ inv, String id) {
  try {
    @IC@ c = inv.getCombinedStorageHotbarBackpack();
    if (c == null) return 0;
    int b0 = @PKG@.AccStore.countOf(inv, id);
    c.addItemStack(new @IS@(id, 1));
    int got = @PKG@.AccStore.countOf(inv, id) - b0;
    return got < 0 ? 0 : got;
  } catch (Throwable t) { return 0; }
}""",
r"""
public static void addCount(java.util.LinkedHashMap m, String id, long n) {
  if (id == null || n == 0L) return;
  Long v = (Long) m.get(id);
  m.put(id, Long.valueOf((v == null ? 0L : v.longValue()) + n));
}""",
# ---- applying the plan; every step read back. null = done, else the reason (the caller rolls everything back)
r"""
public static String takeInv(Object[] ic, int[] a0, int[] a1, java.util.ArrayList undo) {
  @IC@[] cs = (@IC@[]) ic[1];
  int[] ci = (int[]) ic[2];
  short[] si = (short[]) ic[3];
  String[] ids = (String[]) ic[5];
  for (int j = 0; j < ci.length; j++) {
    int d = a0[j] - a1[j];
    if (d == 0) continue;
    if (d < 0 || ci[j] < 0) return "your inventory changed while crafting";
    @IC@ c = cs[ci[j]];
    @IS@ real = c.getItemStack(si[j]);
    if (real == null || real.isEmpty() || !ids[j].equals(real.getItemId()) || real.getQuantity() < d) return "your inventory changed while crafting";
    undo.add(new Object[] { c, Short.valueOf(si[j]), real });
    @ISS@ tx = c.removeItemStackFromSlot(si[j], d);
    if (tx == null || !tx.succeeded()) return "a material could not be taken from your inventory";
    @IS@ now = c.getItemStack(si[j]);
    int left = (now == null || now.isEmpty()) ? 0 : now.getQuantity();
    if (left != real.getQuantity() - d) return "a material could not be taken from your inventory";
  }
  return null;
}""",
r"""
public static String takeVoid(java.util.UUID u, java.util.LinkedHashMap voidT, java.util.LinkedHashMap took) {
  java.util.Iterator it = voidT.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    long n = ((Long) e.getValue()).longValue();
    long got = vcall("sacks:fn:take", u, id, n);
    if (got > 0L) took.put(id, Long.valueOf(got));
    if (got != n) return "the Void gave " + got + " of " + n + " " + shortName(id);
  }
  return null;
}""",
r"""
public static String takeBag(java.util.UUID u, String k, Object[] bc, int[] c0, int[] c1, java.util.ArrayList bagUndo) {
  int[] idx = (int[]) bc[1];
  String[] st = (String[]) bc[2];
  for (int j = 0; j < idx.length; j++) {
    if (idx[j] < 0 || c0[j] - c1[j] <= 0) continue;
    String got = @PKG@.AccStore.unequipK(u, k, idx[j]);
    if (got == null || !got.equals(st[j])) {
      if (got != null) @PKG@.AccStore.putK(u, k, idx[j], got);
      return "your Void Charms changed while crafting";
    }
    bagUndo.add(new Object[] { Integer.valueOf(idx[j]), got });
  }
  return null;
}""",
# everything taken so far goes back where it came from; "" = all back, else what could not (WARN + journal LOST)
r"""
public static String rollback(java.util.UUID u, String k, java.util.ArrayList undo, java.util.LinkedHashMap took, java.util.ArrayList bagUndo) {
  StringBuilder lost = new StringBuilder();
  for (int i = undo.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) undo.get(i);
    try { ((@IC@) e[0]).setItemStackForSlot(((Short) e[1]).shortValue(), (@IS@) e[2]); }
    catch (Throwable t) { lost.append(" inventory slot ").append(e[1]).append(' ').append(e[2]); }
  }
  java.util.Iterator it = took.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    long n = ((Long) e.getValue()).longValue();
    long b = vcall("sacks:fn:put", u, (String) e.getKey(), n);
    if (b != n) lost.append(" Void ").append(e.getKey()).append(' ').append(n - b);
  }
  for (int i = bagUndo.size() - 1; i >= 0; i--) {
    Object[] e = (Object[]) bagUndo.get(i);
    @PKG@.AccStore.putK(u, k, ((Integer) e[0]).intValue(), (String) e[1]);
  }
  if (lost.length() > 0) {
    @PKG@.AccStore.warn("ITEM LOST - a bag craft of " + u + " could not put back:" + lost + " - give it back by hand (crafts.log)");
    journal("LOST " + u + " " + k + lost);
  }
  return lost.toString();
}""",
r"""
public static void commitVoid(java.util.UUID u, java.util.LinkedHashMap took) {
  java.util.Iterator it = took.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    vcall("sacks:fn:commit", u, (String) e.getKey(), ((Long) e.getValue()).longValue());
  }
}""",
# ---- 0.5.21 THE LINE ROWS (tools/accessories_0_5_21_patch.py): one row per accessory line, its NEXT step for this bag only
# the sub tab of an accessory id: stat lines by family (SUB_FAM / SUB_OF, else SUB_DEFAULT), every bench accessory and the Omni = 0
r"""
public static int subOf(String id) {
  if (!@PKG@.AccDefs.isTalisman(id)) return 0;
  String f = @PKG@.AccDefs.familyOf(id);
  for (int i = 0; i < SUB_FAM.length; i++) if (SUB_FAM[i].equals(f)) return SUB_OF[i];
  return SUB_DEFAULT;
}""",
# a recipe into a line's step list: tier order (lowest first); two recipes of the same output -> the smaller recipe id (deterministic)
r"""
public static void addStep(java.util.ArrayList l, @CRR@ r) {
  String id = outId(r);
  int t = @PKG@.AccDefs.tierOf(id);
  for (int i = 0; i < l.size(); i++) {
    @CRR@ x = (@CRR@) l.get(i);
    String xi = outId(x);
    if (xi.equals(id)) {
      if (r.getId().compareTo(x.getId()) < 0) l.set(i, r);
      return;
    }
    if (@PKG@.AccDefs.tierOf(xi) > t) { l.add(i, r); return; }
  }
  l.add(r);
}""",
# every line: Object[] { String line key (AccDefs.groupOf), ArrayList its recipes lowest tier first } - from recipes(), cached per LIST object
r"""
public static synchronized java.util.ArrayList lines() {
  java.util.ArrayList rs = recipes();
  if (LINES != null && LINESRC == rs) return LINES;
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < rs.size(); i++) {
    @CRR@ r = (@CRR@) rs.get(i);
    String g = @PKG@.AccDefs.groupOf(outId(r));
    if (g == null) continue;
    int k = keys.indexOf(g);
    if (k < 0) {
      keys.add(g);
      out.add(new Object[] { g, new java.util.ArrayList() });
      k = out.size() - 1;
    }
    addStep((java.util.ArrayList) ((Object[]) out.get(k))[1], r);
  }
  LINES = out;
  LINESRC = rs;
  return out;
}""",
# the best accessory of line g in bag copy s (its stored id; null = none); retired ones never count
r"""
public static String bestIn(String[] s, String g) {
  String best = null;
  int bt = 0;
  for (int i = 0; s != null && i < s.length; i++) {
    if (s[i] == null || @PKG@.AccDefs.isRetired(s[i])) continue;
    String m = @PKG@.AccDefs.modernOf(s[i]);
    if (!g.equals(@PKG@.AccDefs.groupOf(m))) continue;
    int t = @PKG@.AccDefs.tierOf(m);
    if (best == null || t > bt) { best = s[i]; bt = t; }
  }
  return best;
}""",
# the Omni Accessory in the bag covers every active bench at its top tier (AccDefs.benchList): those bench lines are MAX
r"""
public static boolean omniCovers(String[] s, String g) {
  if (g == null || !@PKG@.AccDefs.hasOmni(s)) return false;
  for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) if (@PKG@.AccDefs.BENCH_IDS[i].equals(g)) return true;
  return false;
}""",
# the line's step for this bag: Object[] { CraftingRecipe or null (MAX), "c" craft / "u" upgrade / "m" max, the bag's best (stored id) or
# null, "o" = covered by the Omni Accessory else "" }
r"""
public static Object[] step(String[] s, Object[] line) {
  String g = (String) line[0];
  java.util.ArrayList l = (java.util.ArrayList) line[1];
  if (omniCovers(s, g)) return new Object[] { null, "m", null, "o" };
  String own = bestIn(s, g);
  if (own == null && @PKG@.AccPower.dropUp(g)) return new Object[] { null, "m", null, "d" };   // 0.5.22: a drop-only line: no row until one is in the bag
  int t = own == null ? 0 : @PKG@.AccDefs.tierOf(@PKG@.AccDefs.modernOf(own));
  for (int i = 0; i < l.size(); i++) {
    @CRR@ r = (@CRR@) l.get(i);
    if (@PKG@.AccDefs.tierOf(outId(r)) > t) return new Object[] { r, own == null ? "c" : "u", own, "" };
  }
  return new Object[] { null, "m", own, "" };
}""",
# the step of the line out belongs to (null = no line has a recipe for it)
r"""
public static Object[] stepOf(String[] s, String out) {
  String g = @PKG@.AccDefs.groupOf(out);
  if (g == null) return null;
  java.util.ArrayList ls = lines();
  for (int i = 0; i < ls.size(); i++) {
    Object[] line = (Object[]) ls.get(i);
    if (g.equals(line[0])) return step(s, line);
  }
  return null;
}""",
# the item a row shows: the next step's output; at MAX the bag's best, or (Omni) the line's top recipe
r"""
public static String shownId(Object[] line, Object[] st) {
  if (st[0] != null) return outId((@CRR@) st[0]);
  if (st[2] != null) return @PKG@.AccDefs.modernOf((String) st[2]);
  java.util.ArrayList l = (java.util.ArrayList) line[1];
  return l.isEmpty() ? null : outId((@CRR@) l.get(l.size() - 1));
}""",
# the sort key (Skyy's standing rule: by tier, then name; LOCKED 2026-10-13 "since the tutorial asks you to craft this, id move it to the
# top. sort them by tier, and per tier,m sort them by easiest to craft"): Workbench Accessory I (the tutorial's first craft) first, then the
# accessory's own ladder tier (bench T1..T7, stat rarity 1..4), the Omni last; inside a tier easiest to craft first = the 0.5.13 / 0.5.15
# cost order (ItemLevel = its place in ORDER, level(); 0 = unknown -> after), then name, then id
r"""
public static int sortTier(String id) {
  if ("@FIRST@".equals(id)) return -1;
  if (@PKG@.AccDefs.OMNI.equals(id)) return 99;
  return @PKG@.AccDefs.tierOf(id);
}""".replace("@FIRST@", "Skyy_Accessory_Workbench_T1"),
r"""
public static int costRank(String id) {
  int v = level(id);
  return v > 0 ? v : 999999;
}""",
r"""
public static boolean rowBefore(Object[] a, Object[] b) {
  String x = (String) a[4];
  String y = (String) b[4];
  int tx = sortTier(x);
  int ty = sortTier(y);
  if (tx != ty) return tx < ty;
  int lx = costRank(x);
  int ly = costRank(y);
  if (lx != ly) return lx < ly;
  int c = accName(x).compareToIgnoreCase(accName(y));
  if (c != 0) return c < 0;
  return x.compareTo(y) < 0;
}""",
# the rows of sub tab sub for bag k: Object[] { recipe or null, mode, own, why, shown id }, sorted (rowBefore)
r"""
public static java.util.ArrayList rowsFor(java.util.UUID u, String k, @PLA@ p, int sub) {
  String[] s = (u == null || k == null) ? new String[0] : bagSnap(u, k);
  java.util.ArrayList ls = lines();
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < ls.size(); i++) {
    Object[] line = (Object[]) ls.get(i);
    Object[] st = step(s, line);
    if ("d".equals(st[3])) continue;   // 0.5.22: a drop-only line with none in the bag (never a from-scratch recipe)
    String shown = shownId(line, st);
    if (shown == null || subOf(shown) != sub) continue;
    out.add(new Object[] { st[0], st[1], st[2], st[3], shown });
  }
  for (int i = 1; i < out.size(); i++) {
    Object x = out.get(i);
    int j = i - 1;
    while (j >= 0 && rowBefore((Object[]) x, (Object[]) out.get(j))) { out.set(j + 1, out.get(j)); j--; }
    out.set(j + 1, x);
  }
  return out;
}""",
r"""
public static String ridOf(Object[] e) {
  return (e == null || e[0] == null) ? null : ((@CRR@) e[0]).getId();
}""",
# plan() with the containers in the order a craft pays from: an UPGRADE takes from the BAG first (the one being upgraded is the bag's copy
# even when another copy sits in the inventory), then inventory, then Void; a craft: inventory, Void, bag (0.5.18). Same Object[] layout.
r"""
public static Object[] planFor(java.util.UUID u, String k, @PLA@ p, @CRR@ r, boolean up) {
  Object[] ic = invCopy(p.getInventory());
  Object[] vc = voidCopy(u, r.getInput());
  Object[] bc = bagCopy(u, k, r.getInput());
  @IC@[] order = up ? new @IC@[] { (@IC@) bc[0], (@IC@) ic[0], (@IC@) vc[0] } : new @IC@[] { (@IC@) ic[0], (@IC@) vc[0], (@IC@) bc[0] };
  return new Object[] { new @CIC@(order), ic, vc, bc };
}""",
# a is the line of b, one tier below or more (the in-place upgrade's old one)
r"""
public static boolean below(String a, String b) {
  if (a == null || b == null) return false;
  String m = @PKG@.AccDefs.modernOf(a);
  String g = @PKG@.AccDefs.groupOf(m);
  return g != null && g.equals(@PKG@.AccDefs.groupOf(b)) && @PKG@.AccDefs.tierOf(m) < @PKG@.AccDefs.tierOf(b);
}""",
# true when an input of the recipe is an accessory (the Omni, an upgrade): such a craft can free its own bag slot
r"""
public static boolean accInputs(@CRR@ r) {
  @MQ@[] in = r.getInput();
  for (int i = 0; in != null && i < in.length; i++) if (in[i] != null && @PKG@.AccDefs.isAccessory(in[i].getItemId())) return true;
  return false;
}""",
# THE IN-PLACE SWAP: slot idx of bag k holds old -> it holds nw; one array change under the bag lock, then one save (tmp + move). ok[0]
r"""
public static boolean swapIn(String[] s, int idx, String old, String nw) {
  if (s == null || idx < 0 || idx >= s.length || s[idx] == null || !s[idx].equals(old)) return false;
  s[idx] = nw;
  return true;
}""",
r"""
public static void swapSlot(java.util.UUID u, String k, int idx, String old, String nw, boolean[] ok) {
  String[] s = @PKG@.AccStore.slotsK(u, k);
  synchronized (@PKG@.AccStore.lock(u)) { ok[0] = swapIn(s, idx, old, nw); }
  if (ok[0]) @PKG@.AccStore.saveK(u, k);
}""",
# ONE ROW of the Craft view: { item id, name, "RARITY - status", rarity colour, cost line, cost colour, "c" / "u" / "m" }
r"""
public static String[] lineRow(java.util.UUID u, String k, @PLA@ p, Object[] e) {
  @CRR@ r = (@CRR@) e[0];
  String shown = (String) e[4];
  String rar = @PKG@.AccDefs.rarityName(shown).toUpperCase();
  if (r == null) {
    String why = "o".equals(e[3]) ? "Your Omni Accessory counts as this bench at its top tier - nothing to craft here." : "Fully upgraded - " + accName(shown) + " is the top of its line.";
    return new String[] { shown, accName(shown), rar + " - MAX", @PKG@.AccDefs.rarityColor(shown), why, GREY, "m" };
  }
  boolean up = "u".equals(e[1]);
  String[] res = new String[] { shown, accName(shown), "", @PKG@.AccDefs.rarityColor(shown), "", GREY, up ? "u" : "c" };
  String g = @PKG@.AccDefs.groupOf(shown);
  try {
    @MQ@[] in = r.getInput();
    boolean kn = p != null && known(p, r);
    @CIC@ comb = null;
    if (p != null && p.getInventory() != null && u != null && k != null) comb = (@CIC@) planFor(u, k, p, r, up)[0];
    StringBuilder sb = new StringBuilder();
    for (int i = 0; in != null && i < in.length; i++) {
      if (in[i] == null) continue;
      if (up && in[i].getItemId() != null && g != null && g.equals(@PKG@.AccDefs.groupOf(@PKG@.AccDefs.modernOf(in[i].getItemId())))) continue;
      long have = comb == null ? 0L : (long) comb.countRemovableMaterial(in[i]);
      if (have > (long) in[i].getQuantity()) have = (long) in[i].getQuantity();
      if (sb.length() > 0) sb.append(", ");
      sb.append(matName(in[i])).append(' ').append(haveText(have)).append('/').append(in[i].getQuantity());
    }
    boolean ok = kn && comb != null && comb.canRemoveMaterials(@CRM@.getInputMaterials(r, 1));
    res[2] = rar + " - " + (!kn ? "LOCKED" : (ok ? (up ? "CAN UPGRADE" : "CAN CRAFT") : "NEEDS MATERIALS"));
    String pre = up ? "Upgrades your " + accName(@PKG@.AccDefs.modernOf((String) e[2])) + " - cost: " : "";
    res[4] = (!kn ? "Locked - " + lockText(shown) + ". " : "") + pre + (sb.length() == 0 ? "nothing else" : sb.toString());
    if (ok) res[5] = GREEN;
  } catch (Throwable t) {
    res[2] = rar;
    res[4] = "the materials could not be read: " + t;
  }
  return res;
}""",
# "<pre><n>"" in the click data -> n (-1 = none); subIndex = a sub tab click "st:<n>"
r"""
public static int numAfter(String data, String pre) {
  if (data == null) return -1;
  int i = data.indexOf(pre);
  if (i < 0) return -1;
  int j = i + pre.length();
  int v = 0;
  int d = 0;
  while (j < data.length() && d < 6) {
    char c = data.charAt(j);
    if (c < '0' || c > '9') break;
    v = v * 10 + (c - '0');
    j++;
    d++;
  }
  if (d == 0 || j >= data.length() || data.charAt(j) != '"') return -1;
  return v;
}""",
r"""
public static int subIndex(String data) {
  int v = numAfter(data, "\"st:");
  return v < SUB_NAMES.length ? v : -1;
}""",
# ---- THE CRAFT (the page click, world thread): the result text for the page's info line. See the patch docstring item 1.
r"""
public static String craft(@PR@ pr, @REF@ ref, @ST@ st, @PLA@ p, java.util.UUID u, String k, String rid) {
  if (!@PKG@.AccDefs.CRAFT) return "@OFF@";
  if (p == null || u == null || k == null || rid == null) return "your player could not be read - nothing was used";
  String blk = @PKG@.AccStore.moveBlock(u);
  if (blk != null) return blk;
  @PKG@.AccStore.slotsK(u, k);
  if (@PKG@.AccStore.isBad(k)) return "your Void Charms file could not be read - nothing was used, tell an admin (server log)";
  Object o = null;
  try { o = @CRR@.getAssetMap().getAsset(rid); } catch (Throwable t) { o = null; }
  if (!(o instanceof @CRR@) || !ours((@CRR@) o)) return "that recipe is not on the list any more - nothing was used";
  @CRR@ r = (@CRR@) o;
  String out = outId(r);
  String nm = accName(out);
  Object[] sp = stepOf(bagSnap(u, k), out);   // 0.5.21: only the line's NEXT step for this bag (a double click / an old row uses nothing)
  if (sp == null || sp[0] == null || !rid.equals(((@CRR@) sp[0]).getId())) return "that row changed - the list is up to date now, nothing was used";
  boolean up = "u".equals(sp[1]);
  String put0 = @PKG@.AccDefs.modernOf(out);
  if (!known(p, r)) return nm + " is locked - " + lockText(out);
  @INV@ inv = p.getInventory();
  if (inv == null) return "your inventory could not be read - nothing was used";
  java.util.List inputs = @CRM@.getInputMaterials(r, 1);
  if (inputs == null || inputs.isEmpty()) return "that recipe has no materials - nothing was made";
  Object[] pl = planFor(u, k, p, r, up);   // 0.5.21: an upgrade takes the bag's copy first
  @CIC@ comb = (@CIC@) pl[0];
  if (!comb.canRemoveMaterials(inputs)) return "not enough materials for " + nm + " - nothing was used";
  if (!up && @PKG@.AccDefs.AUTO && !accInputs(r) && !@PKG@.AccStore.canEquipK(u, k, put0)) return "your Void Charms has no free slot for " + nm + " - free one first, nothing was used";   // 0.5.21
  if (!fire(st, ref, u, r, false)) { journal("REFUSED " + who(pr, u, k) + " " + rid + " (CraftRecipeEvent$Pre cancelled)"); return "this craft was refused - nothing was used"; }
  Object[] ic = (Object[]) pl[1];
  Object[] vc = (Object[]) pl[2];
  Object[] bc = (Object[]) pl[3];
  @SIC@ icc = (@SIC@) ic[0];
  @SIC@ vcc = (@SIC@) vc[0];
  @SIC@ bcc = (@SIC@) bc[0];
  int[] a0 = qty(icc);
  int[] b0 = qty(vcc);
  int[] c0 = qty(bcc);
  try { comb.removeMaterials(inputs); } catch (Throwable t0) { return "the materials could not be counted out (" + t0 + ") - nothing was used"; }
  int[] a1 = qty(icc);
  int[] b1 = qty(vcc);
  int[] c1 = qty(bcc);
  java.util.LinkedHashMap invT = new java.util.LinkedHashMap();
  java.util.LinkedHashMap voidT = new java.util.LinkedHashMap();
  StringBuilder bagT = new StringBuilder();
  String[] iids = (String[]) ic[5];
  String[] vids = (String[]) vc[1];
  String[] bst = (String[]) bc[2];
  for (int j = 0; j < a0.length; j++) { if (a0[j] < a1[j]) return "the materials did not add up - nothing was used"; if (a0[j] > a1[j]) addCount(invT, iids[j], (long) (a0[j] - a1[j])); }
  for (int j = 0; j < b0.length; j++) { if (b0[j] < b1[j]) return "the materials did not add up - nothing was used"; if (b0[j] > b1[j]) addCount(voidT, vids[j], (long) (b0[j] - b1[j])); }
  for (int j = 0; j < c0.length; j++) if (c0[j] > c1[j]) bagT.append(bagT.length() > 0 ? "," : "").append(bst[j]);
  if (invT.isEmpty() && voidT.isEmpty() && bagT.length() == 0) return "nothing would be used - nothing was made";
  // 0.5.21: an UPGRADE whose only bag part is the one of its line below it -> swapped in place (swapSlot) instead of takeBag + equipK
  int un = 0;
  int ux = -1;
  String uold = null;
  int[] bix = (int[]) bc[1];
  for (int j = 0; j < c0.length; j++) if (c0[j] > c1[j]) { un++; ux = bix[j]; uold = bst[j]; }
  boolean swap = up && un == 1 && ux >= 0 && below(uold, put0);
  String plan = "inventory " + invT + " void " + voidT + " bag [" + bagT + "]";
  journal("BEGIN " + who(pr, u, k) + " " + rid + " " + plan);
  java.util.ArrayList undo = new java.util.ArrayList();
  java.util.LinkedHashMap took = new java.util.LinkedHashMap();
  java.util.ArrayList bagUndo = new java.util.ArrayList();
  String bad = null;
  try {
    bad = takeInv(ic, a0, a1, undo);
    if (bad == null) bad = takeVoid(u, voidT, took);
    if (bad == null && !swap) bad = takeBag(u, k, bc, c0, c1, bagUndo);   // 0.5.21: the in-place upgrade swaps its slot below instead
  } catch (Throwable t1) { bad = "internal error (" + t1 + ")"; }
  if (bad != null) {
    String lost = rollback(u, k, undo, took, bagUndo);
    journal("ROLLBACK " + who(pr, u, k) + " " + rid + " (" + bad + ")" + (lost.length() > 0 ? " NOT RETURNED:" + lost : ""));
    return bad + " - nothing was used";
  }
  if (swap) {   // 0.5.21: THE IN-PLACE UPGRADE - the old one leaves the bag only as the new one takes its slot (one bag file write)
    boolean[] sok = new boolean[1];
    swapSlot(u, k, ux, uold, put0, sok);
    if (!sok[0]) {
      String lost3 = rollback(u, k, undo, took, bagUndo);
      journal("ROLLBACK " + who(pr, u, k) + " " + rid + " (the bag slot changed before the upgrade)" + (lost3.length() > 0 ? " NOT RETURNED:" + lost3 : ""));
      return "your Void Charms changed while upgrading - nothing was used";
    }
    commitVoid(u, took);
    try { p.markNeedsSave(); } catch (Throwable t5) { }
    CRAFTED = CRAFTED + 1L;
    journal("DONE " + who(pr, u, k) + " " + rid + " -> bag (upgraded in place, slot " + ux + ": " + uold + " -> " + put0 + ")");
    fire(st, ref, u, r, true);
    @PKG@.AccSnd.equipped(u, uold);
    return "upgraded to " + nm + " in your Void Charms - your " + accName(@PKG@.AccDefs.modernOf(uold)) + " was used for it";
  }
  String put = @PKG@.AccDefs.modernOf(out);
  String res = null;
  try { if (@PKG@.AccDefs.AUTO && @PKG@.AccStore.canEquipK(u, k, put) && swapSafe(p, u, k, put)) res = @PKG@.AccStore.equipK(u, k, put); } catch (Throwable t2) { res = null; }
  String where = null;
  if (res != null) {
    if (res.length() > 0) {
      String old = @PKG@.AccDefs.modernOf(res);
      int g = back(p, u, k, old);
      where = "upgraded in your Void Charms - " + accName(old) + (g == 0 ? " is back in your inventory" : (g == 1 ? " was kept in a free Void Charms slot (inventory full)" : " could not be returned - reported to the server log"));
    } else where = "it went straight into your Void Charms";
  } else {
    int got = addInv(inv, out);
    if (got != 1) {
      String lost2 = rollback(u, k, undo, took, bagUndo);
      journal("ROLLBACK " + who(pr, u, k) + " " + rid + " (no room for the result)" + (lost2.length() > 0 ? " NOT RETURNED:" + lost2 : ""));
      return "no room for " + nm + " in your inventory" + (@PKG@.AccDefs.AUTO ? " or Void Charms" : "") + " - nothing was used";
    }
    where = @PKG@.AccDefs.AUTO ? "it is in your inventory (" + why(u, k, put) + ")" : "it is in your inventory";
  }
  commitVoid(u, took);
  try { p.markNeedsSave(); } catch (Throwable t3) { }
  CRAFTED = CRAFTED + 1L;
  journal("DONE " + who(pr, u, k) + " " + rid + " -> " + (res == null ? "inventory" : (res.length() > 0 ? "bag (upgraded " + res + ")" : "bag")));
  fire(st, ref, u, r, true);
  if (res != null) @PKG@.AccSnd.equipped(u, res);
  return "crafted " + nm + " - " + where;
}""".replace("@OFF@", C8_TEXTS["OFF"]),
# the "cr:<n>" button data -> n (-1 = not a craft click)
r"""
public static int clickIndex(String data) {
  if (data == null) return -1;
  int i = data.indexOf("\"cr:");
  if (i < 0) return -1;
  int j = i + 4;
  int v = 0;
  int d = 0;
  while (j < data.length() && d < 6) {
    char c = data.charAt(j);
    if (c < '0' || c > '9') break;
    v = v * 10 + (c - '0');
    j++;
    d++;
  }
  if (d == 0 || j >= data.length() || data.charAt(j) != '"') return -1;
  return v;
}""",
# ---- AUTO-EQUIP of an accessory crafted at a bench / pocket crafting / /craft
# the identities of the crafter's stacks of id (storage, hotbar, backpack) before the output arrives
r"""
public static java.util.IdentityHashMap snap(@INV@ inv, String id) {
  java.util.IdentityHashMap m = new java.util.IdentityHashMap();
  if (inv == null || id == null) return m;
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) m.put(it, Boolean.TRUE);
    }
  }
  return m;
}""",
# one new stack in slot s of c -> the bag through the Equip button's path. "+" equipped, "+<old id>|<g>" upgraded (g = back()),
# "-<why>" kept in the inventory
r"""
public static String autoOne(java.util.UUID u, @PLA@ p, @IC@ c, short s, @IS@ it) {
  String blk = @PKG@.AccStore.moveBlock(u);
  if (blk != null) return "-your profile is still loading (put it on from the Void Charms page)";
  String k = @PKG@.AccStore.pkey(u);
  @PKG@.AccStore.slotsK(u, k);
  if (@PKG@.AccStore.isBad(k)) return "-your Void Charms file could not be read";
  String id = it.getItemId();
  String put = @PKG@.AccDefs.modernOf(id);
  if (!@PKG@.AccStore.canEquipK(u, k, put)) return "-" + why(u, k, put);
  if (c.getItemStack(s) != it) return "-it moved";
  @ISS@ tx = c.removeItemStackFromSlot(s, 1);
  if (tx == null || !tx.succeeded()) return "-it could not be picked up";
  String res = @PKG@.AccStore.equipK(u, k, put);
  if (res == null) {
    c.setItemStackForSlot(s, it);
    return "-" + why(u, k, put);
  }
  @PKG@.AccSnd.equipped(u, res);
  if (res.length() > 0) {
    String old = @PKG@.AccDefs.modernOf(res);
    return "+" + old + "|" + back(p, u, k, old);
  }
  return "+";
}""",
r"""
public static void say(@PR@ pr, String text, String col) {
  try { pr.sendMessage(@MSG@.raw(text).color(col)); } catch (Throwable t) { }
}""",
# the world task's work: every stack of id that was not in the snapshot (at most cap) -> autoOne; one chat line per outcome kind.
# Returns "none" / "off" / "<equipped> in, <kept> kept" (logs / harness)
r"""
public static String autoRun(@PR@ pr, @PLA@ p, String id, java.util.IdentityHashMap snap, int cap) {
  if (!@PKG@.AccDefs.AUTO) return "off";
  if (pr == null || p == null || id == null) return "none";
  java.util.UUID u = pr.getUuid();
  @INV@ inv = p.getInventory();
  if (inv == null) return "none";
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  int in = 0;
  int kept = 0;
  String oldTxt = "";
  String whyTxt = null;
  for (int c = 0; c < cs.length && in + kept < cap; c++) {   // fix round: the cap counts all three containers together
    if (cs[c] == null) continue;
    short capc = cs[c].getCapacity();
    for (short s = 0; s < capc; s++) {
      if (in + kept >= cap) break;
      @IS@ it = cs[c].getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || (snap != null && snap.containsKey(it))) continue;
      String r = autoOne(u, p, cs[c], s, it);
      if (r.startsWith("+")) {
        in++;
        if (r.length() > 1) {
          int bar = r.indexOf('|');
          String old = r.substring(1, bar);
          String g = r.substring(bar + 1);
          oldTxt = " " + accName(old) + ("0".equals(g) ? " is back in your inventory." : ("1".equals(g) ? " was kept in a free Void Charms slot (inventory full)." : " could not be returned - reported to the server log."));
        }
      } else {
        kept++;
        whyTxt = r.substring(1);
      }
    }
  }
  if (in + kept == 0) return "none";
  String nm = accName(id);
  if (in > 0) {
    AUTOED = AUTOED + (long) in;
    say(pr, "@AUTO_IN_A@" + nm + "@AUTO_IN_B@" + oldTxt, INCOL);
  }
  if (kept > 0) say(pr, "@AUTO_OUT_A@" + nm + "@AUTO_OUT_B@" + whyTxt + "@AUTO_OUT_C@", OUTCOL);
  journal("AUTO " + who(pr, u, @PKG@.AccStore.pkey(u)) + " " + id + " -> " + in + " into the bag, " + kept + " kept" + (whyTxt == null ? "" : " (" + whyTxt + ")"));
  return in + " in, " + kept + " kept";
}""".replace("@AUTO_IN_A@", C8_TEXTS["AUTO_IN"].split("%s")[0]).replace("@AUTO_IN_B@", C8_TEXTS["AUTO_IN"].split("%s")[1])
   .replace("@AUTO_OUT_A@", C8_TEXTS["AUTO_OUT"].split("%s")[0]).replace("@AUTO_OUT_B@", C8_TEXTS["AUTO_OUT"].split("%s")[1])
   .replace("@AUTO_OUT_C@", C8_TEXTS["AUTO_OUT"].split("%s")[2]),
]:
    CM(acr_, _src)
assert C8_TEXTS["AUTO_OUT"].count("%s") == 2 and C8_TEXTS["AUTO_IN"].count("%s") == 1

# ---- AccAutoTask: the world-thread task one craft event sends (it runs after the craft call returned: the world queue is FIFO)
CF(aat_, "public @PR@ pr;")
CF(aat_, "public java.util.UUID wu;")
CF(aat_, "public String id;")
CF(aat_, "public java.util.IdentityHashMap snap;")
CF(aat_, "public int cap;")
CF(aat_, "public Long stamp;")
CF(aat_, "public static boolean FAILED = false;")
aat_.addInterface(pool.get("java.lang.Runnable"))
aat_.addConstructor(CtNewConstructor.make(CJ("public AccAutoTask(@PR@ pr, java.util.UUID wu, String id, java.util.IdentityHashMap snap, int cap, Long stamp) { this.pr = pr; this.wu = wu; this.id = id; this.snap = snap; this.cap = cap; this.stamp = stamp; }"), aat_))
CM(aat_, r"""
public void run() {
  try {
    if (this.stamp != null && this.pr != null) @PKG@.AccCraft.PENDING.remove(this.pr.getUuid().toString() + "|" + this.id, this.stamp);
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID now = this.pr.getWorldUuid();
    if (now == null || !now.equals(this.wu)) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PKG@.AccCraft.autoRun(this.pr, p, this.id, this.snap, this.cap);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("auto-equip of a crafted accessory failed (logged once): " + t); }
  }
}""")
# the hook (both systems): a crafted current accessory -> snapshot + one task. A Post within 5 s of its Pre (an instant craft: Pre and Post in
# the same craftItem call) is skipped - the Pre task covers it; a timed craft's Pre task finds nothing and its Post (per unit) sends its own.
CM(acr_, r"""
public static void seen(int idx, @ACH@ chunk, @ST@ st, @CRE@ e, boolean post) {
  if (!@PKG@.AccDefs.AUTO || e == null || e.isCancelled()) return;
  @CRR@ rc = e.getCraftedRecipe();
  String id = outId(rc);
  if (id == null || !@PKG@.AccDefs.isAccessory(id) || @PKG@.AccDefs.isRetired(id)) return;
  @REF@ r = chunk.getReferenceTo(idx);
  if (r == null) return;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (pr == null || p == null || p.getInventory() == null) return;
  java.util.UUID u = pr.getUuid();
  if (SELF.containsKey(u)) return;
  String pk = u.toString() + "|" + id;
  long now = System.currentTimeMillis();
  if (post) {
    Long t0 = (Long) PENDING.get(pk);
    if (t0 != null && now - t0.longValue() < 5000L) return;
  }
  Object ext = st.getExternalData();
  if (!(ext instanceof @ENS@)) return;
  @WLD@ w = ((@ENS@) ext).getWorld();
  if (w == null) return;
  int units = (post && rc.getTimeSeconds() > 0.0f) ? 1 : Math.max(1, e.getQuantity());
  @MQ@ po = rc.getPrimaryOutput();
  int cap = units * Math.max(1, po == null ? 1 : po.getQuantity());
  if (cap > 16) cap = 16;
  Long stamp = null;
  if (!post) {
    if (PENDING.size() > 2000) PENDING.clear();
    stamp = Long.valueOf(now);
    PENDING.put(pk, stamp);
  }
  w.execute(new @PKG@.AccAutoTask(pr, pr.getWorldUuid(), id, snap(p.getInventory(), id), cap, stamp));
}""")
# ---- the two systems (ONE registerSystem per class: the plugin's setup); the world thread (store.invoke)
for _cls, _ev, _post, _nm in ((apre, C8_PRE, "false", "AccAutoPre"), (apst, C8_POST, "true", "AccAutoPost")):
    _cls.addConstructor(CtNewConstructor.make("public %s() { super(%s.class); }" % (_nm, _ev), _cls))
    CF(_cls, "public static boolean FAILED = false;")
    CM(_cls, r"""
public @QRY@ getQuery() {
  return @ARC@.empty();
}""")
    CM(_cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EVT@ ev) {
  try {
    @PKG@.AccCraft.seen(idx, chunk, st, (@CRE@) ev, @POSTFLAG@);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("@NM@ failed (logged once; the craft itself is not touched): " + t); }
  }
}""".replace("@POSTFLAG@", _post).replace("@NM@", _nm))

# ================= 0.5.22 VOID CHARMS ON THE KIT 1.7 HUB PAGE (tools/accessories_0_5_22_patch.py; research/Menu-Pattern.md, tools/HUBS-CONTRACT.md
# 'Kit 1.7'; Skyy 2026-10-16 "I never want to have to use a back button. The menus at the top should always be there for easy navigation." +
# "id change this to the same grid system you used for the pets"): 1600 x 980, the title bar, row 1 (Home + the hubs) + row 2 (the Character
# tabs, Void Charms selected) from HubBar.page17, the ONE sub-tab row BAG | CRAFT | POWER (HubBar.subTab), the content 1552 x 676, the footer
# (the result line + Close). 0.4.5 - 0.5.21: the vanilla decorated 1210 x 980 window with its own Bag | Craft tab row and two paged lists.
UI_DATA_COLORS = ["#8a97a3"]           # AccDefs.RETIRED_COLOR (0.4.2): a retired accessory's name + rarity word - data, like the rarity colours
ACC_PREFIX = "SkyyAcc"
LF = chr(10)
J_ = SUI.J
VC = SUI.hub_page(ACC_PREFIX, VC_HUB, sub=True, footer=True, body_id="SkyyAccB", content_id="SkyyAccC")
assert (VC.w, VC.h, VC.content_w, VC.content_h, VC.content, VC.sub, VC.foot) == (1600, 980, 1552, 676, "SkyyAccC", "SkyyAccSub", "SkyyAccFoot"), "0.5.22: the hub page"
VC_HUB_JAVA = SUI.java_hub_page(VC, VC_TAB, cls="@PKG@.HubBar")
VC_TABS_NOW = [(r[0], VC_LABEL if r[0] == VC_TAB else SUI.hub_tab_label(VC_HUB, r[0])) for r in SUI.hub_page_tabs(VC_HUB)]
assert VC_TAB in [t for t, _l in VC_TABS_NOW] and SUI.assert_big_tabs_fit(VC_HUB) >= SUI.HUB_BIG_TAB_MIN, "0.5.22: row 2 holds the Void Charms tab"
IW, CH = VC.content_w, VC.content_h
SUB_NAMES22 = ["Bag", "Craft", "Power"]
SUB_ACT22 = ["tb:bag", "tb:craft", "tb:power"]
SUI.assert_sub_tabs_fit(SUB_NAMES22, SUI.SUB_TAB_W)
SEC_H = 28
STRIP_H = 40
FILT_H = SUI.BTN_SMALL_H + 6
ACC_HINT = "Hover an accessory for what it does. Only your best accessory of each line counts."   # the BAG head's tail (player-literal check)
ACC_EMPTY = "Nothing selected - click an accessory in Void Charms or in your inventory"
ACC_NONE = "none - craft one in the Craft tab"
ACC_NONE_OFF = "none - accessory crafting is switched off on this server"
FILT_NAMES = ["All", "Combat", "Gathering", "Benches"]
_tbw = lambda t: max(64, int(-(-SUI.text_width(t, 14, bold=True, upper=True) // 1)) + 2 * SUI.BTN_SMALL_PAD)
FILT_W = [_tbw(t) for t in FILT_NAMES]
CR_FW = [_tbw(n) for n, _t in C9_SUBS]
TGAP, FILT_LW = 4, 64
# the BAG view: the strip (Accessory Power + Power + Change | slots), the filters, ALL 60 bag slots as one icon grid (20 x 3 - the pets
# page's grid; Skyy: "so its easy to see all of them at once"), the selected accessory (Unequip / Equip), the accessories carried (20 x 2)
GCOLS = (IW - 2 * SUI.GRID_WELL_PAD + SUI.GRID_SPACING) // (SUI.GRID_SLOT + SUI.GRID_SPACING)
BAG_ROWS = (CAP + GCOLS - 1) // GCOLS
INV_ROWS = 2
BAG_CELLS, INV_CELLS = GCOLS * BAG_ROWS, GCOLS * INV_ROWS
assert GCOLS == 20 and BAG_ROWS == 3 and BAG_CELLS == CAP == 60, (GCOLS, BAG_ROWS)
GRID_W = GCOLS * SUI.GRID_SLOT + (GCOLS - 1) * SUI.GRID_SPACING
BAG_GRID_H = BAG_ROWS * SUI.GRID_SLOT + (BAG_ROWS - 1) * SUI.GRID_SPACING + 2 * SUI.GRID_WELL_PAD
INV_GRID_H = INV_ROWS * SUI.GRID_SLOT + (INV_ROWS - 1) * SUI.GRID_SPACING + 2 * SUI.GRID_WELL_PAD
SEL_H, SEL_TOP = 56, 6
AP_W, CHG_W = 900, 160
SL_W = IW - AP_W - 8 - CHG_W - 8
BAG_GRID = SUI.item_grid("SkyyAccGrid", GCOLS, BAG_ROWS, tooltips=True, well=True)
INV_GRID = SUI.item_grid("SkyyAccInvG", GCOLS, INV_ROWS, tooltips=True, well=True)
_selrow = lambda act: SUI.static_row("SkyyAccSel", IW, h=SEL_H, icon=J_("selIcon", "Skyy_Accessory_Workbench_T2"), name=J_("selName", "Legendary Speed Accessory"),
                                     sub=J_("selSub", "+10% Speed - in Void Charms"), tag=J_("selTag", "+19 Accessory Power"), tag_col=J_("selTagCol", SUI.STATUS_INFO["gold"]),
                                     tag_w=260, action=act, action_w=140, action_on=True, anchor={"top": SEL_TOP})
SEL_B, SEL_I = _selrow("Unequip"), _selrow("Equip")
assert [x[0] for x in SEL_B.sets] == [x[0] for x in SEL_I.sets]
SEL_NONE = SUI.label("SkyyAccSelNone", "", "captionLight", w=IW, h=SEL_H, size=16, anchor={"top": SEL_TOP, "bottom": SUI.ROW_GAP}, padding={"horizontal": 8})
BAG_USED = STRIP_H + FILT_H + SEC_H + BAG_GRID_H + SEL_TOP + SEL_H + SUI.ROW_GAP + SEC_H + INV_GRID_H
assert BAG_USED <= CH and GRID_W + 2 * SUI.GRID_WELL_PAD <= IW, (BAG_USED, CH)
# the CRAFT view (0.5.21's rows; its sub tabs are now in-page filters - the page has ONE sub-tab row)
CR_HINT_H = 26
ACC_CR_HINT = "One row per accessory: craft it, then upgrade it here. Only Void Charms counts - move one in to upgrade it. Materials: inventory, Void, Void Charms."
ACC_CR_OFFTXT = "Crafting in Void Charms is switched off on this server - accessories can not be crafted right now."
CR_LIST_H = CH - CR_HINT_H - FILT_H - SEC_H
CR_ROW_H = 72
CR_ROW_W = IW - 2 * SUI.WELL_LIST_PAD - SUI.SCROLL_SIZE - SUI.SCROLL_SPACING
CR_ACT_W, CR_ICON, CR_ICON_BOX, CR_PAD, CR_BAR = 112, 40, 52, 8, 12
CR_PANEL_W = CR_ROW_W - 4 - CR_ACT_W
CR_NAME_W, CR_ING_GAP = 360, 12
CR_ING_W = CR_PANEL_W - 2 * CR_PAD - CR_BAR - CR_ICON_BOX - CR_NAME_W - CR_ING_GAP
CR_NAME_H, CR_SUB_H = SUI.fs(14) + 6, SUI.fs(12) + 5
CR_TEXT_TOP = (CR_ROW_H - CR_NAME_H - CR_SUB_H) // 2
assert CR_ING_W >= 600 and CR_TEXT_TOP >= 0 and CR_LIST_H >= 7 * (CR_ROW_H + SUI.ROW_GAP), (CR_ING_W, CR_LIST_H)
assert SUI.text_width(ACC_CR_HINT, 16) <= IW, ("the craft hint fits one line", SUI.text_width(ACC_CR_HINT, 16))
# the POWER view: the strip, two columns (Combat + Combat 15 | Gathering), one row per visible Power (its stats at your AP, Pick)
PCOL_GAP = 24
PCOL_W = (IW - PCOL_GAP) // 2
PROW_W = PCOL_W - 2 * SUI.WELL_LIST_PAD - SUI.SCROLL_SIZE - SUI.SCROLL_SPACING
PROW_H = 50
PCOLS_H = CH - STRIP_H
PNOTE_H = 60
PLIST0_H = PCOLS_H - SEC_H
PLIST1_H = PCOLS_H - SEC_H - PNOTE_H
assert len([_p for _p in PW_TABLE if _p[2] != 2]) * (PROW_H + SUI.ROW_GAP) + 2 * SUI.WELL_LIST_PAD <= PLIST0_H, "the 11 combat Powers show without scrolling"
assert len([_p for _p in PW_TABLE if _p[2] == 2]) * (PROW_H + SUI.ROW_GAP) + 2 * SUI.WELL_LIST_PAD <= PLIST1_H
_prow = lambda on: SUI.static_row("SkyyAccPw" + J_("i", "0"), PROW_W, h=PROW_H, icon=None, name=J_("pnm", "Glass Cannon - PICKED"),
                                  sub=J_("psb", "-8 HP, -4 Def, +25 Str, +6% Crit, +34% Crit Dmg"), name_col=J_("ptc", SUI.STATUS_INFO["gold"]),
                                  action="Pick", action_w=112, action_on=on)
PROW_ON, PROW_OFF = _prow(True), _prow(False)
assert [x[0] for x in PROW_ON.sets] == [x[0] for x in PROW_OFF.sets]
# the longest stat line (the Python twin of AccPower.statText, every stat shown) at a 1,200 AP bag still fits the row's text column
import math as _m22
def _pw_text(i, m):
    out = []
    for _j, _k, _v in PW_E:
        if _j != i:
            continue
        _kd, _lab, _pct, _nd = pw_stat(_k)
        _x = _v * m
        _val = _m22.floor(_x + 0.5) if _kd in (0, 3) else _m22.floor(_x * 10 + 0.5) / 10.0
        if _val == 0:
            continue
        out.append(("+" if _val > 0 else "") + (str(int(_val)) if _kd in (0, 3) else "%g" % _val) + ("% " if _pct else " ") + _lab)
    return ", ".join(out)
_pw_w = max((SUI.text_width(_pw_text(_i, pw_mult(1200)), SUI.fs(12)), _p[1]) for _i, _p in enumerate(PW_TABLE))
assert _pw_w[0] <= PROW_ON.text_w, ("0.5.22: a Power's stat line at 1,200 AP is wider than its row", _pw_w, PROW_ON.text_w)
assert _pw_text(2, pw_mult(350)) == "+4 HP, +2 Def, +15 Str, +21% Crit Dmg", _pw_text(2, pw_mult(350))
PNOTE = "Gathering Powers help their own skill only. A stat shows here once the tool that uses it reads it."
# the footer (every view): the result line left, Close right
STATUS_W = SUI.HUB_PAGE_IW - SUI.FOOT_GAP - SUI.BTN_MIN_W
STATUS_MK = SUI.label("SkyyAccInfo", "", "default", w=STATUS_W, h=SUI.FOOT_BTN_H, size=16, bold=True, col=J_("infoColor(this.info)", SUI.STATUS["+"]),
                      wrap=True, padding={"horizontal": 8})
# ---- the preview recorder: every append of a view lands in PV[view] (checked as one hub page below); the other look of each choose in PV_ALT
PV = {}
PV_KEY = [None]
PV_ALT = []


def pv(key):
    PV_KEY[0] = key
    PV.setdefault(key, SUI.Appends())


def jl(parent, mkup):
    if PV_KEY[0] is not None:
        PV[PV_KEY[0]].append((parent, mkup.a if isinstance(mkup, SUI.Choice) else mkup))
        if isinstance(mkup, SUI.Choice):
            PV_ALT.append((parent, mkup.b))
    return SUI.java_append(parent, mkup, page_root=False)


def jsets(mkup):
    if PV_KEY[0] is not None:
        PV[PV_KEY[0]].sets.extend(getattr(mkup, "sets", []))
    return LF.join(SUI.java_set(i, p, v) for i, p, v in getattr(mkup, "sets", []))


def jtext(ident, expr, sample):
    if PV_KEY[0] is not None:
        PV[PV_KEY[0]].sets.append((ident, "Text", J_(expr, sample)))
    return SUI.java_set(ident, "Text", J_(expr, sample))


def _tog(ident, text, w, sel, left):
    return SUI.button(ident, text, "tertiary", "small", w=w, selected=sel, anchor={"left": left} if left else None)


def toggles(row, ids, texts, widths, cond):
    out = []
    for i in range(len(texts)):
        left = 0 if i == 0 else TGAP
        out.append(jl(row, SUI.choose(cond % i, _tog(ids[i], texts[i], widths[i], True, left), _tog(ids[i], texts[i], widths[i], False, left))))
    return LF.join(out)


def ind(s, n=2):
    return LF.join((" " * n) + l for l in s.split(LF))


# ---- BAG
pv("bag")
BAG_TOP = LF.join([
    jl(VC.content, SUI.group("SkyyAccStrip", "Left", h=STRIP_H)),
    jl("SkyyAccStrip", SUI.label("SkyyAccApL", "", "rowName", w=AP_W, h=STRIP_H, col=SUI.STATUS_INFO["gold"], padding={"horizontal": 4})),
    jl("SkyyAccStrip", SUI.button("SkyyAccChg", "Change Power", "tertiary", "small", w=CHG_W, anchor={"left": 8, "top": (STRIP_H - SUI.BTN_SMALL_H) // 2})),
    jl("SkyyAccStrip", SUI.label("SkyyAccSlotsL", "", "rowSub", w=SL_W, h=STRIP_H, align="End", anchor={"left": 8}, padding={"horizontal": 4})),
    jtext("SkyyAccApL", "apLine", "Accessory Power 352 - Power: Slayer"),
    jtext("SkyyAccSlotsL", "slotsLine", "18 / 60 slots used"),
    jl(VC.content, SUI.group("SkyyAccFilt", "Left", h=SUI.BTN_SMALL_H, anchor={"top": 6})),
    jl("SkyyAccFilt", SUI.label("SkyyAccFiltL", "Show", "bold", w=FILT_LW, h=SUI.BTN_SMALL_H)),
    toggles("SkyyAccFilt", ["SkyyAccF%d" % i for i in range(4)], FILT_NAMES, FILT_W, "this.filt == %d"),
    jl(VC.content, SUI.label("SkyyAccBagH", "", "section", h=SEC_H)),
    jtext("SkyyAccBagH", "bagHead", "All - 12 accessories - " + ACC_HINT),
    jl(VC.content, BAG_GRID),
])
BAG_SEL_B = jl(VC.content, SEL_B) + LF + jsets(SEL_B)
PV_KEY[0] = None
BAG_SEL_I = jl(VC.content, SEL_I) + LF + jsets(SEL_I)
BAG_SEL_0 = SUI.java_append(VC.content, SEL_NONE, page_root=False) + LF + SUI.java_set("SkyyAccSelNone", "Text", J_("selNone", ACC_EMPTY))
pv("bag")
BAG_LOW = LF.join([
    jl(VC.content, SUI.label("SkyyAccInvH", "", "section", h=SEC_H)),
    jtext("SkyyAccInvH", "invHead", "In your inventory - 3 accessories - click one, then Equip"),
    jl(VC.content, INV_GRID),
])
PV_KEY[0] = None
# ---- CRAFT
pv("craft")
CR_TOP = LF.join([
    jl(VC.content, SUI.label("SkyyAccCrHint", "", "default", h=CR_HINT_H)),
    jtext("SkyyAccCrHint", "crHint", ACC_CR_HINT),
    jl(VC.content, SUI.group("SkyyAccCs", "Left", h=SUI.BTN_SMALL_H, anchor={"top": 6})),
    jl("SkyyAccCs", SUI.label("SkyyAccCsL", "Show", "bold", w=FILT_LW, h=SUI.BTN_SMALL_H)),
    toggles("SkyyAccCs", [t for _n, t in C9_SUBS], [n for n, _t in C9_SUBS], CR_FW, "this.craftSub == %d"),
    jl(VC.content, SUI.label("SkyyAccCrH", "", "section", h=SEC_H)),
    jtext("SkyyAccCrH", "crHead", "Benches - 12 accessories"),
    jl(VC.content, SUI.scroll_list("SkyyAccCrRows", h=CR_LIST_H, well=True)),
])
CR_NONE = jl("SkyyAccCrRows", SUI.label("SkyyAccCrNone", "", "caption", h=30, anchor={"left": 2})) + LF + jtext("SkyyAccCrNone", "crNone", ACC_CR_OFFTXT)


def cr_row(rid, act_id, act_text):
    """one line row (0.5.18 / 0.5.21's look, 1532 wide): #<rid> -> panel (bar, icon, name + 'RARITY - status', the cost line) + the button"""
    out = [jl("SkyyAccCrRows", SUI.group(rid, "Left", h=CR_ROW_H, anchor={"bottom": SUI.ROW_GAP})),
           jl(rid, SUI.panel(rid + "P", "row", w=CR_PANEL_W, h=CR_ROW_H, layout="Left", pad={"left": CR_PAD, "right": CR_PAD})),
           jl(rid + "P", SUI.group(rid + "Bar", None, w=4, anchor={"right": 8}, extra="Background: " + SUI.COLOR["selected"])),
           jl(rid + "P", SUI.group(rid + "Ib", None, w=CR_ICON_BOX, h=CR_ROW_H)),
           jl(rid + "Ib", SUI.item_icon(rid + "Ic", J_("safe(ri[0])", "Skyy_Accessory_Omni"), CR_ICON, anchor={"left": 0, "top": (CR_ROW_H - CR_ICON) // 2})),
           jl(rid + "P", SUI.group(rid + "T", "Top", w=CR_NAME_W, h=CR_ROW_H, pad={"top": CR_TEXT_TOP})),
           jl(rid + "T", SUI.label(rid + "Nm", "", "rowName", h=CR_NAME_H, col=J_("ri[3]", SUI.RARITY["Legendary"]))),
           jl(rid + "T", SUI.label(rid + "Rr", "", "rowSub", h=CR_SUB_H, col=J_("ri[3]", SUI.RARITY["Legendary"]))),
           jl(rid + "P", SUI.label(rid + "In", "", "rowSub", w=CR_ING_W, h=CR_ROW_H, wrap=True, col=J_("ri[5]", C8_GREEN), anchor={"left": CR_ING_GAP})),
           jtext(rid + "Nm", "ri[1]", "Legendary Health Accessory"), jtext(rid + "Rr", "ri[2]", "LEGENDARY - CAN CRAFT"),
           jtext(rid + "In", "ri[4]", "Farming Bench 1/1, Copper Bar 4/4")]
    if act_id is not None:
        out.append(jl(rid, SUI.row_action(act_id, act_text, w=CR_ACT_W)))
    return LF.join(out)


_K = J_("k", "0")
CR_ROW_C = cr_row("SkyyAccCr" + _K, "SkyyAccCb" + _K, "Craft")
PV_KEY[0] = None
CR_ROW_U = cr_row("SkyyAccCr" + _K, "SkyyAccCb" + _K, "Upgrade")
CR_ROW_M = cr_row("SkyyAccCr" + _K, None, None)
# ---- POWER
pv("power")
PW_TOP = LF.join([
    jl(VC.content, SUI.group("SkyyAccPs", "Left", h=STRIP_H)),
    jl("SkyyAccPs", SUI.label("SkyyAccPsL", "", "rowName", w=IW // 2, h=STRIP_H, col=SUI.STATUS_INFO["gold"], padding={"horizontal": 4})),
    jl("SkyyAccPs", SUI.label("SkyyAccPsR", "", "rowSub", w=IW - IW // 2, h=STRIP_H, align="End", padding={"horizontal": 4})),
    jtext("SkyyAccPsL", "psL", "Accessory Power 352 - x2.12 - Power: Slayer"),
    jtext("SkyyAccPsR", "psR", "Switching is free - 5 s between two switches"),
    jl(VC.content, SUI.group("SkyyAccPcs", "Left", h=PCOLS_H)),
    jl("SkyyAccPcs", SUI.group("SkyyAccPc0", "Top", w=PCOL_W, h=PCOLS_H)),
    jl("SkyyAccPcs", SUI.group("SkyyAccPc1", "Top", w=PCOL_W, h=PCOLS_H, anchor={"left": PCOL_GAP})),
    jl("SkyyAccPc0", SUI.label("SkyyAccPh0", "", "section", h=SEC_H)),
    jl("SkyyAccPc0", SUI.scroll_list("SkyyAccPl0", h=PLIST0_H, well=True)),
    jl("SkyyAccPc1", SUI.label("SkyyAccPh1", "", "section", h=SEC_H)),
    jl("SkyyAccPc1", SUI.scroll_list("SkyyAccPl1", h=PLIST1_H, well=True)),
    jl("SkyyAccPc1", SUI.label("SkyyAccPn", "", "captionLight", h=PNOTE_H, wrap=True, padding={"horizontal": 4})),
    jtext("SkyyAccPh0", "ph0", "Combat - 5 Powers, 6 more at Combat 15"),
    jtext("SkyyAccPh1", "ph1", "Gathering"),
    jtext("SkyyAccPn", "pnote", PNOTE),
])
PW_ROW0 = jl("SkyyAccPl0", SUI.choose(J_("on"), PROW_ON, PROW_OFF)) + LF + jsets(PROW_ON)
PV_KEY[0] = None
PW_ROW1 = jl("SkyyAccPl1", SUI.choose(J_("on"), PROW_ON, PROW_OFF)) + LF + jsets(PROW_ON)
# ---- the footer
pv("foot")
FOOT = LF.join([jl(VC.foot, STATUS_MK), jl(VC.foot, SUI.spacer(w=SUI.FOOT_GAP, h=SUI.FOOT_BTN_H)),
                jl(VC.foot, SUI.foot_button("SkyyAccClose", "Close", sound="cancel")),
                jtext("SkyyAccInfo", "infoText", "equipped Legendary Health Accessory")])
PV_KEY[0] = None
# ---- the build-time check of every view as ONE hub page (the kit's Python twins of HubBar.page17 / subTab + what the Java appends)
for _v, _keys, _sel in (("bag", ("bag", "foot"), 0), ("craft", ("craft", "foot"), 1), ("power", ("power", "foot"), 2)):
    _pv = SUI.hub_page_preview(VC, tabs=VC_TABS_NOW, my_tab=VC_TAB)
    _pv.extend(SUI.sub_tabs_preview(ACC_PREFIX, SUB_NAMES22, _sel, SUI.SUB_TAB_W))
    for _k in _keys:
        _pv.extend(PV[_k])
        _pv.sets.extend(PV[_k].sets)
    SUI.check_page(_pv, ACC_PREFIX)
    SUI.assert_proven(_pv, what="0.5.22 Void Charms view %s" % _v)
    SUI.check_sky_paths(_pv, tab_icons=True)
    SUI.assert_menu_page(_pv, VC, what="0.5.22 Void Charms view %s" % _v)
SUI.assert_proven(SUI.Appends(PV_ALT), what="0.5.22 Void Charms (the other looks)")
assert SUI.used_width(SUI.Appends([(p_, mk) for p_, mk in PV["foot"] if p_ == VC.foot]), VC.foot) == SUI.HUB_PAGE_IW, "0.5.22: the footer is filled exactly"
ACC_SH = SUI.Appends()   # the player-literal check below reads every markup + b.set text of the page
for _k in ("bag", "craft", "power", "foot"):
    ACC_SH.extend(PV[_k])
    ACC_SH.sets.extend(PV[_k].sets)
print("Void Charms page 0.5.22: %d x %d hub page (%s tab %s), sub-tabs %s; BAG %d px of %d (grid %d x %d = %d slots, inventory %d x %d), CRAFT %d px rows in a %d px list, POWER 2 x %d px columns"
      % (VC.w, VC.h, VC_HUB, VC_TAB, " | ".join(SUB_NAMES22), BAG_USED, CH, GCOLS, BAG_ROWS, BAG_CELLS, GCOLS, INV_ROWS, CR_ROW_H, CR_LIST_H, PCOL_W))
# AccPage.infoColor: the result line's colour from the result text: success green = done, error red = refused, info blue = a note
ACC_INFO_COLOR_SRC = """
public static String infoColor(String t) {
  if (t == null || t.length() == 0) return "%(eq)s";
  if (t.startsWith("upgraded to ")) return t.indexOf(" could not be returned") >= 0 ? "%(no)s" : "%(ok)s";
  if (t.startsWith("equipped ") || t.startsWith("unequipped ") || t.startsWith("Power is now ")) return "%(ok)s";
  if (t.startsWith("crafted ")) return t.indexOf(" could not be returned") >= 0 ? "%(no)s" : "%(ok)s";
  if (t.startsWith("your profile changed") || t.endsWith(" is already your Power") || t.startsWith("selected ")) return "%(eq)s";
  return "%(no)s";
}""" % {"ok": SUI.STATUS["+"], "no": SUI.STATUS["-"], "eq": SUI.STATUS["="]}
page.addMethod(CtNewMethod.make(ACC_INFO_COLOR_SRC, page))
JM(page, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# the grid click's {"a":"g","SlotIndex":3} (the value may be quoted)
JM(page, r"""
public static int jsonInt(String data, String key) {
  if (data == null || key == null) return -1;
  int p = data.indexOf(String.valueOf((char) 34) + key + String.valueOf((char) 34));
  if (p < 0) return -1;
  int c = data.indexOf(':', p);
  if (c < 0) return -1;
  int i = c + 1;
  while (i < data.length() && (data.charAt(i) == ' ' || data.charAt(i) == 34)) i++;
  int j = i;
  while (j < data.length() && (Character.isDigit(data.charAt(j)) || data.charAt(j) == '-')) j++;
  if (j == i) return -1;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""")
# the BAG filter of one accessory: 1 Combat, 2 Gathering, 3 Benches (the CRAFT sub tabs: AccCraft.subOf)
JM(page, r"""
public static int filtOf(String id) {
  int s = @PKG@.AccCraft.subOf(@PKG@.AccDefs.modernOf(id));
  return s == 0 ? 3 : (s == 2 ? 2 : 1);
}""")
JM(page, r"""
public static boolean rarer(String a, String b) {
  int ra = @PKG@.AccDefs.rarityOf(a);
  int rb = @PKG@.AccDefs.rarityOf(b);
  if (ra != rb) return ra > rb;
  return @PKG@.AccDefs.pretty(a).compareToIgnoreCase(@PKG@.AccDefs.pretty(b)) < 0;
}""")
# the accessories of bag copy s shown in the BAG grid (filter f), rarest first, then by name (the sort-by-tier rule)
JM(page, r"""
public static String[] bagOrder(String[] s, int f) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; s != null && i < s.length; i++) {
    if (s[i] == null) continue;
    if (f > 0 && filtOf(s[i]) != f) continue;
    int j = l.size();
    while (j > 0 && rarer(s[i], (String) l.get(j - 1))) j--;
    l.add(j, s[i]);
  }
  return (String[]) l.toArray(new String[0]);
}""")
JM(page, r"""
public static String effects(String id) {
  if (id == null || @PKG@.AccDefs.isRetired(id)) return "";
  String m = @PKG@.AccDefs.modernOf(id);
  if (@PKG@.AccDefs.OMNI.equals(m)) return "Counts as every bench accessory at its top tier";
  int t = @PKG@.AccDefs.tierOf(m);
  if (t > 4) t = 4;
  if (@PKG@.AccDefs.isLantern(m)) return @PKG@.AccDefs.lanText(t);
  if (@PKG@.AccDefs.isTalisman(m)) {
    int li = @PKG@.AccDefs.familyIndex(@PKG@.AccDefs.familyOf(m));
    if (li < 0) return "";
    String[] p = @PKG@.AccDefs.statParts(li, t);
    StringBuilder b = new StringBuilder();
    for (int k = 0; k < p.length; k++) { if (k > 0) b.append(", "); b.append(p[k]); }
    return b.toString();
  }
  return "Unlocks its bench's recipes in /craft";
}""")
# the hover text of a grid cell: rarity, what it does, its Accessory Power (or why it adds none), the drop-only note, the click hint
JM(page, r"""
public static String tip(String id, String[] s, boolean inBag) {
  String q = String.valueOf((char) 34);
  StringBuilder b = new StringBuilder();
  b.append("<color is=" + q + @PKG@.AccDefs.rarityColor(id) + q + ">" + @PKG@.AccDefs.rarityName(id).toUpperCase() + "</color>");
  String fx = effects(id);
  if (fx.length() > 0) b.append("\n" + fx);
  int a = inBag ? @PKG@.AccPower.apOne(s, id) : @PKG@.AccPower.apIf(id);
  if (a > 0) b.append("\n<color is=" + q + "@GOLD@" + q + ">+" + a + " Accessory Power</color>");
  else if (a == -1) b.append("\n<color is=" + q + "@DIM@" + q + ">Does not count - a better one of this line is in Void Charms</color>");
  else if (a == -2) b.append("\n<color is=" + q + "@DIM@" + q + ">Your Omni Accessory already counts as this bench</color>");
  else if (a == -3) b.append("\n<color is=" + q + "@DIM@" + q + ">Its line is switched off on this server</color>");
  else if (a == -4) b.append("\n<color is=" + q + "@DIM@" + q + ">" + @PKG@.AccDefs.retiredWhy(id) + "</color>");
  String d = @PKG@.AccPower.dropText(id);
  if (d.length() > 0) b.append("\n" + d);
  b.append("\n\n<color is=" + q + "@DIM@" + q + ">" + (inBag ? "Click it, then Unequip" : "Click it, then Equip") + "</color>");
  return b.toString();
}""".replace("@GOLD@", SUI.STATUS_INFO["gold"]).replace("@DIM@", SUI.COLOR["disabled"]))
JM(page, r"""
public static @IGS@ cell(String id, String[] s, boolean inBag) {
  @IGS@ g = new @IGS@(new @IS@(id, 1));
  g.setName(@PKG@.AccDefs.pretty(id));
  g.setDescription(tip(id, s, inBag));
  g.setActivatable(true);
  if (inBag && @PKG@.AccPower.apOne(s, id) < 0) g.setItemIncompatible(true);
  return g;
}""".replace("@IGS@", "com.hypixel.hytale.server.core.ui.ItemGridSlot"))
# 0.5.23: the page is still the player's open custom page (a replaced / dismissed page never gets a command - the client would disconnect)
JM(page, r"""
public boolean isOpen() {
  try {
    @REF@ r = this.playerRef.getReference();
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    if (st == null) return false;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.getPageManager() == null) return false;
    return p.getPageManager().getCustomPage() == this;
  } catch (Throwable t) { return false; }
}""")
# the stuck-tooltip guard (SkyyPets 0.4.0 / SkyyMenu 0.1.3): ONE update that empties both grids before the page closes or hands over
# 0.5.23: cells > 0 only while the LAST build was the BAG view (build() resets it), and only while this page is still the open one
JM(page, r"""
public void clearGrid() {
  if (this.cells <= 0) return;
  if (!isOpen()) { this.cells = 0; return; }
  try {
    @UCB@ b = new @UCB@();
    java.util.ArrayList e = new java.util.ArrayList();
    for (int i = 0; i < @BAGC@; i++) e.add(new @IGS@());
    b.set("#SkyyAccGrid.Slots", e);
    java.util.ArrayList e2 = new java.util.ArrayList();
    for (int i = 0; i < @INVC@; i++) e2.add(new @IGS@());
    b.set("#SkyyAccInvG.Slots", e2);
    sendUpdate(b);
    this.cells = 0;
  } catch (Throwable t) { }
}""".replace("@IGS@", "com.hypixel.hytale.server.core.ui.ItemGridSlot").replace("@BAGC@", str(BAG_CELLS)).replace("@INVC@", str(INV_CELLS)))
JM(page, r"""
public static int selMode(String sel) {
  if (sel == null) return 0;
  if (sel.startsWith("b:")) return 1;
  if (sel.startsWith("i:")) return 2;
  return 0;
}""")
JM(page, r"""
public static boolean has(String[] a, String id) {
  for (int i = 0; a != null && id != null && i < a.length; i++) if (id.equals(a[i])) return true;
  return false;
}""")
JM(page, r"""
public static String apTag(String[] s, String id, boolean inBag) {
  int a = inBag ? @PKG@.AccPower.apOne(s, id) : @PKG@.AccPower.apIf(id);
  if (a > 0) return "+" + a + " Accessory Power";
  if (a == -1) return "a better one counts";
  if (a == -2) return "the Omni covers it";
  if (a == -3) return "switched off";
  if (a == -4) return "retired";
  return "no Accessory Power";
}""")
BAG_SRC = r"""
public void buildBag(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ player, String[] s) {
  int cap = @PKG@.AccStore.capOf(s);
  int used = 0;
  for (int i = 0; i < s.length; i++) if (s[i] != null) used++;
  int ap = @PKG@.AccPower.apOf(s);
  int pi = @PKG@.AccPower.effIndex(u, this.key);
  String apLine = "Accessory Power " + ap + (@PKG@.AccPower.ON ? " - Power: " + @PKG@.AccPower.nameOf(pi) : " - Powers are switched off on this server");
  String slotsLine = used + " / " + cap + " slots used";
  if (this.filt < 0 || this.filt > 3) this.filt = 0;
  this.bagIds = bagOrder(s, this.filt);
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  int ni = inv.size() < @INVC@ ? inv.size() : @INVC@;
  this.invIds = new String[ni];
  for (int i = 0; i < ni; i++) this.invIds[i] = (String) inv.get(i);
  int sm = selMode(this.sel);
  String sid = sm == 0 ? null : this.sel.substring(2);
  if (sm == 1 && !has(s, sid)) { sm = 0; this.sel = ""; }
  if (sm == 2 && !has(this.invIds, sid)) { sm = 0; this.sel = ""; }
  String[] fn = new String[] { "All", "Combat", "Gathering", "Benches" };
  String bagHead = fn[this.filt] + " - " + this.bagIds.length + (this.bagIds.length == 1 ? " accessory - " : " accessories - ") + "@HINT@";
  String invHead = "In your inventory - " + (inv.isEmpty() ? (@PKG@.AccDefs.CRAFT ? "@NONE@" : "@NONEOFF@") : inv.size() + (inv.size() == 1 ? " accessory" : " accessories") + " - click one, then Equip" + (inv.size() > ni ? " (the first " + ni + " here)" : ""));
@TOP@
  java.util.ArrayList gl = new java.util.ArrayList();
  for (int i = 0; i < @BAGC@; i++) gl.add(i < this.bagIds.length ? cell(this.bagIds[i], s, true) : new @IGS@());
  b.set("#SkyyAccGrid.Slots", gl);
  if (sm == 0) {
    String selNone = "@EMPTY@";
@SEL0@
  } else {
    String selIcon = safe(sid);
    String selName = @PKG@.AccDefs.pretty(sid);
    String fx = effects(sid);
    String selSub = (fx.length() > 0 ? fx + " - " : "") + (sm == 1 ? "in Void Charms" : "in your inventory");
    String selTag = apTag(s, sid, sm == 1);
    String selTagCol = selTag.startsWith("+") ? "@GOLD@" : "@DIM@";
    if (sm == 1) {
@SELB@
      ev.addEventBinding(@BT@.Activating, "#SkyyAccSelAct", @EVD@.of("a", "un"));
    } else {
@SELI@
      ev.addEventBinding(@BT@.Activating, "#SkyyAccSelAct", @EVD@.of("a", "eq"));
    }
  }
@LOW@
  java.util.ArrayList il = new java.util.ArrayList();
  for (int i = 0; i < @INVC@; i++) il.add(i < ni ? cell(this.invIds[i], s, false) : new @IGS@());
  b.set("#SkyyAccInvG.Slots", il);
  this.cells = @BAGC@ + @INVC@;
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyAccGrid", @EVD@.of("a", "g"), false);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyAccInvG", @EVD@.of("a", "ig"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyAccChg", @EVD@.of("a", "tb:power"));
  for (int i = 0; i < 4; i++) ev.addEventBinding(@BT@.Activating, "#SkyyAccF" + i, @EVD@.of("a", "fl:" + i));
}""".replace("@TOP@", ind(BAG_TOP)).replace("@SEL0@", ind(BAG_SEL_0, 4)).replace("@SELB@", ind(BAG_SEL_B, 6)).replace("@SELI@", ind(BAG_SEL_I, 6)) \
    .replace("@LOW@", ind(BAG_LOW)).replace("@HINT@", ACC_HINT).replace("@NONE@", ACC_NONE).replace("@NONEOFF@", ACC_NONE_OFF).replace("@EMPTY@", ACC_EMPTY) \
    .replace("@IGS@", "com.hypixel.hytale.server.core.ui.ItemGridSlot").replace("@BAGC@", str(BAG_CELLS)).replace("@INVC@", str(INV_CELLS)) \
    .replace("@GOLD@", SUI.STATUS_INFO["gold"]).replace("@DIM@", SUI.COLOR["disabled"])
JM(page, BAG_SRC)
CRAFT_SRC = r"""
public void buildCraft(@UCB@ b, @UEB@ ev, java.util.UUID u, @PLA@ player) {
  if (this.craftSub < 0 || this.craftSub >= @PKG@.AccCraft.SUB_NAMES.length) this.craftSub = 0;
  java.util.ArrayList rs = @PKG@.AccDefs.CRAFT ? @PKG@.AccCraft.rowsFor(u, this.key, player, this.craftSub) : new java.util.ArrayList();
  int n = rs.size();
  this.craftIds = new String[n];
  for (int i = 0; i < n; i++) this.craftIds[i] = @PKG@.AccCraft.ridOf((Object[]) rs.get(i));
  String crHint = "@HINT@";
  String crHead = @PKG@.AccCraft.SUB_NAMES[this.craftSub] + " - " + n + (n == 1 ? " accessory" : " accessories");
  String crNone = @PKG@.AccDefs.CRAFT ? "No accessory in this tab can be crafted on this server - a drop-only accessory shows up once one is in Void Charms." : "@OFFTXT@";
@TOP@
  if (n == 0) {
@NONE@
  }
  for (int k = 0; k < n; k++) {
    String[] ri = @PKG@.AccCraft.lineRow(u, this.key, player, (Object[]) rs.get(k));
    if ("m".equals(ri[6])) {
@ROWM@
    } else if ("u".equals(ri[6])) {
@ROWU@
      ev.addEventBinding(@BT@.Activating, "#SkyyAccCb" + k, @EVD@.of("a", "cr:" + k));
    } else {
@ROWC@
      ev.addEventBinding(@BT@.Activating, "#SkyyAccCb" + k, @EVD@.of("a", "cr:" + k));
    }
  }
  for (int i = 0; i < @PKG@.AccCraft.SUB_NAMES.length; i++) ev.addEventBinding(@BT@.Activating, "#SkyyAccSt" + i, @EVD@.of("a", "st:" + i));
}""".replace("@TOP@", ind(CR_TOP)).replace("@NONE@", ind(CR_NONE, 4)).replace("@ROWM@", ind(CR_ROW_M, 6)).replace("@ROWU@", ind(CR_ROW_U, 6)) \
    .replace("@ROWC@", ind(CR_ROW_C, 6)).replace("@HINT@", ACC_CR_HINT).replace("@OFFTXT@", ACC_CR_OFFTXT)
JM(page, CRAFT_SRC)
POWER_SRC = r"""
public void buildPower(@UCB@ b, @UEB@ ev, java.util.UUID u, String[] s) {
  int ap = @PKG@.AccPower.apOf(s);
  double m = @PKG@.AccPower.mult(ap);
  int pi = @PKG@.AccPower.effIndex(u, this.key);
  long left = @PKG@.AccPower.waitLeft(this.key, System.currentTimeMillis());
  String psL = "Accessory Power " + ap + " - x" + @PKG@.AccPower.multText(m) + " - Power: " + (@PKG@.AccPower.ON ? @PKG@.AccPower.nameOf(pi) : "switched off");
  String psR = !@PKG@.AccPower.ON ? "Accessory Powers are switched off on this server" : (left > 0L ? "You can switch again in " + ((left + 999L) / 1000L) + " s" : "Switching is free - " + @PKG@.AccPower.WAIT + " s between two switches");
  int nc = 0;
  int n15 = 0;
  for (int i = 0; i < @PKG@.AccPower.PW_ID.length; i++) { if (!@PKG@.AccPower.visible(i)) continue; if (@PKG@.AccPower.PW_GRP[i] == 0) nc++; if (@PKG@.AccPower.PW_GRP[i] == 1) n15++; }
  String ph0 = "Combat - " + nc + " Powers" + (n15 > 0 ? ", " + n15 + " more at Combat " + @PKG@.AccPower.UNLOCK : "");
  String ph1 = "Gathering";
  String pnote = "@PNOTE@";
@TOP@
  for (int i = 0; i < @PKG@.AccPower.PW_ID.length; i++) {
    if (!@PKG@.AccPower.visible(i)) continue;
    String lock = @PKG@.AccPower.lockOf(u, i);
    boolean picked = i == pi;
    boolean on = @PKG@.AccPower.ON && !picked && lock == null;
    String pnm = @PKG@.AccPower.PW_NAME[i] + (picked ? " - PICKED" : (lock != null ? " - Combat " + @PKG@.AccPower.UNLOCK : ""));
    String psb = @PKG@.AccPower.statText(i, m);
    String ptc = picked ? "@GOLD@" : (lock != null ? "@DIM@" : "@NAME@");
    if (@PKG@.AccPower.PW_GRP[i] == 2) {
@ROW1@
    } else {
@ROW0@
    }
    if (on) ev.addEventBinding(@BT@.Activating, "#SkyyAccPw" + i + "Act", @EVD@.of("a", "pw:" + i));
  }
}""".replace("@TOP@", ind(PW_TOP)).replace("@ROW0@", ind(PW_ROW0, 6)).replace("@ROW1@", ind(PW_ROW1, 6)).replace("@PNOTE@", PNOTE) \
    .replace("@GOLD@", SUI.STATUS_INFO["gold"]).replace("@DIM@", SUI.COLOR["disabled"]).replace("@NAME@", SUI.COLOR["rowName"])
JM(page, POWER_SRC)
SUBS_JAVA = LF.join('@PKG@.HubBar.subTab(b, ev, "%s", %d, %s, this.mode == %d, "%s", %d);' % (ACC_PREFIX, _i, SUI.java_lit(_t), _i, SUB_ACT22[_i], SUI.SUB_TAB_W)
                    for _i, _t in enumerate(SUB_NAMES22))
BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  this.key = @PKG@.AccStore.pkey(u);   // 0.4.1
  if (this.mode < 0 || this.mode > 2) this.mode = 0;
  if (this.mode == 1 && !@PKG@.AccDefs.CRAFT) this.mode = 0;
  String[] s = @PKG@.AccStore.snapshot(u);
  String infoText = this.info != null && this.info.length() > 0 ? this.info : @PKG@.AccStore.campLine(s);
  this.cells = 0;   // 0.5.23: a CRAFT / POWER view has no grid - clearGrid() must never target #SkyyAccGrid there (client disconnect)
@SHELL@
@HUB@
@SUBS@
  if (this.mode == 1) buildCraft(b, ev, u, player);
  else if (this.mode == 2) buildPower(b, ev, u, s);
  else buildBag(b, ev, u, player, s);
@FOOT@
  ev.addEventBinding(@BT@.Activating, "#SkyyAccClose", @EVD@.of("a", "cl"));
}""".replace("@SHELL@", ind(VC.java("b"))).replace("@HUB@", "  " + VC_HUB_JAVA).replace("@SUBS@", ind(SUBS_JAVA)).replace("@FOOT@", ind(FOOT))
JM(page, BUILD_SRC)
assert BUILD_SRC.count("infoColor(this.info)") == 1 and "#SkyyAccSelAct" in BAG_SRC, "infoColor once"
# giveBack: 0 = back in the inventory, 1 = kept in a free bag slot, 2 = lost (logged with the player's uuid so an admin can give it back)
page.addMethod(CtNewMethod.make(f"""
public static int giveBack({PLA} p, java.util.UUID u, String k, String id) {{
  if (giveOne(p, id)) return 0;
  if ({PKG}.AccStore.stashK(u, k, id)) return 1;   // integration pass: the bag of the click's key k
  {PKG}.AccStore.warn("ITEM LOST - could not return " + id + " to player " + u + " (inventory and Void Charms full), give it back by hand");
  return 2;
}}""", page))
# THE CLICKS: the hub rows first (HubBar.route), Close, the sub-tabs, the filters, the grid selections, Unequip / Equip, Pick, Craft
JM(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.startsWith("hub:") && !a.equals("hub:accessories")) clearGrid();   // never leave a grid tooltip behind
    String hr = @PKG@.HubBar.route(this.playerRef, data, "@HUB@", "@TAB@");   // kit 1.7: row 1 (hub:h:<id>), row 2, the X (null = not a hub click)
    if (hr != null) {
      if (hr.equals("close")) { clearGrid(); close(); return; }
      if (hr.equals("self")) { this.mode = 0; this.info = ""; rebuild(); return; }
      if (!hr.equals("bridge") && !hr.equals("command") && !hr.equals("back") && isOpen()) { this.info = "that tab could not open right now - try again"; rebuild(); }   // 0.5.23: isOpen
      return;
    }
    java.util.UUID u = this.playerRef.getUuid();
    @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    if (a.equals("cl")) { clearGrid(); close(); return; }
    // the sub-tabs, filters and selections move nothing
    if (a.equals("tb:bag")) { this.mode = 0; this.info = ""; rebuild(); return; }
    if (a.equals("tb:craft")) { if (@PKG@.AccDefs.CRAFT) { this.mode = 1; this.info = ""; } else { this.mode = 0; this.info = "@CROFF@"; } rebuild(); return; }
    if (a.equals("tb:power")) { this.mode = 2; this.info = ""; rebuild(); return; }
    if (a.startsWith("fl:") && a.length() == 4 && a.charAt(3) >= '0' && a.charAt(3) <= '3') { this.filt = a.charAt(3) - '0'; this.info = ""; rebuild(); return; }
    int sx = @PKG@.AccCraft.subIndex(data);   // 0.5.21: a sub tab of the Craft view (moves nothing)
    if (sx >= 0) { this.craftSub = sx; this.info = ""; rebuild(); return; }
    if (a.equals("g") || a.equals("ig")) {
      int si = jsonInt(data, "SlotIndex");
      String[] ids = a.equals("g") ? this.bagIds : this.invIds;
      if (ids == null || si < 0 || si >= ids.length || ids[si] == null) return;   // an empty cell: nothing to do
      this.sel = (a.equals("g") ? "b:" : "i:") + ids[si];
      this.info = "selected " + @PKG@.AccDefs.pretty(ids[si]) + (a.equals("g") ? " - Unequip takes it out" : " - Equip puts it in Void Charms");
      rebuild(); return;
    }
    String k = @PKG@.AccStore.pkey(u);   // integration pass: ONE storage key for everything this click does (semantics rule 1)
    if (this.key != null && !this.key.equals(k)) {   // 0.4.1: profile switched since this page was drawn
      this.info = "your profile changed - these are the Void Charms of your current profile now";
      this.sel = "";
      rebuild(); return;
    }
    if (a.startsWith("pw:")) {   // 0.5.22: Pick a Power (free, the switch wait)
      int pi = -1;
      try { pi = Integer.parseInt(a.substring(3)); } catch (Throwable t0) { pi = -1; }
      if (pi < 0 || pi >= @PKG@.AccPower.PW_ID.length) return;
      this.info = @PKG@.AccPower.pick(u, k, @PKG@.AccPower.PW_ID[pi], System.currentTimeMillis(), true);
      rebuild(); return;
    }
    String blk = @PKG@.AccStore.moveBlock(u);   // integration pass: profile:busy / unknown profile state -> move nothing
    if (blk != null) { this.info = blk; rebuild(); return; }
    @PKG@.AccStore.slotsK(u, k);   // 0.5: load the bag first, so a file that cannot be read is known before anything moves
    if (@PKG@.AccStore.isBad(k)) { this.info = "your Void Charms file could not be read - nothing was moved, tell an admin (server log)"; rebuild(); return; }
    int cx = @PKG@.AccCraft.clickIndex(data);   // 0.5.18: a Craft button - the recipe id saved when the page was drawn (craft() checks it again)
    if (cx >= 0) {
      String rid = (this.craftIds != null && cx < this.craftIds.length) ? this.craftIds[cx] : null;
      this.info = rid == null ? "that recipe moved - the list is up to date now, try again" : @PKG@.AccCraft.craft(this.playerRef, ref, st, player, u, k, rid);
      rebuild(); return;
    }
    int sm = selMode(this.sel);
    String sid = sm == 0 ? null : this.sel.substring(2);
    if (a.equals("un")) {   // Unequip the selected accessory (the first slot that holds it)
      if (sm != 1) return;
      String[] cur = @PKG@.AccStore.snapshot(u);
      int idx = -1;
      for (int i = 0; i < cur.length && idx < 0; i++) if (sid.equals(cur[i])) idx = i;
      if (idx < 0) { this.sel = ""; this.info = "that accessory is not in Void Charms any more"; rebuild(); return; }
      String id = @PKG@.AccStore.unequipK(u, k, idx);
      if (id == null) { this.sel = ""; rebuild(); return; }
      String give = @PKG@.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id comes back as the current (upgradable) item
      if (!giveOne(player, give)) { @PKG@.AccStore.putK(u, k, idx, id); this.info = "your inventory is full"; }
      else { this.info = "unequipped " + @PKG@.AccDefs.pretty(give) + (give.equals(id) ? "" : " - your older copy came back as the current item"); this.sel = "i:" + give; }
      rebuild(); return;
    }
    if (a.equals("eq")) {   // Equip the selected inventory accessory
      if (sm != 2) return;
      String id = sid;
      java.util.ArrayList carriedNow = carried(player);
      if (!carriedNow.contains(id)) { this.sel = ""; this.info = "could not find " + @PKG@.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }
      if (@PKG@.AccDefs.isRetired(id)) {   // 0.4.2: retired - refused with the reason, nothing is moved
        this.info = @PKG@.AccDefs.retiredWhy(id);
        try { this.playerRef.sendMessage(@MSG@.raw("[Void Charms] " + @PKG@.AccDefs.retiredChat(id))); } catch (Throwable t2) { }
        rebuild(); return;
      }
      String put = @PKG@.AccDefs.modernOf(id);   // 0.4 / 0.5: an old id is stored as its current id
      String why = "Void Charms is full, or the same or a better " + @PKG@.AccDefs.lineLabel(id) + " is already in it";
      if (!@PKG@.AccStore.canEquipK(u, k, put)) { this.info = why; rebuild(); return; }
      if (!takeOne(player, id)) { this.info = "could not find " + @PKG@.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }
      String res = @PKG@.AccStore.equipK(u, k, put);
      if (res == null) {
        int g = giveBack(player, u, k, id);
        this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free slot" : "could not give " + @PKG@.AccDefs.pretty(id) + " back - inventory and Void Charms full, reported to the server log");
        rebuild(); return;
      }
      @PKG@.AccSnd.equipped(u, res);   // 0.5.14 sound pass: equipped ("") / upgraded in place (the old id)
      if (res.length() > 0) {
        res = @PKG@.AccDefs.modernOf(res);
        int g = giveBack(player, u, k, res);
        String old = @PKG@.AccDefs.pretty(res);
        this.info = "upgraded to " + @PKG@.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in Void Charms - inventory full" : old + " could not be returned - reported to the server log"));
      }
      else this.info = "equipped " + @PKG@.AccDefs.pretty(put) + (put.equals(id) ? "" : " - converted from an older copy");
      this.sel = "b:" + put;
      rebuild(); return;
    }
  } catch (Throwable t) {
    @PKG@.AccStore.warn("Void Charms page event failed: " + t);
    try { this.info = "that click failed - tell an admin (server log)"; rebuild(); } catch (Throwable t2) { }   // 0.5.18: every click is answered
  }
}""".replace("@HUB@", VC_HUB).replace("@TAB@", VC_TAB).replace("@CROFF@", ACC_CR_OFFTXT))

fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.AccPage(({PR}) o);
}}""", fac))

# ================= 0.5 admin give helpers (AccAdmin), the delivery task (AccGiveTask), acc:fn:give (AccGiveFn) =================
JM(adm, r"""
public static void msg(@PR@ pr, String t) {
  if (pr == null) return;
  try { pr.sendMessage(@MSG@.raw("[Void Charms] " + t)); } catch (Throwable e) { }
}""")
# the words after the sub-command word ("accessories give Skyy Skyy_Talisman_Speed_Epic 2" -> "Skyy Skyy_Talisman_Speed_Epic 2"; SkyyGear's rest)
JM(adm, r"""
public static String rest(@CTX@ ctx, String word) {
  String line = "";
  try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
  if (line == null) return "";
  String[] tk = line.trim().split("\\s+");
  StringBuilder sb = new StringBuilder();
  boolean seen = false;
  for (int i = 0; i < tk.length; i++) {
    if (!seen) { if (tk[i].equalsIgnoreCase(word) || tk[i].equalsIgnoreCase("/" + word)) seen = true; continue; }
    if (sb.length() > 0) sb.append(' ');
    sb.append(tk[i]);
  }
  return sb.toString().trim();
}""")
JM(adm, r"""
public static @PR@ findPlayer(String name) {
  if (name == null) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(name.trim())) return (@PR@) o;
    }
  } catch (Throwable t) { }
  return null;
}""")
JM(adm, r"""
public static int amountOf(String t) {
  try {
    int n = Integer.parseInt(t.trim());
    return n >= 1 && n <= 64 ? n : -1;
  } catch (Throwable e) { return -1; }
}""")
# which ids /accessories give takes: the booster table ids, the active bench accessories (up to their top tier), the Omni and the bag
# item; never an old (legacy) id or a retired accessory. null = fine, else the reason (no ids in it: admins see ids via /accessories lines)
JM(adm, r"""
public static String giveable(String id) {
  if (id == null || id.length() == 0) return "no item id given";
  if (@PKG@.AccDefs.isBoosterId(id)) return null;
  if (@PKG@.AccDefs.BAG.equals(id)) return "the old bag item is retired - accessories live in Void Charms now (/charms)";   // 0.5.22
  if (@PKG@.AccDefs.OMNI.equals(id)) return null;
  if (@PKG@.AccDefs.isLanternId(id)) return null;   // 0.5.4: the four Lantern rarities
  if (@PKG@.AccDefs.NV_ID.equals(id)) return @PKG@.AccDefs.NV_GIVE;   // 0.5.4: Night Vision is retired
  if (@PKG@.AccDefs.isLegacy(id)) return "that is an old id - give its current id instead (/charms lines shows them)";
  if (@PKG@.AccDefs.isRetired(id)) return "that accessory is retired and does nothing";
  String bn = @PKG@.AccDefs.benchOf(id);
  if (bn != null && !@PKG@.AccDefs.isTalisman(id)) {
    int t = @PKG@.AccDefs.tierOf(id);
    for (int i = 0; i < @PKG@.AccDefs.BENCH_IDS.length; i++) {
      if (@PKG@.AccDefs.BENCH_IDS[i].equals(bn) && t >= 1 && t <= @PKG@.AccDefs.BENCH_MAX[i] && id.equals("Skyy_Accessory_" + bn + "_T" + t)) return null;
    }
  }
  return "not an accessory of this mod - /charms lines lists the stat accessory ids";
}""")
gtk.addInterface(pool.get("java.lang.Runnable"))
JF(gtk, "public @PR@ admin;")
JF(gtk, "public @PR@ target;")
JF(gtk, "public String id;")
JF(gtk, "public int n;")
JF(gtk, "public boolean onWorld;")
JF(gtk, "public boolean queued;")
gtk.addConstructor(CtNewConstructor.make(JT("public AccGiveTask(@PR@ admin, @PR@ target, String id, int n) { this.admin = admin; this.target = target; this.id = id; this.n = n; this.onWorld = false; this.queued = false; }"), gtk))
# first run: hop to the TARGET player's world (any thread); second run, on that world thread: refuse while the profile loads, deliver,
# tell the admin (and the player), log one INFO line. admin == null = acc:fn:give called off the world thread. queued = true once
# world.execute accepted the second run (acc:fn:give then returns -1, part 2 review finding 2).
JM(gtk, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.AccAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.AccAdmin.msg(this.admin, "that player's world is not loaded - try again"); return; }
      this.onWorld = true;
      w.execute(this);
      this.queued = true;
      return;
    }
    String nm = this.target.getUsername();
    if (@PKG@.AccStore.moveBlock(this.target.getUuid()) != null) { @PKG@.AccAdmin.msg(this.admin, nm + "'s profile is loading - nothing was given, try again in a moment"); return; }
    int[] g = @PKG@.AccStore.deliver(this.target, this.id, this.n);
    if (g == null) { @PKG@.AccAdmin.msg(this.admin, "could not reach " + nm + "'s inventory - nothing was given, try again"); return; }
    String item = @PKG@.AccDefs.pretty(this.id);
    @PKG@.AccAdmin.msg(this.admin, "Gave " + g[0] + " x " + item + " to " + nm + (g[2] > 0 ? " (" + g[2] + " dropped at their feet - inventory full)" : ""));
    if (this.admin == null || !this.admin.getUuid().equals(this.target.getUuid())) @PKG@.AccAdmin.msg(this.target, "You got " + g[0] + " x " + item + (g[2] > 0 ? " (" + g[2] + " dropped at your feet - inventory full)" : ""));
    @PKG@.AccCfg.info("give: " + (this.admin == null ? "acc:fn:give" : this.admin.getUsername()) + " gave " + g[0] + " x " + this.id + " to " + nm + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
  } catch (Throwable t) {
    @PKG@.AccStore.warn("give failed: " + t);
    @PKG@.AccAdmin.msg(this.admin, "give failed - see the server log");
  }
}""")
JM(adm, r"""
public static void giveCmd(@PR@ pr, String rest, boolean byTier) {
  String[] tk = rest == null || rest.trim().length() == 0 ? new String[0] : rest.trim().split("\\s+");
  String id = null;
  int n = 1;
  if (!byTier) {
    if (tk.length < 2 || tk.length > 3) { msg(pr, "usage: /charms give <player> <item id> [amount 1-64]"); return; }
    id = tk[1];
    if (tk.length == 3) n = amountOf(tk[2]);
  } else {
    if (tk.length < 3 || tk.length > 4) { msg(pr, "usage: /charms givetier <player> <line> <rarity> [amount 1-64]"); return; }
    int li = @PKG@.AccDefs.lineOf(tk[1]);
    boolean lnl = li < 0 && @PKG@.AccDefs.isLanName(tk[1]);   // 0.5.4: the Lantern - its own line, Normal to Legendary
    if (li < 0 && !lnl && @PKG@.AccDefs.isNvName(tk[1])) { msg(pr, @PKG@.AccDefs.NV_GIVE); return; }   // 0.5.4: Night Vision is retired
    if (li < 0 && !lnl) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < @PKG@.AccDefs.LINE_ADMIN.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.AccDefs.LINE_ADMIN[i]); }
      sb.append(", ").append(@PKG@.AccDefs.LAN_ADMIN);   // 0.5.4
      msg(pr, "unknown line - use one of: " + sb.toString());
      return;
    }
    int t = @PKG@.AccDefs.rarityIndex(tk[2]);
    if (t < 1) { msg(pr, "unknown rarity - use Normal, Unique, Rare, Legendary or 1 to 4"); return; }
    id = lnl ? @PKG@.AccDefs.LAN_IDS[t - 1] : @PKG@.AccDefs.idOf(li, t);
    if (tk.length == 4) n = amountOf(tk[3]);
  }
  if (n < 1) { msg(pr, "the amount must be a whole number from 1 to 64"); return; }
  String why = giveable(id);
  if (why != null) { msg(pr, why); return; }
  @PR@ target = findPlayer(tk[0]);
  if (target == null) { msg(pr, "no online player called " + tk[0]); return; }
  new @PKG@.AccGiveTask(pr, target, id, n).run();
}""")
# acc:fn:give (spec 5.9) for the later loot pass: booster table ids only; on the player's world thread it delivers at once and returns how
# many were handed out (counted before and after); from any other thread it hops to that world and logs one line.
# THE RESULT (part 2 review finding 2 - the spec's "returns 0" off the thread made a retry-on-0 caller give twice):
#   n > 0 = given now (counted), 0 = NOTHING given and nothing queued (bad id / amount, player offline, profile loading, inventory not
#   reachable, the player's world not loaded), -1 = QUEUED: the give runs later on the player's world thread and its outcome is only
#   logged (it can still give nothing if the player leaves first). A caller must never retry on -1.
JM(adm, r"""
public static int giveFn(java.util.UUID u, String id, int n) {
  if (u == null || !(@PKG@.AccDefs.isBoosterId(id) || @PKG@.AccDefs.isLanternId(id)) || n < 1 || n > 64) return 0;   // 0.5.4: + the Lantern (Night Vision: retired)
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer(u); } catch (Throwable t) { pr = null; }
  if (pr == null || !pr.isValid()) return 0;
  @REF@ r = pr.getReference();
  @ST@ st = r == null ? null : r.getStore();
  if (st != null && st.isInThread()) {
    if (@PKG@.AccStore.moveBlock(u) != null) return 0;
    int[] g = @PKG@.AccStore.deliver(pr, id, n);
    if (g == null) return 0;
    @PKG@.AccCfg.info("give: acc:fn:give gave " + g[0] + " x " + id + " to " + pr.getUsername() + " (" + g[1] + " in the inventory, " + g[2] + " dropped)");
    return g[0];
  }
  @PKG@.AccGiveTask gt = new @PKG@.AccGiveTask(null, pr, id, n);
  gt.run();
  if (!gt.queued) { @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread and could not reach that world - nothing was given, the call returns 0"); return 0; }
  @PKG@.AccStore.warn("acc:fn:give was called off " + pr.getUsername() + "'s world thread - the give runs later on that thread and the call returns -1 (queued: do not retry)");
  return -1;
}""")
gfn.addInterface(pool.get("java.util.function.Function"))
gfn.addConstructor(CtNewConstructor.make("public AccGiveFn() { }", gfn))
JM(gfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Integer.valueOf(0);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String) || !(a[2] instanceof Number)) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.AccAdmin.giveFn((java.util.UUID) a[0], (String) a[1], ((Number) a[2]).intValue()));
  } catch (Throwable t) { @PKG@.AccStore.warn("acc:fn:give failed: " + t); return Integer.valueOf(0); }
}""")

# ================= 0.5 AccNotice: the one-time chat line (spec 5.1) =================
# Checked by the effect tick (world thread, the player is ready) once per player per session (ASKED, forgotten when they leave): a
# player with a bag file from before (bags/<uuid>.properties or bags/<uuid>-p<N>.properties) gets MIG_NOTICE once, ever (unless
# notice.boosters is off: then nothing is looked at or recorded - no directory scan - so switching it on later still tells them); a
# player without one is recorded as new and never gets it. Seen players live in
# Skyy_SkyyAccessories/notices.properties, saved by AccTick (never the world thread), tmp + fsync + move. An unreadable file is left
# alone and the notice is remembered for this session only.
JF(note, "public static java.nio.file.Path FILE;")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static final java.util.concurrent.ConcurrentHashMap ASKED = new java.util.concurrent.ConcurrentHashMap();")
JF(note, "public static volatile boolean DIRTY = false;")
JF(note, "public static boolean BROKEN = false;")
JF(note, "public static boolean SAVEWARNED = false;")
note.addField(CtField.make("public static final String TEXT = %s;" % jlit(MIG_NOTICE), note))
JM(note, r"""
public static void load() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); SEEN.put(k, p.getProperty(k)); }
  } catch (Throwable t) {
    BROKEN = true;
    @PKG@.AccStore.warn("could not read " + FILE + " - the 0.5 notice is remembered for this session only (the file is left untouched): " + t);
  }
}""")
JM(note, r"""
public static boolean hasOldBag(java.util.UUID u) {
  try {
    java.nio.file.Path d = @PKG@.AccStore.DIR;
    if (d == null || !java.nio.file.Files.exists(d, new java.nio.file.LinkOption[0])) return false;
    if (java.nio.file.Files.exists(d.resolve(u.toString() + ".properties"), new java.nio.file.LinkOption[0])) return true;
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d, u.toString() + "-p*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        String nm = String.valueOf(((java.nio.file.Path) it.next()).getFileName());
        if (!nm.endsWith(".more.properties")) return true;
      }
    } finally { ds.close(); }
  } catch (Throwable t) { }
  return false;
}""")
JM(note, r"""
public static void check(@PR@ pr, java.util.UUID u) {
  if (u == null || pr == null) return;
  String us = u.toString();
  if (SEEN.containsKey(us) || ASKED.containsKey(u)) return;
  if (!@PKG@.AccDefs.NOTICE) return;   // part 1 review finding 3: switched off = nothing looked at or remembered, so switching it on still tells them
  ASKED.put(u, Boolean.TRUE);          // (forgotten when the player leaves: AccTick)
  if (!hasOldBag(u)) { SEEN.put(us, "new"); if (!BROKEN) DIRTY = true; return; }
  SEEN.put(us, "boosters-0.5");
  if (!BROKEN) DIRTY = true;
  pr.sendMessage(@MSG@.raw(TEXT).color("@INFOCOL@"));
}""".replace("@INFOCOL@", SUI.STATUS["="]))
JM(note, r"""
public static synchronized void save() {
  if (!DIRTY || BROKEN || FILE == null) return;
  DIRTY = false;
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = SEEN.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty((String) e.getKey(), String.valueOf(e.getValue())); }
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyAccessories one-time notices per player (uuid=boosters-0.5 told / new = joined without accessories)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) {
    DIRTY = true;
    if (!SAVEWARNED) { SAVEWARNED = true; @PKG@.AccStore.warn("could not save " + FILE + " (retried by the next save): " + t); }
  }
}""")

# ================= 0.5 AccRestampTask: the quality restamp on one player's world thread (dispatched by AccTick every 5 s) =================
rtk.addInterface(pool.get("java.lang.Runnable"))
JF(rtk, "public @PR@ pr;")
JF(rtk, "public java.util.UUID expectedWorld;")
JF(rtk, "public static boolean FAILED = false;")
JF(rtk, "public static volatile long STAMPED = 0L;")
rtk.addConstructor(CtNewConstructor.make(JT("public AccRestampTask(@PR@ pr, java.util.UUID w) { this.pr = pr; this.expectedWorld = w; }"), rtk))
JM(rtk, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID nowWorld = this.pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    if (@PKG@.AccStore.moveBlock(this.pr.getUuid()) != null) return;   // the live inventory may not be the active profile's yet
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    int n = @PKG@.AccStore.restamp(p.getInventory());
    if (n > 0) {   // part 1 review note: admins can see that the restamp ran (one line per player per restamp that changed stacks)
      STAMPED = STAMPED + (long) n;
      @PKG@.AccCfg.info("restamp: " + n + " accessory stack(s) of " + this.pr.getUsername() + " moved to the 0.5 rarity look (" + STAMPED + " since the start)");
    }
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("accessory rarity restamp failed (logged once): " + t); }
  }
}""")

# ================= /accessories reload (0.4.4, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) - otherwise
# the engine copies skyyaccessories.admin into /accessories' hytale:Adventurer group (the SkyyIslands 0.5 leak; lint perm_group_leaks).
# The kit's reload op re-checks the node too (denied), reads the file on this thread and the save task runs AccCfg.reload.
rcmd.addConstructor(CtNewConstructor.make("""
public AccReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyAccessories/config.properties after hand edits");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
}""", rcmd))
rcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "reload", pr.getUuid(), pr.getUsername(), "command" }});
    String m = "could not reload - see the server log";
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) m = String.valueOf(((Object[]) o)[2]);
    pr.sendMessage({MSG}.raw("[Void Charms] " + m));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/charms reload failed: " + t);
    pr.sendMessage({MSG}.raw("[Void Charms] could not reload - see the server log"));
  }}
}}""", rcmd))

# ================= /accessories lines (0.5, every player) =================
lcmd.addConstructor(CtNewConstructor.make("""
public AccLinesCmd() {
  super("lines", "Show every accessory line, its rarities and this server's numbers");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", lcmd))
JM(lcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    boolean admin = false;
    try { admin = pr.hasPermission("skyyaccessories.admin"); } catch (Throwable t0) { admin = false; }
    pr.sendMessage(@MSG@.raw("[Void Charms] Accessory lines on this server - only your best accessory of each line counts, and every line stops at Legendary:"));
    String[] ls = @PKG@.AccDefs.linesText(admin);
    for (int i = 0; i < ls.length; i++) pr.sendMessage(@MSG@.raw("  " + ls[i]));
  } catch (Throwable t) {
    @PKG@.AccStore.warn("/charms lines failed: " + t);
    pr.sendMessage(@MSG@.raw("[Void Charms] could not list the lines - see the server log"));
  }
}""")
# ================= /accessories give | givetier (0.5, server admins only) =================
# COMMAND RULES: an admin sub-command under a player command needs requirePermission AND setPermissionGroups(new String[0]) (lint
# perm_group_leaks). The arguments are read from the raw command text (setAllowsExtraArguments, SkyyGear's /gear give way), so there is
# no usage variant and [amount] is simply an optional last word.
gcmd.addConstructor(CtNewConstructor.make("""
public AccGiveCmd() {
  super("give", "(admin) Give an accessory: /charms give <player> <item id> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", gcmd))
JM(gcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "give"), false); }
  catch (Throwable t) { @PKG@.AccStore.warn("/charms give failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")
tcmd.addConstructor(CtNewConstructor.make("""
public AccGiveTierCmd() {
  super("givetier", "(admin) Give by line and rarity: /charms givetier <player> <line> <rarity> [amount]");
  requirePermission("skyyaccessories.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""", tcmd))
JM(tcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.AccAdmin.giveCmd(pr, @PKG@.AccAdmin.rest(ctx, "givetier"), true); }
  catch (Throwable t) { @PKG@.AccStore.warn("/charms givetier failed: " + t); @PKG@.AccAdmin.msg(pr, "give failed - see the server log"); }
}""")

# ================= 0.5.22 /charms (aliases /charm, /ch): Void Charms (Skyy 2026-10-16 "/charm /charms and /ch drop the accessory commands"; HANDOFF
# section 3 rule 3: replaced, not added - /accessories, /acc and /accbag are gone; the lifelong bag item of 0.5.20 is retired, AccOnce* with it)
# /charms power [name]: no name = your Accessory Power, your Power and the list; a name = pick it (the switch wait applies)
apc_.addConstructor(CtNewConstructor.make("""
public AccPowerCmd() {
  super("power", "Your Accessory Power and Power, or pick one: /charms power <name>");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  setAllowsExtraArguments(true);
}""", apc_))
JM(apc_, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.UUID u = pr.getUuid();
    String k = @PKG@.AccStore.pkey(u);
    String w = @PKG@.AccAdmin.rest(ctx, "power");
    if (w.length() > 0) { @PKG@.AccAdmin.msg(pr, @PKG@.AccPower.pick(u, k, w, System.currentTimeMillis(), true)); return; }
    String[] s = @PKG@.AccStore.snapshot(u);
    int ap = @PKG@.AccPower.apOf(s);
    double m = @PKG@.AccPower.mult(ap);
    int i = @PKG@.AccPower.effIndex(u, k);
    @PKG@.AccAdmin.msg(pr, "Accessory Power " + ap + " (x" + @PKG@.AccPower.multText(m) + ") - your Power: " + @PKG@.AccPower.nameOf(i) + (i >= 0 ? " (" + @PKG@.AccPower.statText(i, m) + ")" : "") + (@PKG@.AccPower.ON ? "" : " - Powers are switched off on this server"));
    @PKG@.AccAdmin.msg(pr, @PKG@.AccPower.listText(u) + ". Pick one: /charms power <name> (or Void Charms > Power).");
  } catch (Throwable t) {
    @PKG@.AccStore.warn("/charms power failed: " + t);
    @PKG@.AccAdmin.msg(pr, "could not read your Power - see the server log");
  }
}""")
cmd.addConstructor(CtNewConstructor.make("""
public AccCmd() {
  super("charms", "Open Void Charms: your accessories, their crafting and your Accessory Power");
  addAliases(new String[] { "charm", "ch" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
  addSubCommand(new com.skyy.accessories.AccReloadCmd());   // 0.4.4: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccLinesCmd());    // 0.5: every player (its own hytale:Adventurer group)
  addSubCommand(new com.skyy.accessories.AccPowerCmd());    // 0.5.22: every player (its own hytale:Adventurer group)
  addSubCommand(new com.skyy.accessories.AccGiveCmd());     // 0.5: server admins only (its own groups are cleared)
  addSubCommand(new com.skyy.accessories.AccGiveTierCmd()); // 0.5: server admins only (its own groups are cleared)
}""", cmd))
JM(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.AccPage(pr));
  } catch (Throwable t) {
    @PKG@.AccStore.warn("/charms failed: " + t);
    pr.sendMessage(@MSG@.raw("[Void Charms] could not open Void Charms"));
  }
}""")
# the Character hub's Void Charms tab (HUBS-CONTRACT 1-2): apply(UUID) on the player's world thread (a hub click is the caller) opens the page;
# FALSE -> the bar runs /charms as the player
aho_.addInterface(pool.get("java.util.function.Function"))
aho_.addConstructor(CtNewConstructor.make("public AccHubOpen() { }", aho_))
JF(aho_, "public static volatile long OPENED = 0L;")
JM(aho_, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    if (st == null) return Boolean.FALSE;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    p.getPageManager().openCustomPage(r, st, new @PKG@.AccPage(pr));
    OPENED = OPENED + 1L;
    return Boolean.TRUE;
  } catch (Throwable t) {
    @PKG@.AccStore.warn("the Void Charms hub tab could not open: " + t);
    return Boolean.FALSE;
  }
}""")
JM(aho_, r"""
public static String register() {
  try {
    if (@PKG@.HubBar.put("@HUB@", "@TAB@", "SkyyAccessories", "@LAB@", @ORD@, "@CMD@", new @PKG@.AccHubOpen(), null) != null) return "@HUB@:@TAB@";
  } catch (Throwable t) { @PKG@.AccStore.warn("the Void Charms hub tab could not be registered: " + t); }
  return "off";
}""".replace("@HUB@", VC_HUB).replace("@TAB@", VC_TAB).replace("@LAB@", VC_LABEL).replace("@ORD@", str(VC_ORDER)).replace("@CMD@", VC_CMD))
JM(aho_, r"""
public static int unregister() {
  try { return @PKG@.HubBar.removeAll(); } catch (Throwable t) { return 0; }
}""")

# ================= 0.5.4 THE LANTERN (tools/acc_0_5_4_patch.py): AccLanternMark (the helper's marker component) + its Supplier, AccLantern
# (state + logic; the systems AccLanternSys / AccLanternHelp / AccLanternHide only read the engine components and call it) =================
# AccLanternMark: our marker on every helper entity = its owner's uuid. Registered without a codec (ComponentRegistryProxy.registerComponent
# (Class, Supplier)), on an entity that is NonSerialized anyway: never saved. AccLanternHelp ticks every entity that carries it.
lmk.addInterface(pool.get(COMP))
JF(lmk, "public java.util.UUID owner;")
JF(lmk, "public int slot;")   # 0.5.5: 0 = the light above the wearer, 1..8 = a ring light (AccLantern.RING[slot - 1])
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark() { this.owner = null; this.slot = 0; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u) { this.owner = u; this.slot = 0; }", lmk))
lmk.addConstructor(CtNewConstructor.make("public AccLanternMark(java.util.UUID u, int s) { this.owner = u; this.slot = s; }", lmk))
JM(lmk, LANJ(r"""
public com.hypixel.hytale.component.Component clone() {
  return new @PKG@.AccLanternMark(this.owner, this.slot);
}"""))
lms.addInterface(pool.get("java.util.function.Supplier"))
lms.addConstructor(CtNewConstructor.make("public AccLanternMarkSup() { }", lms))
JM(lms, r"""
public Object get() {
  return new @PKG@.AccLanternMark();
}""")
# AccLantern. Component types are bound ONCE in setup() (bind(); T_MARK from registerComponent) and never looked up per tick - so the
# harness runs this exact code on its own engine ComponentRegistry / Store with its own types (section Q).
# State (all uuid keys, world threads write their own players, AccTick prunes players who left, shutdown clears): CLK float[]{seconds
# since the last decision}; WANT int[]{rarity, glow key (0 = none), helper height, helper level, dead 0/1, table epoch} (absent = nothing
# wanted); HELPER the helper's Ref (pending until its CommandBuffer runs); HSTATE int[]{ticks since spawn, seen valid, light key on it};
# OWNER the player's current entity Ref (AccLanternHelp keeps a helper only while this is valid, in the helper's own store, and the helper
# is the recorded one); HY long[]{cx, cz, feet section, target section, chosen section, ticks} the section check; SPAWNT long[]{last
# spawn ms, spawns in the window, window start ms} the spawn limit.
for _f in ("T_PR", "T_TC", "T_DL", "T_NID", "T_INT", "T_DES", "T_DEATH", "T_MARK", "T_EV"):   # T_EV: the EntityViewer (fix round)
    JF(lan, LANJ("public static volatile @CTY@ %s;" % _f))
JF(lan, LANJ("public static volatile @RTY@ R_TIME;"))
# 0.5.5 THE RING: RING Object[RING_MAX] {the ring lights' Refs by slot - 1}; RSTATE int[RING_MAX x 3] {ticks since spawn, seen valid,
# light key} per slot; RSEC long[RING_MAX x 5] {cx, cy, cz, ok, ticks} the per-slot section check; RSPAWNT the ring's spawn limit (one
# batch a second). WANT gains [6] ring lights and [7] the ring radius in half blocks.
for _f in ("CLK", "WANT", "HELPER", "HSTATE", "OWNER", "HY", "SPAWNT", "RING", "RSTATE", "RSEC", "RSPAWNT"):
    JF(lan, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
# HIDDEN: helpers taken out of other viewers' visible sets (AccLanternHide); CLAMPED: helpers held inside the wearer's view radius
for _f in ("GLOW_ON", "GLOW_SET", "GLOW_OFF", "FOREIGN", "SPAWNS", "HREMOVES", "ORPHANS", "MOVES", "GONE", "LIMITED", "RELIT", "HIDDEN",
           "CLAMPED", "RCLAMPED", "RSKIPPED"):   # 0.5.5: RCLAMPED ring outside the view radius, RSKIPPED a slot in a bad section
    JF(lan, "public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f)
JF(lan, "public static boolean LIMIT_WARNED = false;")
JF(lan, "public static boolean RLIMIT_WARNED = false;")
lan.addField(CtField.make("public static final int RING_MAX = %d;" % LAN_RING_MAX, lan))
lan.addField(CtField.make("public static final double TOP_Y = %r;" % LAN_TOP, lan))
lan.addField(CtField.make("public static final double BOTTOM_Y = %r;" % LAN_BOTTOM, lan))
lan.addField(CtField.make("public static final float DESPAWN_S = %rf;" % LAN_DESPAWN, lan))
lan.addField(CtField.make("public static final int SECTIONS = 10;", lan))
JM(lan, LANJ(r"""
public static void bind() {
  T_PR = @PR@.getComponentType();
  T_TC = @TCO@.getComponentType();
  T_DL = @DLC@.getComponentType();
  T_NID = @NID@.getComponentType();
  T_INT = @INT@.getComponentType();
  T_DES = @DES@.getComponentType();
  T_DEATH = @DTH@.getComponentType();
  T_EV = @EVW@.getComponentType();
  R_TIME = @TMR@.getResourceType();
}"""))
JM(lan, r"""
public static float[] clk(java.util.UUID u) {
  float[] c = (float[]) CLK.get(u);
  if (c == null) { c = new float[] { 1.0f }; CLK.put(u, c); }
  return c;
}""")
JM(lan, r"""
public static int[] hstate(java.util.UUID u) {
  int[] h = (int[]) HSTATE.get(u);
  if (h == null) { h = new int[] { 0, 0, 0 }; HSTATE.put(u, h); }
  return h;
}""")
# the world of an entity store (null for a store that is not a world's - the harness's own stores: no section checks there)
JM(lan, LANJ(r"""
public static @WLD@ worldOf(@ST@ store) {
  if (store == null) return null;
  Object e = store.getExternalData();
  if (e instanceof @ESR@) return ((@ESR@) e).getWorld();
  return null;
}"""))
JM(lan, LANJ(r"""
public static int netId(@ST@ store) {
  Object e = store.getExternalData();
  if (e instanceof @ESR@) return ((@ESR@) e).takeNextNetworkId();
  return 0;
}"""))
# a section the helper may go into: loaded (the ChunkStore has its ref) AND ticking (no NonTicking component) - UpdateLocationSystems
# removes an entity moved into a missing section and parks one moved into a non-ticking section
JM(lan, LANJ(r"""
public static boolean sectionOk(@WLD@ w, int cx, int cy, int cz) {
  if (cy < 0 || cy >= SECTIONS) return false;
  if (w == null) return true;
  @CSR@ cs = w.getChunkStore();
  if (cs == null) return false;
  @REF@ sec = cs.getChunkSectionReference(cx, cy, cz);
  if (sec == null || !sec.isValid()) return false;
  @ST@ ss = cs.getStore();
  if (ss == null) return false;
  @ARC@ a = ss.getArchetype(sec);
  return a != null && !a.contains(ss.getRegistry().getNonTickingComponentType());
}"""))
# the ok sections from the feet section up to the target section, one bit each (the feet section always counts: the player is in it)
JM(lan, LANJ(r"""
public static long sectionMask(@WLD@ w, int cx, int cz, int sy0, int syt) {
  long m = 0L;
  if (sy0 >= 0 && sy0 < 64) m = m | (1L << sy0);
  for (int sy = sy0 + 1; sy <= syt && sy < 64; sy++) if (sectionOk(w, cx, sy, cz)) m = m | (1L << sy);
  return m;
}"""))
# the highest ok section from syt down to sy0 (pure; the harness feeds it masks)
JM(lan, r"""
public static int walk(int sy0, int syt, long mask) {
  for (int sy = syt; sy > sy0; sy--) if (sy >= 0 && sy < 64 && ((mask >> sy) & 1L) != 0L) return sy;
  return sy0;
}""")
# where the helper goes: want blocks above the feet, inside the world (y 1 .. 318), inside the highest ok section; -1 = no room (< 5).
# Room is compared with the LAN_EPS margin: (feet + want) - feet is not always want in doubles (review finding 4)
JM(lan, LANJ(r"""
public static double pickY(java.util.UUID u, @WLD@ w, double x, double feet, double z, int want) {
  double top = feet + (double) want;
  if (top > TOP_Y) top = TOP_Y;
  if (top < BOTTOM_Y || top - feet < (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS) return -1.0;
  if (w == null) return top;
  int cx = ((int) Math.floor(x)) >> 5;
  int cz = ((int) Math.floor(z)) >> 5;
  int sy0 = ((int) Math.floor(feet)) >> 5;
  int syt = ((int) Math.floor(top)) >> 5;
  if (sy0 < 0) sy0 = 0;
  if (syt > SECTIONS - 1) syt = SECTIONS - 1;
  long[] c = (long[]) HY.get(u);
  int sy;
  if (c != null && c[0] == (long) cx && c[1] == (long) cz && c[2] == (long) sy0 && c[3] == (long) syt && c[5] < 20L) {
    sy = (int) c[4];
    c[5] = c[5] + 1L;
  } else {
    sy = walk(sy0, syt, sectionMask(w, cx, cz, sy0, syt));
    HY.put(u, new long[] { (long) cx, (long) cz, (long) sy0, (long) syt, (long) sy, 0L });
  }
  double lim = (double) (sy * 32) + 31.5;
  double y = top < lim ? top : lim;
  if (y - feet < (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS) return -1.0;
  return y;
}"""))
# at most one spawn per second per wearer; more than 20 in a minute (something keeps removing it) -> one WARN, then one per 10 s
JM(lan, r"""
public static boolean maySpawn(java.util.UUID u, long now) {
  long[] st = (long[]) SPAWNT.get(u);
  if (st == null) { st = new long[] { 0L, 0L, now }; SPAWNT.put(u, st); }
  if (now - st[2] > 60000L) { st[1] = 0L; st[2] = now; }
  long gap = st[1] >= 20L ? 10000L : 1000L;
  if (st[0] != 0L && now - st[0] < gap) { LIMITED.incrementAndGet(); return false; }
  st[0] = now;
  st[1] = st[1] + 1L;
  if (st[1] == 21L && !LIMIT_WARNED) { LIMIT_WARNED = true; @PKG@.AccStore.warn("Lantern: a helper light had to be placed again more than 20 times in a minute for " + u + " - something keeps removing it; trying every 10 s now (logged once)"); }
  return true;
}""")
# THE HELPER: the vanilla ambient-emitter entity (Transform + NetworkId + Intangible + NonSerialized) + its light + a 5 s dead-man
# DespawnComponent + our marker, added through the CommandBuffer (the Ref comes back pending: valid once the buffer ran)
JM(lan, LANJ(r"""
public static @REF@ spawnS(java.util.UUID u, int slot, @ST@ store, @CB@ cb, double x, double y, double z, int key) {
  @CRG@ reg = store.getRegistry();
  @HLD@ h = reg.newHolder();
  @TCO@ tc = new @TCO@();
  tc.setPosition(new @V3D@(x, y, z));
  h.addComponent(T_TC, tc);
  h.addComponent(T_DL, new @DLC@(@PKG@.AccDefs.lanColor(key)));
  h.addComponent(T_NID, new @NID@(netId(store)));
  h.ensureComponent(T_INT);
  h.addComponent(reg.getNonSerializedComponentType(), @NSR@.get());
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  if (tr != null) h.addComponent(T_DES, @DES@.despawnInSeconds(tr, DESPAWN_S));
  h.addComponent(T_MARK, new @PKG@.AccLanternMark(u, slot));
  SPAWNS.incrementAndGet();
  return cb.addEntity(h, @ARS@.SPAWN);
}"""))
JM(lan, LANJ(r"""
public static @REF@ spawn(java.util.UUID u, @ST@ store, @CB@ cb, double x, double y, double z, int key) {
  return spawnS(u, 0, store, cb, x, y, z, key);
}"""))
# the helper goes: removed only from its OWN store (a helper left in another world is removed by that world's AccLanternHelp)
JM(lan, LANJ(r"""
public static int drop(java.util.UUID u, @ST@ store, @CB@ cb) {
  Object o = HELPER.remove(u);
  HSTATE.remove(u);
  HY.remove(u);
  if (o instanceof @REF@) {
    @REF@ r = (@REF@) o;
    if (r.getStore() == store && r.isValid()) {
      cb.tryRemoveEntity(r, @RRS@.REMOVE);
      HREMOVES.incrementAndGet();
      return 128;
    }
  }
  return 0;
}"""))
# THE GLOW on the player: want = our light key (0 = none). Ours is recognised by its mark (AccDefs.lanOurs); another light is never
# changed or removed (16), ours comes back once it is gone. 2 added, 4 changed (a new setting), 8 removed.
JM(lan, LANJ(r"""
public static int glow(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int want) {
  if (T_DL == null) return 0;
  @DLC@ dl = (@DLC@) store.getComponent(ref, T_DL);
  if (want == 0) {
    if (dl == null || !@PKG@.AccDefs.lanOurs(dl.getColorLight())) return 0;
    cb.tryRemoveComponent(ref, T_DL);
    GLOW_OFF.incrementAndGet();
    return 8;
  }
  if (dl == null) {
    cb.addComponent(ref, T_DL, new @DLC@(@PKG@.AccDefs.lanColor(want)));
    GLOW_ON.incrementAndGet();
    return 2;
  }
  if (!@PKG@.AccDefs.lanOurs(dl.getColorLight())) { FOREIGN.incrementAndGet(); return 16; }
  if (@PKG@.AccDefs.lanKeyOf(dl.getColorLight()) == want) return 0;
  dl.setColorLight(@PKG@.AccDefs.lanColor(want));
  GLOW_SET.incrementAndGet();
  return 4;
}"""))
# THE REACH: w = WANT (null = none). Every tick: the helper above the player (pickY; never farther up than the wearer's own view radius - 4,
# CollectVisible's radius - so a player with a short view distance still gets it), its WHITE light capped for the height it really got,
# placed when missing (32), moved (64) when it is more than height / 50 blocks (0.1 - 1.5) off its spot or at all BELOW it (closer to the
# wearer = brighter), its light changed (256), its dead-man timer refreshed; removed (128) when not wanted or there is no room; 1024 = a
# spawn waits (the limit). A helper left in another store is forgotten here (its world removes it).
JM(lan, LANJ(r"""
public static int helper(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int[] w) {
  Object hro = HELPER.get(u);
  @REF@ hr = null;
  if (hro instanceof @REF@) hr = (@REF@) hro;
  if (w == null || w[2] <= 0 || w[3] <= 0) return hr == null ? 0 : drop(u, store, cb);
  @TCO@ tc = null;
  if (T_TC != null) tc = (@TCO@) store.getComponent(ref, T_TC);
  if (tc == null) return 0;
  @V3D@ p = tc.getPosition();
  double x = p.x();
  double feet = p.y();
  double z = p.z();
  int want = w[2];
  if (T_EV != null) {
    @EVW@ ev = (@EVW@) store.getComponent(ref, T_EV);
    if (ev != null) {
      int vr = ev.viewRadiusBlocks - @PKG@.AccDefs.LAN_VIEW_MARGIN;
      if (vr < want) { want = vr; CLAMPED.incrementAndGet(); }
    }
  }
  double y = pickY(u, worldOf(store), x, feet, z, want);
  if (y < 0.0) return hr == null ? 0 : drop(u, store, cb);
  int lvl = w[3];
  int hgt = (int) Math.floor(y - feet + @PKG@.AccDefs.LAN_EPS);
  if (hgt < w[2]) {
    int m = @PKG@.AccDefs.lanMaxLevel((double) hgt - @PKG@.AccDefs.LAN_PZ, @PKG@.AccDefs.lanCap(w[0]));
    if (m < lvl) lvl = m;
  }
  if (lvl <= 0) return hr == null ? 0 : drop(u, store, cb);
  int key = @PKG@.AccDefs.lanHKey(lvl);
  int[] hs = hstate(u);
  if (hr != null && hr.getStore() != store) { HELPER.remove(u); hr = null; }
  if (hr != null && !hr.isValid()) {
    if (hs[1] != 0 || hs[0] > 30) { HELPER.remove(u); hr = null; GONE.incrementAndGet(); }
    else { hs[0] = hs[0] + 1; return 0; }
  }
  if (hr == null) {
    if (!maySpawn(u, System.currentTimeMillis())) return 1024;
    hr = spawn(u, store, cb, x, y, z, key);
    HELPER.put(u, hr);
    hs[0] = 0;
    hs[1] = 0;
    hs[2] = key;
    return 32;
  }
  hs[1] = 1;
  hs[0] = hs[0] + 1;
  int code = 0;
  @TCO@ htc = (@TCO@) cb.getComponent(hr, T_TC);
  if (htc != null) {
    @V3D@ hp = htc.getPosition();
    double dx = hp.x() - x;
    double dy = hp.y() - y;
    double dz = hp.z() - z;
    double th = (double) hgt / @PKG@.AccDefs.LAN_MOVE_DIV;
    if (th < @PKG@.AccDefs.LAN_MOVE_MIN) th = @PKG@.AccDefs.LAN_MOVE_MIN;
    if (th > @PKG@.AccDefs.LAN_MOVE_MAX) th = @PKG@.AccDefs.LAN_MOVE_MAX;
    if (dy < -0.02 || dx * dx + dy * dy + dz * dz > th * th) { htc.setPosition(new @V3D@(x, y, z)); MOVES.incrementAndGet(); code = code | 64; }
  }
  if (hs[2] != key) {
    @DLC@ hdl = (@DLC@) cb.getComponent(hr, T_DL);
    if (hdl != null) { hdl.setColorLight(@PKG@.AccDefs.lanColor(key)); hs[2] = key; RELIT.incrementAndGet(); code = code | 256; }
  }
  @DES@ dc = null;
  if (T_DES != null) dc = (@DES@) cb.getComponent(hr, T_DES);
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  if (dc != null && tr != null) dc.setDespawnTo(tr.getNow(), DESPAWN_S);
  return code;
}"""))
# 0.5.5 THE RING. One ring light goes: removed only from its OWN store (a ring light left in another world is removed by that world's
# AccLanternHelp: the slot no longer records it); 128 when one was removed
JM(lan, LANJ(r"""
public static int dropOne(@REF@ r, @ST@ store, @CB@ cb) {
  if (r == null || r.getStore() != store || !r.isValid()) return 0;
  cb.tryRemoveEntity(r, @RRS@.REMOVE);
  HREMOVES.incrementAndGet();
  return 128;
}"""))
# the whole ring goes (not wanted, no room, death, swap to a rarity with one light, switch off) and its state is forgotten
JM(lan, LANJ(r"""
public static int ringDrop(java.util.UUID u, @ST@ store, @CB@ cb) {
  Object o = RING.remove(u);
  RSTATE.remove(u);
  RSEC.remove(u);
  int code = 0;
  if (o instanceof Object[]) {
    Object[] rs = (Object[]) o;
    for (int k = 0; k < rs.length; k++) if (rs[k] instanceof @REF@) code = code | dropOne((@REF@) rs[k], store, cb);
  }
  return code;
}"""))
JM(lan, r"""
public static int[] rstate(java.util.UUID u) {
  int[] h = (int[]) RSTATE.get(u);
  if (h == null) { h = new int[RING_MAX * 3]; RSTATE.put(u, h); }
  return h;
}""")
# one slot's section: loaded AND ticking (sectionOk), re-checked when the slot's section changes or every 20 ticks; a store that is not a
# world's (w null: the harness's own stores) is always fine
JM(lan, LANJ(r"""
public static boolean ringSectionOk(java.util.UUID u, int k, @WLD@ w, double x, double y, double z) {
  if (w == null) return true;
  long cx = (long) (((int) Math.floor(x)) >> 5);
  long cy = (long) (((int) Math.floor(y)) >> 5);
  long cz = (long) (((int) Math.floor(z)) >> 5);
  long[] c = (long[]) RSEC.get(u);
  if (c == null) {
    c = new long[RING_MAX * 5];
    for (int i = 0; i < RING_MAX; i++) c[i * 5 + 4] = 99L;
    RSEC.put(u, c);
  }
  int b = k * 5;
  if (c[b] == cx && c[b + 1] == cy && c[b + 2] == cz && c[b + 4] < 20L) {
    c[b + 4] = c[b + 4] + 1L;
    return c[b + 3] != 0L;
  }
  boolean ok = sectionOk(w, (int) cx, (int) cy, (int) cz);
  c[b] = cx;
  c[b + 1] = cy;
  c[b + 2] = cz;
  c[b + 3] = ok ? 1L : 0L;
  c[b + 4] = 0L;
  return ok;
}"""))
# the ring's spawn limit: the missing lights of a wearer are spawned TOGETHER, at most one batch a second; more than 20 batches in a minute
# (something keeps removing them) -> one WARN, then one batch per 10 s
JM(lan, r"""
public static boolean maySpawnRing(java.util.UUID u, long now) {
  long[] st = (long[]) RSPAWNT.get(u);
  if (st == null) { st = new long[] { 0L, 0L, now }; RSPAWNT.put(u, st); }
  if (now - st[2] > 60000L) { st[1] = 0L; st[2] = now; }
  long gap = st[1] >= 20L ? 10000L : 1000L;
  if (st[0] != 0L && now - st[0] < gap) { LIMITED.incrementAndGet(); return false; }
  st[0] = now;
  st[1] = st[1] + 1L;
  if (st[1] == 21L && !RLIMIT_WARNED) { RLIMIT_WARNED = true; @PKG@.AccStore.warn("Lantern: the ring lights had to be placed again more than 20 times in a minute for " + u + " - something keeps removing them; trying every 10 s now (logged once)"); }
  return true;
}""")
# THE RING (every tick next to helper()): w[6] = M lights at w[7] / 2 blocks around the wearer, at the light-above height w[2] with its
# level w[3] (lowered for the height it really got: the world top), angle 2 pi k / M. A slot outside the wearer's view radius - 4 (3-D) or
# in a section that is not loaded + ticking has no light. Placed (32), moved (64) when more than its distance / 50 blocks (0.1 - 1.5) off
# its spot or at all BELOW it, relit (256), the dead-man refreshed; removed (128) past M or when not wanted; 1024 = a spawn waits.
JM(lan, LANJ(r"""
public static int ring(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, int[] w) {
  Object ro = RING.get(u);
  Object[] rs = null;
  if (ro instanceof Object[]) rs = (Object[]) ro;
  int m = 0;
  if (w != null && w.length > 7 && w[2] > 0 && w[3] > 0) m = w[6];
  if (m > RING_MAX) m = RING_MAX;
  if (m <= 0) return rs == null ? 0 : ringDrop(u, store, cb);
  @TCO@ tc = null;
  if (T_TC != null) tc = (@TCO@) store.getComponent(ref, T_TC);
  if (tc == null) return 0;
  @V3D@ p = tc.getPosition();
  double x = p.x();
  double feet = p.y();
  double z = p.z();
  double rho = (double) w[7] * 0.5;
  double top = feet + (double) w[2];
  if (top > TOP_Y) top = TOP_Y;
  boolean room = top >= BOTTOM_Y && top - feet >= (double) @PKG@.AccDefs.LAN_MINH - @PKG@.AccDefs.LAN_EPS;
  if (room && T_EV != null) {
    @EVW@ ev = (@EVW@) store.getComponent(ref, T_EV);
    if (ev != null) {
      int vr = ev.viewRadiusBlocks - @PKG@.AccDefs.LAN_VIEW_MARGIN;
      if (Math.sqrt(rho * rho + (double) w[2] * (double) w[2]) > (double) vr) { room = false; RCLAMPED.incrementAndGet(); }
    }
  }
  int hgt = (int) Math.floor(top - feet + @PKG@.AccDefs.LAN_EPS);
  int lvl = w[3];
  if (hgt < w[2]) {
    int mx = @PKG@.AccDefs.lanMaxLevel((double) hgt - @PKG@.AccDefs.LAN_PZ, @PKG@.AccDefs.lanCap(w[0]));
    if (mx < lvl) lvl = mx;
  }
  if (!room || lvl <= 0) return rs == null ? 0 : ringDrop(u, store, cb);
  if (rs == null) { rs = new Object[RING_MAX]; RING.put(u, rs); }
  int[] st = rstate(u);
  int key = @PKG@.AccDefs.lanHKey(lvl);
  double th = Math.sqrt(rho * rho + (double) hgt * (double) hgt) / @PKG@.AccDefs.LAN_MOVE_DIV;
  if (th < @PKG@.AccDefs.LAN_MOVE_MIN) th = @PKG@.AccDefs.LAN_MOVE_MIN;
  if (th > @PKG@.AccDefs.LAN_MOVE_MAX) th = @PKG@.AccDefs.LAN_MOVE_MAX;
  @WLD@ wld = worldOf(store);
  @TMR@ tr = null;
  if (R_TIME != null) tr = (@TMR@) store.getResource(R_TIME);
  int asked = 0;
  int code = 0;
  for (int k = 0; k < RING_MAX; k++) {
    @REF@ hr = null;
    if (rs[k] instanceof @REF@) hr = (@REF@) rs[k];
    if (k >= m) {
      if (hr != null) { rs[k] = null; code = code | dropOne(hr, store, cb); }
      continue;
    }
    double a = 6.283185307179586 * (double) k / (double) m;
    double lx = x + rho * Math.cos(a);
    double lz = z + rho * Math.sin(a);
    if (!ringSectionOk(u, k, wld, lx, top, lz)) {
      RSKIPPED.incrementAndGet();
      if (hr != null) { rs[k] = null; code = code | dropOne(hr, store, cb); }
      continue;
    }
    if (hr != null && hr.getStore() != store) { rs[k] = null; hr = null; }
    int b = k * 3;
    if (hr != null && !hr.isValid()) {
      if (st[b + 1] != 0 || st[b] > 30) { rs[k] = null; hr = null; GONE.incrementAndGet(); }
      else { st[b] = st[b] + 1; continue; }
    }
    if (hr == null) {
      if (asked == 0) asked = maySpawnRing(u, System.currentTimeMillis()) ? 1 : 2;
      if (asked != 1) { code = code | 1024; continue; }
      rs[k] = spawnS(u, k + 1, store, cb, lx, top, lz, key);
      st[b] = 0;
      st[b + 1] = 0;
      st[b + 2] = key;
      code = code | 32;
      continue;
    }
    st[b + 1] = 1;
    st[b] = st[b] + 1;
    @TCO@ htc = (@TCO@) cb.getComponent(hr, T_TC);
    if (htc != null) {
      @V3D@ hp = htc.getPosition();
      double dx = hp.x() - lx;
      double dy = hp.y() - top;
      double dz = hp.z() - lz;
      if (dy < -0.02 || dx * dx + dy * dy + dz * dz > th * th) { htc.setPosition(new @V3D@(lx, top, lz)); MOVES.incrementAndGet(); code = code | 64; }
    }
    if (st[b + 2] != key) {
      @DLC@ hdl = (@DLC@) cb.getComponent(hr, T_DL);
      if (hdl != null) { hdl.setColorLight(@PKG@.AccDefs.lanColor(key)); st[b + 2] = key; RELIT.incrementAndGet(); code = code | 256; }
    }
    @DES@ dc = null;
    if (T_DES != null) dc = (@DES@) cb.getComponent(hr, T_DES);
    if (dc != null && tr != null) dc.setDespawnTo(tr.getNow(), DESPAWN_S);
  }
  return code;
}"""))
# 0.5.10 THE MINING HELMET LIGHT: SkyyGear 0.2.15's gear:lamp:<uuid> (Integer 1-4 = the Lantern rarity of the worn active mining helmet)
# -> the tier this player's helmet asks for (0 = none): only while lantern.helmet is on and the profile is not switching (profile:busy).
# A Number or a digit String is read (clamped to 1..4); anything else = 0. Bridge reads only (ConcurrentHashMap: any thread).
JM(lan, r"""
public static int helmetTier(java.util.UUID u) {
  if (u == null || !@PKG@.AccDefs.LAN_HELMET) return 0;
  try {
    java.util.Map b = @PKG@.AccStore.bridge();
    String us = u.toString();
    if (b.get("profile:busy:" + us) != null) return 0;
    Object o = b.get("gear:lamp:" + us);
    if (o == null) return 0;
    int v = 0;
    if (o instanceof java.lang.Number) v = ((java.lang.Number) o).intValue();
    else if (o instanceof String) {
      String x = ((String) o).trim();
      if (x.length() == 1 && Character.isDigit(x.charAt(0))) v = x.charAt(0) - '0';
    }
    if (v <= 0) return 0;
    if (v > 4) v = 4;
    return v;
  } catch (Throwable t) { return 0; }
}""")
# 0.5.10: acc:lamp = "on" while lantern.helmet is on (SkyyGear 0.2.15 shows its tooltip "Lamp:" line only then), "off" otherwise; setup + every
# AccTick (5 s: a live Server Setup change reaches it); removed on shutdown
JM(lan, r"""
public static void pubLamp() {
  try {
    String v = @PKG@.AccDefs.LAN_HELMET ? "on" : "off";
    java.util.Map b = @PKG@.AccStore.bridge();
    if (!v.equals(b.get("acc:lamp"))) b.put("acc:lamp", v);
    String rc = @PKG@.AccDefs.lanReachOf(1) + "," + @PKG@.AccDefs.lanReachOf(2) + "," + @PKG@.AccDefs.lanReachOf(3) + "," + @PKG@.AccDefs.lanReachOf(4);
    if (!rc.equals(b.get("acc:lamp:reach"))) b.put("acc:lamp:reach", rc);   // 0.5.18: the live reach for SkyyGear's helmet tooltip
  } catch (Throwable t) { }
}""")
# ONE TICK for one player (AccLanternSys: u, their entity, its store and CommandBuffer, dt). Decides once a second, at once after a bag change
# (AccStore.LPOKE), at once for a new entity of the player (join, world change: their glow is back on the first tick), at once when a wearer
# died, and when a setting changed the tier table; then the glow (decision ticks) and the helper (every tick while wanted). Returns the OR
# of the glow / helper codes + 1 when it decided.
JM(lan, LANJ(r"""
public static int step(java.util.UUID u, @REF@ ref, @ST@ store, @CB@ cb, float dt) {
  if (u == null || ref == null || store == null || cb == null) return 0;
  Object prev = OWNER.get(u);
  boolean moved = prev != ref;
  if (moved) OWNER.put(u, ref);   // 0.5.12: no map write per player per tick - only when the entity ref changed
  float[] c = clk(u);
  c[0] = c[0] + dt;
  int[] w = (int[]) WANT.get(u);
  boolean poke = @PKG@.AccStore.LPOKE.remove(u) != null;
  if (w == null && !poke && !moved && c[0] < 1.0f && !HELPER.containsKey(u) && !RING.containsKey(u)) return 0;
  boolean dead = T_DEATH != null && store.getComponent(ref, T_DEATH) != null;
  int code = 0;
  if (poke || moved || c[0] >= 1.0f || (w != null && (dead || w[5] != @PKG@.AccDefs.LAN_EPOCH))) {
    c[0] = 0.0f;
    code = 1;
    @PKG@.AccDefs.lanTable();
    int t = 0;
    if (@PKG@.AccDefs.LINE_LANTERN && !dead) t = @PKG@.AccDefs.lanBest(@PKG@.AccStore.snapshot(u));
    if (!dead) {   // 0.5.10: a worn mining helmet (SkyyGear gear:lamp) lights like a Lantern of its rarity - the stronger wins, never both
      int hl = helmetTier(u);
      if (hl > t) t = hl;
    }
    if (t <= 0) {
      WANT.remove(u);
      w = null;
    } else {
      int g = @PKG@.AccDefs.lanGlow(t);
      w = new int[] { t, g > 0 ? @PKG@.AccDefs.lanKey(g) : 0, @PKG@.AccDefs.LAN_TAB_H[t], @PKG@.AccDefs.LAN_TAB_L[t], dead ? 1 : 0, @PKG@.AccDefs.LAN_EPOCH, @PKG@.AccDefs.LAN_TAB_M[t], @PKG@.AccDefs.LAN_TAB_P[t] };
      WANT.put(u, w);
    }
    code = code | glow(u, ref, store, cb, w == null ? 0 : w[1]);
  }
  code = code | helper(u, ref, store, cb, w);
  code = code | ring(u, ref, store, cb, w);   // 0.5.5: the ring lights around the light above
  return code;
}"""))
# AccLanternHelp's question for every helper: keep it? Only while its owner's CURRENT entity is valid, in THIS store, and this helper is
# the recorded one (logout / world change: the old entity ref is invalid or in another store; a duplicate or a parked helper coming
# back is not the recorded one)
JM(lan, r"""
public static boolean keep(java.util.UUID u, @REF@ helper, @ST@ store) {
  if (u == null || helper == null) return false;
  Object o = OWNER.get(u);
  if (!(o instanceof @REF@)) return false;
  @REF@ r = (@REF@) o;
  if (!r.isValid() || r.getStore() != store) return false;
  return HELPER.get(u) == helper;
}""")
# 0.5.5: the same question for any slot (0 = the light above = keep; 1..8 = the ring light the slot records)
JM(lan, r"""
public static boolean keepSlot(java.util.UUID u, int slot, @REF@ helper, @ST@ store) {
  if (slot <= 0) return keep(u, helper, store);
  if (u == null || helper == null) return false;
  Object o = OWNER.get(u);
  if (!(o instanceof @REF@)) return false;
  @REF@ r = (@REF@) o;
  if (!r.isValid() || r.getStore() != store) return false;
  Object ro = RING.get(u);
  if (!(ro instanceof Object[])) return false;
  Object[] rs = (Object[]) ro;
  if (slot > rs.length) return false;
  return rs[slot - 1] == helper;
}""")
# THE REACH LIGHT IS THE WEARER'S OWN (the fix round; AccLanternHide runs this on every viewer in the find-visible group after CollectVisible,
# like the vanilla HideFromNonSpectators): every helper in this viewer's visible set that is not the viewer's own goes out of it, so the
# engine never sends it to them (AddToVisible builds Visible.visibleTo from what is left). lantern.shareReach: only a viewer who hid the
# wearer (HiddenPlayersManager, the vanilla /hide) loses it. Returns how many were taken out.
JM(lan, LANJ(r"""
public static int hideFrom(java.util.UUID me, @HPM@ hm, java.util.Set vis, @CB@ cb) {
  if (vis == null || cb == null || T_MARK == null) return 0;
  boolean share = @PKG@.AccDefs.LAN_SHARE;
  int n = 0;
  java.util.Iterator it = vis.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @REF@)) continue;
    @REF@ r = (@REF@) o;
    if (!r.isValid()) continue;
    @ARC@ a = cb.getArchetype(r);
    if (a == null || !a.contains(T_MARK)) continue;
    @PKG@.AccLanternMark m = (@PKG@.AccLanternMark) cb.getComponent(r, T_MARK);
    java.util.UUID ow = null;
    if (m != null) ow = m.owner;
    if (ow != null && ow.equals(me)) continue;
    if (share && ow != null) {
      boolean hid = false;
      if (hm != null) hid = hm.isPlayerHidden(ow);
      if (!hid) continue;
    }
    it.remove();
    n++;
  }
  if (n > 0) HIDDEN.addAndGet((long) n);
  return n;
}"""))
# 0.5.12 (audit 3b) THE RECORDED HELPERS OF ONE STORE (AccLanternHide's system tick, once per store per tick): every helper ref HELPER and
# RING hold that is valid and lives in this store, with its wearer (the map key = the uuid its AccLanternMark carries). Returns
# Object[] { Ref[] refs, UUID[] owners, Boolean full } - full = the store holds no marked entity outside the list (getEntityCountFor), so
# removing the listed refs is the whole job; false = an unrecorded marked entity exists this tick -> the old walk (hideFrom) for safety.
JM(lan, LANJ(r"""
public static Object[] helpersIn(@ST@ store) {
  java.util.ArrayList rl = new java.util.ArrayList();
  java.util.ArrayList ol = new java.util.ArrayList();
  java.util.Iterator it = HELPER.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object o = e.getValue();
    if (!(o instanceof @REF@)) continue;
    @REF@ r = (@REF@) o;
    if (!r.isValid() || r.getStore() != store) continue;
    rl.add(r);
    ol.add(e.getKey());
  }
  java.util.Iterator rt = RING.entrySet().iterator();
  while (rt.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) rt.next();
    Object o = e.getValue();
    if (!(o instanceof Object[])) continue;
    Object[] rs = (Object[]) o;
    for (int i = 0; i < rs.length; i++) {
      if (!(rs[i] instanceof @REF@)) continue;
      @REF@ r = (@REF@) rs[i];
      if (!r.isValid() || r.getStore() != store) continue;
      rl.add(r);
      ol.add(e.getKey());
    }
  }
  int n = rl.size();
  @REF@[] refs = new @REF@[n];
  java.util.UUID[] owners = new java.util.UUID[n];
  for (int i = 0; i < n; i++) { refs[i] = (@REF@) rl.get(i); owners[i] = (java.util.UUID) ol.get(i); }
  boolean full = false;
  try { full = T_MARK != null && store.getEntityCountFor((@QRY@) T_MARK) <= n; } catch (Throwable t) { full = false; }
  return new Object[] { refs, owners, Boolean.valueOf(full) };
}"""))
# 0.5.12: the same rule as hideFrom on the recorded list only: every listed helper that is not the viewer's own leaves the viewer's visible
# set (Set.remove - the set is never iterated); lantern.shareReach on = only for a viewer who hid that wearer. Returns how many went.
JM(lan, LANJ(r"""
public static int hideKnown(java.util.UUID me, @HPM@ hm, java.util.Set vis, Object[] known) {
  if (vis == null || known == null || vis.isEmpty()) return 0;
  @REF@[] refs = (@REF@[]) known[0];
  java.util.UUID[] owners = (java.util.UUID[]) known[1];
  boolean share = @PKG@.AccDefs.LAN_SHARE;
  int n = 0;
  for (int i = 0; i < refs.length; i++) {
    java.util.UUID ow = owners[i];
    if (ow != null && ow.equals(me)) continue;
    if (share && ow != null) {
      boolean hid = false;
      if (hm != null) hid = hm.isPlayerHidden(ow);
      if (!hid) continue;
    }
    if (vis.remove(refs[i])) n++;
  }
  if (n > 0) HIDDEN.addAndGet((long) n);
  return n;
}"""))
JM(lan, r"""
public static void prune(java.util.Set online) {
  CLK.keySet().retainAll(online);
  WANT.keySet().retainAll(online);
  HELPER.keySet().retainAll(online);
  HSTATE.keySet().retainAll(online);
  OWNER.keySet().retainAll(online);
  HY.keySet().retainAll(online);
  SPAWNT.keySet().retainAll(online);
  RING.keySet().retainAll(online);
  RSTATE.keySet().retainAll(online);
  RSEC.keySet().retainAll(online);
  RSPAWNT.keySet().retainAll(online);
  @PKG@.AccStore.LPOKE.keySet().retainAll(online);
}""")
JM(lan, r"""
public static void clearAll() {
  CLK.clear();
  WANT.clear();
  HELPER.clear();
  HSTATE.clear();
  OWNER.clear();
  HY.clear();
  SPAWNT.clear();
  RING.clear();
  RSTATE.clear();
  RSEC.clear();
  RSPAWNT.clear();
  @PKG@.AccStore.LPOKE.clear();
}""")

# ================= 0.5.17 AccStarter: THE STARTER ACCESSORY BAG (tools/accessories_0_5_17_patch.py; Skyy 2026-10-15 "put the accessory bag in
# your inventory at spawn too"). One task per online player per 5 s AccTick (only while that profile has no answer yet), run on the player's
# world thread: gates, then under AccStore.lock(uuid) with ONE pkey: marker -> already owned -> give (storage first, counted) -> marker.
# Marker = Skyy_SkyyAccessories/starter/<pkey>.properties (starterBag=given | owned-inventory | owned-void), decided only after the bag is
# really in the inventory (or already owned) and WRITTEN ~35 s LATER (review fix 1: the inventory reaches disk with the ~10 s player save
# and SkyyProfiles' crash roll-forward covers 30 s - a crash in between leaves no marker, so the next login checks the inventory again).
# DONE = pkey -> answer (this run), DUE = pkey -> Object[]{answer, Long due time} (written by AccTick when due, all at shutdown; a failed
# write stays and is retried), WAIT = pkey told "inventory full" -> Long next silent retry (review fix 3; until the player leaves),
# BADM = pkey whose marker could not be read (warned; until they leave), WFAIL = pkey whose due write failed (warned once).
for _c, _m in ((IC, "addItemStack"), (INV, "getCombinedStorageHotbarBackpack"), (INV, "getUtility"), (INV, "getTools"),
               (INV, "getBackpack"), (PLA, "markNeedsSave"), (PLA, "isWaitingForClientReady"), (DTH, "getComponentType")):
    B.probe(pool, _c, _m)
ast_.addInterface(pool.get("java.lang.Runnable"))
JF(ast_, "public @PR@ pr;")
JF(ast_, "public java.util.UUID expectedWorld;")
JF(ast_, "public static java.nio.file.Path DIR;")
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();")
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap WAIT = new java.util.concurrent.ConcurrentHashMap();")
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap BADM = new java.util.concurrent.ConcurrentHashMap();")
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap DUE = new java.util.concurrent.ConcurrentHashMap();")
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap WFAIL = new java.util.concurrent.ConcurrentHashMap();")
JF(ast_, "public static volatile long DELAY_MS = 35000L;")   # the marker's disk write waits this long (> SkyyProfiles' 30 s crash window)
JF(ast_, "public static volatile long RETRY_MS = 60000L;")   # a full inventory is tried again silently this often (same session)
JF(ast_, "public static boolean ADDWARNED = false;")
JF(ast_, "public static boolean FAILED = false;")
JF(ast_, "public static volatile long GIVEN = 0L;")
ast_.addField(CtField.make("public static final String GIVE_TEXT = %s;" % jlit(STARTER_GIVE), ast_))
ast_.addField(CtField.make("public static final String FULL_TEXT = %s;" % jlit(STARTER_FULL), ast_))
ast_.addConstructor(CtNewConstructor.make(JT("public AccStarter(@PR@ pr, java.util.UUID w) { this.pr = pr; this.expectedWorld = w; }"), ast_))
# null = this player may get the starter bag checked now, else why not (no state is read or written)
JM(ast_, r"""
public static String gate(java.util.UUID u) {
  if (u == null) return "nouuid";   // 0.5.22: no starter.bag gate - the bag item retirement always runs
  if (@PKG@.AccStore.moveBlock(u) != null) return "blocked";
  try {
    java.util.Map b = @PKG@.AccStore.bridge();
    if (b.get("profile:fn:key") != null && b.get("profile:" + u.toString()) == null) return "noprofile";
  } catch (Throwable t) { return "blocked"; }
  return null;
}""")
JM(ast_, r"""
public static java.nio.file.Path fileOf(String k) {
  if (DIR == null || k == null) return null;
  return DIR.resolve(k + ".properties");
}""")
# the marker of profile k: null = none, "?" = cannot be read (or the folder is unknown), else its answer (a file without the key = "file")
JM(ast_, r"""
public static String markerOf(String k) {
  java.nio.file.Path f = fileOf(k);
  if (f == null) return "?";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    String v = p.getProperty("retiredBag");   // 0.5.22: the retirement marker (folder retired/)
    if (v == null || v.trim().length() == 0) return "file";
    return v.trim();
  } catch (Throwable t) { return "?"; }
}""")
JM(ast_, r"""
public static boolean writeMarker(String k, String why) {
  java.nio.file.Path f = fileOf(k);
  if (f == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("retiredBag", why);
    p.setProperty("at", java.time.Instant.now().toString());
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyyAccessories 0.5.22 - the retired bag item: this profile was told once (the item is removed whenever one turns up)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    return true;
  } catch (Throwable t) { return false; }
}""")
JM(ast_, r"""
public static void record(String k, String why) {
  DONE.put(k, why);
  DUE.put(k, new Object[] { why, Long.valueOf(System.currentTimeMillis() + DELAY_MS) });
}""")
# AccTick (scheduler thread, all = false: the due ones) and shutdown (all = true: every pending one now); a failed write stays pending
JM(ast_, r"""
public static void flush(boolean all) {
  if (DUE.isEmpty()) return;
  long now = System.currentTimeMillis();
  java.util.Iterator it = DUE.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (!all && now < ((Long) v[1]).longValue()) continue;
    String k = (String) e.getKey();
    if (writeMarker(k, String.valueOf(v[0]))) { it.remove(); WFAIL.remove(k); }
    else if (WFAIL.putIfAbsent(k, Boolean.TRUE) == null) @PKG@.AccStore.warn("starter bag: could not write " + fileOf(k) + " (" + v[0] + ") - remembered for this run and retried every 5 s");
  }
}""")
JM(ast_, r"""
public static int countIn(@IC@ c) {
  if (c == null) return 0;
  int n = 0;
  try {
    short cap = c.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = c.getItemStack(s);
      if (it != null && !it.isEmpty() && @PKG@.AccDefs.BAG.equals(it.getItemId())) n = n + it.getQuantity();
    }
  } catch (Throwable t) { }
  return n;
}""")
# bag items anywhere a player keeps items: storage, hotbar, backpack, utility, tools
JM(ast_, r"""
public static int owned(@INV@ inv) {
  if (inv == null) return 0;
  return countIn(inv.getStorage()) + countIn(inv.getHotbar()) + countIn(inv.getBackpack()) + countIn(inv.getUtility()) + countIn(inv.getTools());
}""")
# bag items in SkyySacks' Void (world thread, the active profile): asked only when sacks:fn:catOf gives the bag a home (0.8.x: none = 0);
# -1 = the Void is paused (wait), 0 = none / no SkyySacks
JM(ast_, r"""
public static long inVoid(java.util.UUID u) {
  try {
    java.util.Map b = @PKG@.AccStore.bridge();
    Object cf = b.get("sacks:fn:catOf");
    Object cn = b.get("sacks:fn:count");
    if (!(cf instanceof java.util.function.Function) || !(cn instanceof java.util.function.Function)) return 0L;
    if (((java.util.function.Function) cf).apply(@PKG@.AccDefs.BAG) == null) return 0L;
    Object r = ((java.util.function.Function) cn).apply(new Object[] { u, @PKG@.AccDefs.BAG });
    if (r instanceof Number) {
      long v = ((Number) r).longValue();
      return v < 0L ? -1L : v;
    }
  } catch (Throwable t) { }
  return 0L;
}""")
JM(ast_, r"""
public static void addWarn(String why) {
  if (ADDWARNED) return;
  ADDWARNED = true;
  @PKG@.AccStore.warn("starter bag: the inventory could not be reached (" + why + ") - nothing given, tried again by the next tick (logged once)");
}""")
# one bag into storage, then hotbar, then backpack - never dropped; returns how many really arrived (0 = full), -1 = an error (review
# fix 4: no combined container / an exception - not "full")
JM(ast_, r"""
public static int addOne(@INV@ inv) {
  if (inv == null) { addWarn("no inventory"); return -1; }
  try {
    @IC@ c = inv.getCombinedStorageHotbarBackpack();
    if (c == null) { addWarn("no storage container"); return -1; }
    int before = owned(inv);
    c.addItemStack(new @IS@(@PKG@.AccDefs.BAG, 1));
    int got = owned(inv) - before;
    return got < 0 ? 0 : got;
  } catch (Throwable t) { addWarn(String.valueOf(t)); return -1; }
}""")
JM(ast_, r"""
public static void say(@PR@ pr, String text, String col) {
  try { pr.sendMessage(@MSG@.raw(text).color(col)); } catch (Throwable t) { }
}""")
# 0.5.22 THE BAG ITEM RETIREMENT (Skyy 2026-10-16 "id like to ditch the item and just use the menu"): every copy of the old bag item in a
# player's inventory (storage, hotbar, backpack, utility, tools) is removed - the journal line (retired.log, fsynced) FIRST (no line = nothing
# removed), then the removal, counted before and after. The item never held the accessories (bags/<pkey>.properties does), so nothing is lost.
# Once per profile a chat line (marker retired/<pkey>.properties, written ~35 s later like the 0.5.17 marker - a crash before the player save
# brings the item back and it is removed again). Runs on the player's world thread every 5 s (AccTick -> dispatch); the caller holds the bag lock.
JF(ast_, "public static java.nio.file.Path LOGF;")   # 0.5.22: Skyy_SkyyAccessories/retired.log
JF(ast_, "public static final java.util.concurrent.ConcurrentHashMap STUCK = new java.util.concurrent.ConcurrentHashMap();")   # pkey -> Long ms: copies that would not go (tried again once a minute, quietly in between)
JF(ast_, "public static volatile long STUCK_MS = 60000L;")
JM(ast_, r"""
public static boolean journal(String line) {
  if (LOGF == null) return false;
  try {
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(LOGF.toFile(), true);
    try { out.write((java.time.Instant.now().toString() + " " + line + "\n").getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    return true;
  } catch (Throwable t) { addWarn("retired.log could not be written: " + t); return false; }
}""")
JM(ast_, r"""
public static String where(@INV@ inv) {
  StringBuilder b = new StringBuilder();
  String[] nm = new String[] { "storage", "hotbar", "backpack", "utility", "tools" };
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack(), inv.getUtility(), inv.getTools() };
  for (int i = 0; i < cs.length; i++) {
    int n = countIn(cs[i]);
    if (n <= 0) continue;
    if (b.length() > 0) b.append(", ");
    b.append(nm[i]).append(' ').append(n);
  }
  return b.toString();
}""")
JM(ast_, r"""
public static void removeIn(@IC@ c) {
  if (c == null) return;
  try {
    short cap = c.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = c.getItemStack(s);
      if (it != null && !it.isEmpty() && @PKG@.AccDefs.BAG.equals(it.getItemId())) c.removeItemStackFromSlot(s, it.getQuantity());
    }
  } catch (Throwable t) { addWarn("a bag item could not be removed: " + t); }
}""")
JM(ast_, r"""
public static String stepK(@PR@ pr, @PLA@ p, java.util.UUID u, String k) {
  @INV@ inv = p.getInventory();
  if (inv == null) return "noinv";
  int n = owned(inv);
  if (n <= 0) { STUCK.remove(k); return "none"; }
  long now = System.currentTimeMillis();
  Long st = (Long) STUCK.get(k);
  if (st != null && now >= st.longValue() && now - st.longValue() < STUCK_MS) return "stuck-quiet";   // a copy that would not go: no journal / log flood
  String who = pr.getUsername() + " " + u + " profile " + k;
  if (!journal("REMOVE " + who + ": " + n + " x " + @PKG@.AccDefs.BAG + " (" + where(inv) + ") - the item is retired (0.5.22); the accessories live in bags/" + k + ".properties, never in the item - UNDO: none needed (the item held nothing)")) return "nojournal";
  removeIn(inv.getStorage());
  removeIn(inv.getHotbar());
  removeIn(inv.getBackpack());
  removeIn(inv.getUtility());
  removeIn(inv.getTools());
  int left = owned(inv);
  int gone = n - left;
  if (left > 0) STUCK.put(k, Long.valueOf(now)); else STUCK.remove(k);
  journal("DONE " + who + ": " + gone + " removed" + (left > 0 ? ", " + left + " still there (tried again in a minute)" : ""));
  try { p.markNeedsSave(); } catch (Throwable t) { }
  GIVEN = GIVEN + (long) gone;
  if (!DONE.containsKey(k)) {
    String m = markerOf(k);
    if (m == null) { record(k, "removed-" + gone); say(pr, GIVE_TEXT, "@INFOCOL@"); }
    else if (!"?".equals(m)) DONE.put(k, m);
  }
  @PKG@.AccCfg.info("bag item retired: removed " + gone + " from " + pr.getUsername() + " (profile " + k + ", " + GIVEN + " since the start)");
  return gone > 0 ? "removed" : "stuck";
}""".replace("@INFOCOL@", SUI.STATUS["="]))
# world thread: gates, then ONE pkey for the whole step under the bag lock (one call inside the synchronized block)
JM(ast_, r"""
public static String step(@PR@ pr, @PLA@ p) {
  if (pr == null || p == null) return "none";
  java.util.UUID u = pr.getUuid();
  String g = gate(u);
  if (g != null) return g;
  String k = @PKG@.AccStore.pkey(u);
  String r = null;
  synchronized (@PKG@.AccStore.lock(u)) { r = stepK(pr, p, u, k); }
  return r;
}""")
JM(ast_, LANJ(r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID nowWorld = this.pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    if (st.getComponent(r, @DTH@.getComponentType()) != null) return;   // dead: after the respawn
    step(this.pr, p);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("starter bag failed (logged once): " + t); }
  }
}"""))
# AccTick (scheduler thread): one task to the player's world only while that profile has no answer yet (a given bag costs nothing after)
JM(ast_, r"""
public static void dispatch(@PR@ pr, @WLD@ w, java.util.UUID wu) {
  if (pr == null || w == null) return;
  w.execute(new @PKG@.AccStarter(pr, wu));   // 0.5.22: the bag item retirement - every 5 s (cheap: one inventory scan)
}""")
# the uuid part of a storage key (uuid or uuid-pN)
JM(ast_, r"""
public static String owner(Object k) {
  String s = String.valueOf(k);
  return s.length() >= 36 ? s.substring(0, 36) : s;
}""")
# AccTick: players who left - their "inventory full" wait and unreadable-marker note end (a new session tells once more); DONE answers of
# players who left are dropped (the marker on disk answers next time) unless their marker still waits to be written (DUE)
JM(ast_, r"""
public static void prune(java.util.Set online) {
  java.util.HashSet on = new java.util.HashSet();
  java.util.Iterator oi = online.iterator();
  while (oi.hasNext()) on.add(String.valueOf(oi.next()));
  java.util.Iterator it = WAIT.keySet().iterator();
  while (it.hasNext()) if (!on.contains(owner(it.next()))) it.remove();
  it = BADM.keySet().iterator();
  while (it.hasNext()) if (!on.contains(owner(it.next()))) it.remove();
  it = STUCK.keySet().iterator();   // 0.5.22
  while (it.hasNext()) if (!on.contains(owner(it.next()))) it.remove();
  it = DONE.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (!on.contains(owner(k)) && !DUE.containsKey(k)) it.remove();
  }
}""")

tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public AccTick() { }", tick))
# 0.4.3 review fix: campCheck; 0.5: the notices file (never saved on a world thread) and one AccRestampTask per online player on its world;
# 0.5 part 2: every player who left loses our gear:extra text and movement entry (AccGear.prune) and the notice's once-a-session mark
JF(tick, "public static boolean PRUNE_WARNED = false;")
JM(tick, r"""
public void run() {
  @PKG@.AccStore.publishOnline();
  @PKG@.AccStore.campCheck();
  try { @PKG@.AccNotice.save(); } catch (Throwable t) { }
  try { @PKG@.AccStarter.flush(false); } catch (Throwable t) { }   // 0.5.17: starter bag markers that are due (~35 s after the answer)
  java.util.HashSet online = new java.util.HashSet();
  boolean listed = false;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      online.add(pr.getUuid());
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new @PKG@.AccRestampTask(pr, wu));
      try { @PKG@.AccStarter.dispatch(pr, w, wu); } catch (Throwable t2) { }   // 0.5.22: the bag item retirement (0.5.17: the starter bag)
    }
    listed = true;
  } catch (Throwable t) { }
  if (!listed) return;   // never prune from a player list that could not be read
  try { @PKG@.AccLantern.prune(online); } catch (Throwable t) { }   // 0.5.4: the Lantern state of players who left (their helpers go by themselves)
  @PKG@.AccLantern.pubLamp();   // 0.5.10: acc:lamp follows lantern.helmet
  try {
    @PKG@.AccGear.prune(online);
    @PKG@.AccNotice.ASKED.keySet().retainAll(online);
    @PKG@.AccStarter.prune(online);   // 0.5.17
    @PKG@.AccPower.prune(online);     // 0.5.22: skill:bonus source + acc:power of players who left
  } catch (Throwable t) {
    if (!PRUNE_WARNED) { PRUNE_WARNED = true; @PKG@.AccStore.warn("removing the bridge keys of players who left failed (logged once): " + t); }
  }
}""")

# ================= MoveSync: the shared Skyy movement protocol (tools/skyymove.py; identical code in SkyySkills 0.2) =================
MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".AccStore.warn")

# ================= 0.5.6 AccKnow: the Lantern recipe knowledge (the SkyySacks 0.7.7 KnowSync pattern, the four Lantern ids only) =================
# VERIFIED bytecode (HytaleServer.jar): PlayerConfigData.getKnownRecipes() = an unmodifiable view, setKnownRecipes(Set) stores it and
# marks the data changed (saved with the PLAYER); CraftingPlugin.sendKnownRecipes(Ref, ComponentAccessor) only reads PlayerRef + Player
# and sends UpdateKnownRecipes. Called from AccEffects.tick (world thread, once a second per player). Bridge reads only (java.lang).
KN_PCD = "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData"
KN_CRF = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
for c, m in ((PLA, "getPlayerConfigData"), (KN_PCD, "getKnownRecipes"), (KN_PCD, "setKnownRecipes"), (KN_CRF, "sendKnownRecipes"),
             (ST, "getComponent")):
    B.probe(pool, c, m)
def KNJ(src):
    return src.replace("@PCD@", KN_PCD).replace("@CRF@", KN_CRF)
JF(kn, 'public static final String SFX = "_Recipe_Generated_0";')
JF(kn, "public static volatile boolean SEEN = false;")
JF(kn, "public static volatile boolean FREENOTE = false;")
JF(kn, "public static volatile long WARNAT = 0L;")
# review fixes: SETTLE_MS after a profile:epoch change = change nothing (SkyyCollections republishes coll:recipes for the new profile in
# that time - the SkyySacks settle window); ABSENT_MS without any coll:recipes for a player (managed, settled) = they know no Lantern
JF(kn, "public static volatile long SETTLE_MS = 6000L;")
JF(kn, "public static volatile long ABSENT_MS = 10000L;")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap LASTEP = new java.util.concurrent.ConcurrentHashMap();")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap CHANGEDAT = new java.util.concurrent.ConcurrentHashMap();")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap ABSENT = new java.util.concurrent.ConcurrentHashMap();")
JM(kn, r"""
public static void warnOnce(String m) {
  long now = System.currentTimeMillis();
  if (now - WARNAT > 60000L) { WARNAT = now; @PKG@.AccStore.warn(m); }
}""")
# "managed" = SkyyCollections 0.2.7+ manages the Lantern recipes (coll:lantern, a tier String); "free" = it says "off" (no visible
# TreeSap, also after a reload) or was never seen (missing, older): all four known; "hold" = seen earlier in this JVM and the key is
# gone (a shutdown in progress: change nothing)
JM(kn, r"""
public static String mode() {
  Object v = null;
  try { v = @PKG@.AccStore.bridge().get("coll:lantern"); } catch (Throwable t) { v = null; }
  if (v instanceof String) {
    SEEN = true;
    if (!"off".equals(v)) return "managed";
    if (!FREENOTE) { FREENOTE = true; @PKG@.AccCfg.info("SkyyCollections does not manage the Lantern recipes (no visible Tree Sap collection) - every Lantern recipe stays craftable"); }
    return "free";
  }
  if (SEEN) return "hold";
  if (!FREENOTE) { FREENOTE = true; @PKG@.AccCfg.info("SkyyCollections does not manage the Lantern recipes (not installed, older than 0.2.7, or no Tree Sap collection) - every Lantern recipe stays craftable"); }
  return "free";
}""")
# review fix: false while a profile switch settles (profile:epoch:<uuid> changed less than SETTLE_MS ago; the first value seen is the
# baseline, an absent epoch is no change - PROFILES-CONTRACT 4.2, as SkyySacks' settledKey)
JM(kn, r"""
public static boolean settled(java.util.UUID u) {
  Object e = null;
  try { e = @PKG@.AccStore.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { e = null; }
  long now = System.currentTimeMillis();
  if (e != null) {
    Object le = LASTEP.put(u, e);
    if (le != null && !le.equals(e)) { CHANGEDAT.put(u, Long.valueOf(now)); ABSENT.remove(u); }
  }
  Long t = (Long) CHANGEDAT.get(u);
  if (t == null) return true;
  if (now - t.longValue() < SETTLE_MS) return false;
  CHANGEDAT.remove(u);
  return true;
}""")
# the Lantern item ids this player should know; null = change nothing (hold, a profile switch settling, or SkyyCollections has not
# published this player yet - for up to ABSENT_MS; after that, no coll:recipes = no Lantern known, never another profile's)
JM(kn, r"""
public static java.util.HashSet wanted(java.util.UUID u) {
  String m = mode();
  if (m.equals("hold")) return null;
  String[] ids = @PKG@.AccDefs.LAN_IDS;
  java.util.HashSet out = new java.util.HashSet();
  if (m.equals("free")) {
    for (int i = 0; i < ids.length; i++) out.add(ids[i]);
    return out;
  }
  if (u == null) return null;
  if (!settled(u)) return null;
  Object v = null;
  try { v = @PKG@.AccStore.bridge().get("coll:recipes:" + u.toString()); } catch (Throwable t) { v = null; }
  if (v == null) {
    long now = System.currentTimeMillis();
    Long f = (Long) ABSENT.get(u);
    if (f == null) { ABSENT.put(u, Long.valueOf(now)); return null; }
    if (now - f.longValue() < ABSENT_MS) return null;
    return out;
  }
  ABSENT.remove(u);
  if (!(v instanceof String)) return null;
  String[] parts = ((String) v).split(",");
  java.util.HashSet have = new java.util.HashSet();
  for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) have.add(x); }
  for (int i = 0; i < ids.length; i++) if (have.contains(ids[i] + SFX)) out.add(ids[i]);
  return out;
}""")
# set exactly the four Lantern ids of the known set to want (every other entry kept); true = it changed (the caller sends the packet)
JM(kn, KNJ(r"""
public static boolean apply(@PCD@ d, java.util.HashSet want) {
  if (d == null || want == null) return false;
  java.util.Set known = d.getKnownRecipes();
  String[] ids = @PKG@.AccDefs.LAN_IDS;
  boolean diff = false;
  for (int i = 0; i < ids.length && !diff; i++) {
    boolean has = known != null && known.contains(ids[i]);
    if (has != want.contains(ids[i])) diff = true;
  }
  if (!diff) return false;
  java.util.HashSet ns = known == null ? new java.util.HashSet() : new java.util.HashSet(known);
  for (int i = 0; i < ids.length; i++) {
    if (want.contains(ids[i])) ns.add(ids[i]);
    else ns.remove(ids[i]);
  }
  d.setKnownRecipes(ns);
  return true;
}"""))
# once a second per player (AccEffects.tick, world thread): -1 skipped (no player / profile loading / change nothing), 0 already right,
# 1 changed + UpdateKnownRecipes sent. Never throws (one WARN a minute).
JM(kn, KNJ(r"""
public static int tick(@REF@ ref, @ST@ store, java.util.UUID u) {
  try {
    if (ref == null || store == null || u == null) return -1;
    if (@PKG@.AccStore.moveBlock(u) != null) return -1;
    java.util.HashSet want = wanted(u);
    if (want == null) return -1;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return -1;
    if (!apply(p.getPlayerConfigData(), want)) return 0;
    @CRF@.sendKnownRecipes(ref, store);
    return 1;
  } catch (Throwable t) { warnOnce("Lantern recipe knowledge sync failed: " + t); return -1; }
}"""))

# ================= AccEffects: accessory stats (EntityTickingSystem on Player entities, runs on each world's thread) =================
# Pattern copied from TerrariaAddons 1.7.4 (DivingHelmetSystem: putModifier/removeModifier with a StaticModifier under a fixed key;
# BandOfRegenerationSystem: addStatValue(DefaultEntityStatTypes.getHealth(), n); speed through the Skyy movement protocol). Work is
# throttled to once per second per player. 0.5: the numbers come from the booster table (AccDefs.BOOST, live config), a switched-off
# line counts for nothing, and every publisher has its own try + log-once flag (spec 5.4), so one failing part never stops the others.
eff.addConstructor(CtNewConstructor.make("public AccEffects() { super(); }", eff))
eff.addField(CtField.make("public static boolean FAILED_ONCE = false;", eff))
eff.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", eff))
# 0.4 PERCENT LAYER. Verified in HytaleServer.jar bytecode (EntityStatValue.computeModifiers): max = EntityStatType.max, then
# max + SUM(ADDITIVE MAX amounts), then max * SUM(MULTIPLICATIVE MAX amounts). MULTIPLICATIVE amounts are summed, so ours (1.10) next
# to vanilla's Meat_Buff (1.05) would give x2.15 - not usable. Instead: flat = type max + every OTHER additive MAX modifier (armour,
# SkyySkills, food boosts), ours = ADDITIVE round(flat x pct / 100, 2 decimals) under the 0.2/0.3 key (overwrites the flat value
# those versions saved with the player). A vanilla multiplicative buff then scales flat + ours = flat x (1 + pct) x buff.
eff.addMethod(CtNewMethod.make(f"""
public static float flatMax({ESV} v, int idx, String key) {{
  float base = 0.0f;
  try {{
    {EST} t = ({EST}) {EST}.getAssetMap().getAsset(idx);
    if (t != null) base = t.getMax();
  }} catch (Throwable e) {{ }}
  java.util.Map mods = v.getModifiers();
  if (mods == null) return base;
  java.util.Iterator it = mods.keySet().iterator();
  while (it.hasNext()) {{
    Object k = it.next();
    if (key.equals(k)) continue;
    Object o = mods.get(k);
    if (!(o instanceof {SMO})) continue;
    {SMO} sm = ({SMO}) o;
    if (sm.getTarget() != {MTG}.MAX || sm.getCalculationType() != {CAL}.ADDITIVE) continue;
    base = base + sm.getAmount();
  }}
  return base;
}}""", eff))
# 0.5: set (amt > 0) or remove (amt <= 0) our MAX modifier on one stat, ADDITIVE (never MULTIPLICATIVE: the engine sums every
# multiplicative amount into one factor); only writes when something changes. Throws to the caller's publisher try.
# Never removed on leave or shutdown (as in 0.4.5 and SkyySkills): the modifier is saved with the character, a relog keeps it and the
# next tick corrects it. DEPLOY NOTE (part 2 review finding 3): removing or disabling the mod leaves the last flat bonus on saved
# characters until a later admin cleanup command removes skyyacc_health / skyyacc_stamina / skyyacc_mana.
JM(eff, r"""
public static void modAmt(@ESM@ m, int idx, String key, float amt) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;   // getModifier/putModifier would log "No EntityStatValue found" every second
  @MOD@ cur = m.getModifier(idx, key);
  if (amt <= 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
  @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
  if (cur != null && cur.equals(want)) return;
  m.putModifier(idx, key, want);
}""")
# 0.5.22: a SIGNED MAX modifier (the Power's Health / Mana can be a debuff): 0 removes it; a minus never takes the max below 1 (flatMax:
# the type max + every other ADDITIVE MAX modifier, ours left out)
JM(eff, r"""
public static void modSigned(@ESM@ m, int idx, String key, float amt) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float a = amt;
  if (a < 0.0f) {
    float base = flatMax(v, idx, key);
    if (base + a < 1.0f) a = 1.0f - base;
    if (a > 0.0f) a = 0.0f;
  }
  @MOD@ cur = m.getModifier(idx, key);
  if (a == 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
  @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, a);
  if (cur != null && cur.equals(want)) return;
  m.putModifier(idx, key, want);
}""")
# 0.5.22 Mana: the Mana line's % of the flat Mana (never less than its floor) first, then the Power's flat Mana on top (spec 4: the % never
# multiplies the Power)
JM(eff, r"""
public static void manaMod2(@ESM@ m, int idx, String key, float pct, float floor, float flat) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float amt = 0.0f;
  if (pct > 0.0f) amt = Math.round(flatMax(v, idx, key) * pct) / 100.0f;
  if (floor > amt) amt = floor;
  modSigned(m, idx, key, amt + flat);
}""")
# 0.5 Mana: pct of the FLAT max Mana (flatMax: the type max + every other ADDITIVE MAX modifier, ours left out), never less than floor
JM(eff, r"""
public static void manaMod(@ESM@ m, int idx, String key, float pct, float floor) {
  if (idx < 0) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float amt = 0.0f;
  if (pct > 0.0f) amt = Math.round(flatMax(v, idx, key) * pct) / 100.0f;
  if (floor > amt) amt = floor;
  modAmt(m, idx, key, amt);
}""")
# 0.5 STAMINA REGEN (spec 5.4.1; every call read in HytaleServer.jar bytecode and B.probe'd): the rate vanilla is refilling at RIGHT NOW
# = the sum of amount / interval over the Stamina value's positive ADDITIVE regen entries whose conditions pass
# Condition.allConditionsMet(cb, ref, now, rg) - exactly the check RegeneratingValue.shouldRegenerate makes after its timer step (we
# never call shouldRegenerate / regenerate: they advance the engine's own regen timer); the clock is the store's TimeResource, like
# EntityStatsSystems$Regenerate. The top-up = rate x pct / 100 x the seconds since the last 1 s tick (clamped 0..2), capped at max,
# skipped for a dead player or a full bar, added with addStatValue like the engine. Sprinting / gliding / blocking / the empty-bar pause
# fail those conditions, so the bonus never flows then (sampled once a second: at most one second's bonus either way).
# The rate is the Stamina asset's own ADDITIVE regen entries only (part 2 review finding 4): RegeneratingModifier multipliers and
# armor regen entries are not in it, so "X% faster" and any quoted refill time hold for the vanilla numbers.
JM(eff, r"""
public static void staminaRegen(@ST@ store, @CB@ cb, @REF@ ref, @ESM@ m, float pct, float secs) {
  if (pct <= 0.0f) return;
  int si = @DST@.getStamina();
  if (si < 0) return;
  @ESV@ v = m.get(si);
  if (v == null) return;
  int hi = @DST@.getHealth();
  @ESV@ hv = hi < 0 ? null : m.get(hi);
  if (hv != null && hv.get() <= 0.0f) return;
  float cur = v.get();
  float max = v.getMax();
  if (cur >= max) return;
  @RGV@[] rv = v.getRegeneratingValues();
  if (rv == null || rv.length == 0) return;
  java.time.Instant now = ((@TMR@) store.getResource(@TMR@.getResourceType())).getNow();
  float rate = 0.0f;
  for (int i = 0; i < rv.length; i++) {
    if (rv[i] == null) continue;
    @RGN@ rg = rv[i].getRegenerating();
    if (rg == null || rg.getRegenType() != @RGT@.ADDITIVE) continue;
    float a = rg.getAmount();
    float iv = rg.getInterval();
    if (a <= 0.0f || iv <= 0.0f) continue;
    if (@CND@.allConditionsMet(cb, ref, now, rg)) rate = rate + a / iv;
  }
  if (rate <= 0.0f) return;
  float sec = secs;
  if (sec < 0.0f) sec = 0.0f;
  if (sec > 2.0f) sec = 2.0f;
  float amt = rate * pct / 100.0f * sec;
  if (cur + amt > max) amt = max - cur;
  if (amt > 0.0f) m.addStatValue(si, amt);
}""")
# Movement (0.3 Speed; 0.5 part 2 + Feather): the whole bag is ONE source "accessories.talismans" (layer pct) in the shared movement
# protocol (tools/skyymove.py) - speed 0.10 = +10 %, jump 0.20 = jump HEIGHT x 1.20, fallDamage -0.40 = 40 % less fall damage (the
# config stores the magnitude, the tick adds the minus); all zero removes the entry. MoveSync.sync applies the total of every source:
# baseSpeed = default x clamp((1 + sum flat) x (1 + sum pct), 0.3, 5), jumpForce from the summed jump height (clamped to h0 + 20
# blocks); fall damage is applied ONCE, by the mod holding stat:owner:fallDamage (SkyySkills 0.4.8: its fall filter multiplies by
# MoveSync.fallMultiplier(sums of every source)). Still baseSpeed only for speed (the direction multipliers are factors ON baseSpeed).
# The 0.2 back-off lives on in MoveSync; an unequip restores defaults only for a field still holding the value written. AccGear.MOVED
# remembers who has an entry, so AccTick removes it when they leave (AccGear.prune) and shutdown removes every one.
JM(eff, r"""
public static void move(java.util.UUID u, @PR@ pr, @CB@ cb, @REF@ ref, float speed, float jump, float fall) {
  @PKG@.MoveSync.post(u, @PKG@.AccGear.SOURCE, "pct", speed, jump, fall);
  if (speed != 0.0f || jump != 0.0f || fall != 0.0f) @PKG@.AccGear.MOVED.put(u, Boolean.TRUE);
  else @PKG@.AccGear.MOVED.remove(u);
  @PKG@.MoveSync.sync(u, pr, cb, ref, @PKG@.AccStore.SPEED, "SkyyAccessories");
}""")
# one log-once flag per publisher (spec 5.4; part 2 review finding 1: Health, Stamina and Mana had shared one pools flag, so a
# Health failure hid a later Stamina or Mana failure). F_STAM = the Stamina Regen top-up, F_STAMINA = the max Stamina modifier.
JF(eff, "public static boolean F_HEALTH = false;")
JF(eff, "public static boolean F_STAMINA = false;")
JF(eff, "public static boolean F_MANA = false;")
JF(eff, "public static boolean F_STAM = false;")
JF(eff, "public static boolean F_HEAL = false;")
JF(eff, "public static boolean F_MOVE = false;")
JF(eff, "public static boolean F_GEAR = false;")
JF(eff, "public static boolean F_NOTE = false;")
JF(eff, "public static boolean F_POWER = false;")   # 0.5.22: the Accessory Power tick
JM(eff, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  @REF@ ref = null;
  @PR@ pr = null;
  java.util.UUID u = null;
  float[] c = null;
  float secs = 0.0f;
  int[] best = null;
  @ESM@ m = null;
  String[] snap = null;   // 0.5.22: the bag the Power reads too
  try {
    ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    u = pr.getUuid();
    c = (float[]) @PKG@.AccStore.CLOCK.get(u);
    if (c == null) { c = new float[] { 1.0f, 0.0f }; @PKG@.AccStore.CLOCK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    secs = c[0];
    c[0] = 0.0f;
    @PKG@.AccStore.checkEpoch(u);   // 0.4.1: republish acc:has / acc:tal within a second of a profile switch
    snap = @PKG@.AccStore.snapshot(u);
    best = @PKG@.AccDefs.bestTiers(snap);   // 0.4.1: the ACTIVE profile's bag; only the best rarity of a line
    for (int li = 0; li < best.length; li++) if (!@PKG@.AccDefs.lineOn(li)) best[li] = 0;   // 0.5: a switched-off line counts for nothing
    m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.AccStore.warn("accessory effects failed (logged once): " + t); }
    return;
  }
  float[] bo = @PKG@.AccDefs.BOOST;
  // 0. 0.5.22 Accessory Power: the gathering stats + acc:power are published here; pw = the combat sums { hp, def, str, cc, cd, mp, mana, spd }
  double[] pw = new double[8];
  try { pw = @PKG@.AccPower.tick(u, snap); }
  catch (Throwable t) { pw = new double[8]; if (!F_POWER) { F_POWER = true; @PKG@.AccStore.warn("Accessory Power failed (logged once): " + t); } }
  if (pw == null) return;   // 0.5.22: profile:busy - nothing is written this second (the next tick after the switch writes the new profile's)
  // 1. stat pools: max Health (+ the Power's, signed) and max Stamina flat, max Mana a percent of the flat Mana with a floor + the Power's flat Mana
  if (m != null) {
    try { modSigned(m, @DST@.getHealth(), "skyyacc_health", bo[@E_HF@ * 5 + best[@L_H@]] + (float) pw[0]); }
    catch (Throwable t) { if (!F_HEALTH) { F_HEALTH = true; @PKG@.AccStore.warn("max Health from accessories failed (logged once): " + t); } }
    try { modAmt(m, @DST@.getStamina(), "skyyacc_stamina", bo[@E_SF@ * 5 + best[@L_S@]]); }
    catch (Throwable t) { if (!F_STAMINA) { F_STAMINA = true; @PKG@.AccStore.warn("max Stamina from accessories failed (logged once): " + t); } }
    try { manaMod2(m, @DST@.getMana(), "skyyacc_mana", bo[@E_MP@ * 5 + best[@L_M@]], bo[@E_MF@ * 5 + best[@L_M@]], (float) pw[6]); }
    catch (Throwable t) { if (!F_MANA) { F_MANA = true; @PKG@.AccStore.warn("max Mana from accessories failed (logged once): " + t); } }
  }
  // 2. Stamina Regen top-up (only while vanilla's own refill flows)
  try { if (m != null && best[@L_S@] > 0) staminaRegen(store, cb, ref, m, bo[@E_SR@ * 5 + best[@L_S@]], secs); }
  catch (Throwable t) { if (!F_STAM) { F_STAM = true; @PKG@.AccStore.warn("Stamina Regen from accessories failed (logged once): " + t); } }
  // 3. Regeneration: a percent of the FULL current max Health every regenEverySeconds (the Health bar the item text names)
  try {
    int rt = best[@L_R@];
    if (m != null && rt > 0) {
      c[1] = c[1] + 1.0f;
      if (c[1] >= (float) @PKG@.AccDefs.REGEN_EVERY) {
        c[1] = 0.0f;
        int hi = @DST@.getHealth();
        @ESV@ hv = hi < 0 ? null : m.get(hi);
        if (hv != null) {
          float hnow = hv.get();
          float hmax = hv.getMax();
          float amt = hmax * bo[@E_RP@ * 5 + rt] / 100.0f;
          if (hnow > 0.0f && hnow < hmax) {
            if (hnow + amt > hmax) amt = hmax - hnow;
            m.addStatValue(hi, amt);
          }
        }
      }
    } else c[1] = 0.0f;
  } catch (Throwable t) { if (!F_HEAL) { F_HEAL = true; @PKG@.AccStore.warn("Regeneration from accessories failed (logged once): " + t); } }
  // 4. movement: Speed + Feather (jump height, less fall damage) through the shared protocol (source accessories.talismans, layer
  //    pct, fractions: 0.10 = +10%, fall -0.40 = 40% less)
  try { move(u, pr, cb, ref, (bo[@E_SP@ * 5 + best[@L_SP@]] + (float) pw[7]) / 100.0f, bo[@E_JU@ * 5 + best[@L_FE@]] / 100.0f, 0.0f - bo[@E_FA@ * 5 + best[@L_FE@]] / 100.0f); }
  catch (Throwable t) { if (!F_MOVE) { F_MOVE = true; @PKG@.AccStore.warn("accessory Speed / Feather failed (logged once): " + t); } }
  // 5. combat stats to SkyyGear: ONE text per player in gear:extra:<uuid> (written only when it changes; AccGear's back-off rules)
  try { @PKG@.AccGear.publish(u, pr.getUsername(), @PKG@.AccGear.textOf2(best, pw), System.currentTimeMillis()); }   // 0.5.22: + the Power
  catch (Throwable t) { if (!F_GEAR) { F_GEAR = true; @PKG@.AccStore.warn("accessory combat stats for SkyyGear failed (logged once): " + t); } }
  // 6. the one-time 0.5 notice
  try { @PKG@.AccNotice.check(pr, u); }
  catch (Throwable t) { if (!F_NOTE) { F_NOTE = true; @PKG@.AccStore.warn("the 0.5 notice failed (logged once): " + t); } }
  // 7. 0.5.6: the Lantern recipe knowledge follows SkyyCollections' Tree Sap tiers (AccKnow never throws)
  @PKG@.AccKnow.tick(ref, store, u);
}""".replace("@E_HF@", str(KIND_E["maxHealth"])).replace("@E_SF@", str(KIND_E["maxStamina"])).replace("@E_SR@", str(KIND_E["staminaRegen"]))
     .replace("@E_MP@", str(KIND_E["manaPct"])).replace("@E_MF@", str(KIND_E["manaFloor"])).replace("@E_RP@", str(KIND_E["healPct"]))
     .replace("@E_SP@", str(KIND_E["speedPct"])).replace("@L_H@", str(ENTRIES[KIND_E["maxHealth"]][1]))
     .replace("@L_S@", str(ENTRIES[KIND_E["maxStamina"]][1])).replace("@L_M@", str(ENTRIES[KIND_E["manaPct"]][1]))
     .replace("@L_R@", str(ENTRIES[KIND_E["healPct"]][1])).replace("@L_SP@", str(ENTRIES[KIND_E["speedPct"]][1]))
     .replace("@E_JU@", str(KIND_E["jumpPct"])).replace("@E_FA@", str(KIND_E["fallPct"])).replace("@L_FE@", str(ENTRIES[KIND_E["fallPct"]][1])))
assert ENTRIES[KIND_E["staminaRegen"]][1] == ENTRIES[KIND_E["maxStamina"]][1] and ENTRIES[KIND_E["manaFloor"]][1] == ENTRIES[KIND_E["manaPct"]][1]
assert ENTRIES[KIND_E["jumpPct"]][1] == ENTRIES[KIND_E["fallPct"]][1], "Feather's jump and fall are one line"

# ================= 0.5.4 AccLanternSys: the Lantern on every player (EntityTickingSystem, query = PlayerRef, no group: the world thread, one
# player after another - isParallel is not overridden), AccLanternHelp: every helper entity (query = our marker) and (the fix round)
# AccLanternHide: every viewer (query = EntityViewer, the tracker's find-visible group after CollectVisible) =================
# ONE registerSystem per class (setup). All three only read the engine components and call AccLantern (the harness runs the same code).
lsys.addConstructor(CtNewConstructor.make("public AccLanternSys() { super(); }", lsys))
JF(lsys, "public static boolean FAILED = false;")
JM(lsys, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_PR;
}""")
JM(lsys, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PKG@.AccLantern.T_PR);
    if (pr == null) return;
    @PKG@.AccLantern.step(pr.getUuid(), ref, store, cb, dt);
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern failed (logged once): " + t); }
  }
}""")
lhs.addConstructor(CtNewConstructor.make("public AccLanternHelp() { super(); }", lhs))
JF(lhs, "public static boolean FAILED = false;")
JM(lhs, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_MARK;
}""")
JM(lhs, LANJ(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PKG@.AccLanternMark m = (@PKG@.AccLanternMark) chunk.getComponent(idx, @PKG@.AccLantern.T_MARK);
    java.util.UUID u = null;
    if (m != null) u = m.owner;
    int sl = 0;
    if (m != null) sl = m.slot;
    if (@PKG@.AccLantern.keepSlot(u, sl, ref, store)) return;   // 0.5.5: the ring lights too
    cb.tryRemoveEntity(ref, @RRS@.REMOVE);
    @PKG@.AccLantern.ORPHANS.incrementAndGet();
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern helper clean-up failed (logged once): " + t); }
  }
}"""))
# AccLanternHide (the fix round): THE REACH LIGHT IS THE WEARER'S OWN. Query = the EntityViewer (every viewer), group = the entity tracker's
# FIND_VISIBLE_ENTITIES_GROUP, AFTER CollectVisible - exactly the vanilla SpectatorSystems$HideFromNonSpectators / HideFromPlayer place:
# ClearEntityViewers empties the visible sets BEFORE the group, CollectVisible fills them, we take other wearers' helpers out, and only
# after the group AddToVisible turns what is left into Visible.visibleTo (the viewers DynamicLightTracker / the move tracker / SendPackets
# serve). A world without helpers is skipped (getEntityCountFor, the HideFromNonSpectators short cut). isParallel not overridden (false).
lhd.addConstructor(CtNewConstructor.make("public AccLanternHide() { super(); }", lhd))
JF(lhd, "public static boolean FAILED = false;")
# 0.5.12: the store's recorded helpers (AccLantern.helpersIn) from the system tick to its entity ticks - same thread (sequential group)
JF(lhd, "public static final java.lang.ThreadLocal KNOWN = new java.lang.ThreadLocal();")
JF(lhd, "public static final java.util.concurrent.atomic.AtomicLong FAST = new java.util.concurrent.atomic.AtomicLong();")
JF(lhd, "public static final java.util.concurrent.atomic.AtomicLong WALKS = new java.util.concurrent.atomic.AtomicLong();")
lhd.addField(CtField.make(LANJ("public static final java.util.Set DEPS = java.util.Collections.singleton(new @SDP@(@ORD@.AFTER, @CVS@.class));"), lhd))
JM(lhd, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PKG@.AccLantern.T_EV;
}""")
JM(lhd, LANJ(r"""
public @SGR@ getGroup() {
  return @ETR@.FIND_VISIBLE_ENTITIES_GROUP;
}"""))
JM(lhd, r"""
public java.util.Set getDependencies() {
  return DEPS;
}""")
JM(lhd, r"""
public void tick(float dt, int systemIndex, @ST@ store) {
  if (@PKG@.AccLantern.T_MARK == null || @PKG@.AccLantern.T_EV == null || store == null) return;
  if (store.getEntityCountFor((@QRY@) @PKG@.AccLantern.T_MARK) == 0) return;
  Object[] k = null;
  try { k = @PKG@.AccLantern.helpersIn(store); } catch (Throwable t) { k = null; }
  KNOWN.set(k);
  super.tick(dt, systemIndex, store);
  KNOWN.set(null);
}""")
JM(lhd, LANJ(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @EVW@ v = (@EVW@) chunk.getComponent(idx, @PKG@.AccLantern.T_EV);
    if (v == null) return;
    java.util.UUID me = null;
    @HPM@ hm = null;
    if (@PKG@.AccLantern.T_PR != null) {
      @PR@ pr = (@PR@) chunk.getComponent(idx, @PKG@.AccLantern.T_PR);
      if (pr != null) { me = pr.getUuid(); hm = pr.getHiddenPlayersManager(); }
    }
    Object[] k = (Object[]) KNOWN.get();
    if (k != null && ((Boolean) k[2]).booleanValue()) {
      FAST.incrementAndGet();
      @PKG@.AccLantern.hideKnown(me, hm, v.visible, k);
    } else {
      WALKS.incrementAndGet();
      @PKG@.AccLantern.hideFrom(me, hm, v.visible, cb);   // the safety net: an unrecorded marked entity in this store this tick
    }
  } catch (Throwable t) {
    if (!FAILED) { FAILED = true; @PKG@.AccStore.warn("Lantern: hiding reach lights from other players failed (logged once): " + t); }
  }
}"""))

# ================= 0.5.2: the Workbench tab (tools/skyywbtab.py; WB.probe stops the build when an engine fact it relies on changed)
print(WB.probe(pool))
assert tuple(b[0] for b in ACTIVE) == WB.BENCHES and dict((b[0], b[3]) for b in ACTIVE) == WB.BENCH_TIERS, \
    "0.5.2: the bench table changed - update BENCHES / BENCH_TIERS in tools/skyywbtab.py (the tab order)"
WB_CLASSES = WB.emit(pool, CtField, CtNewMethod, CtNewConstructor, PKG, True, "SkyyAccessories")   # OWNER

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyAccessoriesPlugin({JPI} init) {{ super(init); }}", pl))
_READY = ("[SkyyAccessories] %s ready (%s) - /charms (/charm, /ch; lines, power; admins: give, givetier, reload), Void Charms on the Character hub; %d bench "
          "accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench), Campfire accessory for quick "
          "inventory cooking, the Lantern line (its wearer glows like a torch for everyone; hidden lights above them light farther for the wearer), %d booster lines in the gear rarities Normal to Legendary (%d items + %d old ids, hidden from the creative library; combat stats to SkyyGear "
          "through gear:extra, Feather's jump and fall through the movement protocol), bag up to %d slots, one "
          "bag per profile when SkyyProfiles runs; Craft tab on the bag page (no bench), crafted accessories go straight into the bag, benches use "
          "the bag (acc:fn:bag); accessories are crafted and upgraded only in the bag (one row per line, Benches / Combat / Gathering); the old bag item is retired (removed from inventories, journaled in retired.log); drop-only lines upgrade only in the bag; ") % (VERSION, KIT_ID, sum(b[3] for b in ACTIVE),
                                                       sum(b[3] for b in BENCHES if b[0] in RETIRED), len(BOOSTERS), len(LINE_IDS),
                                                       len(FOLDED) * len(LEGACY_WORDS), CAP)
JM(pl, r"""
public void setup() {
  @PKG@.AccStore.LOG = getLogger();
  @PKG@.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  @PKG@.AccCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("config.properties");   // 0.4.4
  String m51 = @PKG@.AccCfg.migrate051();   // 0.5.1: a 0.5 file gets the Stamina numbers ONCE (History copy first), before the loader
  String m55 = @PKG@.AccCfg.migrate055();   // 0.5.5: a lantern.height line still at 128 becomes 64 ONCE (History copy first), before the loader
  String m518 = @PKG@.AccCfg.migrate0518();   // 0.5.18: lantern.reach / lantern.lights lines still at the 0.5.5 defaults get the new ones ONCE (History copy first)
  String cs = @PKG@.AccCfg.load(true);   // 0.5: a first start writes the 0.5 file; an existing 0.4.x file is updated ONCE (before CfgPub.start)
  if (m51.length() > 0) cs = cs + "; " + m51;
  if (m55.length() > 0) cs = cs + "; " + m55;
  if (m518.length() > 0) cs = cs + "; " + m518;
  @PKG@.AccNotice.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("notices.properties");   // 0.5
  @PKG@.AccNotice.load();
  @PKG@.AccStarter.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("retired");   // 0.5.22: the bag item retirement's one-time line per profile
  @PKG@.AccStarter.LOGF = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("retired.log");   // 0.5.22: its journal
  @PKG@.AccPower.FILE = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("power.properties");   // 0.5.22: Accessory Power settings
  @PKG@.AccPower.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("power");   // 0.5.22: the Power each profile picked
  String pws = @PKG@.AccPower.load();
  @PKG@.AccCraft.LOGF = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("crafts.log");   // 0.5.18: the bag craft journal
  com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction.registerSimple(this, @PKG@.SkyyAccessoriesPlugin.class, "SkyyAccBag", new @PKG@.AccPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.AccCmd());
  @PKG@.AccStore.bridge().put("acc:fn:has", new @PKG@.AccFn());
  @PKG@.AccStore.bridge().put("acc:defs", @PKG@.AccDefs.defsText());     // 0.5: every rarity of every line (the later loot pass)
  @PKG@.AccStore.bridge().put("acc:fn:give", new @PKG@.AccGiveFn());     // 0.5: give a booster to an online player (n given now, 0 none, -1 queued: never retry)
  @PKG@.AccStore.bridge().put("acc:fn:bag", new @PKG@.AccBagFn());       // 0.5.19: benches + /craft count and take accessories from the bag (SkyySacks 0.8.11)
  @PKG@.AccStore.bridge().put("acc:fn:power", new @PKG@.AccPowerFn());   // 0.5.22: the Power get / set (SkyyWardrobe loadouts)
  @PKG@.AccStore.bridge().put("once:item:" + @PKG@.AccDefs.BAG, new @PKG@.AccPowerFn(1));   // 0.5.22: the retired bag item never goes into a starter kit
  String hubTab = @PKG@.AccHubOpen.register();   // 0.5.22: the Character hub's Void Charms tab
  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  @PKG@.AccLantern.bind();   // 0.5.4: the Lantern - the engine's component types once, then our marker and the three systems (one each)
  @PKG@.AccLantern.T_MARK = getEntityStoreRegistry().registerComponent(@PKG@.AccLanternMark.class, new @PKG@.AccLanternMarkSup());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHelp());
  getEntityStoreRegistry().registerSystem(new @PKG@.AccLanternHide());   // the fix round: the reach light is the wearer's own
  getEntityStoreRegistry().registerSystem(new @PKG@.AccAutoPre());    // 0.5.18: auto-equip after a bench / pocket / /craft craft (Pre)
  getEntityStoreRegistry().registerSystem(new @PKG@.AccAutoPost());   // 0.5.18: ... and after a timed craft's unit (Post)
  /* 0.5.22: no lifelong bag item setup */ @PKG@.AccLantern.pubLamp();   // 0.5.10: acc:lamp = "on" (the mining helmet light reader is here)
  @PKG@.MoveSync.checkProto("SkyyAccessories");
@WBSETUP@  this.ticker = com.hypixel.hytale.server.core.HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.AccTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log(@READY@ + cs + "; " + pws + "; hub tab " + hubTab + "; bridge acc:power:<uuid>, acc:fn:power, skill:bonus source accessories; admin settings: SkyWynn Menu -> Server Setup -> Void Charms or /charms reload");
  @PKG@.AccSnd.load(getDataDirectory().resolveSibling("Skyy_SkyyAccessories"));   // 0.5.14 sound pass: sounds.properties (before the kit)
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}""".replace("@READY@", jlit(_READY)).replace("@WBSETUP@", WB.setup_java(PKG)))
pl.addMethod(CtNewMethod.make(WB.start_java(PKG), pl))   # 0.5.2: the Workbench tab once every asset pack is loaded
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:give"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:bag"); } catch (Throwable t) { }   // 0.5.19
  try { com.skyy.accessories.AccStore.bridge().remove("acc:defs"); } catch (Throwable t) { }
  try { com.skyy.accessories.AccGear.shutdownAll(); } catch (Throwable t) { }   // 0.5 part 2: our gear:extra texts + movement entries
  try { com.skyy.accessories.AccLantern.clearAll(); } catch (Throwable t) { }   // 0.5.4: the Lantern state (helpers: NonSerialized + a 5 s despawn)
  try { com.skyy.accessories.AccStore.bridge().remove("acc:lamp"); } catch (Throwable t) { }   // 0.5.10
  try { com.skyy.accessories.AccStore.bridge().remove("acc:lamp:reach"); } catch (Throwable t) { }   // 0.5.18
  try { com.skyy.accessories.AccNotice.save(); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStarter.flush(true); } catch (Throwable t) { }   // 0.5.17: every pending marker now (0.5.22: the retirement line)
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:power"); } catch (Throwable t) { }   // 0.5.22
  try { com.skyy.accessories.AccStore.bridge().remove("once:item:" + com.skyy.accessories.AccDefs.BAG); } catch (Throwable t) { }   // 0.5.22
  try { com.skyy.accessories.AccPower.shutdownAll(); } catch (Throwable t) { }   // 0.5.22: our skill:bonus sources + acc:power keys
  try { com.skyy.accessories.AccHubOpen.unregister(); } catch (Throwable t) { }   // 0.5.22: the hub tab (only while it still holds ours)
  try { com.skyy.accessories.CfgPub.shutdown(); } catch (Throwable t) { }   // 0.4.4: pending config saves + change-log lines now
  super.shutdown();
}""", pl))

for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, lmk, lms, lan, lsys, lhs, lhd, kn, ast_, acr_, aat_, apre, apst, bfn_, apw_, apf_, apc_, aho_, HUBB):   # 0.5.22: + AccPower, AccPowerFn, AccPowerCmd, AccHubOpen, HubBar;   # 0.5.19: + AccBagFn; 0.5.4: the Lantern (AccNv, AccNightVision gone); 0.5.6: + AccKnow; 0.5.17: + AccStarter; 0.5.18: + AccCraft, AccAutoTask, AccAutoPre, AccAutoPost
    c.writeFile(OUT)
for c in WB_CLASSES:   # 0.5.2: WbRank, WbTab, WbAssetL
    c.writeFile(OUT)
# 0.5.22: the lifelong bag classes (AccOnce*, tools/skyyonce.py) are gone with the bag item
kit.write(OUT)   # 0.4.4: deferred kit checks (0.5: AccCfg.reload / checkBoost exist with the right signatures), then the 7 kit classes
print("classes written (+%d config kit)" % len(kit.classes))

# ================= assets: items + lang =================
def item(iid, icon, quality, recipe_in, bench_req, page_id=None, visual=None):
    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
      "Categories": ["Items.Tools"],
      "Icon": icon,
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": bench_req},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
    }
    if visual:
        node.update(visual)   # 0.2 review fix: talismans look like the vanilla crystal they are made from (0.1 placeholder: backpack)
    if page_id:
        node["Interactions"] = {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    return node

WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": [WB.TAB_ID]}]   # 0.5.2: the new tab (was the vanilla Crafting tab)
# 0.2: every recipe input / icon is checked against the vanilla Assets.zip (build fails on a typo instead of a broken recipe in game)
import zipfile
_ASSETS = zipfile.ZipFile(ASSETS_ZIP)   # 0.5.16: the cached copy (read-only)
_ITEMS = {}
for _n in _ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        _ITEMS[os.path.basename(_n)[:-5]] = _n
_COMMON = set(n for n in _ASSETS.namelist() if n.startswith("Common/"))
_RTYPES = set(os.path.basename(n)[:-5] for n in _ASSETS.namelist() if n.startswith("Server/Item/ResourceTypes/") and n.endswith(".json"))
_VNAMES = {}
for _l in _ASSETS.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if _l.startswith("items.") and ".name" in _l and "=" in _l:
        _k, _v = _l.split("=", 1)
        _VNAMES[_k.strip()[len("items."):-len(".name")]] = _v.strip()
def vname(iid):
    """vanilla display name (en-US server.lang), e.g. Ingredient_Bar_Iron -> Iron Ingot"""
    return _VNAMES.get(iid) or iid.replace("Ingredient_", "").replace("Rock_Gem_", "").replace("_", " ")
def need_item(iid):
    assert iid in _ITEMS, "unknown vanilla item id: " + iid
def mat(m, q):
    """recipe input: ItemId for items, ResourceTypeId for resource types (0.1 bug: the Farming Bench upgrades used
    ItemId Wood_Softwood_Trunk etc. - those are ResourceTypes in vanilla Bench_Farming TierLevels, so the recipes could not resolve)"""
    if m in _ITEMS: return {"ItemId": m, "Quantity": q}
    assert m in _RTYPES, "unknown vanilla item / resource type: " + m
    return {"ResourceTypeId": m, "Quantity": q}
def icon_of(iid):
    """the vanilla item's own Icon (follows Parent), checked to exist under Common/"""
    seen = 0
    cur = iid
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        if d.get("Icon"):
            assert "Common/" + d["Icon"] in _COMMON, "missing icon file for %s: %s" % (iid, d["Icon"])
            return d["Icon"]
        cur = d.get("Parent"); seen += 1
    raise SystemExit("no icon for " + iid)
VISUAL_KEYS = ("Model", "Texture", "IconProperties", "Scale", "PlayerAnimationsId", "ItemSoundSetId")
def visual_of(iid):
    """held / dropped look of a vanilla item (follows Parent, the child's value wins); Model and Texture checked to exist under Common/"""
    out = {}
    cur = iid
    seen = 0
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        for k in VISUAL_KEYS:
            if k in d and k not in out: out[k] = d[k]
        cur = d.get("Parent"); seen += 1
    assert "Model" in out and "Texture" in out, "no model for " + iid
    for k in ("Model", "Texture"):
        assert "Common/" + out[k] in _COMMON, "missing %s file for %s: %s" % (k, iid, out[k])
    return out
FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
BAG_REQ = FIELD_REQ + WB_REQ   # 0.5.2: the Void Charms stays pocket crafting AND lists first in the Workbench tab (vanilla two-requirement pattern)
QUAL = [QUAL_IDS[BENCH_RARITY[min(_t, 7)]] for _t in range(8)]   # 0.5: bench tier -> Skyy_Acc_* (I Normal .. IV+ Legendary; = AccDefs.rarityOf)
# 0.5.1: OLD IDS OUT OF THE CREATIVE LIBRARY (Skyy: "this one appears twice in creative"). The legacy booster ids and the retired bench
# accessories stay real items (owned copies load, render, show their tooltip and convert in the bag as before) but get the engine's
# item library filter: "Variant": true (filtered out of the library by default) and no "Categories" (no library tab even with the
# library's Show Variants toggle on). The current items keep Categories ["Items.Tools"] and no Variant (_hidden_checks below).
RETIRED_IDS = ["Skyy_Accessory_%s_T%d" % (_b[0], _t) for _b in BENCHES if _b[0] in RETIRED for _t in range(1, _b[3] + 1)]
HIDDEN_IDS = LEGACY_IDS + RETIRED_IDS + [NV_ID]   # 0.5.4: + the retired Night Vision
assert len(LEGACY_IDS) == 20 and len(RETIRED_IDS) == 5 and len(set(HIDDEN_IDS)) == 26, (len(LEGACY_IDS), RETIRED_IDS)
assert all(py_legacy(_i) for _i in LEGACY_IDS) and not set(HIDDEN_IDS) & set(LINE_IDS)


def hide_item(iid, node):
    """0.5.1: keep an old id out of the creative item library (the Item codec's Variant + Categories, proven by _variant_proof)"""
    assert iid in HIDDEN_IDS, "0.5.1: only the old ids are hidden: " + iid
    del node["Categories"]
    node["Variant"] = True
    return node


files = {}
lang = []
# ---- 0.5 the six quality assets (spec 5.2): the vanilla Common.json field set, SkyyGear's frame art, the kit's rarity colours, the
# label under general.qualities.<id> AND server.general.qualities.<id> (the SkyySacks pattern). Fabled and Mythic ship unused (spec 4.1).
_VQF = set(json.loads(_ASSETS.read("Server/Item/Qualities/Common.json").decode("utf-8-sig")).keys())
_PARTS = set(os.path.basename(n)[:-len(".particlesystem")] for n in _ASSETS.namelist() if n.endswith(".particlesystem"))
def _tex(p):
    q = "Common/" + p
    return q in _COMMON or (q.endswith(".png") and q[:-4] + "@2x.png" in _COMMON)
for _r in range(1, len(DISPLAY)):
    _nm = DISPLAY[_r]
    _tt, _slot, _part = QUAL_ART[_nm]
    _q = {"QualityValue": _r,
          "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _tt,
          "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _tt,
          "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
          "TextColor": SUI.RARITY[_nm].lower(),
          "LocalizationKey": "server.general.qualities." + QUAL_IDS[_r],
          "VisibleQualityLabel": True,
          "RenderSpecialSlot": True,
          "ItemEntityConfig": {"ParticleSystemId": _part}}
    assert set(_q) == _VQF, "0.5: quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _VQF)
    assert _q["QualityValue"] < 8, "0.5: a quality at 8 or more is 'technical' for SkyyAuctions"
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert _tex(_q[_k]), "0.5: quality texture missing in Assets.zip: " + _q[_k]
    assert _part in _PARTS, "0.5: drop particle missing in Assets.zip: " + _part
    files["Server/Item/Qualities/%s.json" % QUAL_IDS[_r]] = json.dumps(_q, indent=2)
    lang.append("general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
    lang.append("server.general.qualities.%s=%s" % (QUAL_IDS[_r], _nm))
# ---- 0.5.8 THE NEW ACCESSORY BAG LOOK: tools/art/make_bags.py (tracked, deterministic) runs IN MEMORY - its write() fills BAG_GEN, its
# clean_old() does nothing; only the Accessory Bag's 3 files ship here (the Pocket Dimension bags' files ship in SkyySacks 0.7.14)
def _bag_art():
    import importlib.util as _ilu2
    _sp = _ilu2.spec_from_file_location("make_bags", os.path.join(os.path.dirname(HERE), "tools", "art", "make_bags.py"))
    _mb = _ilu2.module_from_spec(_sp)
    _sp.loader.exec_module(_mb)
    _got = {}
    def _w(rel, data):
        assert rel not in _got, "make_bags wrote %s twice" % rel
        _got[rel] = bytes(data)
        return rel
    _mb.write = _w
    _mb.clean_old = lambda: None
    _mb.main()
    return _got
BAG_GEN = _bag_art()
BAG_MAN = json.loads(BAG_GEN["manifest.json"].decode("utf-8"))["accessory_bag"]
assert BAG_MAN["item"] == BAG, BAG_MAN["item"]
def _bag_nc(p):
    assert p.startswith("Common/"), p
    return p[len("Common/"):]
BAG_VIS = {"Model": _bag_nc(BAG_MAN["model_path"]), "Texture": _bag_nc(BAG_MAN["texture_path"]), "Icon": _bag_nc(BAG_MAN["icon_path"]),
           "IconProperties": BAG_MAN["icon_properties"]}
BAG_FILES = dict((p, BAG_GEN[p]) for p in (BAG_MAN["model_path"], BAG_MAN["texture_path"], BAG_MAN["icon_path"]))
for _p in BAG_FILES:
    assert _p not in _COMMON, "0.5.8: the bag art would override a vanilla file: " + _p
print("bag art: tools/art/make_bags.py ran in memory (%d files); the Void Charms ships %d (%s)" % (
    len(BAG_GEN), len(BAG_FILES), ", ".join(sorted(BAG_FILES))))
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, BAG_VIS["Icon"], QUAL_IDS[2],
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], BAG_REQ, "SkyyAccBag",
    visual=BAG_VIS), indent=2)   # 0.5.8: the new look through visual= (was the vanilla backpack + Utility_Bag_Seed icon)
_bag_node = json.loads(files["Server/Item/Items/Utility/%s.json" % BAG])   # 0.5.20: lifelong - no recipe (AccStarter gives it, /accbag brings it back)
del _bag_node["Recipe"]
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(_bag_node, indent=2)
for _p, _b in BAG_FILES.items():
    assert _p not in files, _p
    files[_p] = _b
lang.append("items.%s.name=Void Charms" % BAG); lang.append("server.items.%s.name=Void Charms" % BAG)
d = ("Right-click to open. Holds your accessories. Bench accessories in it let /craft make that bench's recipes straight from your "
     "inventory; stat accessories in it add their bonus (only your best of each line counts); the Omni accessory counts as every bench "
     "accessory. It stays with you: it can't be dropped, stored or sold, and /accbag brings it back.")
lang.append("items.%s.description=%s" % (BAG, d)); lang.append("server.items.%s.description=%s" % (BAG, d))
count = 0
retired_count = 0
# 0.4.2: descriptions of the retired bench accessories (asset kept, no recipe)
RETIRED_TAIL = " This accessory does nothing and cannot be equipped; if one is still in your Void Charms, Unequip takes it out."
RETIRED_DESC = {
    "Alchemybench": "Retired. Alchemy is a skill now: brew at a real Alchemy Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
    "Cookingbench": "Retired. Cooking is a skill now: cook at a real Cooking Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
}
assert sorted(RETIRED_DESC) == sorted(RETIRED)
for bench_id, bench_item, name, tiers, ups in BENCHES:
    for t in range(1, tiers + 1):
        iid = "Skyy_Accessory_%s_T%d" % (bench_id, t)
        if t == 1:
            need_item(bench_item)
            rin = [{"ItemId": bench_item, "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}]
        else:
            rin = [{"ItemId": "Skyy_Accessory_%s_T%d" % (bench_id, t - 1), "Quantity": 1}] + [mat(m, q) for m, q in ups[t - 2]]   # 0.2: mat() fixes resource types
        icon = "Icons/ItemsGenerated/%s.png" % ("Bench_Architects" if bench_item == "Bench_Builders" else bench_item)
        node = item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        d = "Put it in your Void Charms to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        if bench_id == "Campfire":   # 0.4.3: back as quick inventory cooking (SkyyCooking cook:fn:campfire through SkyySacks /craft)
            d = CAMPFIRE_DESC
        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
            hide_item(iid, node)  # 0.5.1: not in the creative library
            disp += " (retired)"
            d = RETIRED_DESC[bench_id]
            retired_count += 1
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1
need_item("Ingredient_Bar_Copper"); need_item("Ingredient_Fabric_Scrap_Cotton"); assert "Wood_Trunk" in _RTYPES

# ---- 0.5 THE BOOSTER ITEMS (spec 2.2, 5.6, 5.7): one item per rarity of every line, generated from the booster table.
# Look: the line's crystal fragment MODEL for every rarity; icons Normal crystal fragments, Unique small cluster, Rare large cluster,
# Legendary the gem (each rarity its own icon). Names "<Rarity> <Line> Accessory". Tooltip = vanilla item-text markup: the stat line
# first (<color is="#ffffff">), what it does, the one-per-line rule with the next rarity, an italic flavour line; a line break is the
# two characters \n inside one lang line (a real newline would break the file).
TIP_NL = "\\n"
def _w(t):
    return '<color is="#ffffff">%s</color>' % t
def _n(v):
    return "%g" % v
TIPS = {   # kind -> (stat line, what it does) at one rarity; vals = {kind: number}; kinds without an entry ride along (manaFloor)
    "maxHealth": lambda v: (_w("+%s max Health" % _n(v["maxHealth"])) + " while in your Void Charms.",
                            "Raises your maximum Health; the bar fills up by normal means."),
    "maxStamina": lambda v: (_w("+%s max Stamina" % _n(v["maxStamina"])) + " and " + _w("+%s%% Stamina Regen" % _n(v["staminaRegen"])) +
                             " while in your Void Charms.",
                             "Your Stamina refills %s%% faster whenever it refills (not while you sprint, glide or block)." % _n(v["staminaRegen"])),
    "manaPct": lambda v: (_w("+%s%% max Mana" % _n(v["manaPct"])) + " (at least +%s) while in your Void Charms." % _n(v["manaFloor"]),
                          "A percent of the Mana your level, skills and gear give."),
    "healPct": lambda v: (_w("Heals %s%% of your max Health" % _n(v["healPct"])) + " every %d seconds while in your Void Charms." % REGEN_EVERY,
                          "Works in combat too."),
    "speedPct": lambda v: (_w("+%s%% movement speed" % _n(v["speedPct"])) + " while in your Void Charms.", "Adds on top of Acrobatics."),
    # part 2 (spec 5.7): the stat line first, what it affects, the requirement (no mod names - players do not know "SkyyGear")
    "str": lambda v: (_w("+%s Strength" % _n(v["str"])) + " while in your Void Charms.",
                      "More damage with melee, arrows, thrown weapons and staff melee." + TIP_NL + "Works with gear weapons or bare hands."),
    "mp": lambda v: (_w("+%s Magical Power" % _n(v["mp"])) + " while in your Void Charms.",
                     "More damage with spells." + TIP_NL + "Spell shots only (wand, staff, spellbook)."),
    "def": lambda v: (_w("+%s Defense" % _n(v["def"])) + " while in your Void Charms.",
                      "Takes a little off every hit." + TIP_NL + "Against hits from mobs and players."),
    "cc": lambda v: (_w("+%s%% Crit Chance" % _n(v["cc"])) + " and " + _w("+%s%% Crit Damage" % _n(v["cd"])) + " while in your Void Charms.",
                     "A critical hit does double damage, and Crit Damage makes it hit even harder." + TIP_NL +
                     "Works with gear weapons or bare hands."),
    "fallPct": lambda v: (_w("-%s%% fall damage" % _n(v["fallPct"])) + " and " + _w("+%s%% jump height" % _n(v["jumpPct"])) +
                          " while in your Void Charms.", "Softer landings and higher jumps, on top of Acrobatics."),
}
def booster_name(li, t):
    return "%s %s Accessory" % (DISPLAY[t], BOOSTERS[li][2])
def booster_desc(li, t, legacy=False):
    b = BOOSTERS[li]
    vals = dict((kind, v[t - 1]) for _st, kind, v in b[5])
    main = [k for k in vals if k in TIPS]
    assert len(main) == 1, "0.5: line %s needs exactly one tooltip template among %s" % (b[1], list(vals))
    first, what = TIPS[main[0]](vals)
    nxt = ("Next: %s (upgrade it at a Workbench)." if b[8] is not None else "Next: %s.") % booster_name(li, t + 1) if t < 4 else ""
    rule = "Only your best %s Accessory counts. " % b[2] + (nxt if t < 4 else "Legendary is the top rarity.")
    # part 1 review finding 4: an old copy can be refused as a tie (an equal or better one already equipped) and never converted
    old = ""
    if legacy:
        old = TIP_NL + "An older copy: put it in your Void Charms once and it becomes the current one" + (
            " (only that one can be upgraded)" if t < 4 else "") + ". If it is refused, an equal or better one is already equipped."
    return first + TIP_NL + what + TIP_NL + rule + old + TIP_NL + TIP_NL + "<i>%s</i>" % b[7]
# ---- 0.5.7 OUR OWN BOOSTER ICONS (Skyy 2026-10-07): drawn at BUILD time by the tracked generator tools/art/make_accessory_icons.py
# (pure Python, our own art, never opens Assets.zip, deterministic) - its make() + to_img() + skyyart.png_encode, the bytes its main()
# writes - shipped in the jar at Common/Icons/ItemsGenerated/SkyyAccessories_<Line>_<Rarity>.png. Every booster item (40 line ids,
# 4 Lantern ids, the 20 hidden legacy ids at their tier) points its Icon there; the 3D model stays the vanilla look (visual_of).
import importlib.util as _ilu
_ART = os.path.join(os.path.dirname(HERE), "tools", "art", "make_accessory_icons.py")
_spec = _ilu.spec_from_file_location("make_accessory_icons", _ART)
MAI = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(MAI)
import skyyart as _SA   # the generator's own PNG codec (tools/skyyart.py)
OWN_RARITY = [None] + [_r[0] for _r in MAI.RARITIES]
assert OWN_RARITY == [None, "Normal", "Unique", "Rare", "Legendary"], OWN_RARITY
assert sorted(_l[1] for _l in MAI.LINES) == sorted([_b[0] for _b in BOOSTERS] + [LAN_FAM]), [_l[1] for _l in MAI.LINES]
OWN_ICON = {}   # (family key, tier 1..4) -> the item's Icon path (relative to Common/, like vanilla)
OWN_PNG = {}    # the same key -> PNG bytes
for _name, _fam, _what, _fn in MAI.LINES:
    for _t in range(1, 5):
        _cur, _leg = MAI.item_ids(_fam, _t)
        if _fam == LAN_FAM:
            assert _cur == LAN_IDS[_t - 1] and _leg == [], (_cur, _leg)
        else:
            _b = BOOSTERS[[_x[0] for _x in BOOSTERS].index(_fam)]
            assert _cur == booster_id(_b, _t), ("0.5.7: the generator's id differs from the build's", _cur, booster_id(_b, _t))
            assert _leg == (["Skyy_Talisman_%s_%s" % (_fam, _w) for _w, _lt in LEGACY_WORDS if _lt == _t] if _b[9] == "word" else []), _leg
        _px = MAI.make(_fn, _t - 1)
        assert len(_px) == 64 and all(len(_row) == 64 for _row in _px), (_name, _t)
        assert all(_px[_y][_x][3] == 0 for _y in range(64) for _x in range(64)
                   if _x < MAI.MARGIN or _y < MAI.MARGIN or _x >= 64 - MAI.MARGIN or _y >= 64 - MAI.MARGIN), ("2 px clear margin", _name, _t)
        _png = _SA.png_encode(MAI.to_img(_px))
        _rel = "Icons/ItemsGenerated/SkyyAccessories_%s_%s.png" % (_name, OWN_RARITY[_t])
        assert "Common/" + _rel not in _COMMON, "0.5.7: our icon would override a vanilla file: " + _rel
        OWN_ICON[(_fam, _t)] = _rel
        OWN_PNG[(_fam, _t)] = _png
        files["Common/" + _rel] = _png
# 0.5.16 THE METAL LANTERN ICONS (Skyy 2026-10-15: "if it takes copper to craft it should look like copper"; tools/accessories_0_5_16_patch.py):
# each Lantern rarity is drawn by the same painter with the tier ramp of ITS recipe's metal bar as its metal (the generator file is not
# edited: the rarity's metal is swapped for this one call, then restored - every other icon was drawn above and stays byte-identical).
LAN_METAL = [None, "Copper", "Copper", "Iron", "Thorium"]   # rarity 1..4 -> the metal bar its recipe takes (asserted in _metal_lantern_checks)
LAN_ICON_RAMP = {   # ui-data (art, not UI): the light-armor / mining sheets' tier ramps (outline .. highlight), shared SkyWynn tier hues
    "Copper": MAI.ramp('#3b1a0c', '#8a4220', '#c26a34', '#e89558', '#ffc48e'),   # ui-data
    "Iron": MAI.ramp('#24282e', '#5c646e', '#8e97a2', '#bcc4cc', '#eef2f5'),     # ui-data
    "Thorium": MAI.ramp('#1c3324', '#3f6b4a', '#5e9468', '#8cc08e', '#cdebc6'),  # ui-data
}


def lan_metal_icon(t):
    """our Lantern icon of rarity t with LAN_METAL[t]'s tier ramp as its metal (64 x 64 PNG bytes, premultiplied like every own icon)"""
    fn = [_l[3] for _l in MAI.LINES if _l[1] == LAN_FAM]
    assert len(fn) == 1
    old = MAI.RARITIES[t - 1]
    assert old[0] == OWN_RARITY[t] and len(old) == 4, old
    MAI.RARITIES[t - 1] = old[:3] + (LAN_ICON_RAMP[LAN_METAL[t]],)
    try:
        px = MAI.make(fn[0], t - 1)
    finally:
        MAI.RARITIES[t - 1] = old
    assert MAI.RARITIES[t - 1] is old
    assert len(px) == 64 and all(len(_row) == 64 for _row in px)
    assert all(px[_y][_x][3] == 0 for _y in range(64) for _x in range(64)
               if _x < MAI.MARGIN or _y < MAI.MARGIN or _x >= 64 - MAI.MARGIN or _y >= 64 - MAI.MARGIN), "0.5.16: 2 px clear margin"
    return _SA.png_encode(MAI.to_img(px))


for _t in range(1, 5):
    _mi = lan_metal_icon(_t)
    assert _mi != OWN_PNG[(LAN_FAM, _t)], "0.5.16: the %s Lantern icon must change" % OWN_RARITY[_t]
    OWN_PNG[(LAN_FAM, _t)] = _mi
    files["Common/" + OWN_ICON[(LAN_FAM, _t)]] = _mi
print("lantern icons (0.5.16): drawn with the recipe metal - %s" % ", ".join("%s %s" % (OWN_RARITY[_t], LAN_METAL[_t]) for _t in range(1, 5)))
assert len(OWN_ICON) == 44 and len(set(OWN_ICON.values())) == 44 and len(set(OWN_PNG.values())) == 44, "0.5.7: 44 distinct icons"
print("own icons: %d drawn by tools/art/make_accessory_icons.py (%d bytes), shipped under Common/Icons/ItemsGenerated/" % (
    len(OWN_PNG), sum(len(_v) for _v in OWN_PNG.values())))
tal_count = 0
legacy_count = 0
ICONS = {}
for li, b in enumerate(BOOSTERS):
    fam, adm, line, crystal, gem, stats, src, flavour, recipes, style = b
    if crystal is not None:   # crystal style: the crystal fragment model in the line's colour for every rarity (clusters / gems are blocks)
        _v = visual_of("Ingredient_Crystal_" + crystal)
        visuals = [None, _v, _v, _v, _v]
        icons = [None, icon_of("Ingredient_Crystal_" + crystal), icon_of("Rock_Crystal_%s_Small" % crystal),
                 icon_of("Rock_Crystal_%s_Large" % crystal), icon_of(gem)]
    else:                     # part 2 item style (spec 5.6): each rarity copies the model and icon of its own vanilla item
        visuals = [None] + [visual_of(x) for x in gem]
        icons = [None] + [icon_of(x) for x in gem]
    assert len(set(icons[1:])) == 4, "0.5: two rarities of the %s line share an icon: %s" % (adm, icons)
    icons = [None] + [OWN_ICON[(fam, _t)] for _t in range(1, 5)]   # 0.5.7: our own icons (the vanilla ones above stay checked, unused)
    ICONS[adm] = icons
    for t in range(1, 5):
        iid = LINE_IDS[li * 4 + t - 1]
        if recipes is None:
            rin = []                  # part 2: no recipe (admin give only until the loot pass)
        elif t == 1:
            rin = [mat(m, q) for m, q in recipes[0]]
        else:
            rin = [{"ItemId": LINE_IDS[li * 4 + t - 2], "Quantity": 1}] + [mat(m, q) for m, q in recipes[t - 1]]
        node = item(iid, icons[t], QUAL_IDS[t], rin, WB_REQ, visual=visuals[t])
        if recipes is None:
            del node["Recipe"]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, t))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, t)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, t))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, t)))
        tal_count += 1
    if style != "word":
        continue              # the new lines have no old ids
    # the old ids (0.2/0.3 Talisman / Ring / Artifact and 0.4's fifth id Legendary): asset kept so owned copies still load and render,
    # NO recipe; the look, name and text of the rarity they count as (players never see ids); equip / unequip turns them into that id
    vis = visuals[1]
    for word, lt in LEGACY_WORDS:
        iid = "Skyy_Talisman_%s_%s" % (fam, word)
        node = item(iid, icons[lt], QUAL_IDS[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
        hide_item(iid, node)      # 0.5.1: not in the creative library (Skyy saw the old Artifact next to the Legendary)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, booster_name(li, lt))); lang.append("server.items.%s.name=%s" % (iid, booster_name(li, lt)))
        lang.append("items.%s.description=%s" % (iid, booster_desc(li, lt, True))); lang.append("server.items.%s.description=%s" % (iid, booster_desc(li, lt, True)))

        legacy_count += 1
print("booster items:", tal_count, "old ids kept (no recipe):", legacy_count)

# 0.4 OMNI accessory: Workbench recipe = the max-tier accessory of every bench; counts as all of them (AccDefs.benchList); 0.5 Legendary
omni_in = []
for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: retired benches are no inputs (13 -> 10); 0.4.3: the Campfire is again (11)
    top = "Skyy_Accessory_%s_T%d" % (bench_id, tiers)
    assert "Server/Item/Items/Utility/%s.json" % top in files, top
    omni_in.append({"ItemId": top, "Quantity": 1})
assert len(omni_in) == len(ACTIVE) == 11
assert {"ItemId": "Skyy_Accessory_Campfire_T1", "Quantity": 1} in omni_in   # 0.4.3
files["Server/Item/Items/Utility/%s.json" % OMNI] = json.dumps(item(OMNI, icon_of("Rock_Gem_Diamond"), QUAL_IDS[4], omni_in, WB_REQ), indent=2)
lang.append("items.%s.name=Omni Accessory" % OMNI); lang.append("server.items.%s.name=Omni Accessory" % OMNI)
d = ("Legendary accessory. Keep it in your Void Charms and it counts as EVERY bench accessory at its highest tier (%s), so /craft shows "
     "all of their recipes. It has its own slot rule, so it can sit next to other bench accessories. Crafted at a Workbench from all %d "
     "top-tier bench accessories. Campfire dishes made through it are quick inventory cooking, like the Campfire accessory. Alchemy "
     "and Cooking are table-only, so the retired Alchemy Bench and Cooking Bench accessories are not part of it and are not covered.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in ACTIVE), len(ACTIVE))
lang.append("items.%s.description=%s" % (OMNI, d)); lang.append("server.items.%s.description=%s" % (OMNI, d))
lang.extend(WB.LANG_LINES)   # 0.5.2: the tab name (benchCategories.workbench.skyyaccessories + the server. twin)
# ---- 0.5.3 THE NIGHT VISION ITEM, RETIRED in 0.5.4: still the vanilla Lightning Essence look, Rare frame, no recipe, now hidden from the
# creative library (Variant, no Categories - hide_item) with the retired name and text; its 4 lang lines stay where 0.5.3 had them
_nvnode = item(NV_ID, icon_of(NV_LOOK), QUAL_IDS[NV_TIER], [], WB_REQ, visual=visual_of(NV_LOOK))
del _nvnode["Recipe"]
hide_item(NV_ID, _nvnode)
files["Server/Item/Items/Utility/%s.json" % NV_ID] = json.dumps(_nvnode, indent=2)
NV_NAME = "%s Accessory (retired)" % NV_LINE
NV_DESC = ("Retired. The Lantern Accessory replaced it: craft one at a Workbench. This accessory does nothing and cannot be equipped; if "
           "one is still in your Void Charms, Unequip takes it out.")
NV_LANG = ["items.%s.name=%s" % (NV_ID, NV_NAME), "server.items.%s.name=%s" % (NV_ID, NV_NAME),
           "items.%s.description=%s" % (NV_ID, NV_DESC), "server.items.%s.description=%s" % (NV_ID, NV_DESC)]
lang.extend(NV_LANG)


# ---- 0.5.4 THE LANTERN ITEMS: one per rarity, the look of a vanilla lantern (its block model + texture + icon, the Slowness Totem pattern),
# the Workbench tab recipe (Normal from vanilla items, every other rarity from the one below), vanilla-style text. Their 16 lang lines go
# last: server.lang = 0.5.3's (the Night Vision text changed in place) + these lines.
def block_visual_of(iid):
    """a vanilla block item's look for a plain item: its BlockType custom model + first texture (both checked under Common/), a scale for
    a hand-held accessory (0.6 x the block's own CustomModelScale), the item hold animation, the vanilla IconProperties when it has some"""
    need_item(iid)
    d = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
    bt = d.get("BlockType") or {}
    out = {"Model": bt.get("CustomModel"), "Texture": ((bt.get("CustomModelTexture") or [{}])[0]).get("Texture"),
           "Scale": round(0.6 * float(bt.get("CustomModelScale", 1.0)), 3), "PlayerAnimationsId": "Item"}
    assert out["Model"] and out["Texture"] and bt.get("DrawType") == "Model", "0.5.4: %s has no custom block model: %r" % (iid, bt)
    for k in ("Model", "Texture"):
        assert "Common/" + out[k] in _COMMON, "0.5.4: missing %s file for %s: %s" % (k, iid, out[k])
    if "IconProperties" in d:
        out["IconProperties"] = d["IconProperties"]
    return out


TORCH_DATA = {}
for _ti in TORCH_ITEMS:
    need_item(_ti)
    TORCH_DATA[_ti] = (json.loads(_ASSETS.read(_ITEMS[_ti]).decode("utf-8-sig")).get("BlockType") or {}).get("Light")


def _torch_proof():
    """0.5.4: the vanilla torch's light from Assets.zip = the Lantern's default glow (#RGB = one hex digit per channel; the harness runs the
    engine's own ColorParseUtil on it)"""
    for ti, li in TORCH_DATA.items():
        assert li == {"Radius": 0, "Color": TORCH_HEX} or li == {"Color": TORCH_HEX, "Radius": 0}, "0.5.4: %s light changed: %r" % (ti, li)
    assert tuple(int(ch, 16) for ch in TORCH_HEX[1:]) == TORCH_RGB and TORCH_RGB[0] == LAN_TORCH
    assert (lan_key(LAN_TORCH) >> 16) & 255 == 11 and (lan_key(LAN_TORCH) >> 8) & 255 == 10 and lan_key(LAN_TORCH) & 255 == 9
    print("lantern: the vanilla torch light (%s) = %s radius 0 = levels %d / %d / %d - the default glow sends exactly that (+ the radius-1 "
          "owner mark, no visible change)" % (", ".join(TORCH_ITEMS), TORCH_HEX, TORCH_RGB[0], TORCH_RGB[1], TORCH_RGB[2]))


_torch_proof()
LAN_NAMES = ["%s %s Accessory" % (DISPLAY[_t], LAN_LINE) for _t in range(1, 5)]
LAN_DESCS = []
for _t in range(1, 5):
    _first = _w("Glows like a torch and lights about %d blocks around you" % LAN_SHOWN[_t]) + " while in your Void Charms."   # 0.5.18
    _what = ("Everyone around you sees the glow - like carrying a torch, with your hands free - and a hidden light above you lights farther." if _t == 1 else
             "A hidden light above you reaches farther than the rarity below, while the light around you stays about torch-bright.")
    _rule = "Only your best Lantern Accessory counts. " + ("Next: %s (upgrade it at a Workbench)." % LAN_NAMES[_t] if _t < 4 else
                                                          "Legendary is the top rarity.")
    LAN_DESCS.append(_first + TIP_NL + _what + TIP_NL + _rule + TIP_NL + TIP_NL + "<i>%s</i>" % LAN_FLAVOUR)
# 0.5.11 THE LANTERN ITEM TEXTURES (tools/accessories_0_5_11_patch.py): the client logs "Cannot use Blocks/... as texture for item" and
# drops the texture of any item whose Texture is a BLOCK texture. The vanilla lantern texture's bytes (Assets.zip, read at build time,
# never committed) ship under our item folder - the one the Accessory Bag's texture loads from - so the model's UVs see the same pixels.
LAN_TEX_REL = {}   # rarity 1..4 -> (our Common-relative path, the vanilla Common-relative source path)
# 0.5.16 THE METAL LANTERN TEXTURES (tools/accessories_0_5_16_patch.py): each Lantern's texture = its vanilla one recoloured by
# tools/skyyart.py to the vanilla tones of its recipe metal (SA.metal_gradient: that metal's pickaxe head + bar). Parts = blockymodel nodes
# (or (node, face) pairs) of each look; the glowing core (LAN_LIGHT nodes) keeps its vanilla pixels; texels no part uses stay vanilla.
LAN_LIGHT = ("Light_On", "Light_Off")
LAN_LOOK_PARTS = {   # look -> [(part, nodes or (node, face) pairs, recolor settings, rim (edge, inner) or None)]
    "Deco_Lantern": [   # the Village lantern: X cage, two caps (their faces toward the flame are lit), hook
        ("cage bars", ("Frame",), {"lo": 0.12, "hi": 0.7, "smooth": 0.3, "rank": 0.5}, None),
        ("caps", ("Lantern", "Lantern2"), {"lo": 0.1, "hi": 0.95, "smooth": 0.9, "rank": 0.5}, (0.14, -0.04)),
        ("caps lit by the flame", (("Lantern", "bottom"), ("Lantern2", "top")), {"lo": 0.35, "hi": 1.0, "smooth": 0.8, "rank": 0.5}, None),
        ("hook", ("hook", "Hook"), {"lo": 0.1, "hi": 0.8, "smooth": 0.5, "rank": 0.5}, None)],
    "Furniture_Kweebec_Lantern": [   # branch cage, two caps, hook (no glowing core texels)
        ("branch cage", ("Block",), {"lo": 0.12, "hi": 0.75, "smooth": 0.3, "rank": 0.5}, None),
        ("caps", ("Lantern1",), {"lo": 0.1, "hi": 0.95, "smooth": 0.9, "rank": 0.5}, (0.14, -0.04)),
        ("hook", ("hook",), {"lo": 0.1, "hi": 0.8, "smooth": 0.5, "rank": 0.5}, None)],
    "Furniture_Desert_Lantern": [   # frame, base + dome (the teal glass with gold bands is the glowing core)
        ("frame", ("Lantern",), {"lo": 0.1, "hi": 0.9, "smooth": 0.75, "rank": 0.5}, None),
        ("base and dome", ("Base", "Dome", "Dome2", "Dome3", "Dome4", "Dome5", "Dome6", "Dome7"), {"lo": 0.1, "hi": 0.95, "smooth": 0.6,
                                                                                                 "rank": 0.5}, None)],
    "Furniture_Temple_Light_Lantern": [   # marble body + dark cage grid in one tonal range (their faces share texels)
        ("body and cage", ("Top", "Frame", "Lantern_Frame"), {"lo": 0.05, "hi": 1.0, "smooth": 0.5, "rank": 0.5}, None)],
}


def lan_metal_parts(look, model):
    """{part: UV rects} of a lantern model + its light rects; asserts every textured node is either in a part or the light, the parts are
    disjoint and never touch the light"""
    faces = _SA.model_faces(model)
    spec = LAN_LOOK_PARTS[look]
    pairs = set()
    for _part, names, _tune, _rim in spec:
        for nm in names:
            if isinstance(nm, tuple):
                pairs.add(nm)
    rects = {}
    for part, names, _tune, _rim in spec:
        out = []
        for f in faces:
            key = (f["node"], f["face"])
            if any(isinstance(nm, tuple) for nm in names):
                hit = key in names
            else:
                hit = f["node"] in names and key not in pairs
            if hit:
                r = _SA.face_rect(f)
                if r not in out:
                    out.append(r)
        assert out, "0.5.16: %s part %s has no texels (the vanilla model changed)" % (look, part)
        rects[part] = out
    light = _SA.node_rects(model, list(LAN_LIGHT))
    names = [p[0] for p in spec]
    for i, a in enumerate(names):
        assert not _SA.rects_overlap(rects[a], light), "0.5.16: %s %s shares texels with the glowing core" % (look, a)
        for b in names[i + 1:]:
            assert not _SA.rects_overlap(rects[a], rects[b]), "0.5.16: %s %s and %s share texels" % (look, a, b)
    used = set(f["node"] for f in faces)
    covered = set(nm for _p, ns, _t, _r in spec for nm in ns if not isinstance(nm, tuple)) | set(nm[0] for nm in pairs) | set(LAN_LIGHT)
    assert used <= covered, "0.5.16: %s has textured nodes no part names (the vanilla model changed): %s" % (look, sorted(used - covered))
    return rects, light


def lan_metal_texture(t, png, model_rel):
    """0.5.16: the vanilla lantern texture of rarity t (PNG bytes) recoloured to LAN_METAL[t] (deterministic)"""
    look = LAN_LOOKS[t - 1]
    rects, _light = lan_metal_parts(look, _ASSETS.read("Common/" + model_rel))
    grad = _SA.metal_gradient(_ASSETS, LAN_METAL[t])
    img = _SA.png_decode(png)
    for part, _names, tune, rim in LAN_LOOK_PARTS[look]:
        p = dict(tune)
        if rim:
            p["lift"] = _SA.rim_lift(rects[part], rim[0], rim[1])
        img = _SA.recolor(img, grad, rects[part], as_img=True, **p)
    return _SA.png_encode(img)


def lan_item_texture(t, vanilla_rel):
    """0.5.11: copy Common/<vanilla_rel> (a vanilla lantern block texture) into the jar at our item path for rarity t; return that path"""
    assert vanilla_rel.startswith("Blocks/") and vanilla_rel.endswith(".png"), vanilla_rel
    rel = "Items/SkyyAccessories/SkyyAccessories_Lantern_%s_Texture.png" % DISPLAY[t]
    assert "Common/" + rel not in _COMMON, "0.5.11: our Lantern texture would override a vanilla file: " + rel
    assert "Common/" + rel not in files, "0.5.11: two Lanterns share a texture path: " + rel
    png = _ASSETS.read("Common/" + vanilla_rel)
    assert png[:8] == b"\x89PNG\r\n\x1a\n", vanilla_rel
    png = lan_metal_texture(t, png, block_visual_of(LAN_LOOKS[t - 1])["Model"])   # 0.5.16: the recipe metal's look
    files["Common/" + rel] = png
    LAN_TEX_REL[t] = (rel, vanilla_rel)
    return rel


LAN_LANG = []
for _t in range(1, 5):
    _iid = LAN_IDS[_t - 1]
    _look = block_visual_of(LAN_LOOKS[_t - 1])
    _look["Texture"] = lan_item_texture(_t, _look["Texture"])   # 0.5.11: an item path in OUR jar (the client refuses Blocks/ textures for items)
    if _t == 1:
        _rin = [mat(m, q) for m, q in LAN_RECIPES[0]]
    else:
        _rin = [{"ItemId": LAN_IDS[_t - 2], "Quantity": 1}] + [mat(m, q) for m, q in LAN_RECIPES[_t - 1]]
    _node = item(_iid, OWN_ICON[(LAN_FAM, _t)], QUAL_IDS[_t], _rin, WB_REQ, visual=_look)   # 0.5.7: our own icon
    _node["Recipe"]["KnowledgeRequired"] = True   # 0.5.6: unlocked through the Tree Sap collection (AccKnow follows coll:recipes)
    if "IconProperties" not in _look:
        del _node["IconProperties"]   # the backpack's icon framing would not fit (the icon is the vanilla lantern's own PNG)
    files["Server/Item/Items/Utility/%s.json" % _iid] = json.dumps(_node, indent=2)
    LAN_LANG += ["items.%s.name=%s" % (_iid, LAN_NAMES[_t - 1]), "server.items.%s.name=%s" % (_iid, LAN_NAMES[_t - 1]),
                 "items.%s.description=%s" % (_iid, LAN_DESCS[_t - 1]), "server.items.%s.description=%s" % (_iid, LAN_DESCS[_t - 1])]
lang.extend(LAN_LANG)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
# 0.5.9: the tab icon = OUR Accessory Bag icon (art/accessory-bag-icon/, original art, committed - Skyy 2026-10-08 "Yes, the bag icon looks
# good, commit it"), copied byte for byte into the jar where tab icons live (0.5.2 - 0.5.8: Assets.zip's Utility_Bag_Seed.png). SkyySacks'
# fallback copy (tools/skyywbtab.py ICON_SRC, its own path) is untouched.
TAB_ICON_DIR = os.path.join(os.path.dirname(HERE), "art", "accessory-bag-icon")
TAB_ICON_REL = "Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png"
TAB_ICON_SRC = os.path.join(TAB_ICON_DIR, *TAB_ICON_REL.split("/"))


def _tab_icon():
    """0.5.9: the art folder's icon, checked: sha256 + size = its manifest.json, a 64 x 64 RGBA PNG (8-bit) like the vanilla tab icons
    (Assets.zip Workbench/Processing.png size), alpha only 0 or 255, the jar path is no vanilla file"""
    import hashlib as _hl, struct as _st, zlib as _zl
    data = open(TAB_ICON_SRC, "rb").read()
    man = json.load(open(os.path.join(TAB_ICON_DIR, "manifest.json"), encoding="utf8"))
    ent = [f for f in man["files"] if f["path"] == TAB_ICON_REL]
    assert len(ent) == 1, "0.5.9: the art manifest lists %s once" % TAB_ICON_REL
    assert _hl.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], "0.5.9: the icon is not the art manifest's"
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", "0.5.9: the tab icon is not a PNG"
    w, h = _st.unpack(">II", data[16:24])
    ref = _ASSETS.read("Common/Icons/CraftingCategories/Workbench/Processing.png")
    assert (w, h) == _st.unpack(">II", ref[16:24]) == (64, 64) and data[24:26] == b"\x08\x06", "0.5.9: not 64 x 64 RGBA8 like the vanilla tab icons"
    # alpha only 0 / 255 (straight or premultiplied is then the same): inflate the IDAT stream, undo the PNG row filters
    i, idat = 8, b""
    while i < len(data):
        ln = _st.unpack(">I", data[i:i + 4])[0]
        if data[i + 4:i + 8] == b"IDAT":
            idat += data[i + 8:i + 8 + ln]
        i += 12 + ln
    raw_ = _zl.decompress(idat)
    bpp, stride, prev, alphas = 4, w * 4, bytearray(w * 4), set()
    for y in range(h):
        ft, row = raw_[y * (stride + 1)], bytearray(raw_[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = row[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ft == 1:
                row[x] = (row[x] + a) & 255
            elif ft == 2:
                row[x] = (row[x] + b) & 255
            elif ft == 3:
                row[x] = (row[x] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[x] = (row[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            else:
                assert ft == 0, "0.5.9: PNG filter %d" % ft
        alphas.update(row[3::4])
        prev = row
    assert alphas <= {0, 255} and alphas == {0, 255}, "0.5.9: the tab icon must have hard alpha (0 / 255): %s" % sorted(alphas)[:8]
    return data


files["Common/" + WB.icon_path("SkyyAccessories")] = _tab_icon()
assert "Common/" + WB.icon_path("SkyyAccessories") not in _COMMON, "0.5.9: the tab icon path would override a vanilla file"
print("Workbench tab icon: %s (%d bytes, art/accessory-bag-icon) -> %s" % (TAB_ICON_REL.split("/")[-1], len(files["Common/" + WB.icon_path("SkyyAccessories")]),
                                                                           WB.icon_path("SkyyAccessories")))
print("accessory items:", count, "retired (no recipe):", retired_count)


def _wbtab_checks():
    """0.5.2 build checks: every recipe of this mod in the new tab and nowhere else, the Void Charms still pocket crafting, the full
    in-tab order (both mods) printed and asserted, ingredients / outputs untouched (only BenchRequirement differs from 0.5.1's rule)"""
    own = [i for i in WB.EXPECTED if i.startswith(("Skyy_Accessory_", "Skyy_Talisman_")) and i != BAG]   # 0.5.20: the bag has no recipe
    lan_paths = ["Server/Item/Items/Utility/%s.json" % i for i in LAN_IDS]   # 0.5.4: not in the shared kit's table (checked below)
    got = WB.recipe_checks(dict((p, t) for p, t in files.items() if p not in lan_paths), own, bag_req_id=None)
    assert len(got) == 46 and BAG not in got and "Recipe" not in json.loads(files["Server/Item/Items/Utility/%s.json" % BAG]), len(got)
    for t, i in enumerate(LAN_IDS, 1):
        rq = json.loads(files["Server/Item/Items/Utility/%s.json" % i])["Recipe"]["BenchRequirement"]
        assert rq == WB_REQ, "0.5.4: %s must sit in the Workbench tab only: %r" % (i, rq)
    print("Workbench tab: the 4 Lantern recipes sit in the tab only (0.5.13: their place comes from _wbtab_order)")
    lmap = dict(l.split("=", 1) for l in lang if "=" in l)
    names = WB.default_names()
    for i in own:
        names[i] = lmap["server.items.%s.name" % i]
    for l in WB.LANG_LINES:
        assert l in lang, l
    print("Workbench tab: %d recipes of this mod in '%s' (Void Charms also in pocket crafting), none in a vanilla tab; tab protocol %s"
          % (len(got), WB.TAB_TEXT, WB.WB_VERSION))


_wbtab_checks()


# ================= 0.5.13: THE WORKBENCH TAB ORDER (Skyy 2026-10-13: "since the tutorial asks you to craft this, id move it to the top. sort them
# by tier, and per tier,m sort them by easiest to craft."; full notes in tools/accessories_0_5_13_patch.py). Workbench Accessory I first; then
# by tier (= the item's rarity Quality, no exceptions), inside a tier by cost (raw materials, 3 ** (material tier - 1) each),
# ties by English name then id; the Omni Accessory last (not listed: the kit's rankOld keeps it at 9000000).
from fractions import Fraction as _Frac
ORD_FIRST = "Skyy_Accessory_Workbench_T1"
ORD_LAST = OMNI
ORD_BASE = 3                     # cost of one raw material = ORD_BASE ** (material tier - 1)
ORD_SHIFT = 500000               # a pattern-ranked id (kit rule, t * 1000000 + < 400000) moves after the listed ids of its tier
# vanilla inputs that are themselves crafted from the tab's point of view: expanded through their Assets.zip recipe
ORD_EXPAND = ("Bench_", "Deco_Lantern", "Furniture_Crude_Torch", "Furniture_Crude_Candle", "Ingredient_Life_Essence_Concentrated")
# RAW material tiers (where a player first finds it: 1 = first-zone basics, 2 = Iron / medium hides / second-zone wood and crops,
# 3 = Thorium, Silver, Gold, gems, heavy hides, silk, 4 = Cobalt, Fire / Ice, 5 = Shadoweave, Cindercloth, Void / Lightning,
# 6 = Voidheart and the last crops / wood of the Farming Bench ladder). A missing input stops the build.
MAT_TIER = {}
for _t, _ids in ((1, "res:Wood_Trunk res:Rock res:Rubble res:Wood_Softwood_Trunk res:Salvage_Wood Ingredient_Stick Ingredient_Fibre "
                     "Ingredient_Tree_Sap Ingredient_Bar_Copper Ingredient_Leather_Light Ingredient_Hide_Light Ingredient_Fabric_Scrap_Linen "
                     "Ingredient_Fabric_Scrap_Cotton Ingredient_Feathers_Light Ingredient_Bone_Fragment Ingredient_Life_Essence "
                     "Plant_Crop_Wheat_Item Plant_Crop_Lettuce_Item Ingredient_Crystal_Red Ingredient_Crystal_Yellow Ingredient_Crystal_Blue "
                     "Ingredient_Crystal_Green Ingredient_Crystal_Cyan"),
                 (2, "Ingredient_Bar_Iron Ingredient_Leather_Medium Ingredient_Hide_Medium Ingredient_Feathers_Blue Ingredient_Sac_Venom "
                     "Wood_Azure_Trunk res:Wood_Lightwood_Trunk Plant_Crop_Carrot_Item Plant_Crop_Corn_Item"),
                 (3, "Ingredient_Bar_Thorium Ingredient_Bar_Silver Ingredient_Bar_Gold Ingredient_Leather_Heavy Ingredient_Hide_Heavy "
                     "Ingredient_Fabric_Scrap_Silk Rock_Gem_Topaz Rock_Gem_Ruby Rock_Gem_Emerald Rock_Gem_Sapphire Rock_Gem_Zephyr "
                     "Ingredient_Chitin_Sturdy Plant_Crop_Cauliflower_Item Plant_Crop_Turnip_Item res:Wood_Hardwood_Trunk"),
                 (4, "Ingredient_Bar_Cobalt Ingredient_Fire_Essence Ingredient_Ice_Essence Plant_Crop_Aubergine_Item Plant_Crop_Pumpkin_Item "
                     "res:Wood_Drywood_Trunk"),
                 (5, "Ingredient_Fabric_Scrap_Shadoweave Ingredient_Bolt_Cindercloth Ingredient_Void_Essence Ingredient_Lightning_Essence "
                     "Plant_Crop_Tomato_Item Plant_Crop_Chilli_Item res:Wood_Darkwood_Trunk"),
                 (6, "Ingredient_Voidheart Plant_Crop_Cotton_Item Plant_Crop_Rice_Item Wood_Redwood_Trunk")):
    for _i in _ids.split():
        assert _i not in MAT_TIER, _i
        MAT_TIER[_i] = _t


def _ord_items():
    """our generated item JSONs by id (every recipe of the tab and every input that is one of our items)"""
    out = {}
    for p, t in files.items():
        if p.startswith("Server/Item/Items/") and p.endswith(".json"):
            out[os.path.basename(p)[:-5]] = json.loads(t)
    return out


def _ord_key(x):
    return x.get("ItemId") if x.get("ItemId") else "res:" + x["ResourceTypeId"]


def _ord_cost(iid, own, memo, path=()):
    """(cost as an exact Fraction, highest raw material tier) of ONE iid"""
    if iid in memo:
        return memo[iid]
    assert iid not in path, "0.5.13: recipe loop %s" % (path + (iid,),)
    if iid in MAT_TIER:
        out = (_Frac(ORD_BASE) ** (MAT_TIER[iid] - 1), MAT_TIER[iid])
    elif iid in own or iid.startswith(ORD_EXPAND):
        if iid in own:
            node = own[iid]
        else:
            need_item(iid)
            node = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
        r = node.get("Recipe")
        assert r and r.get("Input"), "0.5.13: %s has no recipe to expand" % iid
        oq = r.get("OutputQuantity") or 1
        c, top = _Frac(0), 0
        for x in r["Input"]:
            cc, tt = _ord_cost(_ord_key(x), own, memo, path + (iid,))
            c += cc * int(x.get("Quantity", 1))
            top = max(top, tt)
        out = (c / int(oq), top)
    else:
        raise SystemExit("0.5.13 Workbench tab order: the recipe input %s (via %s) has no material tier - add it to MAT_TIER" % (iid, " > ".join(path)))
    memo[iid] = out
    return out


def ord_rank_py(rid):
    """the Python mirror of the 0.5.13 WbRank.rank (the harness compares both on every id it sees)"""
    if rid is None:
        return 9900000
    b = WB.base_py(rid)
    if b in ORD_POS:
        i = ORD_POS[b]
        return ORD_TIER[i] * 1000000 + 1000 + i
    r = WB.rank_py(rid)
    return r + ORD_SHIFT if 1000000 <= r < 5000000 else r


def _wbtab_order():
    global ORDER, ORD_TIER, ORD_POS, ORD_COST, ORD_NAMES
    own = _ord_items()
    tab = sorted(i for i, n in own.items() if n.get("Recipe") and any(WB.TAB_ID in (q.get("Categories") or []) for q in
                                                                       n["Recipe"].get("BenchRequirement") or []))
    assert len(tab) == 50 and ORD_FIRST in tab and ORD_LAST in tab and BAG not in tab, (len(tab), tab[:3])   # 0.5.20: the bag has no recipe
    lmap = dict(l.split("=", 1) for l in lang if "=" in l)
    ORD_NAMES = dict((i, lmap["server.items.%s.name" % i]) for i in tab)
    memo = {}
    rows = []
    for i in tab:
        q = own[i]["Quality"]
        t = QUAL_IDS.index(q)
        assert 1 <= t <= 4, (i, q)
        c, top = _ord_cost(i, own, memo)
        rows.append((t, c, ORD_NAMES[i], i, top))
    ORD_COST = dict((r[3], r[1]) for r in rows)
    body = sorted(r for r in rows if r[3] not in (ORD_FIRST, ORD_LAST))
    first = [r for r in rows if r[3] == ORD_FIRST][0]
    assert first[0] == 1, first
    ORDER = [ORD_FIRST] + [r[3] for r in body]
    ORD_TIER = [0] + [r[0] for r in body]
    ORD_POS = dict((i, k) for k, i in enumerate(ORDER))
    # the rules, asserted
    assert ORDER[0] == ORD_FIRST and ORD_LAST not in ORDER and sorted(ORDER + [ORD_LAST]) == tab
    assert all(ORD_TIER[k] <= ORD_TIER[k + 1] for k in range(len(ORDER) - 1)), "tiers ascending"
    assert all(body[k][:3] <= body[k + 1][:3] for k in range(len(body) - 1)), "inside a tier: cost, then name ascending"
    assert ORD_COST[ORD_LAST] > max(ORD_COST[i] for i in ORDER), "the Omni Accessory is also the most expensive recipe"
    for i in tab:   # an upgrade never lists before what it consumes
        for x in own[i]["Recipe"]["Input"]:
            k = _ord_key(x)
            if k in ORD_POS and i in ORD_POS:
                assert ORD_POS[k] < ORD_POS[i], "0.5.13: %s lists before its input %s" % (i, k)
    rids = [i + WB.RECIPE_SUFFIX + "0" for i in tab]
    want = [i + WB.RECIPE_SUFFIX + "0" for i in ORDER + [ORD_LAST]]
    assert sorted(rids, key=lambda r: (ord_rank_py(r), r)) == want, "the mirror sorts the tab exactly as ORDER + Omni"
    assert ord_rank_py("Skyy_Talisman_Crit_Epic_Recipe_Generated_0") > ord_rank_py("Skyy_Accessory_Farmingbench_T7_Recipe_Generated_0") and \
        ord_rank_py("Skyy_Talisman_Crit_Epic_Recipe_Generated_0") < ord_rank_py(OMNI) and \
        ord_rank_py("Skyy_Talisman_Crit_Uncommon") < ord_rank_py("Skyy_Talisman_Vitality_Rare"), "a future line sorts after its tier, before the next"
    # ---- WbRank: the kit's rank(String) becomes rankOld(String); rank(String) = the table first (written again over the 0.5.2 class file)
    wr = WB_CLASSES[0]
    assert str(wr.getName()) == PKG + ".WbRank"
    wr.defrost()
    m0 = wr.getDeclaredMethod("rank")
    wr.addMethod(CtNewMethod.copy(m0, "rankOld", wr, None))
    wr.removeMethod(m0)
    wr.addField(CtField.make("public static final String[] ORDER = new String[] { %s };" % jstrs(ORDER), wr))
    wr.addField(CtField.make("public static final int[] TIER = new int[] { %s };" % ", ".join(str(t) for t in ORD_TIER), wr))
    wr.addMethod(CtNewMethod.make("""
public static long rank(String id) {
  if (id == null) return 9900000L;
  int i = idx(ORDER, base(id));
  if (i >= 0) return TIER[i] * 1000000L + 1000L + i;
  long r = rankOld(id);
  if (r >= 1000000L && r < 5000000L) return r + %dL;
  return r;
}""" % ORD_SHIFT, wr))
    wr.writeFile(OUT)
    print("Workbench tab order (0.5.13, %d recipes; tier = rarity, cost = raw materials x %d ** (material tier - 1), * = pinned):" % (len(tab), ORD_BASE))
    rowp = []
    for k, i in enumerate(ORDER + [ORD_LAST], 1):
        t = ORD_TIER[k - 1] if k <= len(ORDER) else 4
        c = ORD_COST[i]
        rowp.append("%2d %s%s T%d %s" % (k, "*" if i in (ORD_FIRST, ORD_LAST) else " ", ORD_NAMES[i], max(t, 1),
                                          ("%d" % c) if c.denominator == 1 else ("%.1f" % float(c))))
    for k in range(0, len(rowp), 3):
        print("   " + " | ".join(rowp[k:k + 3]))


_wbtab_order()


# ================= 0.5.15: THE CLIENT-SORT KEY (Skyy 2026-10-15: "sort the accessories by tier. T1 at the top. easiest to craft first."; full
# notes in tools/accessories_0_5_15_patch.py). The native client re-sorts a bench tab by the outputs' numbers (ItemLevel / rarity) and our 51
# recipes all tied (ItemLevel absent = 0) -> each recipe's item gets ItemLevel = its place in ORDER + Omni (1 .. 51). Nothing else changes.
CLIENT_LEVEL0 = 1


def client_key_py(node):
    """the client-sort key the harness checks: (ItemLevel, rarity tier) of one generated item JSON"""
    return (int(node.get("ItemLevel", 0)), QUAL_IDS.index(node["Quality"]))


def _client_order():
    global CLIENT_LEVEL
    tab = ORDER + [ORD_LAST]
    CLIENT_LEVEL = {}
    for k, iid in enumerate(tab):
        p = "Server/Item/Items/Utility/%s.json" % iid
        txt = files[p]
        node = json.loads(txt)
        assert json.dumps(node, indent=2) == txt, "0.5.15: %s must round-trip byte for byte" % iid
        assert "ItemLevel" not in node, "0.5.15: %s already has an ItemLevel" % iid
        node["ItemLevel"] = CLIENT_LEVEL0 + k
        CLIENT_LEVEL[iid] = node["ItemLevel"]
        files[p] = json.dumps(node, indent=2)
    # the rules, asserted on the files that go into the jar
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    intab = sorted(i for i, n in items.items() if n.get("Recipe") and any(WB.TAB_ID in (q.get("Categories") or []) for q in
                                                                          n["Recipe"].get("BenchRequirement") or []))
    assert intab == sorted(tab) and len(tab) == 50, "0.5.15: every recipe of the tab (and only those) gets a level (0.5.20: 50, the bag has no recipe)"
    assert not any("ItemLevel" in n for i, n in items.items() if i not in CLIENT_LEVEL), "0.5.15: no other item gets an ItemLevel"
    keys = [client_key_py(items[i]) for i in tab]
    assert len(set(k[0] for k in keys)) == len(tab), "0.5.15: no two recipes of the tab share an ItemLevel (no ties)"
    assert all(keys[k][0] < keys[k + 1][0] and keys[k][1] <= keys[k + 1][1] for k in range(len(tab) - 1)), \
        "0.5.15: ItemLevel and rarity both rise along the tab order"
    for key in (lambda i: client_key_py(items[i]), lambda i: client_key_py(items[i])[::-1], lambda i: client_key_py(items[i])[0]):
        assert sorted(tab, key=key) == tab, "0.5.15: every client key candidate sorts the tab as ORDER + Omni"
    assert tab[0] == ORD_FIRST and tab[-1] == ORD_LAST
    print("Workbench tab, client-sort key (0.5.15): ItemLevel %d .. %d in the tab order - %s = %d first, %s = %d last" % (
        CLIENT_LEVEL0, CLIENT_LEVEL0 + len(tab) - 1, ORD_NAMES[ORD_FIRST], CLIENT_LEVEL[ORD_FIRST], ORD_NAMES[ORD_LAST], CLIENT_LEVEL[ORD_LAST]))


_client_order()
# 0.4.2 build check: no generated recipe takes a retired bench accessory, and no retired accessory has a recipe
_RET_IDS = set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in BENCHES if b[0] in RETIRED for t in range(1, b[3] + 1))
assert retired_count == len(_RET_IDS) == 5, (retired_count, sorted(_RET_IDS))   # 0.4.3: Alchemy Bench T1-T4 + Cooking Bench
for _fn, _body in files.items():
    if not _fn.endswith(".json") or not _fn.startswith("Server/Item/Items/"):
        continue
    _node = json.loads(_body)
    _iid = os.path.basename(_fn)[:-5]
    if _iid in _RET_IDS:
        assert "Recipe" not in _node, "retired accessory still has a recipe: " + _iid
    for _inp in (_node.get("Recipe") or {}).get("Input", []):
        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))
# 0.4.3 build check: the Campfire accessory is back - the 0.4.1 Workbench recipe, its own name + description, an Omni input; 0.5 Normal
_CF = "Skyy_Accessory_Campfire_T1"
assert _CF not in _RET_IDS
_cfn = json.loads(files["Server/Item/Items/Utility/%s.json" % _CF])
assert (_cfn.get("Recipe") or {}).get("Input") == [{"ItemId": "Bench_Campfire", "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}], _cfn.get("Recipe")
assert _cfn["Recipe"]["BenchRequirement"] == WB_REQ and _cfn["Quality"] == QUAL_IDS[1], _cfn
for _pre in ("items.", "server.items."):
    assert (_pre + _CF + ".name=Campfire Accessory") in lang, _pre
    assert (_pre + _CF + ".description=" + CAMPFIRE_DESC) in lang, _pre
assert not any(l.startswith(("items." + _CF + ".", "server.items." + _CF + ".")) and "etired" in l for l in lang), "Campfire text still says retired"
_omn = json.loads(files["Server/Item/Items/Utility/%s.json" % OMNI])["Recipe"]["Input"]
assert sorted(i["ItemId"] for i in _omn) == sorted("Skyy_Accessory_%s_T%d" % (b[0], b[3]) for b in ACTIVE) and len(_omn) == 11, _omn
print("campfire accessory: recipe back, Omni input %d of %d, retired ids: %s" % (_omn.index({"ItemId": _CF, "Quantity": 1}) + 1, len(_omn), ", ".join(sorted(_RET_IDS))))


def _booster_asset_checks():
    """0.5 part 1 build checks on the generated assets (research/Booster-Accessories-Spec.md 6.1)"""
    import re as _re
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    assert sorted(quals) == sorted(QUAL_IDS[1:]) and len(quals) == 6, sorted(quals)
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\n") if "=" in l)
    for qid in quals:
        assert lmap.get("general.qualities." + qid) == lmap.get("server.general.qualities." + qid) == qid[len("Skyy_Acc_"):], qid
    # every item's quality is shipped here; an item with a recipe (booster, bench, Omni, bag) is never above Legendary
    for iid, node in items.items():
        assert node["Quality"] in quals, "%s uses quality %s that is not shipped" % (iid, node["Quality"])
        if "Recipe" in node:
            assert QUAL_IDS.index(node["Quality"]) <= MAX_LINE_RARITY, "crafted %s is above Legendary (%s)" % (iid, node["Quality"])
    assert items[OMNI]["Quality"] == QUAL_IDS[4] and items[BAG]["Quality"] == QUAL_IDS[2]
    for b in BENCHES:
        for t in range(1, b[3] + 1):
            assert items["Skyy_Accessory_%s_T%d" % (b[0], t)]["Quality"] == QUAL_IDS[BENCH_RARITY[min(t, 7)]], (b[0], t)
    # the booster ids: exactly 4 rarities Normal..Legendary per line, the Workbench ladder (folded lines), no recipe (part 2 lines),
    # the old ids without a recipe
    for li, b in enumerate(BOOSTERS):
        ids = LINE_IDS[li * 4:li * 4 + 4]
        assert [items[i]["Quality"] for i in ids] == QUAL_IDS[1:5], (b[1], [items[i]["Quality"] for i in ids])
        assert len(set(items[i]["Icon"] for i in ids)) == 4, "%s: two rarities share an icon" % b[1]
        if b[9] != "word":
            assert all("Recipe" not in items[i] for i in ids), "%s: a part 2 line has a recipe (admin give only)" % b[1]
            assert all(i.endswith("_T%d" % (t + 1)) and not i.startswith("Skyy_Accessory_") for t, i in enumerate(ids)), ids
            assert not any(("Skyy_Talisman_%s_%s" % (b[0], w)) in items for w, _t in LEGACY_WORDS), "%s: no old ids" % b[1]
            continue
        for t in range(2, 5):
            assert {"ItemId": ids[t - 2], "Quantity": 1} in items[ids[t - 1]]["Recipe"]["Input"], "%s: the ladder is broken at %s" % (b[1], ids[t - 1])
        for w, t in LEGACY_WORDS:
            lid = "Skyy_Talisman_%s_%s" % (b[0], w)
            assert "Recipe" not in items[lid] and items[lid]["Quality"] == QUAL_IDS[t] and items[lid]["Icon"] == items[ids[t - 1]]["Icon"], lid
            assert lmap["server.items.%s.name" % lid] == lmap["server.items.%s.name" % ids[t - 1]], lid
    assert not any(i.endswith("_Legendary") and i.startswith("Skyy_Talisman_") and "Recipe" in n for i, n in items.items())
    assert not any(inp.get("ItemId", "").startswith("Skyy_Talisman_") and inp.get("ItemId", "").endswith("_Legendary")
                   for n in items.values() for inp in (n.get("Recipe") or {}).get("Input", [])), "a recipe still takes an old _Legendary id"
    # names: exactly "<Rarity> <Line> Accessory" for all 60 stat accessory ids (40 modern + 20 old); lang lines are one line each
    for li, b in enumerate(BOOSTERS):
        for t in range(1, 5):
            assert lmap["items.%s.name" % LINE_IDS[li * 4 + t - 1]] == "%s %s Accessory" % (DISPLAY[t], b[2])
            d = lmap["items.%s.description" % LINE_IDS[li * 4 + t - 1]]
            assert d.startswith('<color is="#ffffff">') and "while in your Void Charms." in d.split("\\n")[0], "stat line first: " + d[:80]
            if b[8] is None:
                assert "Workbench" not in d, "a part 2 tooltip promises a Workbench upgrade: " + d
    assert all("\r" not in l for l in lang) and len(lt.split("\n")) == len(lang) + 1, "a lang value holds a real line break"
    # no scrapped name or the old item word in anything a player reads: lang values, Server Setup labels + help (admins), config text
    bad = ("Vitality", "Endurance", "Intelligence", "Talisman")
    for k, v in lmap.items():
        assert not any(w in v for w in bad) and "talisman" not in v.lower(), "a player text says %r: %s=%s" % ([w for w in bad if w in v], k, v)
    for r in CFG_ROWS:
        assert not any(w in r[1] + r[10] for w in bad) and "talisman" not in (r[1] + r[10]).lower(), r[0]
    assert not any(w in CONFIG_TEXT for w in bad) and "talisman" not in CONFIG_TEXT.lower()
    print("booster assets: %d lines x 4 rarities (%d with a Workbench ladder, %d admin give only), %d old ids, 6 qualities (%s), "
          "names and texts checked" % (len(BOOSTERS), len(FOLDED), len(BOOSTERS) - len(FOLDED), len(LEGACY_IDS), ", ".join(DISPLAY[1:])))


_booster_asset_checks()


def _hidden_checks():
    """0.5.1 build check: exactly the old ids are hidden from the creative library, every current id stays listed"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    lt = files["Server/Languages/en-US/server.lang"]
    lmap = dict(l.split("=", 1) for l in lt.split("\n") if "=" in l)
    hidden = sorted(i for i, n in items.items() if "Variant" in n)
    assert hidden == sorted(HIDDEN_IDS), "0.5.1: the hidden items differ from HIDDEN_IDS: %s" % sorted(set(hidden) ^ set(HIDDEN_IDS))
    for iid in HIDDEN_IDS:
        n = items[iid]
        assert n["Variant"] is True and "Categories" not in n and "Recipe" not in n, "0.5.1: %s is not hidden right: %r" % (iid, n)
        assert py_legacy(iid) or iid in RETIRED_IDS or iid == NV_ID, iid   # 0.5.4: + the retired Night Vision
        assert n["Quality"] in quals and n["MaxStack"] == 1 and n.get("Icon") and lmap.get("server.items.%s.name" % iid) and \
            lmap.get("server.items.%s.description" % iid), "0.5.1: %s lost its look or text" % iid
        if py_legacy(iid):   # it still looks and reads like the rarity it counts as (0.5's rule, re-checked on the hidden item)
            cur = items[py_modern(iid)]
            assert n["Quality"] == cur["Quality"] and n["Icon"] == cur["Icon"] and n["Model"] == cur["Model"], iid
            assert lmap["server.items.%s.name" % iid] == lmap["server.items.%s.name" % py_modern(iid)], iid
    current = sorted(i for i in items if i not in HIDDEN_IDS)
    want = set(LINE_IDS) | set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in ACTIVE for t in range(1, b[3] + 1)) | {OMNI, BAG} | set(LAN_IDS)   # 0.5.4
    assert set(current) == want, "0.5.1: current items differ: %s" % sorted(set(current) ^ want)
    for iid in current:
        assert "Variant" not in items[iid] and items[iid].get("Categories") == ["Items.Tools"], "0.5.1: %s must stay listed" % iid
    for iid, n in items.items():
        for inp in (n.get("Recipe") or {}).get("Input", []):
            assert inp.get("ItemId") not in HIDDEN_IDS, "0.5.1: %s takes the hidden %s" % (iid, inp.get("ItemId"))
    assert not any(q.get("HideFromSearch") for q in quals.values()), "0.5.1: a quality hides items (the qualities are shared)"
    print("creative library: %d old ids hidden (Variant true, no Categories: %d legacy booster ids + %d retired bench accessories + the "
          "retired Night Vision), %d current ids listed" % (len(HIDDEN_IDS), len(LEGACY_IDS), len(RETIRED_IDS), len(current)))   # 0.5.4


_hidden_checks()


def _nv_retired_checks():
    """0.5.4 build check: the retired Night Vision item - the same look and Rare frame, no recipe, hidden from the creative library, the
    retired name and text (items. + server.items.), still never a booster / bench / Workbench-tab id"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    n = items[NV_ID]
    v = visual_of(NV_LOOK)
    assert n["Quality"] == QUAL_IDS[NV_TIER] == "Skyy_Acc_Rare" and "Recipe" not in n and n.get("Variant") is True and "Categories" not in n, n
    assert n["MaxStack"] == 1 and n["Icon"] == icon_of(NV_LOOK) and "Interactions" not in n and all(n[k] == v[k] for k in v), n
    lt = files["Server/Languages/en-US/server.lang"].split("\n")
    i0 = lt.index(NV_LANG[0])
    assert lt[i0:i0 + 4] == NV_LANG and lt[-17:-1] == LAN_LANG and lt[-1] == "", lt[-20:]
    assert NV_NAME == "Night Vision Accessory (retired)" and "Lantern" in NV_DESC and "replaced" in NV_DESC
    assert NV_ID not in WB.EXPECTED and NV_ID in HIDDEN_IDS and NV_ID not in LINE_IDS
    print("night vision: retired - %s keeps its look, no recipe, hidden from the creative library, text: %s" % (NV_ID, NV_DESC[:60]))


_nv_retired_checks()


def _lantern_asset_checks():
    """0.5.4 build check: the four Lantern items - qualities Normal..Legendary, the Workbench tab recipe ladder (each from the one below),
    four distinct vanilla lantern looks and icons, listed in the creative library, names + vanilla-style tooltips, never a booster / bench /
    legacy / hidden id"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    lmap = dict(l.split("=", 1) for l in files["Server/Languages/en-US/server.lang"].split("\n") if "=" in l)
    for t, i in enumerate(LAN_IDS, 1):
        n = items[i]
        assert n["Quality"] == QUAL_IDS[t] and n["Categories"] == ["Items.Tools"] and "Variant" not in n and n["MaxStack"] == 1, (i, n)
        assert n["Icon"] == OWN_ICON[(LAN_FAM, t)] and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)   # 0.5.7
        assert n["Recipe"].get("KnowledgeRequired") is True, ("0.5.6: a Lantern recipe must be a knowledge recipe", i)
        ins = n["Recipe"]["Input"]
        if t == 1:
            assert ins == [mat(m, q) for m, q in LAN_RECIPES[0]] and not any(x.get("ItemId", "").startswith("Skyy_") for x in ins), ins
        else:
            assert ins[0] == {"ItemId": LAN_IDS[t - 2], "Quantity": 1} and ins[1:] == [mat(m, q) for m, q in LAN_RECIPES[t - 1]], ins
        assert lmap["items.%s.name" % i] == lmap["server.items.%s.name" % i] == "%s Lantern Accessory" % DISPLAY[t], i
        d = lmap["items.%s.description" % i]
        assert d == lmap["server.items.%s.description" % i] and d.startswith('<color is="#ffffff">Glows like a torch') and \
            "while in your Void Charms." in d.split("\\n")[0] and d.count("\\n") == 4, d
        assert ("Next: %s Lantern Accessory (upgrade it at a Workbench)." % DISPLAY[t + 1] in d) if t < 4 else ("top rarity" in d), d
        assert ("about %d blocks" % LAN_SHOWN[t]) in d.split("\\n")[0], d   # 0.5.18: Normal too
    assert len(set(items[i]["Icon"] for i in LAN_IDS)) == 4 and len(set(items[i]["Model"] for i in LAN_IDS)) == 4
    _kr = sorted(i for i, n in items.items() if (n.get("Recipe") or {}).get("KnowledgeRequired"))
    assert _kr == sorted(LAN_IDS), ("0.5.6: exactly the four Lantern recipes are knowledge recipes", _kr)
    assert not set(LAN_IDS) & set(HIDDEN_IDS + LINE_IDS + list(WB.EXPECTED))
    for m, q in [x for r in LAN_RECIPES for x in r]:
        need_item(m)
        assert m != "Ingredient_Motes_Light", "Motes of Light have no vanilla source"
    print("lantern items: %s - recipes at the Workbench tab, each from the one below; looks %s" % (", ".join(LAN_NAMES), ", ".join(LAN_LOOKS)))


_lantern_asset_checks()


def _item_texture_checks():
    """0.5.11 build check: no item of this jar uses a BLOCK texture (the client refuses it: "Cannot use Blocks/... as texture for item");
    the four Lantern items use our copies - each the vanilla lantern texture byte for byte, at our own item path, the same model as 0.5.10"""
    import struct as _st
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    bad = sorted(i for i, n in items.items() if str(n.get("Texture", "")).startswith("Blocks/"))
    assert not bad, "0.5.11: items with a block texture (the client refuses them): %s" % bad
    assert sorted(LAN_TEX_REL) == [1, 2, 3, 4] and len(set(v[0] for v in LAN_TEX_REL.values())) == 4
    for t, i in enumerate(LAN_IDS, 1):
        n = items[i]
        rel, van = LAN_TEX_REL[t]
        bt = json.loads(_ASSETS.read(_ITEMS[LAN_LOOKS[t - 1]]).decode("utf-8-sig"))["BlockType"]
        assert n["Texture"] == rel and n["Model"] == bt["CustomModel"] and van == bt["CustomModelTexture"][0]["Texture"], (i, n["Texture"], n["Model"])
        assert rel.startswith("Items/SkyyAccessories/") and ("Common/" + rel) not in _COMMON, rel
        assert files["Common/" + rel] == lan_metal_texture(t, _ASSETS.read("Common/" + van), bt["CustomModel"]), \
            "0.5.16: %s is not the %s recolour of %s" % (rel, LAN_METAL[t], van)
        w, h = _st.unpack(">II", files["Common/" + rel][16:24])
        print("lantern texture: %s <- %s (%d x %d, %d bytes)" % (rel, van, w, h, len(files["Common/" + rel])))


_item_texture_checks()


def _on_gradient(c, grad, tol=3.0):
    """True when colour c lies on the gradient polyline (within tol per channel, the recolour's rounding)"""
    for i in range(len(grad) - 1):
        a, b = grad[i], grad[i + 1]
        d = [b[k] - a[k] for k in range(3)]
        dd = sum(v * v for v in d)
        u = 0.0 if dd == 0 else max(0.0, min(1.0, sum((c[k] - a[k]) * d[k] for k in range(3)) / dd))
        if all(abs(c[k] - (a[k] + d[k] * u)) <= tol for k in range(3)):
            return True
    return False


def _metal_lantern_checks():
    """0.5.16 build check (Skyy 2026-10-15): the Normal Lantern recipe = Crude Torch x4 + Copper Bar x2 (no Deco Lantern); every rarity's
    look metal = the one metal bar of its recipe; each texture = its vanilla pixels with the same alpha, the glowing core and unused
    texels unchanged, every recoloured texel on that metal's vanilla gradient; each icon = our drawing in that metal"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    n1 = items[LAN_IDS[0]]
    assert n1["Recipe"]["Input"] == [{"ItemId": "Furniture_Crude_Torch", "Quantity": 4}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 2}], n1
    assert not any("Deco_Lantern" == x.get("ItemId") for i in LAN_IDS for x in items[i]["Recipe"]["Input"]), "0.5.16: no Lantern takes a Deco Lantern"
    rows = []
    for t in range(1, 5):
        n = items[LAN_IDS[t - 1]]
        bars = [x.get("ItemId") for x in n["Recipe"]["Input"] if x.get("ItemId", "").startswith("Ingredient_Bar_")]
        assert bars == ["Ingredient_Bar_" + LAN_METAL[t]], ("0.5.16: the look metal must be the recipe's bar", LAN_IDS[t - 1], bars)
        assert n["Recipe"].get("KnowledgeRequired") is True and n["Recipe"]["BenchRequirement"] == WB_REQ, n["Recipe"]
        rel, van = LAN_TEX_REL[t]
        bt = json.loads(_ASSETS.read(_ITEMS[LAN_LOOKS[t - 1]]).decode("utf-8-sig"))["BlockType"]
        rects, light = lan_metal_parts(LAN_LOOKS[t - 1], _ASSETS.read("Common/" + bt["CustomModel"]))
        grad = _SA.metal_gradient(_ASSETS, LAN_METAL[t])
        a, b = _SA.png_decode(_ASSETS.read("Common/" + van)), _SA.png_decode(files["Common/" + rel])
        assert (a.w, a.h) == (b.w, b.h)
        inside = set()
        for part in rects:
            for x0, y0, x1, y1 in rects[part]:
                for y in range(y0, y1):
                    for x in range(x0, x1):
                        inside.add((x, y))
        changed, off = 0, []
        for y in range(a.h):
            for x in range(a.w):
                ca, cb = a.get(x, y), b.get(x, y)
                assert ca[3] == cb[3], ("0.5.16: alpha changed", rel, x, y)
                if (x, y) not in inside:
                    assert ca == cb, ("0.5.16: a texel outside the metal parts changed (glowing core / unused)", rel, x, y)
                elif cb[3]:
                    changed += ca != cb
                    if not _on_gradient(cb, grad):
                        off.append((x, y, cb))
        assert not off, ("0.5.16: recoloured texels off the %s gradient" % LAN_METAL[t], rel, off[:5])
        assert changed > 200, ("0.5.16: too few texels recoloured", rel, changed)
        assert files["Common/" + OWN_ICON[(LAN_FAM, t)]] == lan_metal_icon(t) and n["Icon"] == OWN_ICON[(LAN_FAM, t)]
        rows.append("%s %s: %d texels (%s)" % (OWN_RARITY[t], LAN_METAL[t], changed, ", ".join(rects)))
    print("metal lanterns (0.5.16): Normal recipe %s; %s; glowing cores and alpha unchanged" % (
        " + ".join("%s x%d" % (x["ItemId"], x["Quantity"]) for x in n1["Recipe"]["Input"]), " | ".join(rows)))


_metal_lantern_checks()


def _ladder_audit():
    """0.5.4 build check, Skyy 2026-10-03: "all accessories and bags cost the last rarity/size to craft the next one". Every ladder of this
    mod: an item of rarity / tier n > 1 that HAS a recipe must take the n-1 item of its line exactly once; the first rung takes none of its
    own line. Lines: the crafted stat lines (word ids), the bench accessory ladders (_T<n>), the Lantern. Single items (Omni, Void Charms,
    Campfire) and lines without recipes (part 2 lines: admin give until the loot pass; retired / legacy ids) are listed."""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    ladders = {}
    for b in FOLDED:
        ladders["%s line" % b[2]] = [booster_id(b, t) for t in range(1, 5)]
    for b in ACTIVE:
        if b[3] > 1:
            ladders["%s accessory" % b[2]] = ["Skyy_Accessory_%s_T%d" % (b[0], t) for t in range(1, b[3] + 1)]
    ladders["Lantern line"] = list(LAN_IDS)
    for name, ids in ladders.items():
        for k, i in enumerate(ids):
            ins = [x.get("ItemId") for x in items[i]["Recipe"]["Input"]]
            if k == 0:
                assert not any(x in ids for x in ins), "%s: %s takes its own line" % (name, i)
            else:
                assert ins.count(ids[k - 1]) == 1 and not any(x in ids and x != ids[k - 1] for x in ins), \
                    "%s: %s must be crafted from %s (the previous tier rule): %r" % (name, i, ids[k - 1], ins)
    no_recipe = [b[2] for b in BOOSTERS if b[8] is None]
    assert all("Recipe" not in items[i] for b in BOOSTERS if b[8] is None for i in [booster_id(b, t) for t in range(1, 5)])
    singles = [i for i in (OMNI, BAG, "Skyy_Accessory_Campfire_T1") if "Recipe" in items[i]]
    print("previous-tier audit: %d ladders follow it (%s); single items %s; no recipe (admin give): %s"
          % (len(ladders), ", ".join(sorted(ladders)), ", ".join(singles), ", ".join(no_recipe)))


_ladder_audit()


def _own_icon_checks():
    """0.5.7 build check: every booster id (40 line + 4 Lantern + 20 hidden legacy) shows our own icon of its line and tier, the PNG is in
    the jar at Common/<Icon>, 64 x 64 RGBA, premultiplied; 44 distinct icons; every other item keeps a vanilla icon (or the bag's)"""
    items = dict((os.path.basename(p)[:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    want = {}
    for li, b in enumerate(BOOSTERS):
        for t in range(1, 5):
            want[LINE_IDS[li * 4 + t - 1]] = OWN_ICON[(b[0], t)]
        if b[9] == "word":
            for w, t in LEGACY_WORDS:
                want["Skyy_Talisman_%s_%s" % (b[0], w)] = OWN_ICON[(b[0], t)]
    for t in range(1, 5):
        want[LAN_IDS[t - 1]] = OWN_ICON[(LAN_FAM, t)]
    assert len(want) == 64 and len(set(want.values())) == 44, (len(want), len(set(want.values())))
    for iid, rel in want.items():
        assert items[iid]["Icon"] == rel, (iid, items[iid]["Icon"], rel)
        png = files["Common/" + rel]
        img = _SA.png_decode(png)
        assert (img.w, img.h) == (64, 64) and png[24] == 8 and png[25] == 6, ("64x64 RGBA8", rel)
        px = img.px
        assert all(px[k] <= px[k - (k % 4) + 3] for k in range(len(px)) if k % 4 != 3), ("premultiplied", rel)
    own = set("Common/" + r for r in OWN_ICON.values()) | {"Common/" + BAG_VIS["Icon"]}   # 0.5.8: + the Void Charms' own icon
    assert sorted(p for p in files if p.startswith("Common/Icons/ItemsGenerated/")) == sorted(own), "0.5.8: exactly our 44 icons + the bag icon in ItemsGenerated"
    for iid, n in items.items():
        if iid not in want and iid != BAG:
            assert "Common/" + n["Icon"] in _COMMON and not n["Icon"].startswith("Icons/ItemsGenerated/SkyyAccessories_"), (iid, n["Icon"])
    print("own icon audit: %d booster ids (40 line + 4 Lantern + 20 hidden legacy) -> %d distinct own 64x64 icons; %d other items keep "
          "their vanilla icon; the Void Charms has its own" % (len(want), len(set(want.values())), len(items) - len(want) - 1))


_own_icon_checks()


def _bag_look_check():
    """0.5.8 build check: the Void Charms = the manifest look (model / texture / icon / IconProperties), its 3 files ship (bytes, never a
    vanilla path), no animation / player set; the PNGs have the manifest sizes; no Parallel with fewer than 2 entries in the jar"""
    import struct as _st
    n = json.loads(files["Server/Item/Items/Utility/%s.json" % BAG])
    for k, v in BAG_VIS.items():
        assert n[k] == v, (k, n[k], v)
    assert "Animation" not in n and "PlayerAnimationsId" not in n and "Particles" not in n, "the bag keeps the vanilla Item hold"
    assert n["Interactions"] == {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": "SkyyAccBag"}}]}}, n["Interactions"]
    for k in ("Model", "Texture", "Icon"):
        assert isinstance(files["Common/" + n[k]], bytes) and ("Common/" + n[k]) not in _COMMON, k
    tw, th = _st.unpack(">II", files["Common/" + n["Texture"]][16:24])
    iw, ih = _st.unpack(">II", files["Common/" + n["Icon"]][16:24])
    assert [tw, th] == BAG_MAN["texture_size"] and (iw, ih) == (64, 64), (tw, th, iw, ih)
    bad = []
    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                bad.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    nj = 0
    for p, t in files.items():
        if p.startswith("Server/") and p.endswith(".json"):
            walk(p, json.loads(t))
            nj += 1
    assert not bad, "a Parallel with fewer than 2 entries (the engine refuses the whole pack): %s" % bad
    print("bag look checked: %s = %s (texture %d x %d, icon 64 x 64), %d JSON files without a short Parallel" % (BAG, n["Model"], tw, th, nj))


_bag_look_check()


def _gem_order_check():
    """0.5.9 build check: the Void Charms model's 5 gems (tools/art/make_bags.py ACC_GEMS, left to right) = the approved icon's gems
    (art/accessory-bag-icon/manifest.json gems_left_to_right hex_mid): Option B - Health red, Stamina yellow, Mana blue, Regeneration
    green, Speed cyan; the tab icon is the art folder's file byte for byte"""
    import importlib.util as _ilu3
    _sp = _ilu3.spec_from_file_location("make_bags_gems", os.path.join(os.path.dirname(HERE), "tools", "art", "make_bags.py"))
    _mb = _ilu3.module_from_spec(_sp)
    _sp.loader.exec_module(_mb)
    mids = ["#%02x%02x%02x" % tuple(g[2]) for g in _mb.ACC_GEMS]
    man = json.load(open(os.path.join(TAB_ICON_DIR, "manifest.json"), encoding="utf8"))
    ent = [f for f in man["files"] if f["path"] == TAB_ICON_REL][0]
    want = [g["hex_mid"].lower() for g in ent["gems_left_to_right"]]
    assert [g["line"] for g in ent["gems_left_to_right"]] == ["Health", "Stamina", "Mana", "Regeneration", "Speed"], ent["gems_left_to_right"]
    assert mids == want == ["#d23a3a", "#d6a800", "#2f6fe0", "#2fb34f", "#4ac0cc"], (mids, want)   # ui-data: the gem art colours, no UI
    assert files["Common/" + WB.icon_path("SkyyAccessories")] == open(TAB_ICON_SRC, "rb").read()
    print("gem order checked: the bag model's gems = the icon's, left to right %s" % ", ".join(mids))


_gem_order_check()


def _player_literals_check():
    """0.5 build check: no Java string literal of this script says Vitality / Endurance / Intelligence / Talisman / talisman, except
    item ids and id words (the id rules need them), the movement source name and the one notice text (MIG_NOTICE, spec 5.1). Scans every
    string constant / f-string of this script that holds Java (a "public " member) - chat, page, refusal and command texts included."""
    import ast as _ast, re
    tree = _ast.parse(
open(os.path.abspath(__file__), encoding="utf8").read())
    ok_exact = set(["Vitality", "Endurance", "Intelligence", "Talisman", "Ring", "Artifact", "Legendary", "accessories.talismans",
                    "_Talisman", "_Ring", "_Artifact", "Skyy_Talisman_", "T:"])
    id_re = re.compile(r"^Skyy_[A-Za-z0-9_]*$")
    lit_re = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
    n = 0
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            txt = node.value
        elif isinstance(node, _ast.JoinedStr):
            txt = "".join(v.value for v in node.values if isinstance(v, _ast.Constant) and isinstance(v.value, str))
        else:
            continue
        if not re.search(r"(^|\n)\s*(public|protected)\s", txt):
            continue
        txt = re.sub(r"//[^\n]*", "", txt)
        for m in lit_re.finditer(txt):
            lit = m.group(1)
            n += 1
            if lit in ok_exact or id_re.match(lit) or lit == jlit(MIG_NOTICE)[1:-1]:
                continue
            if any(w in lit for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in lit.lower():
                raise SystemExit("0.5: a Java string literal says an old name (players must only see line names): %r" % lit)
    page = [ACC_HINT, ACC_NONE, ACC_NONE_OFF, ACC_EMPTY] + [SUI.render(v) for _p, mk in ACC_SH for v in (mk.variants() if isinstance(mk, SUI.Choice) else (mk,))] + \
        [SUI.render(v) for _i, _p, v in ACC_SH.sets]   # 0.5.22: the Void Charms views (an Appends)

    for t in page:
        if any(w in t for w in ("Vitality", "Endurance", "Intelligence", "Talisman")) or "talisman" in t.lower():
            raise SystemExit("0.5: a page text says an old name: %r" % t[:200])
    print("player texts: %d Java string literals and %d page texts scanned, no old names" % (n, len(page)))


_player_literals_check()

# ================= 0.5.4 ACCESS AUDIT (the SkyyUiProbe 0.3.1 lesson; this repo's SkyyArmory 0.1 audit): what the JVM would refuse at RUN time
# with IllegalAccessError - javassist compiles a call to a protected / package-private member from any class and -Xverify:all does not catch
# it. Every class / member reference in the final class bytes is resolved with the JVM's rules; the build stops on any refused one.
import jpype as _jpa
_JMod = _jpa.JClass("javassist.Modifier")
_JConstPool = _jpa.JClass("javassist.bytecode.ConstPool")
_JClassFile, _JDataIn, _JByteIn = (_jpa.JClass("javassist.bytecode.ClassFile"), _jpa.JClass("java.io.DataInputStream"),
                                   _jpa.JClass("java.io.ByteArrayInputStream"))
_AUDIT_OPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
              0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
              0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}


def _audit_pkg(name):
    return name.rsplit(".", 1)[0] if "." in name else ""


def _audit_elem(name):
    n = name.replace("/", ".").lstrip("[")
    if n.startswith("L") and n.endswith(";"):
        return n[1:-1]
    return None if len(n) == 1 and name.startswith("[") else n


def access_audit(items_):
    refused, used, seen = [], set(), 0
    for D, cf in items_:
        dn = str(D.getName())
        for mi in cf.getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it = mi.getConstPool(), ca.iterator()
            while it.hasNext():
                pos = it.next()
                op = it.byteAt(pos)
                if op not in _AUDIT_OPS:
                    continue
                where = "%s.%s @%d %s" % (dn.rsplit(".", 1)[-1], mi.getName(), pos, _AUDIT_OPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic (javassist never writes one)")
                    continue
                idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != _JConstPool.CONST_Class:
                    continue
                if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                    cname, member = str(cp.getClassInfo(idx)), None
                elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                    cname, member = str(cp.getFieldrefClassName(idx)), ("field", str(cp.getFieldrefName(idx)), str(cp.getFieldrefType(idx)))
                elif tag == _JConstPool.CONST_InterfaceMethodref:
                    cname, member = str(cp.getInterfaceMethodrefClassName(idx)), ("method", str(cp.getInterfaceMethodrefName(idx)),
                                                                                  str(cp.getInterfaceMethodrefType(idx)))
                else:
                    cname, member = str(cp.getMethodrefClassName(idx)), ("method", str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                seen += 1
                try:
                    en = _audit_elem(cname)
                    if en is not None and _audit_pkg(en) != _audit_pkg(dn) and not _JMod.isPublic(pool.get(en).getModifiers()):
                        refused.append("%s: class %s is not public - the JVM refuses it from %s (IllegalAccessError)" % (where, en, dn))
                    if member is None:
                        continue
                    kind, name, desc = member
                    Cc = pool.get("java.lang.Object" if cname.startswith("[") else cname)
                    if kind == "field":
                        x = Cc.getField(name, desc)
                    elif name == "<init>":
                        x = Cc.getConstructor(desc)
                    else:
                        x = Cc.getMethod(name, desc)
                    md, decl = x.getModifiers(), x.getDeclaringClass()
                    dcn = str(decl.getName())
                    if _JMod.isPublic(md) or (_audit_pkg(dcn) == _audit_pkg(dn) and not _JMod.isPrivate(md)):
                        continue
                    if _JMod.isPrivate(md):
                        ok = dcn == dn
                    elif _JMod.isProtected(md):
                        ok = bool(D.subclassOf(decl))
                    else:
                        ok = False
                    use = "%s %s.%s%s" % (_JMod.toString(md), dcn, name, "" if kind == "field" else desc)
                    if ok:
                        used.add("%s.%s (from %s)" % (dcn.rsplit(".", 1)[-1], name, dn.rsplit(".", 1)[-1]))
                    else:
                        refused.append("%s: %s - the JVM refuses it from %s (IllegalAccessError)" % (where, use, dn))
                except Exception as e:
                    refused.append("%s: %s %s does not resolve: %s" % (where, cname, member, e))
    return refused, sorted(used), seen


def _audit_cf(data):
    return _JClassFile(_JDataIn(_JByteIn(data)))


_st = pool.makeClass(PKG + ".AccessAuditSelfTest")
_st.addMethod(CtNewMethod.make("public static void bad(com.hypixel.hytale.server.core.plugin.JavaPlugin p) { p.setup(); }", _st))
_st_refused, _st_used, _st_n = access_audit([(_st, _audit_cf(_st.toBytecode()))])
_st.detach()
assert len(_st_refused) == 1 and "setup" in _st_refused[0] and "IllegalAccessError" in _st_refused[0], \
    "access audit self-test: a protected JavaPlugin.setup() call from a non-subclass must be refused: %s" % _st_refused
_aitems = []
for _root, _dirs, _fls in os.walk(OUT):
    for _fn in sorted(_fls):
        if _fn.endswith(".class"):
            _cn = os.path.relpath(os.path.join(_root, _fn), OUT)[:-6].replace(os.sep, ".")
            with open(os.path.join(_root, _fn), "rb") as _fh:
                _aitems.append((pool.get(_cn), _audit_cf(_fh.read())))
AUDIT_REFUSED, AUDIT_USED, AUDIT_N = access_audit(_aitems)
if AUDIT_REFUSED:
    raise SystemExit("ACCESS AUDIT: %d reference(s) the JVM would refuse at run time (IllegalAccessError):\n  %s"
                     % (len(AUDIT_REFUSED), "\n  ".join(AUDIT_REFUSED)))
print("access audit: %d class / member references in %d classes, 0 the JVM would refuse; non-public engine members used: %s"
      % (AUDIT_N, len(_aitems), ", ".join(AUDIT_USED) or "none"))

# ================= 0.5.21: ACCESSORY RECIPES ONLY IN THE ACCESSORY BAG (tools/accessories_0_5_21_patch.py; Skyy 2026-10-16 "we can then remove
# them from the crating and the bench. because they are crafted in the accessory bag."). After every earlier check ran on the 0.5.20 files:
# each of the 50 recipes (all sat in the Workbench tab, WB_REQ) gets the bag's own BenchRequirement - ids, inputs, outputs, KnowledgeRequired,
# ItemLevel unchanged; the lines are the only change in each item file (key order kept).
BAGCRAFT_REQ = [{"Type": "Crafting", "Id": BAGCRAFT_ID, "Categories": [BAGCRAFT_CAT]}]
_c9 = []
for _p9 in sorted(files):
    if not (_p9.startswith("Server/Item/Items/") and _p9.endswith(".json")):
        continue
    _n9 = json.loads(files[_p9])
    if not _n9.get("Recipe"):
        continue
    assert json.dumps(_n9, indent=2) == files[_p9], "0.5.21: %s must round-trip byte for byte" % _p9
    assert _n9["Recipe"]["BenchRequirement"] == WB_REQ, "0.5.21: %s is not a Workbench-tab recipe: %r" % (_p9, _n9["Recipe"]["BenchRequirement"])
    _n9["Recipe"]["BenchRequirement"] = BAGCRAFT_REQ
    files[_p9] = json.dumps(_n9, indent=2)
    _c9.append(os.path.basename(_p9)[:-5])
assert len(_c9) == 50 and BAG not in _c9 and OMNI in _c9 and set(LAN_IDS) <= set(_c9), len(_c9)
assert not any(WB.TAB_ID in files[_p9] for _p9 in files if _p9.startswith("Server/Item/Items/")), "0.5.21: no item of this mod is in the Workbench tab"
# the texts that said "at a Workbench" (item tooltips, both key twins) -> the bag's Craft tab
_lt9 = files["Server/Languages/en-US/server.lang"]
for _o9, _w9 in ((" (upgrade it at a Workbench).", " (upgrade it in the Craft tab of your Void Charms)."),
                 ("Crafted at a Workbench from all", "Crafted in the Craft tab of Void Charms from all"),
                 ("craft one at a Workbench.", "craft one in the Craft tab of your Void Charms.")):
    assert _lt9.count(_o9) >= 2 and _lt9.count(_o9) % 2 == 0, (_o9, _lt9.count(_o9))
    print("0.5.21 tooltip text: %d x '%s' -> '%s'" % (_lt9.count(_o9), _o9.strip(), _w9.strip()))
    _lt9 = _lt9.replace(_o9, _w9)
assert "at a Workbench" not in _lt9, "0.5.21: no tooltip sends players to a Workbench any more"
files["Server/Languages/en-US/server.lang"] = _lt9
print("0.5.21: %d accessory recipes moved off the Workbench tab into the Void Charms (BenchRequirement %s / %s); none on a bench or in /craft"
      % (len(_c9), BAGCRAFT_ID, BAGCRAFT_CAT))

# ================= 0.5.22 (tools/accessories_0_5_22_patch.py): THE DROP-ONLY LINES UPGRADE IN THE BAG (spec 5.2; Skyy "the ones that can be upgraded
# only appear in the craft menu when you have one equipped"): Unique / Rare / Legendary of Brawler, Runic, Stonehide, Razorfang and Feather get an
# upgrade recipe in the bag's own category (each takes the rarity below + its materials, DROP_UP_RECIPES); the Normal never gets one (it drops).
# AccCraft shows a drop-up line only while one of it is in the bag (AccCraft.step 'd'). Their tooltips name the bag's Craft tab.
_li22 = dict((_b[0], _li) for _li, _b in enumerate(BOOSTERS))
_n22 = 0
_lt22 = files["Server/Languages/en-US/server.lang"].split("\n")
for _fam in DROP_UP:
    _li = _li22[_fam]
    for _t in range(2, 5):
        _iid = LINE_IDS[_li * 4 + _t - 1]
        _p22 = "Server/Item/Items/Utility/%s.json" % _iid
        _node = json.loads(files[_p22])
        assert "Recipe" not in _node and _node["Quality"] == QUAL_IDS[_t], (_iid, "0.5.22: a part 2 id had no recipe")
        _node["Recipe"] = {"Input": [{"ItemId": LINE_IDS[_li * 4 + _t - 2], "Quantity": 1}] + [mat(_m, _q) for _m, _q in DROP_UP_RECIPES[_fam][_t - 2]],
                           "BenchRequirement": BAGCRAFT_REQ}
        files[_p22] = json.dumps(_node, indent=2)
        _n22 += 1
    for _t in range(1, 4):   # "Next: <next rarity>." -> where the upgrade is made
        _iid = LINE_IDS[_li * 4 + _t - 1]
        _old = "Next: %s." % booster_name(_li, _t + 1)
        _new = "Next: %s (drop only - upgrade it in the Craft tab of Void Charms)." % booster_name(_li, _t + 1)
        for _k in ("items.%s.description=" % _iid, "server.items.%s.description=" % _iid):
            _hit = [_x for _x, _l in enumerate(_lt22) if _l.startswith(_k)]
            assert len(_hit) == 1 and _lt22[_hit[0]].count(_old) == 1, (_k, _old)
            _lt22[_hit[0]] = _lt22[_hit[0]].replace(_old, _new)
assert _n22 == 15, _n22
# THE RETIRED BAG ITEM (Skyy "id like to ditch the item and just use the menu"): the item stays defined (a stray copy in a chest still loads,
# right-click still opens Void Charms) but leaves the creative library (Variant, no Categories) and says what happened
_bn22 = json.loads(files["Server/Item/Items/Utility/%s.json" % BAG])
assert "Recipe" not in _bn22 and "Categories" in _bn22, "0.5.22: the bag item had no recipe since 0.5.20"
del _bn22["Categories"]
_bn22["Variant"] = True
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(_bn22, indent=2)
_bname = "Old Accessory " "Bag"
_bdesc = ("Retired - your accessories live in Void Charms now: SkyWynn Menu > Character > Void Charms, or /charms. This item holds nothing "
          "and is removed from your inventory; right-click opens Void Charms.")
_bk = 0
for _x, _l in enumerate(_lt22):
    for _pre in ("items.%s.name=" % BAG, "server.items.%s.name=" % BAG):
        if _l.startswith(_pre):
            _lt22[_x] = _pre + _bname
            _bk += 1
    for _pre in ("items.%s.description=" % BAG, "server.items.%s.description=" % BAG):
        if _l.startswith(_pre):
            _lt22[_x] = _pre + _bdesc
            _bk += 1
assert _bk == 4, _bk
files["Server/Languages/en-US/server.lang"] = "\n".join(_lt22)
# the kit's Sky Window art (the hub page; HUBS-CONTRACT 2.7: all 59 files, byte-identical in every hub jar)
_kit22 = SUI.kit_texture_files()
assert len(_kit22) == 59 and not set(_kit22) & set(files), "0.5.22: the kit art"
files.update(_kit22)
print("0.5.22: %d drop-only upgrade recipes (%s: Unique / Rare / Legendary, in the bag's own category), the bag item retired (hidden, "
      "renamed '%s'), %d kit art files" % (_n22, ", ".join(DROP_UP), _bname, len(_kit22)))

jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyAccessories", VERSION, "SkyWynn Void Charms: bench accessories unlock /craft (SkyySacks) recipes; stat accessories in ten lines (Health, Stamina with Stamina Regen, Mana, Regeneration, Speed, and admin-given Brawler, Runic, Stonehide, Razorfang and Feather - combat stats through SkyyGear, fall damage through SkyySkills) in the gear rarities Normal to Legendary add their bonus while they sit in the bag, only the best of each line counts; the Omni accessory counts as every bench accessory; the Lantern line (Normal to Legendary, each crafted from the rarity below) makes its wearer glow like a torch for everyone and lights farther with each rarity through a hidden light above them; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol; up to 60 bag slots (18 by default); one bag per SkyyProfiles profile when that mod is installed; the Campfire accessory is quick inventory cooking (campfire dishes in /craft at reduced Cooking XP and bonus with SkyyCooking); the Alchemy Bench and Cooking Bench accessories are retired; bag slots, every booster number and the line switches are server settings (config.properties, editable in game through SkyWynn Menu -> Server Setup); /charms lines lists every line. Zero dependencies.", PKG + ".SkyyAccessoriesPlugin"), OUT, files)
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", "Frame_Character", "Tertiary")) == 59, "0.5.22: the jar's kit art"
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyAccessories.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyAccessories" % VERSION, disable_prefix="Skyy:")
