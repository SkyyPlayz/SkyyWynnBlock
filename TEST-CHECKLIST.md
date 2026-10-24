# SKYY'S TEST CHECKLIST

Short version since 2026-10-05. The numbered in-game steps live in `docs/tests/<period>.md` (word for word); every section ever written is
listed in [docs/tests/README.md](docs/tests/README.md). Each deploy adds ONE section at the END of the newest month file
(`docs/tests/2026-10.md`) and one line under "Test next" below; a line leaves this list once Skyy has tested it (log the result in
`docs/log/<YYYY-MM>.md`).

## Test next - only what still needs your hands (trimmed 2026-10-24)

Skyy 2026-10-24: "go over the entire beta test list, and trim it to the things you actually need me to test still." 243 lines -> the ones
below (old numbers kept so the steps in `docs/tests/2026-10.md` still match). Dropped lines + reasons: `docs/tests/2026-10-24-trim.md`.
Each deploy adds its numbered line at the very end.

### A. Probes first - they unlock the next builds
231. UI TOUR `/skyprobe tour` - 15 cases, ~5 min, send the log (unlocks UI rounds R1b-R5; then SkyyUiProbe is retired)

### B. Fixes of Skyy's own reports - confirm they hold
27, 192. Monk Skipping Bounds / mid-air skip fires (beta bug 5), no hits through blocks (bug 6), Pole-Vault skip
182. Big Fens trees - every log picked up, none fall on the ground (dropped again 10-17); Fortune on Vein Mine / felled logs
20, 196, 202. Soul Cage takes any Soul Orb rarity (beta bug 20), any orb for the next tier, Bindings solid ~2x faster
198, 199. No cut-off text (quest widget wraps, Collections grid, Zen tree), furnace Charcoal counts, no mob one-shots, class primary + secondary on Create Profile
200. Island camp / boss leftovers despawn after restart; island sky follows the hub clock (beta 19 / 9)
201, 204, 205, 208, 209. LAG pass (beta bug 4, still open): respawn = one load, zone trips little "Waiting for chunks", minimap no flood, no season-tint stall
195. BetterMap in every zone, mob level plates, wand hold-right = block, second egg hatches
229, 239. Radial /tree pages: zoomed Trees / Nexus keep their place on click, Learn / respec, never stuck "Loading"
247. Hatch reel never freezes, Dog / Corgi portraits, totem tier-up on its page, totem in the island CENTRE
78, 84, 89. Auto-pickup to Void / inventory / feet, F-harvest, killer + top-damager loot (beta video: "not clear"); pet kills now that pets fight

### C. New features / feel / look - never confirmed
236, 238. Dragon fights + boss dragon eggs (bites, Defend / Follow, DOWN, Mythic cap); Zone-1 wild adult dragons (OPEN-QUESTIONS)
150, 142, 194. Pet eggs + Pets page (grid, hover, filters); Food families (Veggie HP / Fruit Mana / Meat Stamina / Mushroom Str) + the 11 + 12 new dishes
233, 234. Elements: coloured numbers, mob + pet element plates, element Defence, Poison, charms; elemental swords (real longsword damage, Flame longsword)
241, 243, 244, 183. Ability 1 on every weapon (block, Bo / wraps / kunai / spellbook), Mythic 40-60% faster charge, summon slot at Beastmastery 10, dragon FIGHTER + MOUNT, HUD ability icons
127, 151, 153, 180. Traversal feel: staff blink past mobs + trail, Crescent Rush lunge, Warrior dash, Arcane Breach arc, wand hold launch ~12 blocks
6, 178, 190, 191, 217. UT + Mythic: Armory armor / weapons drop from mobs, UT bands + per-item charge rows, orange UT items, Mythic craft block, UT meter /gear
168, 179. Salvage via Requip (two clicks, materials not coins; Salvagebench refuses rolled Armory pieces) - Salvage tab was empty in the beta video
184-189, 203, 146, 240, 242, 154. Metal ladder: T1-T15 tags, ore hit speeds (never slower), Fortune +10, speed / jump bonuses, tier-ups gated by collections, one Harvester (Crude full on wheat), Breaking Speed row, harvest swing, Motherlode x3
213, 219, 225, 223. Tree upgrades are buyable AND work (Weapon Tempering, Masterwork Pick, Accessory Compass / Sprint, Spoils, Stoneskin; Beastmastery /skills row + levels from pet XP)
245, 232. Tier tag first + real set names + green / red requirements + full-set craft button; crouch x2 folds the tracker, /quests widget, Stats by source table
210, 211, 129. Per-profile world chests with sparkles, Infinite Water Bucket; benches keep their upgrade tier; +1 Tree Sap on ~10% of natural logs
228, 237. Structure packs: Souls-like Bosses level + rank, DungeonBosses on boss islands, River Bridges in NEW chunks, Structure Money -> coins, no guns drop
92, 136, 97. Lost Loot piles + airdrop (gear cap); Sigils apply on the Anvil, boss Sigil roll
107, 110, 112. Sounds: quest / reward / portal / pet / claim, level-up, Void full, big /pay, Bazaar / AH; "Mod sounds" switch mutes them
47, 164. Party TPA + Accept TPA (needs 2 players), bags blocked in /trade, Disband needs two clicks
98, 111. Admin page (4 tabs, confirm buttons, permission hiding) + /settings /modconfig search + Go to

### D. Balance (numbers, feel)
214, 230, 216. XP pace: same levels kept, XP rises with tier, catch-up; Mining / Foraging / Beastmastery feel; rebirth pace + Nexus page; furnace 4x, totem idle 3 days
215, 59. Combat: Lv 40 sword vs Lv 40 wolf ~12 hits, casters dry in 20-30 s (P9 F5 caster Mana), elites 3x; Perfect Parries per class (too easy / hard?)
221, 226, 227, 145, 212. Economy: collection tiers, Anvil costs, +10 level-up, Bazaar prices by tier + buy orders / sell offers, death 5%, merchants by zone, level-up coins, respec cost

## If anything crashes or misbehaves
Send the newest `...\Saves\HUD mod\logs\<time>_server.log` (and the client log from `UserData\Logs`) plus a screenshot; fixes from Skyy's
tests always come first.

### Latest
248. (zone reset + undo PASSED) still open: shard ores regrow, Requip pet portraits, "... Modifier" names, unspent tree points in Right now
249. BIG BATCH 2026-10-24: starter archipelago + shard doors, mob drops -> Combat bag, Harvester / seasonal crops count + Farming XP, great shield Bulwark Charge, Weaponcraft x1.5, Beastmastery hatching nodes, Wardrobe coin slots, whole-island gathering + regrowing trees
250. BATCH 2 2026-10-24: floating islands in the void (black grass fixed, round islands + trees, spacing, heights, flying islands on), auto-compact per-bag upgrade + crafting opens Enchanted + Unpack, gathering armor upgrades in place, Ornate Bronze combat set, tooltip header order, Fishing stage 2 (Zone 2-3 fish, T3-T9 rods)
251. BATCH 3 2026-10-24: radial Shard Upgrade Map + re-balance (+3 % a level, Offline Harvest), saplings from leaves + stump replant, Farming tree = crop level, A1 alts as late either/or paths (+50 %), pet rarity colours, 'Your Islands' archipelago quest line
