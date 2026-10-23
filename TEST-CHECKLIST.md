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
51. Visible pets: Rabbit follows, Hawk flies around you, F to pet (hearts), babies until Lv 30, vanish + return on world / profile / death / logout, Show my pets in /settings
52. SkyyMenu 0.3.14 Pets tile (top row, per profile) + SkyyPets 0.2.1 petting plays once (Hawk/Fox/Cat/Rabbit)
53. SkyyArmory 0.1.16 wand hops once + shorter; SkyyMenu 0.3.15 sky-island menu item; HyFishing gone
54. SkyyArmory 0.1.17: wand hop 18, heal aura where you land (5 s), quick shot 32 blocks (50% past 16)
55. BIG BATCH 2026-10-10: Pets 0.2.3 (roles, summon look, loadout bridge, skeletons), Menu 0.3.17 (layout D, icons, editor), Wardrobe 0.1, Soul Cage (Armory 0.1.19-0.1.20), wand single launch + keeps damaging falls, tool rarity + reforge + multitools (Gear 0.2.17-0.2.20), new tooltips, Lantern textures, WorldGen 0.5 islands (/zone proof -> skywynn_proof2), Multitools on, KeyProbe off, BetterMap all worlds
56. SkyyGear 0.2.22 (Reforge tabs Reforge/Upgrade/Multitool, /upgrade Soul Cages, /multitool merge, [Lv N] names), Collections 0.2.9, UI PROBE /skyprobe kit (screenshots k1a-k1h, t1, h1)
57. SkyyArmory 0.1.21 Soul Orb: Life Essence recipe, Thorium ~7.5 per tick, wispy vs solid lines, Wings of Fate (hold LEFT click)
58. REQUIP /requip (pool, Use what I wear, Deposit all gear, loadouts pick from the pool), /smithing (set cards, class filter, craft into Requip, Reforge/Upgrade/Multitool tabs), hotbar Pocket block refill

Seen working 2026-10-08/09: bag art (0.7.14), fishing widgets, Copper axe Attack Speed line, sprint roll forward + forward diagonals.
Already seen working since 2026-10-01 (details in `docs/log/2026-10.md`): SkyyMobs 0.1 / 0.1.1 / 0.1.2, SkyySacks 0.7.11 refill + 0.7.12
bench + inventory crafting, SkyySkills 0.4.12 - 0.4.14, SkyyHud 0.3.11 + 0.3.12, SkyyBank 0.1.6, SkyyWorldGen 0.1, SkyyMenu 0.3.6
(stuck-page fix), SkyyArmory 0.1 staffs (+ the Iron wand in play), SkyyTrees 0.3.1 probe page, SkyyGear 0.2.2 tooltips, SkyyUiProbe 0.4
minimap probes, SkyyAccessories 0.5.4 Lantern, SkyyAccessories 0.5.5 Lantern edges (2026-10-05), SkyySkills 0.4.16 Mining
level-up payout (log + coins checked 2026-10-05), SkyyCooking 0.1.5 + 0.1.6 XP (skewers + Flour, 2026-10-05).

