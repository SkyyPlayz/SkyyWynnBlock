# SKYY'S TEST CHECKLIST

Short version since 2026-10-05. The numbered in-game steps live in `docs/tests/<period>.md` (word for word); every section ever written is
listed in [docs/tests/README.md](docs/tests/README.md). Each deploy adds ONE section at the END of the newest month file
(`docs/tests/2026-10.md`) and one line under "Test next" below; a line leaves this list once Skyy has tested it (log the result in
`docs/log/<YYYY-MM>.md`).

## Test next - deployed, still needs your test (cleaned 2026-10-10)

Only things still waiting on you. Steps for each: search the name in `docs/tests/2026-10.md`. Removed today as replaced or gone: the
reel / Monk / old town / old key probes (retired or replaced by newer probes), The Armory test (Armory is off until 0.7), the older
fishing, luggage, sprint-tap and Stats-page versions (their newest version is below).

### A. Probes first - they unlock the next builds (one session each, send the log)
1. SkyyPetProbe 0.1 - DONE except: `/petprobe p6`, log out + back in (pets gone?), then `/petprobe clear`. Results: research/Pet-Probe-Results.md.
2. SkyyTownProbe 0.2 - `/townprobe all` ... `/townprobe report` (17 quest probes incl. Pebble hat + name swap). Unlocks quests.
3. SkyyKeyProbe 0.2 - `/keyprobe sprint`, press W / A / D / S + sprint and sprint standing still, `/keyprobe sprint`. Side / back rolls.
4. SkyyGatherProbe 0.1 + B - `/gprobe kit`, P1-P6, trees (one session, then removed). Unlocks the gathering ladder.
5. SkyyWorldGen 0.3 + 0.4 - `/zone proof`: fly the islands (necks, arch, 40-block bridge gap), `/tp 1139 192 -331` down to the lava caverns
   (y ~57). Tell me before we build the real Zone 1 islands.

### B. New since 2026-10-09 (newest version only)
6. Untiered first batch - `/gear ut`, `/gear ut give Paperweight 22`, orange bags (Lv 15-29), each item's trick + downside, market wall.
7. Rarity: Mythic only from bosses, level-up caps per rarity, Armor sets table, `/gear set`.
8. Mining armor - metal armor = Mining Sets, Mining-level gate, stats only with a pickaxe / shovel, full-set Fortune; helmet glows in caves.
9. Tools - Chopping / Mining Power (Iron hatchet 3 hits per log at Lv 15+), Fortune, under-level tool = plain tool, Gear -> Tools tab.
10. Crude / Scrap weapons show Attack Speed + Charged lines; no "Missing interaction ... Mace" in the log.
11. Abilities (Mage + Priest) - `/cast list`, `/cast 1` / `2`, `/cast page`, shapes via `/classadmin shape`, HUD Abilities widget,
    Meteor, Mana Barrier, Frost Nova, Starfall / Arcane Beam, Sacred Heal, Shield Bubble, Guardian Spirit, Sanctuary / Martyr's Grace.
12. Class power split - class Mana / Stamina pools, Mana on hit, mining Stamina, foraging Defense, class balance boost.
13. Monk skill named Zen everywhere (XP kept); Stats page Defense shows "Skills", Class Weapon Damage shows "Class balance".
14. SkyyPets 0.1 + Skills 0.4.29 - `/pets`, starter Rabbit, slot buffs, pet XP right away, `/petadmin`.
15. SkyyProfiles 0.1.9 - 8 profile slots, Spellblade card "coming later", `/profileadmin bonus`.
16. SkyyMerchants - rumour in chat + `/merchants` (shop + buying seen working 2026-10-10; 0.1.1 adds one weapon per class).
17. Mystery bags from mobs, identify / re-identify (luggage sacks seen working 2026-10-10).
18. Bags - Omni hidden until all 5 Legendary bags, Normal bags = 20 Plant Fiber + 4 Sticks, bag held higher / in front.
19. Collections - CRAFT buttons, LOCKED RECIPES list, Mining bags now on Cobblestone I / III / V / VII.
20. Fishing 0.1.2 - Wooden rod (sticks), bench takes from bags, string tip -> bobber, no white cloud, idle bobber under the tip,
    no false "in the way" / "too shallow" (tune "Line start" in Server Setup if needed; does a 2nd player see the string?).
