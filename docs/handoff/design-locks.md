# HANDOFF - design locks + goal (2026-09-22 to 2026-10-01)

> Moved word for word from HANDOFF.md on 2026-10-05 (docs consolidation). History: newer files win - see INDEX.md.
> Newer answers are in docs/answered/<topic>.md and beat this file. Skyy's own gear docs: SkyyGear-Plan.md, SkyyGear-Stat-Catalog.md.

# SKYWYNN — HANDOFF
*Rewritten 2026-09-22 21:00, restructured 2026-09-23 20:45 (session 4): section 3 = current state (always current), section 6 = running log (append-only). Read this first; every other doc in this folder is detail. Owner: Skyy (GitHub: SkyyPlayz).*

## GEAR LOCKS (2026-09-25) - status 2026-10-01

**SkyyGear is BUILT and live (0.1.3):** rarities, unidentified drops + /identify, reforge, levels per material, charged attack damage, every world chest's gear unidentified. **Next: SkyyGear 0.2 Wynn-style item levels** (research/Gear-Levels-Wynn-Spec.md, Skyy's answers in its section 11; queued after the 2026-10-06 usage reset - RESUME.md section 3).

**The locks below still hold.** Do not invent the open numbers. Detail is in `SkyyGear-Plan.md` and `SkyyGear-Stat-Catalog.md` (Skyy's docs - never edit them).

- Gear rules: level and rarity on every item, smithing rarity, reforge roll range, unidentified drops, `/identify` then an NPC, any-rarity drops, set bonuses, Equipment bar, loadouts, Accessory Power system.
- Combat, defence, and mana (change note 9). **Magical Power** is the spell-damage stat. **Strength** is melee or hit damage. Mage staff melee uses Strength. Spells use Magical Power (change note 22).
- Movement (change note 10). Gathering (change note 11). Loot and luck (change notes 12–13). XP and wisdom (change note 14).
- Other table is scrap as gear IDs. Breathing uses Hytale oxygen. A separate accessory boosts water swim speed (change notes 15–16).
- Accessory craft ladder (change note 17). Enrichments (change note 18). **Ferocity** enchant cap 300, total cap 600 (change note 20).
- Starters: Tank, Balance, Slayer, Lucky, Fast, Magical.
- Combat 15: Fortress, Harmony, Glass Cannon, Fortune, Blitz, Arcane. Buffs and debuffs. Amounts scale with Accessory Power. Exact curves are not locked.
- Accessory Power model (change note 23): each accessory has its own buffs and adds flat +10 to +25 Accessory Power by rarity. Exact table is not set. Total is the sum of equipped accessories. The selected profile scales from that total.
- Default profile is Balance (change note 24). No empty profile. Players can switch to Tank, Slayer, Lucky, Fast, Magical, or the Combat 15 ladder when unlocked.
- Gear pipeline (change note 25): combat gear first. Every piece has a rarity. Rarity drives modifier count and power. Crafted gear rolls on craft. Mob drops identify to reveal the item and the roll. The Keep list is the modifier pool.

**Answered 2026-09-25 (Skyy, in chat; SkyWynn-Decisions change notes 2026-09-25 #5):** rarities = Wynn (Normal, Unique, Rare, Legendary,
Fabled, Mythic + Set); level requirement = the player's class weapon skill; SkyyGear REPLACES SkyyRolls; mob AND world-chest gear drops
unidentified, old gear stays plain until reforged (rolled items keep their rolls).
**GEAR LEVEL CAP BY GEAR TYPE (Skyy, 2026-09-25):** your CLASS level (class weapon skill) caps COMBAT gear; your MINING level caps MINING
gear; your FORAGING level caps FORAGING gear; FARMING caps farming gear; etc. (fishing and others later). So every gear piece carries a
GATE SKILL (combat -> the class weapon skill; mining/foraging/farming gear -> that gathering skill), and the level check is generic. Stage 1
builds combat gear only, but the data model and the check must already support the gathering gate skills.

**STILL OPEN.** Do not block the build on these. Do not invent them.

- Tuning table.
- Stone powers. Do not extend the Hypixel stone list.
- Wynn Major IDs.
- Exact numeric curves. The +10 to +25 Accessory Power range is locked. The table is not.
- Magical Power on enrichments or tuning.
- Gathering gear (mining, farming, foraging). Combat gear is the first build.
- Pets, fishing, and hunting.
- Fortress extra debuff, if any. Do not add one until Skyy picks it.

---

## 1. THE GOAL

Build **SkyWynn**: a public Hytale server that fuses Hypixel SkyBlock (economy, sacks, collections, bazaar/AH, minions, islands, slayers) with Wynncraft (classes, quests, map, party) — plus a Lunar/Wynntils-style QoL layer (customizable HUD, map+minimap, party widget, quest nav).

It is built as a **family of standalone mods** ("Skyy*" mods). Each one must:
- Work alone with **zero external dependencies** (bundle anything needed into the jar — never "requires HyUI").
- Carry its version at the **start of the display name**: `"0.2.4 SkyyHud"` (so they sort together in the mod list).
- Be designed to **integrate with the future SkyWynn systems** (map, party, quests, coins, collections) even if those don't exist yet.
- Be **clean-room our own code**. Existing mods are reference only — but **Skyy's rule: "never build new when you can steal what already works"**: find a working mod in the Mods folder that does the thing and mirror its exact calls.

### Locked decisions (Skyy) — don't re-ask
| Topic | Decision |
|---|---|
| Server type | Public |
| World | Hand-built on the server (team later); build all mods first. Spine = zone island chain; hub = spawn / social (2026-09-23 lock). **2026-09-24:** much of the chain is server-side hand-built shared worlds. Solo players get a planned mod, **SkyyWorldGen** (name TBD), using Hytale World Gen 2 to auto-generate flying islands split by zone. World Gen 2 capability ANSWERED 2026-10-01: yes - plan in research/SkyyWorldGen-Plan.md (one world per zone island, terraced rings = levels, zone bands Z1 1-20 / Z2 20-30 / Z3 30-45 / Z4 45-60, summit portal after the boss, a vanilla-temple starter town per zone; the Zone 1 town is the hub). Not built yet |
| Classes | Wynn's five stay: **Warrior, Archer, Mage, Assassin, Shaman**. Launch: Archer, Warrior, Mage. Assassin and Shaman later. **Berserker + Priest locked (Skyy, 2026-09-25):** Berserker = weapon skill **Fury**, weapons axes, battleaxes, maces, clubs. **Priest** (new) = an **AoE healing support** class, weapon skill **Divinity**, weapons wands + spellbooks; much of it will be custom later. Until the spell system exists, a Priest's weapon hits heal nearby party members (placeholder). Every class gets a **class kit** with its basic weapon, given automatically when the class is selected. Launch roster: Archer, Warrior, Mage, Berserker, Priest; Assassin and Shaman later (Shaman gets a custom weapon later). Combat-only lock (gathering stays open). Per-weapon class skills; no shared Combat skill. A new class is a **new profile and a new island from zero**. Ability keys are the standing input note (2026-09-21). **Magic system is open** (batch 2) — not locked to Chapter 1 runes. **Code:** 0.1.2+ set `ALLOW_SWITCH=false` (paid switch removed) and removed Berserker. Current jar is 0.1.4 and still has no Berserker. Putting Berserker back is future code work |
| Profiles | Full saves; the class selector. **Default cap 6** (2026-09-24, raised from 4). In-game ways to raise it higher; method TBD. SkyyProfiles 0.1 still caps at 4 (`DEF_MAX_PROFILES = 4`) — code follow-up, do not change it in a docs pass |
| Collections bypass | **Tiered (2026-09-24):** coins bypass collections in the early game and the first half of mid game. Toward late game those items cannot be bought or sold (bazaar/market). Many items have level requirements; **every gear item** has one (change note 6). **Open:** cutoff per collection/tier; level type (skill vs class vs combat). SkyyCollections 0.2 still uses the older per-curve walls; SkyyBazaar 0.1.1 has no sell wall. Code follow-ups only |
| Garden | **Parked (2026-09-24).** Farming stays on the main islands (private island and the zone chain) for now. The 2026-09-23 "most farming is in the Garden" lock is reversed |
| Death penalty | **10–25%** of coins, reaffirmed 2026-09-23. **Editable in-game**: `/deathpenalty 5%` (fixed) or `/deathpenalty 5%-10%` (random in range) |
| Name | **SkyWynn** is the quick reference. Repo name stays **SkyyWynnBlock** |
| UI | Best placeholders we can ship, refined as we go. **Exception:** no buttons or custom UI on the **inventory screen** (Hytale will change that UI). HUD, pages, and other windows are in scope. F5/F6/F7 stay locked |
| HUD | Lunar-style editor for OUR widgets (move/scale/toggle), layout export/import codes; rebindable edit hotkey (engine-limited today) |
| Party widget | Name + HP + stamina + mana per member; same party system feeds map positions |
| Map | ONE renderer for full map + minimap, party + quest layers. **Not built yet — design for integration only** |
| Quest nav | Compass marker default; on-demand beacon/particle trail toggle |
| Voiceovers | Later |
| Hotkeys (F5/F6/F7 recipe/AH/uses) | Wait for engine keybind support; rebindable normal keys |
| Research | Always use cheap models (sonnet) for research/review agents |
| **Bench accessories** (Skyy 2026-09-23) | Inventory crafting = OUR crafting page (`/craft`, also a Craft tab in `/pd`): shows the basic Fieldcraft recipes by default; carrying a **bench accessory** (one item per bench: Workbench, Forge, ...; later lives in the SkyBlock-style accessory bag) unlocks that bench's full recipe list in the page. Materials are counted from inventory + bags; the engine's `CraftingManager.craftItem` consumes and gives output. Vanilla pocket crafting stays vanilla (client-gated, cannot see bags). **Collections unlock recipes** that also appear in this page (SkyyCollections publishes `coll:recipes:<uuid>` = comma-separated recipe ids through the JVM bridge). End state (Skyy): everything is inventory crafting through this page, no benches needed |
| Multiplayer | Everything per player (Skyy 2026-09-23): pools, bag pages, sweep exemptions, crafting feed, coins, layouts are keyed by player UUID; a player may only craft from their own pocket dimension. Verify with 2 accounts (TEST-CHECKLIST) |
| **Magic Bags** (was "sacks", 2026-09-22 late) | Items are "Magic Bags" opening onto the player's **pocket dimension** (flavor text). Strict access: you must carry a bag of the category to open/withdraw it; the pool itself persists per player (never lost). Bag rarity caps **each item** (Small 640 / Medium 2,240 / Large 20,160), best bag carried counts; works from storage, hotbar or backpack. `/sacks` = `/pd` = `/bags`. Next: workbench + inventory crafting pull from the bags |
| **In-game server setup** (Skyy 2026-09-24) | Everything a server owner might change must be editable IN GAME: SkyWynn Menu -> Mods (admins) -> click a mod -> its config page; NPC shops, NPC quests, ranks + permissions, island template, market, progression numbers. Files stay and always match. Plan: `docs/plans/SkyWynn-Server-Setup-Plan.md` |
| **SkyyEconomy** (Skyy 2026-09-24) | Coins + Bank + Bazaar + Auction House become ONE mod (next round after the separate versions are tested), later NPC shops + item value. Same save folders, bridge keys, commands and permission nodes; per-part on/off switches. `/trade` goes in SkyyEssentials. Plan: `docs/plans/SkyyEconomy-Plan.md` |

### Design lock (voice call, 2026-09-23 night)

Overrides older draft spine, class roster, Combat skill, guild phase, and skill-gate wording. Detail: `docs/plans/SkyWynn-Decisions.md` (call-lock notes), `docs/plans/SkyWynn-Master-Plan.md` Part 2–3, and the `Skyy*-Plan.md` feature plans.

1. **Private island** = progression home (minions, upgrades, co-op, size tiers) **plus** free creative building. Not creative-only.
2. **Leveling spine** = **island chain**: one floating island per Hytale zone, biomes ramp difficulty as you cross it, finish a zone's island before the next unlocks. Replaces hub + level-gated open-world zones. **Hub** stays the shared spawn / gathering / social point. **2026-09-24:** much of the chain is server-side hand-built shared worlds. Solo generation is the planned **SkyyWorldGen** mod (name TBD, not started). World Gen 2 capability ANSWERED 2026-10-01: yes - plan in research/SkyyWorldGen-Plan.md (one world per zone island, terraced rings = levels, zone bands Z1 1-20 / Z2 20-30 / Z3 30-45 / Z4 45-60, summit portal after the boss, a vanilla-temple starter town per zone; the Zone 1 town is the hub). Not built yet.
3. **Classes** = Wynn's five (Warrior, Archer, Mage, Assassin, Shaman). Archer, Warrior, Mage first; Assassin and Shaman later. Combat-only lock. The 2026-09-23 "drop Berserker" line is **reversed 2026-09-24**: Berserker is back, status PENDING (see the locked-decisions table). Do not design it here.
4. **No shared Combat skill.** Combat XP goes into the equipped class's weapon skill (Archery, Swordsmanship, Sorcery at launch; Assassination with Assassin; Shaman's weapon skill when that class is designed).
5. **Skills** = full SkyBlock-style tree **plus** extras (Smithing, Exploration, and the rest). Keep the ambitious list; trim later.
6. **Minions** on the private island. Helpful, not mandatory.
7. **Dungeons** = story beats through the island chain + one endgame capstone after the last island. Extra dungeons and raids are side content. Slayers move to the core loop in batch 2; they are not the spine.
8. **Guilds** in the core loop with parties. Not Phase 7. Territory war stays later.
9. **Skill gating** = soft gate with a ceiling. Uneven progress is allowed; drifting too far slows you until you catch up.

