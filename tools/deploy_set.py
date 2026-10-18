"""Deploy the whole SkyWynn test set to the "HUD mod" world in one step - ONLY after Skyy says "deploy".

Usage (game closed):   python tools/deploy_set.py            -> shows the plan, asks for "yes"
                       python tools/deploy_set.py --yes      -> no question (Skyy already said deploy)
                       python tools/deploy_set.py --check    -> only checks that every jar exists

It does exactly what each build script's --deploy block does (B.deploy + B.enable_in_world with disable_prefix="Skyy:"), for every mod
in SET, using the jars that are ALREADY BUILT (it never rebuilds). It refuses to run while a Hytale server (HytaleServer.jar java
process) is running, because replacing a mod jar under a running server can break it. Mods not in SET are left alone.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skyybuild as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = "NewBetaTest"   # 2026-10-15 Skyy: "im starting a new world to test from scratch" (was "HUD mod" until 2026-10-15)
# (mod, version) - keep in sync with HANDOFF section 3 "Versions"
SET = [
    ("SkyyCore", "1.0.0"),   # 2026-10-15 merge phase 1: the shared library - MUST stay first while any pinned jar depends on it
    # SkyyGear 0.3.0 (2026-10-13, lifelong tools + tier gate): ROLLBACK to 0.2.26 is item-safe, but tools become droppable / sellable /
    # craftable again and the per-profile tool points (Skyy_SkyyGear lifelong data) are ignored until 0.3.x returns.
    ("SkyyHud", "0.3.32"), ("SkyySacks", "0.8.21"), ("SkyyCoins", "0.1.9"), ("SkyyCollections", "0.2.25"), ("SkyyParty", "0.1.10"),
    ("SkyyBank", "0.1.16"), ("SkyyIslands", "0.5.19"), ("SkyyBazaar", "0.1.20"), ("SkyyGear", "0.3.21"), ("SkyySkills", "0.4.50"),
    ("SkyyAccessories", "0.5.25"), ("SkyyClasses", "0.1.37"), ("SkyyMenu", "0.3.38"), ("SkyyEssentials", "0.1.15"), ("SkyyProfiles", "0.1.17"),
    ("SkyyCooking", "0.1.11"), ("SkyyTrees", "0.3.23"),
    # Exploration round (research/Exploration-Build-Spec.md section 5): SkyySkills 0.4.1+ has the Exploration row, SkyyTrees 0.2+ the
    # Acrobatics + Exploration trees; never go back to SkyySkills 0.4 once Exploration XP exists (0.4 drops the unknown Exploration
    # keys on its next save)
    ("SkyyExploration", "0.2.14"),
    # party + guild round (Skyy 2026-09-24, 2-player test): SkyyHud's Party + Guild widgets read only the bridge keys SkyyParty 0.1.3
    # (party:fn:members / party:leader / party:name / party:stats) and SkyyGuilds (guild:<uuid> / guild:info / guild:fn:online) publish
    ("SkyyGuilds", "0.1.11"),
    # beta backlog round (Skyy 2026-09-24 20:10 list, cross-checked together): SkyySkills 0.4.2 + SkyyTrees 0.2.1 + SkyyCollections
    # 0.2.1 deploy TOGETHER (felled-log crediting: Skills -> coll:fn:add "skills:felled" + skill:on:felled; Double Jump: Trees posts
    # skill:bonus "doublejump.acrobatics", Skills publishes skill:dj:key); SkyyTrees 0.2.1 rewrites Acrobatics.RDodge as RDouble on
    # the next save, so do not go back to SkyyTrees 0.2 after it ran. SkyyIslands 0.5 migrates island files at start (0.4.x copies
    # kept as <key>.properties.v4bak). SkyyMenu 0.1.3 runs /island menu, /bank, /vault, /reforge, /party, /guild of the pins here.
    ("SkyyVault", "0.1.9"),
    # auction house (Skyy 2026-09-24, BIN only; research/Auction-House-Spec.md). Merges into SkyyEconomy 0.1 later (SkyyEconomy-Plan.md)
    ("SkyyAuctions", "0.1.12"),
    # in-game server setup (research/Server-Setup-Spec.md): SkyyMenu 0.3 = player Settings (0.2) + admin Server Setup / Mods section;
    # SkyyRanks 0.1 = ranks + grants + per-player denies + chat prefix, made in game (never removes hytale:Adventurer).
    # SkyyIslands 0.5.1 = SECURITY hotfix (0.5 gave every player skyyislands.admin through /island reload) - never deploy 0.5 again.
    ("SkyyRanks", "0.1.2"),
    # vanilla UI pass (2026-09-29): DEV/TEST mod - /skyprobe (admin only) opens the shared kit's probe pages so Skyy can confirm the
    # vanilla look works inline before any restyled page ships. Move it to RETIRED once the probe results are in.
    # gathering probe pack P0 (2026-10-06, research/Gathering-Progression-Spec.md): op-only dev mods for ONE test session - remove BOTH after Skyy's
    # test. SkyyGatherProbeB-0.1.jar is built into SkyyGatherProbe/ and moved to SkyyGatherProbeB/ by hand.
    # FLOOR (2026-10-07): never roll SkyyArmory below 0.1.6 once spellbooks / kunai exist in player hands (15 new item ids -> unknown
    # items). SkyyGear below 0.2.8 with Armory 0.1.6 shows the new kunai as Lv 20-27 and changes the vanilla Weapon_Kunai damage base
    # (no data loss). Armory 0.1.6 + Classes 0.1.13 + Gear 0.2.8 deploy TOGETHER.
    # FLOOR (2026-10-07): never roll SkyyArmory below 0.1.7 once Bo staffs / hand wraps / gauntlets exist in player hands (new item
    # ids -> unknown items). Armory 0.1.7 + Gear 0.2.9 deploy TOGETHER (Gear 0.2.9 scales the Monk weapons; 0.2.8 under-scales them).
    # FLOOR (2026-10-07, Monk + Assassin playable): SkyyClasses 0.1.14 + SkyySkills 0.4.21 + SkyyProfiles 0.1.6 + SkyyMenu 0.3.9 deploy
    # TOGETHER (never Classes 0.1.14 without Skills 0.4.21 - the Monk would earn no XP). Roll back below them only if no Monk profile
    # exists; otherwise roll back all four together and expect classless Monk profiles (no items / coins / XP lost; Combat.Shaman kept).
    # FLOOR (2026-10-08, perks25): before rolling SkyySkills below 0.4.25 switch "Class Stamina" and "Class balance boost" OFF in Server
    # Setup and let players log in once (0.4.24 never removes the saved modifiers skyyskill_classstamina / classboosthp / classboostmana / classbooststamina).
    # FLOOR (2026-10-09, mining armor): SkyyGear 0.2.15 -> 0.2.14 is safe for items, but BEFORE rolling back delete the 7 set.mining_*
    # lines from Skyy_SkyyGear/config.properties (0.2.14 would turn Adamantite / Mithril / Onyxium spd into an always-on full-set Speed bonus).
    # FLOOR (2026-10-08, loot round): never roll SkyyGear below 0.2.11 without first setting unid.bags=false and having players identify every
    # mystery bag (bags become unknown items in 0.2.10). Never roll SkyyExploration below 0.2.4 without first setting luggage.enabled=false,
    # visiting each world until /exploreadmin stats shows out 0 / claimed 0, then deleting Skyy_SkyyExploration/luggage/. SkyyMobs 0.1.5: no floor.
    # FLOOR (2026-10-08, class path trees): rolling SkyyTrees back to 0.3.2 loses players' path picks (nothing else; 0.3.2 reads the
    # migrated files). SkyyArmory 0.1.9 is safe with Trees 0.3.2 (reads 0 for every node).
    # SkyyFishing 0.1 (2026-10-08, stage 1): takes over the reel probe's rod ids + SkyyFishing_Reel stat. Rollback floor: once players hold
    # fishing items, removing SkyyFishing turns rods / reels / parts / fish into unknown items.
    ("SkyyFishing", "0.1.10"),
    # mob levels (Skyy 2026-10-02, Q&A round 5): NEW standalone mod, stage 1 - hostile mobs + neutral fighters get a level from the
    # zone / biome they spawn in, more health + damage per level (Difficulty), "[Lv 9] Name" plates, /mobs, mob:fn:level. No dependency,
    # no data migration, nothing else needs a bump.
    ("SkyyMobs", "0.1.10"), ("SkyyWorldGen", "0.7.3"),
    # Zone 1 town probe (2026-10-08, admin-only, test island only): REMOVE after Skyy's test - run /townprobe undo until "Nothing to undo" first.
    # key probe (2026-10-08, op only): which client keys reach the server -> class ability hotkeys. REMOVE after Skyy's test.
    # SkyyMerchants 0.1 (2026-10-09, roaming merchants): no dependency. Rollback: set part.merchants=false, let each zone world be visited
    # until /merchantadmin list shows no merchant out, then remove the jar (else Temple_Klops NPCs named "Traveling Merchant" stay).
    ("SkyyMerchants", "0.1.6"),
    # SkyyPets 0.1 (2026-10-09, slot pets phase 1: records + buffs, no creatures). FLOOR: before removing SkyyPets switch Server Setup >
    # Pets > Pets OFF and let players log in once (the skyypet_* max-stat modifiers are saved with the player).
    # SkyyPets 0.2 (2026-10-10, visible pets): REMOVAL / ROLLBACK FLOOR - pet creatures get saved in chunks (P5: NonSerialized does not stop it).
    # Before rolling back to 0.1 or removing SkyyPets: Server Setup > Pets > "Show pets in the world" OFF (or every player logged out), then restart.
    ("SkyyPets", "0.4.3"),
    ("SkyyWardrobe", "0.2.9"),
    # SkyyQuests 0.2 (2026-10-13, quest answers: class gear rewards, skip, area lines, co-op, feed only). ROLLBACK FLOOR to 0.1: players with
    # "=gear|" in Skyy_SkyyQuests/players/*.properties run /quests claim first; Undo the reward lines in Server Setup > Changes
    # (defeat_mobs / mini_boss); optionally restore quests/tutorial.properties from tutorial.properties.0.1.bak.
    ("SkyyQuests", "0.4.1"),  # 2026-10-13 quest engine + tutorial line + quest widget (research/SkyyQuests-Tutorial-Spec.md Q1)
    ("SkyyRebirth", "0.3.5"),  # 2026-10-14 NEW rebirth R2 (OFF by default). Removing it drops rebirth counts + raised caps (skill XP past the base cap stays in the skill files); nothing else depends on it
    ("SkyyShards", "0.4.2"),  # 2026-10-14 NEW shard worlds (Gathering phase 5); deploy WITH Islands 0.5.8 + Menu 0.3.22. FLOOR: once a skyy-shard-<pkey> world exists, never drop Shards or roll Islands below 0.5.8
    # FLOOR (2026-10-15, SkyySkills 0.4.43): Battlemagic = class-skill slot 19 (saved key Combat.Spellblade). 0.4.42 reads such files but its save DROPS the key - never roll Skills below 0.4.43 once Spellblades played on it.
    # SkyyWorldGen 0.7 (2026-10-15): a jar without the SkyWynnZones2 type cannot decode skywynn_zones2's config.json (one SEVERE
    # "Failed to load world" at boot, every other world fine). Before rolling back to 0.6: players /zone leave, stop the server, delete
    # universe/worlds/skywynn_zones2, mods/Skyy_SkyyWorldGen/zone2_layout_20261014.bin and the skywynn_zones2.* lines of
    # mods/Skyy_SkyyWorldGen/worlds.properties. skywynn_zones (0.6) is untouched by 0.7 and keeps working on 0.6.
    # FLOOR (2026-10-16, SkyyBazaar 0.1.14): rollback to 0.1.13 is NOT safe as-is - 0.1.13 has no sell caps and would sell Eternal seeds / raised seeds / saplings at the new prices (~21x recipe cost). First restore the newest Skyy_SkyyBazaar/config-history/Skyy_SkyyBazaar~products.properties.<stamp>.bak as products.properties and remove the migrated.0.1.14 line from pricing.properties.
    # 2026-10-14 WorldGen 0.6 (zones as floating islands, new world skywynn_zones; /zone 1-5 go there, /zone old = old test island). ROLLBACK below 0.6: server stopped, delete universe/worlds/skywynn_zones + its skywynn_zones.* lines in mods/Skyy_SkyyWorldGen/worlds.properties + zone_layout_20261014.bin first.
    # 2026-10-14 evening: Gear 0.3.6 + Fishing 0.1.6 together; FLOOR Gear 0.3.6 once any of the 68 gathering armor pieces exists (0.3.5 = unknown items). Classes 0.1.25 + Trees 0.3.10 together (Spellblade, rebirth slots 3-4). Islands 0.5.10 + Quests 0.3.2 together (3 starter islands; Server Setup can switch back to Classic).
    # 2026-10-14 rebirth6: Skills 0.4.39 FLOOR while rebirth stat bonuses exist (0.4.38 never removes skyyskill_rebirth* modifiers) - switch "Rebirth stat boosts" off with players online first.
    # 2026-10-14 18:17: Classes 0.1.24 + Trees 0.3.9 together (Warrior / Berserker / Archer). Classes Server Setup rows at 63.5 of 64 KB: split rows into a 2nd holder BEFORE any new rows.
    # 2026-10-14 13:10: Classes 0.1.23 + Trees 0.3.8 together (Monk + Assassin, rebirth R5/R6 parts). FLOOR once any rebirth ran: never below these. Do not add classes / trees to SkyyRebirth PARTS until the 3rd modifier slot (every 5th rebirth) is built.
    # 2026-10-14 12:45: Shards 0.2 FLOOR once any totem / modifier item exists or a totem is placed (pick totems up before a rollback); Rebirth 0.3 needs Bazaar 0.1.11+ + Auctions 0.1.5+ (STOP below); Skills 0.4.37 rollback drops Fishing / Ranching / Orchard XP.
    # 2026-10-14 FLOORS: Skills 0.4.36 / Bank 0.1.11 / Coins 0.1.7 once any profile rebirthed; Rebirth never below 0.2 while a journal is open; Profiles not below 0.1.13 once rebirth is ON.
    # 2026-10-14: before rolling Classes below 0.1.22 set abil.runeHud=false and let every Mage + Priest log in once. Exploration below 0.2.8: airdrop.enabled=false + no drops out first.
    # 2026-10-14: Gear 0.3.4 + Armory 0.1.24 + Collections 0.2.13 together (Sigils); Quests 0.3 + Fishing 0.1.4 + Hud 0.3.23 together (remove the 2 quest NPCs before a Quests rollback); Vault rollback only 30 s+ after the last /pickaxe fetch.
    # SkyySkills 0.4.35 (2026-10-14, rebirth R1): caps from rebirth:fn:cap, skill:fn:run, half Farming XP above tool tier (farming.tierUpXpFactor); no data migration - rolling back to 0.4.34 is safe
    ("SkyyAbilityProbe", "0.1"),  # 2026-10-13 ability keys on 0.7 (research/Ability-Framework-Mage-Spec.md B1) - ONE Skyy test session, then RETIRED
    ("SkyyUiProbe", "0.6"), ("SkyyUiProbeB", "0.5"),  # 2026-10-11 kit / tab / quality-tooltip probes (K1 H1 T1) - ONE Skyy test session, then RETIRED again  # 2026-10-10 Skyy: "build the wardrobe/ loadout system too" - loadouts (armor + hotbar + pets + abilities), per profile
    # SkyyArmory round (2026-10-03): SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 deploy TOGETHER (the 8 ladder staffs move from
    # SkyySkills to SkyyArmory; the wand heal caps read SkyyArmory).
    # 0.1.10 (2026-10-08 hotfix): the 7 spellbook Levitate interactions no longer use a one-entry Parallel (the server refused 0.1.6-0.1.9).
    # 0.1.11 (2026-10-08): Bo staffs lose the charged magic orb (one shared swing root); the vanilla Wood / Bamboo Bo stay SkyySkills' until 0.4.22 hands them over.
    ("SkyyArmory", "0.1.31"),
    # 2026-10-06 evening: SkyySkills 0.4.19 (dodge move gate, no Acrobatics XP cap - roll back only after Undo of acro.maxXpPerMinute 240 -> 0),
    # SkyyHud 0.3.14 (minimap widget, needs BetterMap), SkyyGear 0.2.6 (weapon speed tiers, weapons only).
    # Mob curve (2026-10-06, research/Mob-Curve-Spec.md): SkyyMobs 0.1.4 + SkyyGear 0.2.5 + SkyySkills 0.4.17 TOGETHER (STOP check below). Never roll
    # one back alone; rolling all three back = Undo the "strength.shape linear -> curve" change first (or 0.1.3 runs per level with the file's values).
    # 2026-10-06 night: SkyyArmory 0.1.4 (blink.distance 10 -> 16 + blink.floorCheck 12 -> 0, one-time migration of untouched lines; rolling back
    # keeps 16 / 0 in the file) + SkyyGear 0.2.7 (Charged trust for the two _Wynn crossbows). No other data change; each rolls back alone.
    # SkyyArmory 0.1.3 (2026-10-06 evening): bow leap + blast, wand hang, particle lifespans, hop.force 30, crossbows Weapon_Crossbow_Copper_Wynn /
    # _Onyxium_Wynn. Rolling back below 0.1.3 leaves those crossbow stacks as unknown items - avoid once players crafted them.
    # SkyyArmory 0.1.2 (2026-10-06): crossbow Grapple Bolt (right click = grapple, replaces the guard) + trav.staminaCap 10 -> 5 (one-time
    # migration of an untouched 10 only). Rolling back to 0.1.1 brings the guard back; the cap line stays 5 (hand-edit back if wanted).
    # Traversal round (2026-10-06): SkyyClasses 0.1.12 -> SkyyArmory 0.1.1 -> SkyyGear 0.2.4 together (staff blink, wand hop / burst / heal orb,
    # quick shots; research/Magic-Traversal-Spec.md). No saved-data change; roll back all three together.
    # Sell from bags (2026-10-06): SkyyBazaar 0.1.5 needs SkyySacks 0.7.13 for bag sales (sacks:fn:count/all/take/put/commit); with an older
    # SkyySacks it behaves like 0.1.4. No data migration - rolling either back is safe.
    # Lantern-behind-Tree-Sap (2026-10-06): SkyyCollections 0.2.7 + SkyyAccessories 0.5.6 deploy TOGETHER (coll:lantern bridge; Accessories 0.5.6
    # with Collections 0.2.6 = every Lantern craftable). Rolling back is safe (no data rewritten; Lanterns go back to plain Workbench recipes).
]
# round 6 (2026-09-25): SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2 deploy TOGETHER (Berserker/Fury, Priest/Divinity, class kits;
# Profiles 0.1.1 only draws 6 class cards). Never go back to SkyySkills 0.4.3 once Fury/Divinity XP exists (0.4.3 drops those keys).
# adoption round (2026-09-25): the 16 bumps above register their admin settings (tools/skyycfg.py -> Server Setup) + player Settings
# switches; they need SkyyMenu 0.3. SkyyProfiles 0.1.1 raises an untouched maxProfiles=4 file to 6 (Skyy's 6-profile default).
# third-party mods that are part of the pack (enabled in the world by their manifest key; their files are NOT in this repo -
# a server owner installs them from their authors, see PACK.md). Never disabled by this script.
# 2026-10-06 (Skyy: "add hyfishing right now, along side dynamic season"): HyFishing (fishing until our own fishing mod replaces it) + Dynamic
# Seasons (its fishing seasons must keep working with our fishing mod later). Both only need Hytale modules; Dynamic Seasons optionally
# integrates Angler's Almanac / HyFishing.
PACK_THIRD_PARTY = ["Serj:More Crossbow Tiers",
                    "NoCube:[NoCube's] Orchard",
                    "IBC:Multitools", "BlueOrbit:DynamicSeasons", "dev.ninesliced:BetterMap", "narwhals:Perfect Parries",
                    "LadyPaladra:TheArmory", "EnsoX:WeaponCustomHUD", "MarckAA:ZipLinePlugin", "com.astryxworld:ZoneViewControl",
                    "BlackAures:Aures - Dragon Nestkeeper"]  # 2026-10-17 Skyy: Dragon Nestkeeper "Add it" (popup 1/7; ARR, modpacks allowed; research/Nestkeeper-Pack-Check.md)  # 2026-10-15 Skyy: The Armory 1.23.0 back ON for a test (0.7.2 engine audit clean); WeaponCustomHUD / Zip Line / Zone View Control packed (mod checks 10-15)  # 2026-10-13 0.7.1: DynamicSeasons 7.0.2, BetterMap 1.3.9, Perfect Parries 0.9.7 back ON (authors updated) -  # 2026-10-11 Skyy: "lets add perfect parries" - All Rights Reserved: install from CurseForge, never bundled; per-class tuning goes into ITS world config (tune_perfect_parries)  # 2026-10-10 Skyy: Multitools in the pack (MIT, credit InkBlindCat); SkyyGear 0.2.18+ changes its recipe + stats at runtime  # 2026-10-09 Skyy: test BME main mod (GPLv3, credit in PACK.md + server credits); Humans add-on stays OFF ("No guns")  # 2026-10-08 Skyy: "switch the armory on" - CC BY-NC (credit, never sell; PACK.md); combat armor + Warrior / Berserker / Assassin weapons + boss specials (research/Pack-Armor-Plan.md)  # 2026-10-06: the SkyyHud 0.3.14 minimap reads the map it streams (AGPL - never bundled, never called)  # 2026-10-06 Skyy: fruit trees, Fruit Press + juices (modpacks allowed by its page)
# Advanced Farming was NOT added (Skyy 2026-10-06: out of date, no longer updated -> build its tools into our own mod).
# Skyy mods that were MERGED into another mod and must be switched OFF in the world config on every deploy (their jar may stay in Mods;
# a disabled key is not loaded). Without this, deploy_set only disables older versions of the SAME mod name, and a retired mod would keep
# loading next to its replacement (duplicate commands, two systems). Example: SkyyRolls once SkyyGear replaces it; SkyyCoins, SkyyBank,
# SkyyBazaar and SkyyAuctions once SkyyEconomy replaces them. A name here must not also be in SET.
# round 8 (2026-09-28): SkyySacks 0.7.7 + SkyyCollections 0.2.3 deploy TOGETHER (bag recipe ids, coll:fn:where, migrated rewards file).
# Never roll back below SkyySacks 0.7.7 (Rare/Omni bags + Skyy_Bag_* qualities), SkyySkills 0.4.6 (saved max modifiers - switch Base Mana
# and Overall Level OFF and let players log in once first), or SkyyCollections 0.2.3 without restoring rewards-0.2.properties.
# round 9 + SkyyGear (2026-09-29): SkyyGear 0.1 REPLACES SkyyRolls (migrates SkyyRolls rolls on first touch; SkyyRolls switched off
# below). SkyyAuctions 0.1.2 + SkyyMenu 0.3.3 deploy with SkyyGear 0.1 (gear text, Identify tile). SkyyClasses 0.1.7 needs SkyySkills 0.4.6+.
# Never roll back below SkyyTrees 0.2.4 (Double Jump slot moved in saves). Rolling SkyyAuctions back to 0.1.1: restore 48h:1200 in its
# config.properties by hand first (0.1.1 cannot read 48h:x2).
# vanilla UI pass (2026-09-30): Skyy opened probe pages base1-base4 in game with no disconnect -> the 12 look-only restyles ship:
# Bank 0.1.4, Party 0.1.6, Accessories 0.4.5, Classes 0.1.8, Profiles 0.1.3, Vault 0.1.4, Collections 0.2.4, Guilds 0.1.4 (+ xpSkills
# mid-run fix), Islands 0.5.4, Skills 0.4.7 + Trees 0.2.5 + Exploration 0.2.2 (together). Rolling any of them back to the previous pin
# is safe (no data migration); the rollback floors above still apply.
# SkyyProfiles 0.1.5 (2026-10-01): profile delete + 6-hour undo + admin archive. ROLLBACK FLOOR once any profile was deleted:
# 0.1.4 treats a deleted profile as live again and can reuse an archived profile's id (the new profile would inherit its
# island, coins and bags) - never roll Profiles back below 0.1.5 after a delete.
# SkyyGear 0.2.2 (2026-10-03): wand / staff shot lines, Damage Data box hidden per type (row view.hideDamageBox, restart), crit popup + sparks; no migration - rolling back to 0.2.1 is safe (the box comes back on the next start).
# SkyyGear 0.2.1 (2026-10-03): rolling back to 0.2 is safe - 0.2 ignores the 0.2.1 config block, re-renders the tooltips and clears the
# armor Health lock bonus within one second. The floor stays 0.2.
# SkyyGear 0.2 (2026-10-02): ROLLBACK FLOOR - never roll SkyyGear below 0.2 without first restoring the config History copy
# 'before the 0.2 level bands' (Server Setup -> History): 0.1.3 cannot read '<min>,<cap>' rows, so items would fall back to Hytale's
# own item level (the kit wand / staff would read about Lv 40). Items themselves are safe to roll back.
# SkyyMobs 0.1.3 (2026-10-03): client health-bar fix only (MobLevel.writeValue: min/maxStatValue after a modifier change); no saved-data change - rolling back to 0.1.2 is safe.
# SkyyMobs 0.1 (2026-10-02): rolling it back = take it out of SET and add "SkyyMobs" to RETIRED. Saved mobs keep a Health modifier
# 'skyymobs_lv<N>' and a '[Lv N] Name' plate until they die; to strip them first: Server Setup > Mobs > Never level these = * , then
# walk / reload the chunks, then retire. Settings stay in mods/Skyy_SkyyMobs.
# SkyyWorldGen 0.1 (2026-10-03, NEW): removing it after /zone 1 has run = stop the server and delete
# Saves/HUD mod/universe/worlds/skywynn_z1 FIRST (the saved island names the WorldStructure SkyWynn_Z1_Small from the jar; without the
# jar the generator falls back to empty chunks and saves void into the island), then take it out of SET and add "SkyyWorldGen" to
# RETIRED. Settings stay in mods/Skyy_SkyyWorldGen.
# SkyyTrees 0.3 (2026-10-03): ROLLBACK FLOOR - never roll SkyyTrees below 0.3 once it saved a player file (0.2.5 drops every Alchemy /
# Smithing / class node level on its next save and leaves the skyytree_mana modifier unmanaged; Tokens / Dust are computed, nothing else is
# lost). Respec Alchemy + Smithing (+ class) first if a rollback is unavoidable.
# SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 (2026-10-03): deploy and roll back TOGETHER. Before SkyySkills goes below 0.4.15:
# switch Base Mana off and let players log in once. To roll SkyyArmory back: take it out of SET, add it to RETIRED and put SkyySkills back
# to 0.4.14 in the same deploy (vanilla staff files would charge 50 Mana behind a 10-Mana check otherwise). SkyyClasses back to 0.1.10 is safe.
RETIRED = ["SkyyRolls", "SkyyMonkProbe", "SkyyReelProbe", "SkyyTownProbe", "SkyyPetProbe", "SkyyKeyProbe", "SkyyGatherProbe", "SkyyGatherProbeB", "SkyyFlaskProbe"]  # FlaskProbe 2026-10-17: FP0 passed, Skyy ran /flaskprobe clear ("already did. it worked"); FP1 = SkyyCooking 0.1.11  # GatherProbe(+B) 2026-10-13: broken on Hytale 0.7 (3 removed engine calls), never tested; the gathering spec re-probes on 0.7   # SkyyMonkProbe: tested 2026-10-08 (TEST 48), the real moves are SkyyArmory 0.1.12


# Third-party pack mods switched OFF in the world on every deploy (kept installed).
# 2026-10-09 Skyy: "Armory off until 0.7" - The Armory (708 textures) overflowed the client item/creature texture atlas
# (8192x16384 needed, max 8192x8192: 395 of 2808 images dropped = broken copper ore, talismans, swords). Re-test on Hytale 0.7.
# 2026-10-15 merge PHASE 0 (research/Architecture-Spec.md 2.3): stable-name probe jars for ONE Skyy test (/coreprobe); remove after.
# 2026-10-15 ABILITY TREE REDESIGN (abiltree2): SkyyTrees 0.3.13 + SkyyClasses 0.1.26 deploy TOGETHER. FLOORS: never roll Trees below
# 0.3.13 or Classes below 0.1.26 once a profile migrated (abil.tree2=done) - older jars drop the new A1.<Mod> / A4a / A4b node ids.
STABLE_PROBES = [("SkyyCoreProbe", "0.1.0"), ("SkyyDepProbe", "0.1.0")]
# 2026-10-15 SkyyCore 1.0 (merge PHASE 1, research/Architecture-Spec.md, tools/CORE-CONTRACT.md). HOW TO PIN IT: ("SkyyCore", "1.0.0") as
# the FIRST SET entry (main() STOPs otherwise), then the pilots SkyyBank 0.1.14 / SkyyParty 0.1.9. Stable-name jars (manifest Name =
# the bare mod name, e.g. SkyyCore / SkyyBank) are enabled under their stable world key "Skyy:<Mod>" (read from the jar's manifest),
# and every "Skyy:<ver> <Mod>" key of the same mod is switched off - and the other way round on a rollback to a versioned jar
# (skyybuild.enable_in_world / same_mod_keys). A jar whose manifest has "Dependencies" needs each one in the SET at a version inside
# its range, and only Skyy:SkyyCore may be one (main() STOPs otherwise). Once SkyyCore is pinned the phase 0 probe pair above is no
# longer deployed and its keys are switched off (CORE_RETIRES) - the probes were the throwaway proof, SkyyCore is the real thing.
# FLOORS: none for the pilots' DATA (SkyyBank 0.1.14 / SkyyParty 0.1.9 keep every file byte-compatible): rolling back to SkyyBank
# 0.1.13 / SkyyParty 0.1.8 is safe (the versioned key comes back, Skyy:SkyyBank / Skyy:SkyyParty go off). The one rule: SkyyCore stays
# in the SET while any pinned jar depends on it (rolling SkyyCore back = first roll its dependents back to their pre-Core versions).
CORE_RETIRES = ["SkyyCoreProbe", "SkyyDepProbe"]
PACK_DISABLED = ["TheRedlotus:HyFishing", "Helios:Saplings From Trees", "Frah:Better Mob Expansion", "com.example:ExtendedBackpacks", "Allomere:Tainted Roots"]  # 2026-10-15 Skyy: Extended Backpacks OFF (replaces the vanilla Workbench + Backpack Upgrade items), Tainted Roots OFF for now; Saplings From Trees / BME / HyFishing not updated for 0.7  # 2026-10-13 0.7.1: BetterMap 1.3.9, DynamicSeasons 7.0.2, Perfect Parries 0.9.7 updated by their authors -> back ON (engine-API audit clean)  # 2026-10-13 BetterMap (18 removed engine calls: map packets, waypoints, cave mode) + Perfect Parries (CombatTextUpdate ctor) would crash on 0.7 in play - off until their authors update; 2026-10-13 DynamicSeasons crashes the world on 0.7 (SeasonWeatherSystem -> removed WorldChunk.getBlockChunk) when a player joins  # 2026-10-12 Hytale 0.7.0: Saplings From Trees fails to load (Plant_Leaves_Fig_Blue) and BME fails NPC validation (Template_BME_Goblin_Kamikaze -> missing BME_Bomb_Damage) = the 0.7 server refuses to boot; back ON when their authors update  # 2026-10-10 Skyy: HyFishing OFF ("Switch HyFishing off") - SkyyFishing replaces it


def disable_third_party(world, key):
    import json
    cfg = os.path.join(B.USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    # a key missing from the world config still LOADS (the server enables mods it has no entry for) - write Enabled false then too
    if mods.get(key, {}).get("Enabled", True):
        mods[key] = {"Enabled": False}
        json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
        print("world", world, "switched off", key)


# Perfect Parries (narwhals, pack mod by runtime id) - Skyy 2026-10-11: every class may parry, tuned per class (docs/answered/classes.md):
# melee gets the full parry (stun, counter-hit), Archer / Mage / Priest only a short deflect (no counter bonus) if their weapon can block.
# Its weapon_parry_settings.json takes exact item ids first, then wildcard patterns; the two vanilla Bo staffs are exact ids so they are
# not caught by the Mage's Weapon_Staff_*. Fields: the mod's own (parryWindowMs, counterattack*, knockback*, reflectDamagePercent ...).
_PP_MELEE = {"Warrior": dict(parryWindowMs=260, counterattackWindowMs=500, counterattackDamageMultiplier=1.25, stunnedDamageMultiplier=2.5,
                             knockbackX=6, knockbackY=5, reflectDamagePercent=0.2),
             "Berserker": dict(parryWindowMs=200, counterattackWindowMs=450, counterattackDamageMultiplier=2.0, stunnedDamageMultiplier=3.0,
                               knockbackX=6, knockbackY=5, reflectDamagePercent=0.15),
             "Assassin": dict(parryWindowMs=140, counterattackWindowMs=300, counterattackDamageMultiplier=2.5, stunnedDamageMultiplier=3.0,
                              knockbackX=2.5, knockbackY=2.5, reflectDamagePercent=0.05),
             "Monk": dict(parryWindowMs=180, counterattackWindowMs=600, counterattackDamageMultiplier=1.5, stunnedDamageMultiplier=2.5,
                          knockbackX=4, knockbackY=4, reflectDamagePercent=0.1)}
_PP_DEFLECT = dict(parryWindowMs=120, counterattackWindowMs=0, counterattackDamageMultiplier=1.0, stunnedDamageMultiplier=1.0,
                   knockbackX=3, knockbackY=2, reflectDamagePercent=0.0)
PP_WEAPONS = {"Weapon_Sword_*": "Warrior", "Weapon_Longsword_*": "Warrior", "Weapon_Spear_*": "Warrior", "Weapon_Shield_*": "Warrior",
              "Weapon_Axe_*": "Berserker", "Weapon_Battleaxe_*": "Berserker", "Weapon_Mace_*": "Berserker", "Weapon_Club_*": "Berserker",
              "Weapon_Daggers_*": "Assassin", "Weapon_Kunai*": "Assassin",
              "Weapon_Staff_Bo_Wood": "Monk", "Weapon_Staff_Bo_Bamboo": "Monk", "Weapon_Bo_*": "Monk", "Weapon_Fist_*": "Monk",
              "Weapon_Shortbow_*": "deflect", "Weapon_Crossbow_*": "deflect", "Weapon_Staff_*": "deflect", "Weapon_Spellbook_*": "deflect",
              "Weapon_Wand_*": "deflect"}


def tune_perfect_parries(world):
    """Add our per-class entries to the world's Perfect Parries weapon config. Only MISSING fields are written, so anything Skyy (or a
    server owner) later edits in that file is kept; the mod itself adds its own default entries on load."""
    import json
    d_ = os.path.join(B.USERDATA, "Saves", world, "mods", "Perfect_Parries")
    cfg = os.path.join(d_, "weapon_parry_settings.json")
    d = json.load(open(cfg, encoding="utf-8")) if os.path.isfile(cfg) else {}
    added = 0
    for pat, who in PP_WEAPONS.items():
        want = _PP_DEFLECT if who == "deflect" else _PP_MELEE[who]
        cur = d.setdefault(pat, {})
        for k, v in want.items():
            if k not in cur:
                cur[k] = v
                added += 1
    if added:
        os.makedirs(d_, exist_ok=True)
        tmp = cfg + ".tmp"
        open(tmp, "w", encoding="utf-8").write(json.dumps(d, indent=2))
        os.replace(tmp, cfg)
        print("Perfect Parries: %d per-class fields written for world %s" % (added, world))


def sync_bettermap_worlds(world):
    """BetterMap (pack mod, dev.ninesliced) only maps worlds named in its allowedWorlds list (exact names, no wildcard), so every
    zone / island world shows "usage in this world is not tracked". Skyy 2026-10-10: "see if you can get better maps to work in every
    zone properly" -> on each deploy (game closed) add every world folder of this save to the list. Server-owner config only (no
    BetterMap file is shipped or called); worlds created after the deploy are added by the next deploy."""
    import json
    save = os.path.join(B.USERDATA, "Saves", world)
    cfg = os.path.join(save, "mods", "BetterMap", "config.json")
    wdir = os.path.join(save, "universe", "worlds")
    if not (os.path.isfile(cfg) and os.path.isdir(wdir)):
        return
    raw = open(cfg, encoding="utf-8").read()
    d = json.loads(raw)
    have = d.get("allowedWorlds")
    if not isinstance(have, list):
        return
    add = sorted(n for n in os.listdir(wdir) if os.path.isdir(os.path.join(wdir, n)) and n not in have)
    if add:
        d["allowedWorlds"] = have + add
        tmp = cfg + ".tmp"
        open(tmp, "w", encoding="utf-8").write(json.dumps(d, indent=2))
        os.replace(tmp, cfg)
        print("world", world, "BetterMap now maps", len(add), "more world(s):", ", ".join(add))


def retire_in_world(world, mod):
    """Disable every world-config key 'Skyy:<ver> <mod>' (all versions) and the stable key 'Skyy:<mod>'. Returns how many were switched
    off."""
    import json
    cfg = os.path.join(B.USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    n = 0
    for k in list(mods):
        if (k == "Skyy:" + mod or (k.startswith("Skyy:") and k.endswith(" " + mod))) and mods[k].get("Enabled"):
            mods[k] = {"Enabled": False}
            n += 1
    json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
    print("world", world, "retired", mod, "(%d key(s) switched off)" % n)
    return n


def server_running():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              # java.exe only: the query's own powershell command line contains the search text and would match itself
                              "Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -like '*HytaleServer*' } | Measure-Object | Select-Object -ExpandProperty Count"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return out not in ("", "0")
    except Exception as e:
        print("could not check for a running server:", e)
        return True


def newer_builds(mod, ver):
    """Versions of <mod>-<version>.jar on disk that are HIGHER than the pinned one. A note only: SET decides what deploys (a newer jar
    can be an unreviewed build), but it makes a forgotten SET bump visible instead of silently redeploying the old set."""
    import re
    def v(s):
        return tuple(int(x) for x in s.split("."))
    d = os.path.join(ROOT, mod)
    if not os.path.isdir(d):
        return []
    out = []
    for n in os.listdir(d):
        m = re.match(r"^%s-(\d+(?:\.\d+)*)\.jar$" % re.escape(mod), n)
        if m and v(m.group(1)) > v(ver):
            out.append(m.group(1))
    return sorted(out, key=v)


def world_key_of(mod, ver):
    """the world-config key a SET jar is enabled under: its manifest's Group:Name (stable "Skyy:SkyyCore" or versioned
    "Skyy:0.1.13 SkyyBank"); a jar without a readable manifest = the versioned form as before."""
    man = B.jar_manifest(os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver)))
    return B.world_key(man) if man and man.get("Name") else "Skyy:%s %s" % (ver, mod)


def dependency_stops(pins):
    """[(mod, why)] for SET jars whose manifest Dependencies are not met by the SET (SkyyCore era rules, see SET comments)."""
    out = []
    keys = {}
    for mod, ver in pins:
        man = B.jar_manifest(os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver)))
        if man:
            keys[B.world_key(man)] = (mod, str(man.get("Version", ver)))
    for mod, ver in pins:
        man = B.jar_manifest(os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))) or {}
        for dk, rng in (man.get("Dependencies") or {}).items():
            if dk != B.CORE_ID:
                out.append((mod, "depends on %s - only %s may be a hard dependency" % (dk, B.CORE_ID)))
            elif dk not in keys:
                out.append((mod, "needs %s %s, which is not in SET (pin SkyyCore first)" % (dk, rng)))
            else:
                try:
                    ok = B.range_ok(rng, keys[dk][1])
                except ValueError as e:
                    ok = False
                if not ok:
                    out.append((mod, "needs %s %s, SET has %s" % (dk, rng, keys[dk][1])))
    return out


def main():
    bad = [a for a in sys.argv[1:] if a not in ("--yes", "--check")]
    if bad:   # 2026-09-24: builders ran it with --help and landed on the deploy prompt; unknown arguments now only print the usage
        print(__doc__)
        print("unknown argument(s): %s - nothing done" % " ".join(bad))
        return 2
    clash = [m for m in RETIRED if m in [x[0] for x in SET]]
    if clash:
        print("STOP: retired mod(s) still in SET: %s" % ", ".join(clash))
        return 1
    _p = dict(SET)
    _v = lambda s: tuple(int(x) for x in s.split("."))
    if (_v(_p.get("SkyySkills", "0")) >= (0, 4, 15)) != ("SkyyArmory" in _p):
        print("STOP: SkyySkills 0.4.15+ and SkyyArmory deploy together (the staff handover) - pin both or neither"); return 1
    if "SkyyArmory" in _p and _v(_p.get("SkyyClasses", "0")) < (0, 1, 11):
        print("STOP: SkyyArmory needs SkyyClasses 0.1.11+ (the wand heal caps) in the same deploy"); return 1
    # traversal round (2026-10-06): SkyyArmory 0.1.1 calls class:fn:heal (SkyyClasses 0.1.12) - never roll SkyyClasses below 0.1.12 while it is pinned
    if _v(_p.get("SkyyArmory", "0")) >= (0, 1, 1) and _v(_p.get("SkyyClasses", "0")) < (0, 1, 12):
        print("STOP: SkyyArmory 0.1.1+ needs SkyyClasses 0.1.12+ (class:fn:heal for the heal orb) in the same deploy"); return 1
    # mob curve round (2026-10-06): SkyyMobs 0.1.4 + SkyyGear 0.2.5 + SkyySkills 0.4.17 deploy and roll back TOGETHER (mob:fn:info, gear:fn:curve, the level gap)
    _mob = _v(_p.get("SkyyMobs", "0")) >= (0, 1, 4)
    if _mob and _v(_p.get("SkyyGear", "0")) < (0, 2, 5):
        print("STOP: SkyyMobs 0.1.4+ needs SkyyGear 0.2.5+ (gear:fn:curve, the gear level curves) in the same deploy"); return 1
    if _mob and _v(_p.get("SkyySkills", "0")) < (0, 4, 17):
        print("STOP: SkyyMobs 0.1.4+ needs SkyySkills 0.4.17+ (kill XP by mob level through mob:fn:info) in the same deploy"); return 1
    if (_v(_p.get("SkyyGear", "0")) >= (0, 2, 5) or _v(_p.get("SkyySkills", "0")) >= (0, 4, 17)) and not _mob:
        print("STOP: SkyyGear 0.2.5+ / SkyySkills 0.4.17+ deploy with SkyyMobs 0.1.4+ (the mob curve round) - pin all three or none"); return 1
    # pack drops (2026-10-17, PR #17, research/Pack-Drops-Spec.md): Gear 0.3.19 + Mobs 0.1.10 may roll back alone, but OPEN or IDENTIFY all
    # Mythic boss bags first (0.3.18 ignores the bag zone pz and would identify them from the normal pool).
    # ores (2026-10-17, research/Zone-Ores-Alloys-Spec.md): WorldGen 0.7.3 (new ores / ingots / alloys) + Collections 0.2.25 (their collections +
    # Enchanted ingot recipes) + Sacks 0.8.20 + Accessories 0.5.25 (acc:smelt with the profile-key field) deploy and roll back TOGETHER.
    _ores = [_v(_p.get("SkyyCollections", "0")) >= (0, 2, 25), _v(_p.get("SkyyWorldGen", "0")) >= (0, 7, 3),
             _v(_p.get("SkyySacks", "0")) >= (0, 8, 20), _v(_p.get("SkyyAccessories", "0")) >= (0, 5, 25),
             _v(_p.get("SkyyBazaar", "0")) >= (0, 1, 20)]
    if any(_ores) and not all(_ores):
        print("STOP: the ores round deploys together - SkyyWorldGen 0.7.3+, SkyyCollections 0.2.25+, SkyySacks 0.8.20+, SkyyAccessories 0.5.25+, SkyyBazaar 0.1.20+ (pin all five or none)"); return 1
    # shards03 (2026-10-14): Collections 0.2.15 routes fish / animal / fruit XP to Fishing / Ranching / Orchard (SkyySkills 0.4.38+). Shards 0.3 FLOOR as 0.2.
    if _v(_p.get("SkyyCollections", "0")) >= (0, 2, 15) and _v(_p.get("SkyySkills", "0")) < (0, 4, 38):
        print("STOP: SkyyCollections 0.2.15+ needs SkyySkills 0.4.38+ (new skill XP routes)"); return 1
    # econ39 (2026-10-14): Rebirth 0.3.2 lists gear as a part; Guilds 0.1.8 asks coins:fn:sameacct. Never roll Rebirth below 0.3.2 while a journal is open.
    if _v(_p.get("SkyyRebirth", "0")) >= (0, 3, 2) and _v(_p.get("SkyyGear", "0")) < (0, 3, 5):
        print("STOP: SkyyRebirth 0.3.2+ needs SkyyGear 0.3.5+ (the gear rebirth part)"); return 1
    if _v(_p.get("SkyyGuilds", "0")) >= (0, 1, 8) and _v(_p.get("SkyyCoins", "0")) < (0, 1, 8):
        print("STOP: SkyyGuilds 0.1.8+ needs SkyyCoins 0.1.8+ (coins:fn:sameacct)"); return 1
    # rebirth4 (2026-10-14): SkyyRebirth 0.3 Continue calls bazaar:fn:closeall / ah:fn:closeall
    if _v(_p.get("SkyyRebirth", "0")) >= (0, 3) and (_v(_p.get("SkyyBazaar", "0")) < (0, 1, 11) or _v(_p.get("SkyyAuctions", "0")) < (0, 1, 5)):
        print("STOP: SkyyRebirth 0.3+ needs SkyyBazaar 0.1.11+ and SkyyAuctions 0.1.5+ (rebirth Continue)"); return 1
    # pickup2 (2026-10-14): SkyySacks 0.8.4 + SkyyMobs 0.1.8 deploy and roll back TOGETHER (pet kills / harvest to the Void; mixing works but Skyy asked for both)
    if (_v(_p.get("SkyySacks", "0")) >= (0, 8, 4)) != (_v(_p.get("SkyyMobs", "0")) >= (0, 1, 8)):
        print("STOP: SkyySacks 0.8.4+ and SkyyMobs 0.1.8+ deploy together (pickup2) - pin both or neither"); return 1
    # monk moves round (2026-10-08): SkyySkills 0.4.22 stops shipping the vanilla Wood / Bamboo Bo -> SkyyArmory 0.1.11+ must own them
    if _v(_p.get("SkyySkills", "0")) >= (0, 4, 22) and _v(_p.get("SkyyArmory", "0")) < (0, 1, 11):
        print("STOP: SkyySkills 0.4.22+ needs SkyyArmory 0.1.11+ (the Wood / Bamboo Bo handover) in the same deploy"); return 1
    # wood wand signature (2026-10-08): SkyySkills 0.4.24 wands name SkyyArmory_Wand_Signature (SkyyArmory 0.1.14) - never roll Armory below 0.1.14 while Skills is 0.4.24+
    if _v(_p.get("SkyySkills", "0")) >= (0, 4, 24) and _v(_p.get("SkyyArmory", "0")) < (0, 1, 14):
        print("STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+ (the root SkyyArmory_Wand_Signature it names) in the same deploy"); return 1
    # Monk "Zen" round (2026-10-09): SkyyClasses 0.1.15 publishes class:skill "Zen"; SkyyMobs / SkyyGear ask skill:fn:level with it
    if _v(_p.get("SkyyClasses", "0")) >= (0, 1, 15) and _v(_p.get("SkyySkills", "0")) < (0, 4, 27):
        print("STOP: SkyyClasses 0.1.15+ needs SkyySkills 0.4.27+ (the Monk skill Zen) in the same deploy"); return 1
    if _v(_p.get("SkyySkills", "0")) >= (0, 4, 27) and _v(_p.get("SkyyClasses", "0")) < (0, 1, 15):
        print("STOP: SkyySkills 0.4.27+ deploys with SkyyClasses 0.1.15+ (else SkyyHud's class line shows '-')"); return 1
    # Ability engine R1 (2026-10-09): SkyyClasses 0.1.16 tags ability damage; SkyySkills 0.4.28 credits ability kills (class XP after a weapon swap)
    if _v(_p.get("SkyyClasses", "0")) >= (0, 1, 16) and _v(_p.get("SkyySkills", "0")) < (0, 4, 28):
        print("STOP: SkyyClasses 0.1.16+ needs SkyySkills 0.4.28+ (ability kill XP) in the same deploy"); return 1
    # Multitools (2026-10-10): with IBC:Multitools in the pack, SkyyGear must be 0.2.18+ (else multitools keep their own cheap recipe)
    if "IBC:Multitools" in PACK_THIRD_PARTY and _v(_p.get("SkyyGear", "0")) < (0, 2, 18):
        print("STOP: IBC:Multitools needs SkyyGear 0.2.18+ (the pickaxe + hatchet recipe and the multitool stats)"); return 1
    # FLOOR SkyyWorldGen 0.5 (2026-10-10): a jar below 0.5 cannot load the world skywynn_proof2 - before a rollback stop the server, delete
    # universe/worlds/skywynn_proof2 and its lines in worlds.properties.
    # Requip batch (2026-10-11): SkyyWardrobe 0.2 + SkyySacks 0.7.17 + SkyyGear 0.2.23 deploy TOGETHER (4-arg sacks:fn:deposit, stamp copy).
    # FLOORS: never roll SkyyWardrobe below 0.2 once 0.1 files migrated (0.1 cannot see the pool); SkyyGear >= 0.2.23 while Requip runs (stamp copy).
    if _v(_p.get("SkyyWardrobe", "0")) >= (0, 2) and (_v(_p.get("SkyySacks", "0")) < (0, 7, 17) or _v(_p.get("SkyyGear", "0")) < (0, 2, 23)):
        print("STOP: SkyyWardrobe 0.2 needs SkyySacks 0.7.17+ and SkyyGear 0.2.23+ (deploy the Requip batch together)"); return 1
    # fish018 (2026-10-16): SkyySacks 0.8.10 stores weighed fish through SkyyFishing 0.1.8's fishing:fn:fishOf / fishDoc / pond - deploy + roll back TOGETHER.
    # Before rolling SkyySacks back below 0.8.10: players take their fish out of the Void first (0.8.9 cannot show them; nothing is deleted).
    if _v(_p.get("SkyySacks", "0")) >= (0, 8, 10) and _v(_p.get("SkyyFishing", "0")) < (0, 1, 8):
        print("STOP: SkyySacks 0.8.10 needs SkyyFishing 0.1.8+ (fish in the Void)"); return 1
    # cls0130 (2026-10-16): modifiers left the class tree - Trees 0.3.18 + Classes 0.1.30 deploy + roll back TOGETHER (one-time abil.tree3 updates
    # in both, History copies in each mod's history/abiltree3/; rolling back only one leaves modifiers locked).
    if (_v(_p.get("SkyyTrees", "0")) >= (0, 3, 18)) != (_v(_p.get("SkyyClasses", "0")) >= (0, 1, 30)):
        print("STOP: SkyyTrees 0.3.18 and SkyyClasses 0.1.30 go together"); return 1
    # armory0129 (2026-10-16): Great Shields (Weapon_GreatShield_*) - FLOOR: never roll SkyyArmory below 0.1.29 once players hold one (unknown items).
    # SkyyClasses 0.1.31 assigns them to the Spellblade + the armory:fn:mine / class:fn:momAdd Momentum bridge - deploy TOGETHER.
    if _v(_p.get("SkyyArmory", "0")) >= (0, 1, 29) and _v(_p.get("SkyyClasses", "0")) < (0, 1, 31):
        print("STOP: SkyyArmory 0.1.29 needs SkyyClasses 0.1.31+"); return 1
    # farm01 (2026-10-16): SkyyGear 0.3.14 rolls boss Sigils + publishes gear:sigil:drops; SkyyArmory 0.1.30 skips its own boss roll while it is TRUE.
    # Deploy TOGETHER (Armory 0.1.29 with Gear 0.3.14 = bosses roll Sigils twice). Rolling Armory back alone is safe (double roll again).
    # Gear 0.3.14 merges hoe + sickle into the Harvester (History copy; /gear harvmerge undo <player> [force]).
    if _v(_p.get("SkyyGear", "0")) >= (0, 3, 14) and "SkyyArmory" in _p and _v(_p.get("SkyyArmory", "0")) < (0, 1, 30):
        print("STOP: SkyyGear 0.3.14 needs SkyyArmory 0.1.30+ (one boss Sigil roll)"); return 1
    # hubchar (2026-10-16): Stats merged into the Skills tab, Class into the Trees tab (skyyui HUB_MERGED) - SkyyMenu 0.3.33 + SkyySkills 0.4.45 +
    # SkyyTrees 0.3.19 + SkyyClasses 0.1.33 deploy + roll back TOGETHER (mixed = Stats unreachable / Class shortcut locked). No data change.
    _hc = [_v(_p.get(m, "0")) >= v for m, v in (("SkyyMenu", (0, 3, 33)), ("SkyySkills", (0, 4, 45)), ("SkyyTrees", (0, 3, 19)), ("SkyyClasses", (0, 1, 33)))]
    if any(_hc) and not all(_hc):
        print("STOP: SkyyMenu 0.3.33, SkyySkills 0.4.45, SkyyTrees 0.3.19, SkyyClasses 0.1.33 go together (hub merges)"); return 1
    # hubcoll (2026-10-16): /recipes moved from SkyySacks' /craft alias to SkyyCollections (recipes inside each collection) - Collections 0.2.22
    # and Sacks 0.8.13 deploy + roll back TOGETHER (mixed = /recipes registered twice or missing).
    if (_v(_p.get("SkyyCollections", "0")) >= (0, 2, 22)) != (_v(_p.get("SkyySacks", "0")) >= (0, 8, 13)):
        print("STOP: SkyyCollections 0.2.22 and SkyySacks 0.8.13 go together (/recipes)"); return 1
    # smithhub (2026-10-16): SkyyGear 0.3.15 owns the Crafting-hub tabs (Smithing / Anvil with Identify merged / Upgrade = tools); SkyyMenu 0.3.34 drops
    # its Identify + Auctions stand-ins and maps old shortcuts - deploy + roll back TOGETHER (mixed = missing or doubled Identify tab). No data change.
    if (_v(_p.get("SkyyGear", "0")) >= (0, 3, 15)) != (_v(_p.get("SkyyMenu", "0")) >= (0, 3, 34)):
        print("STOP: SkyyGear 0.3.15 and SkyyMenu 0.3.34 go together (Crafting hub tabs)"); return 1
    # petmenu (2026-10-16): FLOOR - never roll SkyyPets below 0.4.1 once eggs sit in the Hatchery (0.4.0 ignores hatchery.* lines: those eggs
    # would be invisible, kept not lost; bench egg recipes + right-click hatching would come back).
    # menu sweep S1 (2026-10-16): Trees 0.3.20 + Classes 0.1.34 deploy + roll back together (one sub row on the merged Trees tab; no data).
    if (_v(_p.get("SkyyTrees", "0")) >= (0, 3, 20)) != (_v(_p.get("SkyyClasses", "0")) >= (0, 1, 34)):
        print("STOP: SkyyTrees 0.3.20 and SkyyClasses 0.1.34 go together (menu sweep S1)"); return 1
    # menu sweep S2 (2026-10-16): Bazaar 0.1.18 + Auctions 0.1.10 share one Market sub row (ah:fn:view) - deploy + roll back together; Vault 0.1.9 + Bank 0.1.16 pinned together. No data.
    if (_v(_p.get("SkyyBazaar", "0")) >= (0, 1, 18)) != (_v(_p.get("SkyyAuctions", "0")) >= (0, 1, 10)):
        print("STOP: SkyyBazaar 0.1.18 and SkyyAuctions 0.1.10 go together (menu sweep S2)"); return 1
    # FP1 (2026-10-17): Potion Flask + Food Pouch. SkyyCooking 0.1.11 needs SkyySacks 0.8.18 (asks supply:fn:claims, never sweeps Skyy_Flask_* /
    # Skyy_Food_Pouch_*) + SkyyWardrobe 0.2.8 (Requip keeps them). FLOOR: never roll SkyyCooking below 0.1.11 once stores exist (supplies/*.properties
    # hold players' potions + food; the items become unknown below) - Take all out first.
    if _v(_p.get("SkyyCooking", "0")) >= (0, 1, 11) and (_v(_p.get("SkyySacks", "0")) < (0, 8, 18) or _v(_p.get("SkyyWardrobe", "0")) < (0, 2, 8)):
        print("STOP: SkyyCooking 0.1.11 needs SkyySacks 0.8.18 + SkyyWardrobe 0.2.8 (FP1)"); return 1
    # AP1 (2026-10-16): SkyyAccessories 0.5.22 = Void Charms (/charms /charm /ch replace /accessories /acc /accbag), Accessory Power, bag item retired.
    # Needs SkyyMenu 0.3.36+ (its help / Mods texts name /charms). Rollback to 0.5.21 is safe (the removed bag item is not given back; /accbag recalls).
    if _v(_p.get("SkyyAccessories", "0")) >= (0, 5, 22) and _v(_p.get("SkyyMenu", "0")) < (0, 3, 36):
        print("STOP: SkyyAccessories 0.5.22 needs SkyyMenu 0.3.36+ (Void Charms texts)"); return 1
    # T1 (2026-10-16): SkyyGear 0.3.17 + SkyySkills 0.4.48 deploy + roll back TOGETHER (uncapped Fortune / triple drops, tool lines per tier, salvage bridge).
    # FLOORS: before rolling Gear below 0.3.17 Undo tool.fortune.cap, lifelong.perkSpeed, lifelong.perkFortune in Server Setup > Changes;
    # before rolling Skills below 0.4.48 set perk.fortuneMax back to 2.0 (Undo). Items are safe either way.
    if (_v(_p.get("SkyyGear", "0")) >= (0, 3, 17)) != (_v(_p.get("SkyySkills", "0")) >= (0, 4, 48)):
        print("STOP: SkyyGear 0.3.17 and SkyySkills 0.4.48 go together (T1)"); return 1
    # coll24 (2026-10-16): Collections 0.2.24 (Life Essence -> Greater Essence 1:1, Eternal Seeds at tier 4, gift sizing) needs Bazaar 0.1.19 (Eternal buy lock,
    # Enchanted listing; needs Sacks 0.8.14+). Rollback Bazaar: put the migrate119 .bak back + delete migrated.0.1.19 from pricing.properties.
    # FUTURE FLOOR: before any round deletes Skyy_Ench_LifeEssence, convert it in chests / Vault / Bank / Wardrobe / AH escrow / profile snapshots first.
    if (_v(_p.get("SkyyCollections", "0")) >= (0, 2, 24)) != (_v(_p.get("SkyyBazaar", "0")) >= (0, 1, 19)):
        print("STOP: SkyyCollections 0.2.24 and SkyyBazaar 0.1.19 go together (coll24)"); return 1
    # pets043 (2026-10-16): FLOOR - never roll SkyyPets below 0.4.3 once a new-kind pet exists (Mosshorn, Bison, CrystalGolem, Molerat, Moose, Owl, Antelope, Deer).
    # trees21 (2026-10-16): SkyyClasses 0.1.35 (Radiant Pulse, Elemental Bubble, Siphon) needs SkyyTrees 0.3.21+ (Feller table, swing readers, Siphon -5% Health).
    if _v(_p.get("SkyyClasses", "0")) >= (0, 1, 35) and _v(_p.get("SkyyTrees", "0")) < (0, 3, 21):
        print("STOP: SkyyClasses 0.1.35 needs SkyyTrees 0.3.21+"); return 1
    # wd027 (2026-10-16): Requip SALVAGE uses SkyyGear 0.3.17's gear:fn:salvage (write-ahead salvage-<eid>.txt journals; never coins).
    if _v(_p.get("SkyyWardrobe", "0")) >= (0, 2, 7) and _v(_p.get("SkyyGear", "0")) < (0, 3, 17):
        print("STOP: SkyyWardrobe 0.2.7 (Requip SALVAGE) needs SkyyGear 0.3.17+"); return 1
    # fishvoid (2026-10-16): SkyyFishing 0.1.10 + SkyySacks 0.8.17 deploy TOGETHER (the Fishing Bench sells / fillets Void fish via sacks:fn:fishList /
    # fishTake / fishPut / fishTaken with take tokens). Either rolls back alone safely (bench lists the inventory only).
    if _v(_p.get("SkyyFishing", "0")) >= (0, 1, 10) and _v(_p.get("SkyySacks", "0")) < (0, 8, 17):
        print("STOP: SkyyFishing 0.1.10 goes with SkyySacks 0.8.17+ (Void fish at the bench)"); return 1
    # roll01 (2026-10-16): SkyySkills 0.4.44 writes our dodge root into each player's saved Interactions Dodge slot. FLOOR: before rolling below
    # 0.4.44 (or removing SkyySkills), switch Server Setup -> Acrobatics -> 'Roll every direction' OFF and let every player log in once.
    # pets040 (2026-10-16): FLOOR - never roll SkyyPets below 0.4.0 once Skyy_PetEgg_* items exist (unknown items below); SkyyCollections must keep
    # the Skyy_Ench_* items the egg recipes use (Cobblestone, Iron, Oak, Maple, Wheat, Carrot, Copper).
    # SkyyVoid batch (2026-10-13): SkyySacks 0.8.0 (Bags v2, shown as SkyyVoid) + SkyyBazaar 0.1.9 deploy TOGETHER (Fishing tab, crystal products).
    # FLOOR: never roll SkyySacks below 0.8.0 once it has run - run /pdadmin legacybags <player> for every player BEFORE any rollback (converted bags are gone).
    if (_v(_p.get("SkyyBazaar", "0")) >= (0, 1, 9)) and _v(_p.get("SkyySacks", "0")) < (0, 8, 0):
        print("STOP: SkyyBazaar 0.1.9 needs SkyySacks 0.8.0 (deploy the SkyyVoid batch together)"); return 1
    # Auto-pickup (2026-10-13): SkyySacks 0.8.3 + SkyyMobs 0.1.7 deploy and roll back TOGETHER (kill credit via mob:fn:credit); no data floor
    if (_v(_p.get("SkyySacks", "0")) >= (0, 8, 3)) != (_v(_p.get("SkyyMobs", "0")) >= (0, 1, 7)):
        print("STOP: SkyySacks 0.8.3 (auto-pickup) and SkyyMobs 0.1.7 (kill credit) go together"); return 1
    # Untiered batch (2026-10-09): SkyyGear 0.2.16 + SkyyArmory 0.1.15 deploy TOGETHER (the 3 Armory UT items + their numbers from SkyyGear)
    if (_v(_p.get("SkyyGear", "0")) >= (0, 2, 16)) != (_v(_p.get("SkyyArmory", "0")) >= (0, 1, 15)):
        print("STOP: SkyyGear 0.2.16+ and SkyyArmory 0.1.15+ deploy together (the Untiered batch) - pin both or neither"); return 1
    # FLOOR: never roll SkyyGear below 0.2.16 or SkyyArmory below 0.1.15 once UT items exist (unknown items); set part.utLines=false before any rollback.
    # SkyyGear 0.2.14 (rarity G1): do not roll back to 0.2.13 while any Skyy_Unid_Bag_Untiered exists (identify or clear them first); odds.mythic stays 0,0,0.
    # SkyyBazaar 0.1.7: rollback to 0.1.6 safe; ship with SkyyGear 0.2.14 for the full market wall.
    # SkyyCore era (2026-10-15): Core is the FIRST pin; every manifest dependency is met by the SET
    if "SkyyCore" in _p and SET[0][0] != "SkyyCore":
        print("STOP: SkyyCore must be the FIRST SET entry (it is the library every Core-mode module depends on)"); return 1
    _dep = [(m, w) for m, w in dependency_stops(SET) if os.path.isfile(os.path.join(ROOT, m, "%s-%s.jar" % (m, _p[m])))]
    if _dep:
        for m, w in _dep:
            print("STOP: %s %s" % (m, w))
        return 1
    missing = []
    plan = []
    for mod, ver in SET:
        jar = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
        if not os.path.isfile(jar):
            missing.append(jar)
        plan.append((mod, ver, jar))
    for mod, ver, jar in plan:
        print("  %-16s %-6s %s" % (mod, ver, "OK" if os.path.isfile(jar) else "MISSING " + jar))
    newer = [(mod, ver, newer_builds(mod, ver)) for mod, ver in SET]
    newer = [x for x in newer if x[2]]
    if newer:
        print("NOTE: newer builds are on disk than SET pins (SET decides what deploys - bump it, and HANDOFF section 3, only for the "
              "builds Skyy approved):")
        for mod, ver, vs in newer:
            print("  %-16s pinned %-6s newer on disk: %s" % (mod, ver, ", ".join(vs)))
    if missing:
        print("STOP: %d jar(s) missing - build them first (python <build script>, no --deploy)." % len(missing))
        return 1
    if "--check" in sys.argv:
        print("all %d jars present" % len(plan))
        return 0
    if server_running():
        print("STOP: a Hytale server is running. Close the world / game first, then run this again.")
        return 1
    if "--yes" not in sys.argv:
        if input("Deploy these %d mods to world '%s'? type yes: " % (len(plan), WORLD)).strip().lower() != "yes":
            print("cancelled")
            return 1
    for mod, ver, jar in plan:
        B.deploy(jar, mod + ".jar")
        B.enable_in_world(WORLD, world_key_of(mod, ver), disable_prefix="Skyy:")   # 2026-10-15: the manifest's key (stable or versioned)
    for key in PACK_THIRD_PARTY:
        B.enable_in_world(WORLD, key)
    core_pinned = "SkyyCore" in _p
    for mod, ver in ([] if core_pinned else STABLE_PROBES):     # stable-name test jars (world key "Skyy:<Mod>", no version)
        B.deploy(os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver)), mod + ".jar")
        B.enable_in_world(WORLD, "Skyy:" + mod)
    for mod in RETIRED + (CORE_RETIRES if core_pinned else []):
        retire_in_world(WORLD, mod)
    sync_bettermap_worlds(WORLD)
    tune_perfect_parries(WORLD)
    for key in PACK_DISABLED:
        disable_third_party(WORLD, key)
    print("deployed %d mods. Start the world and watch the server log for every '[Skyy...] ready' line." % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