21. Bazaar search bar; Auction House categories / sort / rarity / level range / Reset.
22. Better Mob Expansion - new Zone 1-4 mobs get levels, rats / spiders / snakes behave normally, no crowding.
23. The Armory OFF - copper ore, bars, talismans, swords have textures again.
24. SkyyTrees 0.3.4 - no "Missing interaction ... Skyy_Tree" in the log; chopping feels the same.

### C. Older, never confirmed
25. Signature charge kept per weapon on swap; metal + Wood / Rotten / Tribal wands ricochet signature through 8 enemies.
26. Roll on sprint press (forward), spammable, hold = sprint out; dodge key rolls in all 8 directions; Shadow Step on release.
27. Monk moves - Pole-Vault on every Bo, Skipping Bounds, Rising Strike + Plunge Punch (`/armory debug monk on`); Monk weapons, block.
28. Spellbooks (Page Burst, Levitate, Mage-only) + kunai (throw, hold-teleport); Shadow Step on daggers (backstab bonus).
29. Metal Bo staffs - hold attack casts nothing; accessory icons (44) + metal staff models in the hand.
30. Staff blink 16 / wand hop + burst + heal orb / Grapple Bolt / bow leap + blast arrow; Copper + Onyxium crossbows (3rd bolt).
31. Class path trees (trunk + 3 paths, Priest Open Aura, free respec); Assassin playable.
32. SkyyProfiles 0.1.7 - SWITCH confirm, each profile keeps its Health; profile delete + 6-hour undo.
33. Stats page (5 tabs, Change Profile, /stats); Accessory Bag icon + gem colours; SkyyHud 256x256 icon (no client warning).
34. Chat mirror (chat lines in the server log).
35. Mob curve - higher-level mobs tougher, level gap, gear curves, Reforge level-up, kill XP by level; health bar follows Strength.
36. Weapon speed tiers + minimap (BetterMap) on the island, no overlap with Zone / Online / Day.
37. Bazaar - Smithing tab, progression prices, sell straight from bags; Buy/Sell with Hytale stacks.
38. Lantern recipes at Tree Sap tiers I / III / V / VIII; locks follow profile switches.
39. Mining's own slower curve + level-up coins; Priest heal XP 1 / 1.25 per HP; class Mana per level.
40. SkyyGear 0.1.3 world-chest drops unidentified + non-metal level rows; crafting gear pays Smithing XP.
41. Cooking food Grade strength (+32% per Grade).
42. SkyyTrees Alchemy + Smithing trees; class trees ON (`/tree class`).
43. SkyyMenu Mods list shows today's versions; menu item per profile; Server Setup times in seconds.
44. SkyyHud small widget boxes (Game Clock in the corner) + combat widget colours.
45. SkyyExploration Overview never sticks on "Loading..."; /collections top hides deleted / archived profiles.
46. Guilds - % disband refunds, Contribution column, 35% leave refund; island closes to co-op when the owner is deleted.
47. Party TPA button + Accept TPA (2 players); bags blocked in /trade; coins never buy tiers / recipes / bags.
48. Warrior Wood Shield in the kit; Priest self-heal 100%.
49. Pack mods HyFishing + Dynamic Seasons + NoCube's Orchard work next to ours (Dynamic Seasons crashed once - report drafted).
50. Merchant: a weapon for every class each visit ('Berserker - ...' rows)

Seen working 2026-10-08/09: bag art (0.7.14), fishing widgets, Copper axe Attack Speed line, sprint roll forward + forward diagonals.
Already seen working since 2026-10-01 (details in `docs/log/2026-10.md`): SkyyMobs 0.1 / 0.1.1 / 0.1.2, SkyySacks 0.7.11 refill + 0.7.12
bench + inventory crafting, SkyySkills 0.4.12 - 0.4.14, SkyyHud 0.3.11 + 0.3.12, SkyyBank 0.1.6, SkyyWorldGen 0.1, SkyyMenu 0.3.6
(stuck-page fix), SkyyArmory 0.1 staffs (+ the Iron wand in play), SkyyTrees 0.3.1 probe page, SkyyGear 0.2.2 tooltips, SkyyUiProbe 0.4
minimap probes, SkyyAccessories 0.5.4 Lantern, SkyyAccessories 0.5.5 Lantern edges (2026-10-05), SkyySkills 0.4.16 Mining
level-up payout (log + coins checked 2026-10-05), SkyyCooking 0.1.5 + 0.1.6 XP (skewers + Flour, 2026-10-05).

## If anything crashes or misbehaves
Send the newest `...\Saves\HUD mod\logs\<time>_server.log` (and the client log from `UserData\Logs`) plus a screenshot; fixes from Skyy's
tests always come first.