### Design lock, batch 2 (same call)

Batch 1 above stays. This list adds to it.

1. Death penalty stays **10–25%** coin loss.
2. **Magic Bags / sacks** stay and are **core QoL**.
3. **Accessories + magical power** are **core**, not later-game.
4. **IDs + reforges** are **core**. Every item has rarity and stats. Reforge swaps bonuses. **Tightened later the same day** (`SkyyGear-Plan.md`, change notes 6–8): every gear item has a level requirement and a rarity tier (names and colours open); higher rarity means a wider, higher reforge roll range; mobs drop unidentified weapons and armor. `/identify` opens the menu for now; later an NPC does it. Cost is coins and scales with rarity and level (formula open). Drops can be any rarity. Some sets are drop-only and some are craft-only. Sets have set bonuses. Smithing level feeds smithing rarity. An Equipment bar (necklace, cloak, ring, belt; name not final) sits next to armor. A loadout saves armor, that bar, and the selected Accessory Power buff (pets once pets exist). Wardrobe stays a placeholder, not on the inventory screen.
5. **Wynn's five elements + powders.** Powders replace SkyBlock runes. This is gear, not the open magic thread.
6. **Co-op:** players can share and visit each other's private islands.
7. **Slayers** are **core loop**, not side content, and not the island-chain spine.
8. **HOTM-style trees** unlock from that skill's levels, not from a location.
9. **Garden:** parked 2026-09-24. Farming stays on the main islands for now. The "most farming is in the Garden" sentence is the 2026-09-23 lock, reversed.
10. **Coin-bypass** is tiered (2026-09-24): early game and the first half of mid game. Toward late game those items cannot be bought or sold. Many items have level requirements; **every gear item** has one. Cutoff and level type are open. The "off at the endgame wall" sentence is the older wording. SkyyCollections 0.2 and SkyyBazaar 0.1.1 do not implement the new wall (code follow-up).
11. **Profiles** are full saves. Swapping profile changes the island and everything else. A new class is a new profile and a new island from zero. **Default cap 6** (raised from 4). In-game raise method TBD. SkyyProfiles 0.1 still caps at 4. Paid class switch: removed in SkyyClasses 0.1.2 (`ALLOW_SWITCH=false`). The 0.1.1 jar that sold a switch is not the current jar (0.1.4).
12. **SkyWynn** / repo **SkyyWynnBlock**.
13. **UI:** placeholders, refined continuously. Inventory screen is the only UI we skip.
14. **Magic: open.** Wait on Chapter 1 runes. Do not treat "class abilities are engine runes" as locked.