## If anything crashes or misbehaves
Send the newest `...\Saves\HUD mod\logs\<time>_server.log` (and the client log from `UserData\Logs`) plus a screenshot; fixes from Skyy's
tests always come first.
59. PERFECT PARRIES (pack mod): block right as a hit lands - Warrior sword/shield easiest (wide window, long stun), Berserker big counter-hit, Assassin daggers tight window + huge counter, Monk Bo/wraps long counter window, Archer/Mage/Priest only a short deflect (no counter bonus). Too easy / too hard? Tell me which class.
60. HYTALE 0.7: the world boots again (Saplings From Trees + Better Mob Expansion switched off until their authors update). AVOID new islands / new profiles until the 0.7 port (island fill + spawn calls broke); expect errors on Exploration / Merchants / Menu Spawn / crit popups.
61. HYTALE 0.7 batch 1: new island (blocks, chest, kit), /hub, /explore tabs + luggage, merchant spawn, mob levels, Armory weapons + essence drops
62. HYTALE 0.7 batch 2: Menu Spawn + island teleports, /bank + back-pay 1, CRIT! popup, weapon feel, profile switch, /zone
63. SkyySkills 0.4.31: class Mana pools (Mage 45, Priest 42), 10 / 5 Mana casts, regen 5/s + 6 s combat slow, Acrobatics XP line
64. LAG FIXES: /pay + restart balance, Bazaar / guild bank / auctions, bags sweep + refill + craft, lantern, Requip equip, collection tier once
65. Armory 0.1.23 feel check + ABILITY PROBE /aprobe (about 10 min, results read from the log)
66. LAG FIXES 2: gear stats + join, HUD clock / zone / layout, tree felling XP, /skills top, fishing rod, merchant move, luggage claim, island trust after restart
67. HUB HOTKEY (double-tap crouch) + /skyprobe hubpanel probe + bank / settings after restart
68. ANVIL tab: /reforge on a Soul Cage - Reforge + Upgrade cards, Identify / Re-identify / Identify all, 1080p fit
69. FEED: /skyyhud testfeed - cards, merge x9, fade, XP flash, HUD editor + Server Setup Feed / Messages
70. SKYYVOID: migration lines + Pocket Dimension, /pd six tabs + amount box, auto-sweep limit, Upgrade pays once, /bazaar Fishing tab
71. ENCHANTED (tier III, Compressing tab, Void, Bazaar) + QUESTS 0.1 (welcome, Quest Tracker, out-of-order tasks, /quests, place arrow)
72. MANA 3.3/s out of combat, 2.5/s in combat + Workbench Accessories tab order (Accessory I first, tier then cost)
73. PETS: shots, swings, spells pass through your pet; F-to-pet + nameplate still work
74. PROFILES rename + '<Class> <Name>' + admin no cap; /pdadmin rarity reset (no item loss)
75. BANK title class once + MENU Pets tile full '<Class> <name>'
76. QUESTS 0.2: Skip + optional tasks, I know how to play, rank-up fix, combat gear bags, feed-only, hub areas (/questadmin place set hub.mining ...), co-op
77. LIFELONG TOOLS: migration, /toolpoints, no drop / craft / AH, /pickaxe + /lifelong, tier gate (crudeFactor), Anvil Copper tier-up
78. AUTO-PICKUP: blocks + mob drops to Void / inventory / feet, feed cards, killer + top damager loot, island denial
79. CHAT -> FEED: XP flash, double drop / tree / heal / progress cards, one-line rank-up + /craft, NEW recipe marks
80. MESSAGE ROUTES per player (/settings General) + Ability casts default row
81. SETTINGS Messages tab + ability casts in feed (refusals stay in chat)
82. 0.7.1: BetterMap map + minimap, DynamicSeasons 7.0.2 seasons, Perfect Parries 0.9.7 parry
83. TOOL SPEED: Crude normal on Oak / copper, 2.5x one tier up, 10x two up, refused 3+
84. AUTO-PICKUP 2: F-harvest to the Void, Q-drop not eaten, Void full -> inventory -> feet (pet kills wait for SkyyPets)
85. LOST TOOL: /pickaxe etc. summon your exact tool from chest / Vault / Requip, else an exact copy; one working tool only
86. TOOL PERKS: Vein Mine +1 ore / level, Tree Feller on the lifelong tool only, cap 8
87. REBIRTH R1+R2: skills unchanged, half Farming XP above tool tier, /rebirth Nexus page + tooltip (admin view, feature OFF)
88. HARVEST GATE: crops 2+ tiers above your hoe refused (click + F), 1 up = half XP
89. PET OWNER key: ready line names pets:fn:ownerOf (pet-kill loot waits for fighting pets, SkyyPets 0.4)
90. AH CLOSEALL: /ahadmin closeall (+ confirm) cancels your listings to claims, once
91. VAULT FETCH hook: /vault info normal + ready line (the /pickaxe part comes with SkyyGear 0.3.5)
92. LOST LOOT: new pile looks, reveal cards, /exploreadmin airdrop supply drop claim once
93. REBIRTH R3: /rebirthadmin dryrun / rebirth / crashtest on a test profile, coins pay again x0.9
94. SHARDS: /shardadmin give, place on island, Enter, Collect, Grow, menu tile
95. ABILITIES: Ability 2/3 + crouch cast Mage / Priest runes; /tree class ability panel; levels + modifiers; send logs (U1-U10)
96. QUESTS: /questadmin npc add board / marlow, markers, daily jobs, pole once
97. SIGILS: apply on the Anvil, AH yes / Bazaar no; Mining armor follows Mining level; hoe tills an area
98. ADMIN PAGE: /modconfig admin, 4 tabs, confirm buttons, permission hiding
99. REBIRTH TREE: /rebirthadmin points all 50, buy / rows / refund; Continue closes AH listings
100. TOTEMS: Totems tab, place / pick up exact tier, craft, booster; shard credit counts
101. PERFECT DODGE + Fishing / Ranching / Orchard XP (/skills stats fishing)
102. GEAR 0.3.5: /pickaxe from closed Vault, bare hands = Crude on crops, identify reveal cards, /pole lifelong rod, multitool after rebirth 1
103. MONK + ASSASSIN: Enable in /tree class, Ability 2/3 + crouch casts, God Killer on a boss, per-ability modifiers
104. HUD: Fishing / Ranching / Orchard lines, Farming (F / R / O), ability names show (Lv N)
105. ECON: /skills shows 12 rows, coin factor 0.8 row + Undo, AH buy from own other profile refused, /rebirthadmin crashtest parses
106. REBIRTH 0.3.2 + GUILDS 0.1.8: admin rebirth resets lifelong tools, Void-Forged Pick node, guild bank coins stay with the depositing profile
107. SOUNDS: /soundtest list / next / more, quest + reward + NPC + portal + pet + claim + interest sounds, Server Setup sound rows; Admin page rebirth buttons
108. SHARDS 0.3: /shardadmin give <you> <kind> for the 5 new shards, enter, collect, compactor / time compressor, Soul Cage; fish / animal / fruit collection XP to the new skills
109. WARRIOR / BERSERKER / ARCHER: ability keys + crouch alts, shields Warrior-only, Blood Frenzy toggle, Banner, nets, Explosive Arrow; send logs
110. REBIRTH STATS + SKILL SOUNDS: level-up / overall / perfect-dodge sounds, Vitality / Focus nodes raise max Health / Mana (admin test)
111. SEARCH: /settings + /modconfig search find settings across mods, Go to jumps; Mod sounds switch; Admin Shards buttons
112. SOUNDS 2: Void full / upgrade, collection tier, big /pay, accessory equip / upgrade, Bazaar buy / sell, AH buy / sell / claim, shard collect / grow / totem; Mod sounds switch mutes them
113. GATHERING ARMOR: bark / crop / angler sets level + tier up, pole perks on /toolpoints, gear sounds
114. SPELLBLADE: Momentum, Breach + Sunder, Imbue element; rebirth slots 3-4; Fishing tree Sea Legs; Farming tree uses the average
115. 3 STARTER ISLANDS: fresh profile -> island 1 / 2 / 3, gather, crude tools, bridge, tasks 11 + 19 tick; old islands unchanged
116. ZONES: /zone 1-5 floating islands (new world skywynn_zones), /zone info, Zone 5 Onyxium; /zone old = old island
117. HOTBAR SUMMONS + IRON 10 HITS + WORKBENCH ORDER (Accessory I first) + HUD +N contrast, labelled progress cards, editor rows
118. CHOPPED TRUNK to Void + /craft copper pickaxe refused + totem textures (no client WARNs)
119. PACK: The Armory 1.23.0 back on - copper ore, bars, talismans, swords have textures, no purple/missing squares; Extended Backpacks + Tainted Roots gone
120. STARTER: cave mouth, merged Gather logs/stone/copper task + early progress, counted quest cards, saplings replant on felled trees
121. OWN ICONS in menu / teleport / players + TREE buttons Fishing / Alchemy / Smithing + cooked food heals on 0.7 + cooking sounds
122. TREES branch downward (all skill trees + class pages), gold links, window fits
123. CAMP SKELETONS + SHARDKEEPER / HUB SHARD + PORTAL TO HUB + RESPAWN ON ISLAND + STAFF / WAND SPEED TIERS (same DPS / Mana per second)
124. MERGE PROBE + UI KIT PROBE (one session): /coreprobe -> C1 + C2 PASS in chat, the 'Core probe' page shows a gold frame 'CORE' / green 'OK' (C3); then quit, switch OFF only SkyyCoreProbe in the world Mods list, start: world loads, /coreprobe unknown; switch it back on. Also /skyprobe kit screenshots (k1a-k1h) for the hubs. Send both logs.
125. SHARDS: right-click a shard on your island for its own menu, Totem Bench per shard (unbreakable, tiers), hand-held Rain / Fertilizer / Sun, no Shards tile
126. ABILITY TREE: modifier nodes 1 AP, free Root, pick-one A4, owned-only Abilities + focus, Loadout click-to-place, migration keeps everything
127. STAFF BLINK goes past mobs along the crosshair
128. KEEP INVENTORY on death in every world (mob drops unchanged)
129. SAP: +1 Tree Sap on ~10% of chopped natural logs, counts in /collections; placed logs nothing
130. ISLANDS: island / shard time = hub time, portal faces the doorway without the frame, camp stops after the quest, log in on your island
131. HUBS: /character /travel /social /settings open framed hub windows with tabs; /storage /market say coming soon
132. SMITHING: no kick on set cards, Identify tab (tick + Identify picked, Re-identify list), Craft = 4 gathering armor tabs, higher tiers via Anvil
133. CHARACTER HUB: /character tabs Stats / Skills / Trees / Class / Pets / Collections / Profiles in the sky frame
134. HUBS: /market /storage /social /travel /settings HUD tabs in the sky frame; nothing kicks
135. SKYYCORE: Bank + Party run on SkyyCore (same pages, Server Setup History intact)
136. Class tab opens the class tree (/class too); Island 2 boss stays down + island respawn; Lost Loot gear cap; Lantern recipe; Void Artifacts tab - in the NEW world NewBetaTest
137. Big batch in NewBetaTest: Battlemagic XP, health regen, fortune card, Tools tab tier up, furnace fuel, pets fuse/rebirth, tier tags, starter Accessory Bag, Requip rows, natural cave, Assassin kunai, Tree Feller row III, clean first-profile page
138. Batch 2 in NewBetaTest: Home menu + Teleport centre, Smithing UPGRADE tab, sickle sweep + fewer sticks, pole in kit + no-tackle fishing, Crescent Rush + sword guard, bag Craft tab + auto-equip + lanterns, Requip pet/ability slots, bag costs + rebalance, Bazaar CONFIRM + prices, new Zone 1 (/zone 1)
139. HUD widget backgrounds off by default (not the Quest Tracker) - /skyyhud reset
140. Crops + apples + goats back (Compost_Soft fix)
141. Menu 0.3.30: bigger menu, 5x5 grid, unique icons, Right now panel, Smithing opens, HUD tile opens editor
142. Food families: Veggie HP / Fruit Mana / Meat Stamina / Mushroom Strength, faster eating, 11 new dishes
143. Fishing line over water (beads), fish into the Fishing bag, tackle + totem modifier models
144. Class tree top-down, modifiers out of the tree (AP refunded), every ability says what it does
145. Bazaar 0.1.15: x4.5 prices (Eternal seeds kept), crop groups by tier, saplings in Foraging, SELL <TAB> + SELL ALL TABS
146. Lifelong watering can (hold to water), Harvester, SMITHING tab, Upgrade 8 rows
147. Requip 4 ability rows + modifiers, hoe into Requip, Crude Hatchet ghost gone
148. Crafting hub (Crafting + Smithing), crafter look + tier sort, ADD FUEL, benches use the Accessory Bag, Void DEPOSIT ALL
149. Zone 1 = server spawn (/zone setlanding, /spawn for admins, no-island logins), zones weather NPE gone
150. Pet eggs (30), two-reel hatching, round egg model, Pets page grid / hover stats / filters
151. Normal tools off everywhere, Enchanted Sticks, collection rewards swapped, Great Shield, Crescent Rush lunge, Mage blink trail, Warrior dash
152. Lifelong Accessory Bag / Pocket Dimension / Menu item (/accbag /pocket /menuitem), no 2nd bag on reset, Enchanted Stick in Foraging bag
153. Arcane Breach flying arc (6.5 blocks, 1.4x, 5 s), Stacks HUD widget
154. Dodge every way (backwards too), Rebirth on, Loot Bag / Magic Box, /spawn, food Strength, guild symbols, collections redesign, one Harvester (Crude full on wheat), one boss Sigil roll
155. Menu merges (Character / Vault / Market / Collections recipes), one food = one bar, accessory crafting in the bag
156. Deposit All takes all Enchanted, /craft scroll list + big rows, no accessories in /craft, Void upgrade without level
157. Crafting hub tabs + big top row on Smithing, Upgrade buttons, pets Eggs + Hatchery
158. No false Mana / spell-cost WARNs, quiet minimap shutdown (log only)
159. Requip scroll + search on top + take-out stays out
160. Menu cleanup step 1 (SkyWynn Menu pages on the one frame, no back buttons)
161. Menu cleanup step 2: Character hub pages (no back buttons, scroll lists)
162. Menu cleanup step 3: Storage + Market pages
163. Menu cleanup step 4: smithing, Quests redesign, Islands, Explore, Guilds
164. Party page + Disband needs two clicks
165. HUD widget list, Void Charms + Power, Greater Essence + Eternal lock + Enchanted Bazaar, tool upgrades, pets need-N + roster, menus done
166. Seeds / saplings toggles, pickup popup hidden, AH auto-claim on rebirth
167. Tree nodes, Sap Tapper counts, Tree Feller table, Breaking Speed buyable
168. Requip Salvage (two clicks, materials not coins)
169. Class crests + ability icons; /flaskprobe test (then /flaskprobe clear)
170. Explore admin editor in the frame (admin)
171. Fishing Bench uses Void fish; Fishing Power pickable
172. Void Charms Market no crash; Upgrade rows + colour lists; /is sethome <name>
173. Potion Flask + Food Pouch, Storage > Supplies, /flask /pouch; then /flaskprobe clear
174. C:/Program Files/Git/back, /sethome + /home, Teleport page tiles + Arrange, /warpadmin icons
175. Server Setup says Void Charms, not Accessories
176. Void Charms texts, Arrange Prev/Next, Breach x Mark, Requip leaves Pouch food, Nestkeeper dragons
177. Zone ores (Lead/Chromium/Slag/Titanium), alloys + Electrum, Furnace Charm I-V + Eternal Flame, ore + Charcoal collections, Bazaar listings
178. Armory armor / weapons drop from mobs, Mythic boss bags, Mythic/UT craft block, Alteration keeps rolls, salvage via Requip
179. Salvagebench refuses rolled Armory pieces (moves them out), crafted pieces still salvage
180. Wood / Rotten / Tribal wand hold leap
181. Camp quest: full class armor set + secondary weapon (free identify); 8 zone Mining sets; armor weight in flavor text
182. Big Fens trees: all logs picked up; Mining Fortune uncapped; Smelting Fortune on mined ore
183. HUD ability icons for every class, dimmed on cooldown
184. New T1-T15 metal tags, ore hit speeds (never slower), pickaxe Fortune +10, Mage PA4 rift Meteor
185. New metal tools + tier-ups, 76 new metal weapons, soul cage branch, Bazaar unchanged
186. Speed + jump bonuses no longer paused by The Armory
187. 80 new metal swords / axes / bows / spears / shields etc.
188. Metal tool tier-ups gated by collections; Supplies tab picture
189. Merge lifelong pickaxe + hatchet into one multitool (two stat sets)
190. 5 Armory UTs drop as orange Untiered items
191. UT bands + less Mana + mob hit cap 35% + elite no Mythic + Void Charms hint
192. Fortune +3 a level no cap + weapon bags typed at identify + Pole-Vault skip + no hits through walls
193. Island respawn + sky snap + camp clear + island pond
194. Wand launch ~12 blocks + one-handed Soul Orb / menu item + guaranteed vein + feller + 12 new dishes + furnace queue / fuel / ready lists
195. Map in every zone + mob level plates + wand hold right = block + second egg hatches
196. Level bands batch: bands + ladder + alloys + gathering armor + no XP caps + pet portraits + Soul Cage takes any orb
197. Create Profile: bigger class cards, emblem + primary + secondary weapon (Priest Soul Cage)
198. C:/Program Files/Git/class primary + secondary (Soul Cage), no cut tree text, quest widget wraps (beta bugs 13, 15)
199. furnace Charcoal counts, Collections grid text fits, no mob one-shots (beta bugs 3, 13, 16)
200. island camp / boss leftovers despawn after restarts; island sky = hub sky, /time on an island reaches the hub (beta bugs 19, 9)
201. less stutter: minimap sends at most 16 pictures a second (beta bug 4 part)
202. Soul Cage Bindings turn solid ~2x faster (0.8 s Copper)
203. Copper on Iron full speed; no Bronze armor from bags
204. respawn = one world load, no zone flash / freeze (beta bug 4 part)
205. zone trips: little or no 'Waiting for chunks' (beta bug 4 part)
206. XP caps gone in Cooking / Guilds / Exploration; Totem Bench uses the lowest-rarity orb
207. Sacred Heal 8 s; rebirths unlimited; Enchanted alloys pay Smithing XP
208. retired / offline island worlds + old zones unload when empty and reload on demand (beta bug 4 part)
209. Dynamic Seasons tints off in our worlds: world changes stutter less (no 0.2-0.7 s tint stall); seasons, weather and events still run (pack config, no jar change)
210. Skill Trees 3 (Borderlands-style rows, no Dust, coin refund), per-profile world chests with sparkles, Infinite Water Bucket
211. benches keep their upgrade tier when broken and placed again (our own; KeepBenchTiers + Workbench Tier Keeper stay off)
212. class trees fully live (capstones, Shadow Clone, gates 0/5/10/15/20/25), 26 skill-tree upgrades live, Bazaar buy orders / sell offers, Rebirth Void Particles + keep buff, NEW SkyyZones protection (op)
213. skill-tree gates to 0/5/10/15/20/25 where possible, Head Start + Beastmastery Echo work, Weapon Tempering, Masterwork Pick, Accessory Compass / Sprint
214. Balance P3 XP: same levels kept, XP rises with tier, catch-up + past-life boost; pets level at the old pace; ores/stone regrow in SKYBLOCK zones
215. Balance P4 combat: Lv 40 sword vs Lv 40 wolf ~12 hits, casters dry in 20-30 s then quick refill, Mage slow in heavy, elites 3x
216. Rebirth pace (past-life list, no 200 % clamp, unlimited rebirths), Tropical Smoothie XP, Furnace 4x faster + 1000 queue, totem idle 3 days, new-land zone crops
217. Balance P5: weapon lines x1.18, armor Defense + Health %, UT meter /gear, unidentified weapons hide type, Fabled/Mythic charms, pet % stats
219. P8b: Mining / Foraging / Combat tree upgrades buyable + working, Stoneskin + Combat Focus free perks, Spoils extra drops (never gear)
220. Tree-page probe: /skyprobe m1..m7 (big map opens fast? 1,200 / 1,600 elements? lines crisp? picture swap, ring move, tooltips)
221. P6b: collection tiers shorter, Anvil costs, own-tier ore 2+ hits, F-pickup lock, +10 level-up, armor bags hidden, UT >= Fabled
222. Left Alt after closing another page opens at once; element lines in %; Normal bags / charms still white
223. Beastmastery: /skills row, levels from pet XP, /tree beasts upgrades, rebirth resets it
224. Probe 0.7.1: clicks no longer hang; M4 picture swap, M5 ring move, M6 tooltips (then retire the probe)
225. P8d: new tree upgrades buyable, Alchemy / Smithing / Fishing rows open, Beastmastery VP
226. P7: Bazaar prices by tier, death 5 % (island safe), merchants by zone, AH no gathering armor, Smithing Combat section (rolls rarity, never UT / Mythic)
227. Bronze lock says Copper/Iron V; backpacks craftable; level-up coins on the curve; respec cost; Wanderer/Cartographer coins
228. PACK: StructureV2 + Souls like Bosses ON - explore NEW land for camps / towers / ships / boss islands (no traveling merchant); Structure Money turns into coins; Souls bosses show a level + boss rank; no guns drop (they turn into a crossbow / arrows)
229. Radial tree pages: /tree maps, page switching, Learn / respec, zoom + scroll, Class Loadout, never stuck Loading
230. P9 Skills defaults in Server Setup; Mining / Foraging / Beastmastery XP feel; round /rebirth Nexus page (11 arms, Learn, zoom)
231. UI test tour: /skyprobe tour - 15 cases (heads, dialogue bar, tiles, key hints, vanilla feed, trail, zoom scroll)
232. ALT key hint, crouch x2 folds tracker, /quests widget, Stats by source table
233. Elements: coloured element numbers, mob element plates, pet elements, element Defence, Poison, element charms, Stats element charts, UT bands
234. Elemental swords: real longsword damage + element numbers, Poison DoT, not craftable, Mythic drops per zone
235. Dragon pet: hatch, one per profile, summon + stages, void return
236. Dragon fights + boss dragon eggs: bites, Defend / Follow, DOWN, egg drop + Mythic cap
237. joszza pack: DungeonBosses (Bandit Boss on boss islands, Astral Voidcaller via Astral Sigil, Ice Magus at the frozen tower; levelled by our ranks, Structure Money -> coins) + River Bridges (bridges over rivers in NEW chunks; its archer guard does not load - joszza bug, needs MajorDungeons' Mb_Bandit group)
238. Dragon riding (fly / glide), pet tooltips by type, dragon icons, Quirk's Multitool / Harvester, Flame longsword, StructureV2 freeze stopgap