### Focus call (Skyy, 2026-09-23 late): what gets built now
- **Classes:** Archer, Warrior, Mage now. Assassin and Shaman later. Berserker is PENDING (2026-09-24) — not in the "now" list and not timed against Assassin/Shaman.
- **Skills NOW:** Mining, Foraging, Farming, Acrobatics, the class weapon skills, **Alchemy (build it)**, **Exploration (add it: research SkyBlock + Wynncraft rewards first, Skyy picks)**, **Smithing kept** (leveled by reforging and adding powders).
- **A skill tree per gathering skill: YES** (Mining, Foraging, Farming).
- **Alchemy + Cooking are table-only:** remove the Alchemy Bench + Cooking Bench accessories (and the /craft Alchemy tab + cooking recipes); the vanilla tables draw from sacks. **Furnace smelting gives Smithing XP** (vanilla Furnace + SkyySacks Furnace tab).
- **Shelved / later:** Fishing, Enchanting (not in Hytale), Taming + pets, Carpentry (skip), Hunting (big SkyBlock feature, later project), Runecrafting, Social, Dungeoneering.
- **Cooking: BUILD NOW next to Alchemy** - food you cook gets stronger and lasts longer with your Cooking level (x2 at level 50, x4 at level 100); skill-tree modifiers push it further. Condition: the engine must allow it.
Full table: docs/plans/SkyySkills-Plan.md.

### Feedback on the build round (Skyy, 2026-09-24)
- SkyyCooking and the skill trees: approved ("great"). Smithing tab (tools/weapons/armor incl. wood/crude): approved.
- **Campfire accessory comes BACK** for quick inventory cooking (it already limits you to the campfire dishes): Cooking XP x0.5 and the buffs the Cooking skill adds x0.75 when cooking through it (an emergency cook). Alchemy + Cooking Bench accessories stay retired.
- Smithing XP = smelting ore into bars only; mining never gives Smithing XP (confirmed in SkyySkills 0.4: SmeltSys + Sacks Furnace tab only).
- **Bags (Skyy):** smelted bars go in the MINING bag (SkyBlock's Mining Sack holds ingots too); a Smithing bag can come later for reforge stones / powders. The Combat bag exists (Small Combat Bag = 3 Wool Bolts + 4 Bone Fragments at a Workbench) but the bags page only shows tabs for bags you carry: show all four tabs, with how to craft the missing bag. -> SkyySacks 0.7.5 after 0.7.4.
- **Tree Feller rework:** Hytale already fells a tree when its whole base is broken, so Tree Feller breaks extra logs HORIZONTALLY on the broken block's Y level: level 1 = the next log beside it, max level = every log of that tree on that Y level. No vertical reach. Trees will get a SkyBlock-style rework on the server later.

### Pack goal (Skyy, 2026-09-24)
Get the pack to where it is **100% usable for solo and private multiplayer worlds**, and **prepared for server use** - if someone else wants to run a server with it, the pack is good to go. Many server features stay on the back burner, but their BACKBONES get built (config/admin driven, multiplayer-safe) so a server builder only has to add content.

### Own content (Skyy, 2026-09-24)
Third-party mods are fine for now, but EVENTUALLY EVERY MOD IN THE PACK IS OUR OWN. Third-party features get replaced by our own versions (e.g. More Crossbow Tiers -> our own crossbow line). Gear is locked in SkyyGear-Plan.md (2026-09-24): combat armor and weapons copy Wynncraft, gathering armor is SkyBlock-style (farming and foraging sets; mining likely the same), every gear item has a level requirement and a rarity, mobs drop unidentified weapons and armor, Smithing level raises a smithing rarity stat, higher rarity means better reforge rolls, and wardrobe + loadouts are in (placeholders, not on the inventory screen). A loadout saves armor, the Equipment bar, and the selected Accessory Power buff. Identification is `/identify` for now and an NPC later. Stats: change note 9 replaces the five Wynn skill points on gear. Combat, defence, and mana are locked in SkyyGear-Plan.md. Movement is locked (change note 10, 2026-09-25): flat +Speed; Sprint scrap (Hytale stamina); Stamina Regen armor-only; Jump Height on skill trees and accessories; Rift Speed scrap. Gathering is locked (change note 11): Breaking Power, Mining Speed (pick swing speed), Pick Breaking Damage (blocks only), Mining Spread, one Mining Fortune, Auto Smelt, Farming Fortune, Foraging Fortune, and Timber (horizontal extra breaks; not Sweep). Loot and luck is finished (change notes 12 and 13): Loot Bonus, Loot Quality, Stealing, and Trophy Hunter (Magic Find is scrap as the name). Pet Luck is keep later (build when pets exist). Fear and Tracking are scrap. XP and wisdom is locked (change note 14): one Wisdom per skill we have. Combat Wisdom is one modifier for every class. XP Bonus is a flat small % on all XP. The Other table is scrap as gear IDs (change note 15): Heat Resistance, Cold Resistance, Respiration, Pressure Resistance, Rift Time, Rift Damage, Rift Intelligence, Hearts. Breathing uses Hytale oxygen, not a Respiration ID. Accessories can raise oxygen. A max-level oxygen line allows full underwater breathing. A separate accessory boosts water swim speed (change note 16). Most accessories are crafted. Collections unlock the next craft tier. The next rarity needs the previous rarity (change note 17). Enrichments keep Speed, Crit Damage, Crit Chance, Strength, Defense, Health, and Attack Speed. Intelligence Enrichment is Mana % enrichment. Magic Find Enrichment is scrap. Sea Creature Chance is later. Ferocity Enrichment is pending. Ferocity stays. Enchant cap 300. Total cap 600. Combat, gear, and accessories (change note 20). Custom starters: Tank, Balance, Slayer, Lucky, Fast, Magical. Hypixel names Fortuitous, Pretty, Protected, Simple, and Warrior are scrap. Powers use flat mana. Dedicated mana accessories use +% mana. Combat 15 powers mirror those themes and are more extreme. They use buffs and debuffs. Amounts scale with Accessory Power (change note 21). Fortress, Harmony, Glass Cannon, Fortune, Blitz, and Arcane are Keep (change note 22). Fortune is high Crit Chance, good Crit Damage, slight Strength, −Health, and −Defense. Blitz is high Speed and Attack Speed, −Health, and −Defense. Arcane boosts Magical Power more, with −Defense and −Strength. Magical Power is a spell-damage stat. Strength is melee or hit damage. Mage staff melee uses Strength. Spells use Magical Power. It rolls on weapons, armor, Equipment, and accessories. It is not the bag score. The starter Magical also boosts it. Hypixel names Commando, Disciplined, Inspired, Ominous, and Prepared are scrap. No Power is scrap (change note 24). The default profile is Balance. Whether Magical Power joins enrichments or tuning is open. Change note 25: start building combat gear. Gathering gear is later. Rarity drives modifier count and power. Crafted gear rolls on craft. Mob drops identify to reveal the item and the roll; rarity is already set. Keep modifiers are the roll pool. The catalog's next blank table is stone powers. Do not block on it. Class skill trees are Borderlands-style research (Borderlands 4), not designed. It still sits on SkyyRolls' rolls + the native ItemDisplay tooltip. SkyyRolls 0.1.3 shows rolls immediately and does not implement unidentified drops, smithing rarity, or a rarity-based roll range — future code, not this docs pass. Rule: REBUILD features ourselves - do not copy other authors' files (items, models, textures, code) unless their license allows it; check each mod's license first.

### Exploration call (Skyy, 2026-09-24) - full detail in docs/plans/SkyyExploration-Plan.md
- **Now:** Exploration boosts max Stamina a little per level + coins per level; XP from first opening world chests (+ chest luck = extra roll chance per level), map coverage (new chunks, no XP while flying), Hytale zone discovery; titles; Exploration AND Acrobatics each get their own skill tree (health bonus in the Exploration tree, a Stamina node in the Acrobatics tree; the rest of the Exploration tree is 'figure out later').
- **Later (server):** discovery/secret spots, island arrival, dungeons, finder sense, Echo Shards (hand in 5 = backpack slots; half = no coin loss when falling into the void; all = creative flight on your private island), island %, zone hunt, town warps (starter town free, others via quests/scrolls), lootrun camps, map reveal.
- **Rules:** Exploration is per profile (keep the map, lose the warps); one-time sources; no XP boosters; no /fly on the main exploration islands (teleport does not block); chain islands are SHARED worlds (only your island is private). Bags: each bag's main expansion will come from a collection in its field (e.g. Mining bag per Iron tier), Exploration gives slight boosts - a later bag restructure.
- **Profiles (Skyy):** bank interest and everything in Skills are per profile.
- **Future project (named 2026-09-24):** **SkyyWorldGen** (name TBD). Planned, not started. For solo players it uses Hytale's World Gen 2 to auto-generate the world as flying islands split by zone. The server chain stays hand-built shared worlds. World Gen 2 capability ANSWERED 2026-10-01: yes - plan in research/SkyyWorldGen-Plan.md (one world per zone island, terraced rings = levels, zone bands Z1 1-20 / Z2 20-30 / Z3 30-45 / Z4 45-60, summit portal after the boss, a vanilla-temple starter town per zone; the Zone 1 town is the hub). Not built yet.
- **Island checklist (C2): build the BACKBONE now** (per-island checklist per profile, % on /explore, entries from config + admin commands, with admin-placed discovery/secret spots as its first content source); the actual checklist content waits for the server.
- **Island settings (Skyy):** copy the Minecraft SkyBlock plugins' island settings menu (roles + permission flags, visitors on/off, biome, ...) -> SkyyIslands 0.5 (workflow skywynn-island-settings running).

SkyyClasses **0.1.1** (historical, not the current jar) had Berserker in the roster, Combat.<Class> skill keys, and a paid class switch. **0.1.2+ already removed that:** Berserker is gone from the jar and `ALLOW_SWITCH=false` (no paid switch). Current code is **0.1.4**. Design as of 2026-09-24 wants Berserker **back**, status PENDING — future code work, not a return to the 0.1.1 spike. Shaman, per-weapon skills, and one class per profile still hold. This note does not rebuild the mod.

Full rationale: `docs/plans/SkyWynn-Decisions.md` (rows 10.17–10.28 locked, plus the 2026-09-23 ✔ rows and the 2026-09-24 change notes), `docs/plans/SkyWynn-Master-Plan.md`, `docs/plans/SkyWynn-QoL-Catalog.md`. `docs/archive/SkyWynn-Mod-Roster.md` is stale as of 2026-09-22; prefer `docs/archive/DESIGN-STATUS.md` and this file. SkyyWorldGen is the one roster addition from 2026-09-24.

---

