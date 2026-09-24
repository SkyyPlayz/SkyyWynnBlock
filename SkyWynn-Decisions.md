# SKYWYNN — ELEMENT-BY-ELEMENT DECISION WORKSHEET
*The thorough dive. Every element from both games, one line each.*
*Fill the ☐ DECISION column: **TAKE** / **SKIP** / **MODIFY (how)** / **LATER (which phase)**.*
*"Draft call" = Claude's suggestion from the master plan — overrule freely.*

**Already locked (don't re-decide):** public server • hand-built world • Archer/Warrior/Mage first, Assassin and Shaman later (Wynn's five; no Berserker) • death = 10–25% coin loss • clean-room code • name **SkyWynn** (quick reference); repo name stays **SkyyWynnBlock** • the call locks below. Ability-key casting is the standing input note from 2026-09-21. The magic system behind it is an open thread (batch 2), not a lock.

## Call lock notes (2026-09-23)

Voice call, night of 2026-09-23. These override older draft text in this sheet and in `SkyWynn-Master-Plan.md`. Rows marked ✔ below are locked; unmarked rows stay open.

1. **Private island** — easy to read the old 3.1 line as a creative plot only. Locked: it is the progression home (minions, upgrades, co-op, size tiers) **and** free creative building. Building is free; progression systems still live on the island.
2. **Leveling spine** — 1.7 and 7.1 drafted hub + level-gated open-world zones as the path. Locked: an **island chain**. One floating island per Hytale zone; that island's biomes ramp difficulty as you cross it; finish the zone's island before the next unlocks. Hub town stays the shared spawn / gathering / social point, not the main leveling world.
3. **Classes** — Archer / Warrior / Mage first was already locked; Assassin and Shaman were only "confirm later." Locked: both come later, and both are wanted. Roster is Wynn's five (Warrior, Archer, Mage, Assassin, Shaman). Drop Berserker and any other non-Wynn name. Combat-only lock: the class locks the combat path; gathering stays open for everyone.
4. **Combat skill** — 2.5 drafted a shared Combat skill, separate from Class Level. Locked: **no shared Combat skill.** Skills are per weapon / per class. Combat XP goes into the weapon skill of the equipped class.
5. **Skill list** — keep the full SkyBlock-style tree **plus** extras (Smithing, Exploration, and the other non-SkyBlock rows on this sheet). Do not drop Smithing or Exploration because SkyBlock lacked them. Trim later.
6. **Minions** — 3.3 was TAKE with no word on whether they are required. Locked: they live on the private island and are helpful, **not mandatory**. Nice AFK help, not required to progress.
7. **Dungeons** — the draft mixed in-world keyed dungeons with a later floor dungeon, and left raids feeling like the climb. Locked: story beats woven through the island-chain progression, plus **one** endgame capstone dungeon after the last island. Extra dungeons and raids stay **side content**, not the spine. Slayers were grouped with that side pile in the first write-up; batch 2 moves slayers onto the core loop. The dungeon spine is unchanged.
8. **Guilds** — 8.2 said "later phase" (master plan P7). Locked: guilds move into the **core loop with parties**. Territory war (8.3) stays later.
9. **Skill gating** — 1.3 ("neglect a skill → held back") could be read as a hard togetherness gate or as a nudge with no ceiling. Locked: a **soft gate with a ceiling**. Uneven progression is allowed; drifting too far slows you until you catch up. Not "all skills must advance together," and not unlimited neglect.

## Call lock notes, batch 2 (2026-09-23, same call)

Added after batch 1. Batch 1 stays in force. Where a line below names a batch 1 row, it tightens that row; it does not replace the island, class roster, skill list, minion, guild, or skill-gate locks.

1. **Death penalty** — reaffirmed. Keep **10–25% coin loss** on death (the 2026-09-21 lock). Softeners (row 4.8) stay open.
2. **Sacks / Magic Bags** — 4.4 was TAKE with no phase. Locked: **keep**, and they are **core QoL**, not an optional later feature.
3. **Accessories + magical power** — 5.10 was TAKE with no phase. Locked: **core**, not later-game.
4. **IDs + reforges** — 5.3 and 5.4 were TAKE; 5.5 was undecided. Locked: **core**. Every item has rarity and stats. Reforge swaps bonuses. Both live on items; not a drops-versus-crafted split.
5. **Elements + powders** — 5.8 drafted "elements-lite"; 9.3 drafted swapping in Hytale's element set. Locked: bring in **Wynn's five elements** and **powders**. Powders **replace SkyBlock runes**. Gear elements are not replaced by Hytale's set.
6. **Co-op islands** — 3.2 was TAKE. Locked: multiplayer. Players can **share and visit** each other's private islands.
7. **Slayers** — batch 1 had filed them with side content. Locked: **core loop**, not side content. They are still not the leveling spine (that stays the island chain).
8. **HOTM-style mini-trees** — 2.13 stays on the list. Locked: bring them in, **tied to the skill itself** (Mining levels unlock Mining's tree, and the same pattern for the others). **Not location-locked.**
9. **Garden** — 3.8 was LATER. Locked: fold farming in. Some farming on the main islands (private island and the zone chain); **most farming is in the Garden.**
10. **Coin-bypass** — 1.2 reaffirmed. Players can buy collection unlocks with coins early, at steep prices, until the midgame wall. Endgame recipes stay collection-locked.
11. **Profiles** — 1.8 was LATER; 1.9 drafted multiple class slots on one account. Locked: full SkyBlock-style profiles. Swapping profile means a different island and different everything. **Profiles are how you select a class.** A new class is a **new profile and a new island from zero.** The batch 1 roster, phase order, and combat-only lock still apply inside a profile.
12. **Name** — **SkyWynn** is the quick reference. **SkyyWynnBlock** stays the repo name.
13. **UI** — 10.22 was a full UI build freeze until NoesisGUI. Locked: build the **best placeholders possible** and keep refining them. **Exception:** do not add buttons or custom UI on the **inventory screen** (Hytale will change that UI). Wait on the inventory screen only. F5/F6/F7 and the other QoL rows stay locked.
14. **Magic system** — **open, not locked.** Wait to see how Hytale Chapter 1 handles runes before choosing the magic approach. Rows 9.1 and 9.2 are that open thread. This does not reopen the class roster, the combat-only lock, or powders-on-gear.

---

## 1. PROGRESSION SPINE

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 1.1 | Collections (self-gathered counts → recipe unlocks) | SkyBlock | TAKE — the backbone | |
| 1.2 | Coin-bypass of collection gates until mid-game wall | Skyy's rule | TAKE — steep prices, endgame = no bypass | ✔ KEEP — coins buy collection unlocks early, steep prices, until the midgame wall. Endgame stays collection-locked |
| 1.3 | Multi-skill soft-gating (neglect a skill → held back) | Skyy's rule | TAKE | ✔ Soft gate **with a ceiling**: uneven progress is allowed; drift too far and gains slow until you catch up. Not a hard togetherness gate, and not unlimited neglect |
| 1.4 | SkyBlock account level (whole-profile number) | SkyBlock | TAKE (cheap, good goalpost) | |
| 1.5 | Class Level (char level → ability points) | Wynn | TAKE | |
| 1.6 | Skill Points (STR/DEX/INT/DEF/AGI) + gear SP requirements | Wynn | TAKE — but maybe 5 stats is a lot on top of skills+abilities? | |
| 1.7 | Level-gated world zones | Wynn | TAKE | ✔ MODIFY — not the spine. Replaced by the zone island chain (7.1). Hub is spawn / social only |
| 1.8 | Profiles (multiple saves per account) | SkyBlock | LATER — public server may not want it | ✔ TAKE — full SkyBlock-style profiles. A swap is a different island and different everything |
| 1.9 | Multiple class slots per account | Wynn | TAKE (replaces 1.8?) | ✔ MODIFY — the profile is the class selector. A new class is a new profile and a new island from zero. Not several classes on one island. Roster and combat-only lock (6.1) still apply |

## 2. SKILLS (unified list — confirm each)

**List lock (2026-09-23):** full SkyBlock-style tree plus extras. Smithing and Exploration stay. Trim later. The exception is 2.5: no shared Combat skill.

| # | Skill | Origin blend | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 2.1 | Farming | both | TAKE | ✔ Kept on the ambitious list |
| 2.2 | Mining | both | TAKE | ✔ Kept on the ambitious list |
| 2.3 | Foraging / Woodcutting | both | TAKE | ✔ Kept on the ambitious list |
| 2.4 | Fishing | both | TAKE | ✔ Kept on the ambitious list |
| 2.5 | Combat (weapon XP, separate from Class Level) | SkyBlock | TAKE | ✔ MODIFY — **no shared Combat skill.** Per-weapon class skills; combat XP goes into the equipped class's weapon skill. Class Level (1.5) stays separate |
| 2.6 | **Smithing** (Wynn ingredient-crafting + SkyBlock reforging, one skill) | Skyy's invention | TAKE — headline feature | ✔ KEEP — do not drop |
| 2.7 | Enchanting | SkyBlock | TAKE | ✔ Kept on the ambitious list |
| 2.8 | Alchemy (potions) | both | TAKE | ✔ Kept on the ambitious list |
| 2.9 | Cooking (separate from Alchemy?) | Wynn | MERGE into Alchemy? or own skill | ✔ TAKE as its own skill for now; trim later if we merge it |
| 2.10 | Taming (pets) | SkyBlock | TAKE | ✔ Kept on the ambitious list |
| 2.11 | Carpentry (furniture + quickcraft unlocks) | SkyBlock | TAKE | ✔ Kept on the ambitious list |
| 2.12 | Exploration (discoveries, quests, caves) | Wynn-ish | TAKE as XP-earning meta skill | ✔ KEEP — do not drop |
| 2.13 | HOTM-style token mini-trees per gathering skill | SkyBlock (generalized) | Mining first, others LATER | ✔ TAKE — tied to the skill. That skill's levels unlock its tree. Not location-locked. Mining can still be built first |
| 2.14 | Dungeoneering as its own skill | SkyBlock | LATER (with dungeons phase) | LATER — not the spine (dungeons are story beats + a capstone, not a skill you must grind) |

## 3. ISLAND LIFE

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 3.1 | Private island (instanced, teleport home) | SkyBlock | TAKE | ✔ Progression home (minions, upgrades, co-op, size tiers) **plus** free creative building. Building is free; progression still lives here. Not creative-only |
| 3.2 | Co-op islands (shared island) | SkyBlock | TAKE — public server social glue | ✔ Multiplayer: players can share and visit each other's private islands. Part of the progression home |
| 3.3 | Minions (offline generators, tiers) | SkyBlock | TAKE | ✔ On the private island. Helpful, **not mandatory** — AFK help, not required to progress |
| 3.4 | Minion upgrades: fuel / storage / compactor | SkyBlock | TAKE | |
| 3.5 | Minion hoppers (auto-sell) | SkyBlock | TAKE — but watch economy inflation on public | |
| 3.6 | Minion slots earned by crafting unique minions | SkyBlock | TAKE | |
| 3.7 | Minion items count toward collections | SkyBlock | TAKE (bazaar-bought never counts) | |
| 3.8 | Garden (dedicated farming island) | SkyBlock | LATER | ✔ TAKE — some farming on the main islands; most farming is in the Garden |
| 3.9 | Island upgrades/size tiers | SkyBlock | TAKE | ✔ Part of the progression home |

## 4. ECONOMY

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 4.1 | Coins as the currency (single currency) | SkyBlock | TAKE — skip Wynn emerald denominations? | |
| 4.2 | Bazaar: instant buy/sell + order book | SkyBlock | TAKE | |
| 4.3 | Auction House + BIN for uniques | SkyBlock | TAKE | |
| 4.4 | Sacks (bulk material storage) | SkyBlock | TAKE — Void Vault is the prototype | ✔ KEEP — Magic Bags / sacks are **core QoL**, not optional later |
| 4.5 | Personal bank + interest + upgrade tiers | SkyBlock | TAKE | |
| 4.6 | NPC shops (sell/buy) | both | TAKE | |
| 4.7 | Wynn emerald denominations (E→EB→LE) | Wynn | SKIP (coins do the job) | |
| 4.8 | Death coin-loss softeners (bank protects; "piggy bank"-style item?) | SkyBlock | DECIDE: does bank shelter coins from the 10–25%? | |
| 4.9 | Trade Market 3-slot limit style listing caps | Wynn | TAKE some cap for anti-flood on public | |

## 5. GEAR & ITEMIZATION

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 5.1 | 7-tier rarity ladder (Common→Divine style) | fused | TAKE | ✔ Core — every item has a rarity |
| 5.2 | Recombobulator-style rarity upgrader | SkyBlock | TAKE (endgame sink) | |
| 5.3 | Identifications (RNG rolled stats on dropped gear + re-roll sink) | Wynn | TAKE | ✔ Core — every item has stats |
| 5.4 | Reforging (prefix via anvil + reforge stones) | SkyBlock | TAKE — folded into Smithing | ✔ Core — reforge swaps bonuses. Still folded into Smithing |
| 5.5 | Both 5.3 AND 5.4 on the same item? | — | DECIDE: drops get IDs, crafted gets reforges? both everywhere? | ✔ Both, on items in general. Stats stay on the item; reforge swaps the bonuses. Not a drops-versus-crafted split |
| 5.6 | Ingredient-based crafting (materials + ingredients → custom stats) | Wynn | TAKE — the Smithing core | |
| 5.7 | Powders (elemental socketables T1–T6) | Wynn | TAKE | ✔ TAKE — powders replace SkyBlock runes |
| 5.8 | Elements (5-element damage/defense matrix) | Wynn | TAKE "elements-lite" v1 | ✔ TAKE Wynn's five. Not elements-lite, and not a swap to Hytale's set (9.3) |
| 5.9 | Enchanting (table + books + anvil + ultimates) | SkyBlock | TAKE | |
| 5.10 | Accessories/talismans + Accessory Bag + Magical Power + tuning | SkyBlock | TAKE | ✔ **Core**, not later-game |
| 5.11 | Set items (bonus for wearing the set) | Wynn | TAKE (cheap, fun) | |
| 5.12 | Durability: only on crafted gear (Wynn) vs all gear vs none | Wynn | DECIDE — pack currently has durability-off mod! | |
| 5.13 | Pets (leveling companions, rarity, pet items) | SkyBlock | TAKE | |
| 5.14 | Wardrobe / Ender-chest / backpacks | SkyBlock | TAKE | |
| 5.15 | Tomes & Aspects (raid-earned class modifiers) | Wynn | LATER (raids phase) | |

## 6. COMBAT & CLASSES

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 6.1 | Archer / Warrior / Mage v1 (locked) — Assassin & Shaman | Wynn | LATER — confirm both wanted eventually | ✔ LOCKED — launch Archer, Warrior, Mage; Assassin and Shaman later. Roster is Wynn's five only (no Berserker). Combat-only lock; gathering stays open. Class choice is a new profile (1.9) |
| 6.2 | Archetypes (3 themed sub-builds per class) | Wynn | v1: 1–2 archetypes per class, 3rd later | |
| 6.3 | Ability tree size: Wynn has 70+ nodes/class | Wynn | ~25 nodes/class v1 — enough? | |
| 6.4 | Mana / intelligence resource for abilities | Wynn | TAKE | |
| 6.5 | SkyBlock stat sheet (Crit Chance/Damage, Ferocity, etc.) | SkyBlock | TAKE — merged with Wynn SP stats (needs a unified stat sheet design) | |
| 6.6 | Healer/Tank dungeon-class variants (SkyBlock Catacombs style) | SkyBlock | SKIP? classes already cover roles | |
| 6.7 | Slayers (spawn-a-boss quest chains + slayer XP) | SkyBlock | TAKE (midgame) | ✔ **Core loop**, not side content. Not the leveling spine (that stays the island chain) |
| 6.8 | Boss altars (summon boss with materials) | Wynn | TAKE (cheap early bosses) | |
| 6.9 | Bestiary (kill collections → small stats) | SkyBlock | TAKE | |

## 7. WORLD & CONTENT

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 7.1 | Hub town + level-gated zones (hand-built, locked) | Wynn | v1 scope: hub + how many zones? (draft: 3) | ✔ MODIFY — hub stays shared spawn / gathering / social. Spine = one floating island per Hytale zone; biomes ramp difficulty across that island; finish it before the next unlocks |
| 7.2 | Quests with XP/item/unlock rewards | Wynn | TAKE — v1 target ~20 quests | |
| 7.3 | Cinematic main-quest arc | Wynn | LATER — v1 side-quests only? | |
| 7.4 | Keyed dungeons in-world + corrupted hard modes | Wynn | TAKE | ✔ MODIFY — story beats woven through the island chain. Extra / corrupted dungeons are side content, not the spine |
| 7.5 | Floor-style endgame dungeon (Catacombs-like) | SkyBlock | LATER (endgame) | ✔ TAKE as the **one** endgame capstone dungeon after the last island |
| 7.6 | Raids (team gauntlets) | Wynn | LATER (P7) | ✔ LATER — **side content**, not the spine |
| 7.7 | Kuudra-style faction raid w/ gear tiers | SkyBlock | SKIP v1 — one raid system is enough? | |
| 7.8 | World Events (dynamic wave-defense) | Wynn | TAKE | |
| 7.9 | Lootrunning (roguelite loot circuit) | Wynn | LATER | |
| 7.10 | The Rift-style weird alt dimension | SkyBlock | SKIP (far future) | |
| 7.11 | Fairy Souls / Discoveries → one collectible system | both | TAKE (name TBD) | |
| 7.12 | Mayor elections (rotating global buffs, player-voted) | SkyBlock | TAKE — great for public server | |
| 7.13 | Seasonal festivals/events | SkyBlock | LATER, but design calendar hooks early | |
| 7.14 | Mounts/horses | both | TAKE (mod patterns exist) | |
| 7.15 | Mob totems | Wynn | SKIP? (world events cover it) | |

## 8. SOCIAL & META

| # | Element | From | Draft call | ☐ DECISION |
|---|---|---|---|---|
| 8.1 | Parties | both | TAKE | ✔ Core loop, together with guilds |
| 8.2 | Guilds: bank, XP, seasons | Wynn | TAKE (later phase) | ✔ TAKE in the **core loop with parties** — not a later phase |
| 8.3 | Guild territory war map | Wynn | LATER — big system, public-server endgame | LATER — territory war stays late; guilds themselves moved up (8.2) |
| 8.4 | Quick Craft v2: craft-from-storage, bulk, recipe book w/ tracking | SkyBlock+Skyy | TAKE — bench-link prototype exists | |
| 8.5 | Leaderboards (skills, collections, slayers) | SkyBlock-ish | TAKE — public server wants these | |
| 8.6 | Chocolate-Factory-style idle minigame | SkyBlock | SKIP | |

## 9. HYTALE CHAPTER 1 / RUNE SYSTEM (new — see master plan Part 4)

| # | Element | Draft call | ☐ DECISION |
|---|---|---|---|
| 9.1 | Build class abilities ON the engine rune system (class + tree = which runes you can equip) instead of spell mods | TAKE — strongly recommended | **OPEN — not locked.** Magic approach waits on how Hytale Chapter 1 handles runes |
| 9.2 | Ability-tree nodes double as modifier-rune unlocks | TAKE | **OPEN** — same thread as 9.1. Not locked |
| 9.3 | Elements: adopt Hytale's native element/reaction set (fire/water/lightning/poison/wind/ice...) instead of Wynn's 5 | TAKE — engine does reactions for free | ✔ MODIFY — gear uses Wynn's five + powders (5.7, 5.8). Do not replace those with Hytale's set. Ability reactions wait on 9.1 |
| 9.4 | Fold rune-crafting into Smithing + collections (wrap official Runeforging when it ships) | TAKE | **OPEN** for Hytale ability-runes / Runeforging (same thread as 9.1). Powders replacing SkyBlock runes is locked at 5.7 |
| 9.5 | Co-op elemental combos (fireball + friend's tornado) as intended gameplay in dungeons/raids | TAKE — encounter design leans into it | OPEN — waits with the magic thread (9.1). Not locked |
| 9.6 | Use Encounter Manager (already in pre-release) for dungeons/slayers/raids/boss altars | TAKE — evaluate in P0 | |
| 9.7 | Goblin-Breach-style regenerating instanced worlds as the lootrun/Rift template | TAKE (later phase) | |
| 9.8 | Build all SkyWynn UI behind an abstraction (NoesisGUI UI rework lands in 1–2 months) | TAKE — protects vault/AH UI | ✔ Abstraction stays for our pages. Inventory screen is the exception (10.22) |
| 9.9 | Hold Smithing bench mechanics loosely until Chapter 2 crafting rework is visible | TAKE | |
| 9.10 | Minions vs Chapter-2 Companions: keep minions = island resource automation; consider building them AS companions with custom jobs when tech lands | DECIDE | |
| 9.11 | Cubic-chunks sky islands (real height/depth) for private islands | DECIDE — cool but young tech | |
| 9.12 | Distribute the SkyWynn client pack via the in-game Mod Browser | TAKE when it supports it | |
| 9.13 | Watch Hypixel's open-sourced minigame server libraries as a possible server-code foundation | TAKE — reassess at P0 | |
| 9.14 | Hardcore mode → future "ironman" SkyWynn profiles | LATER | |
| 9.15 | Machinima cutscenes for main-story quests | LATER (P6) | |

## 10. CLIENT-MOD QoL, MADE NATIVE (from Skyy's Lunar SkyBlock stack — see SkyWynn-QoL-Catalog.md)

| # | Element | Draft call | ☐ DECISION |
|---|---|---|---|
| 10.1 | Equipment/accessory/pet slots visible in the inventory screen | TAKE — day one | WAIT — not on the inventory screen. That screen is the exception (10.22). Show them on our own pages until then |
| 10.2 | Quick-access button rail on every window (storage/wardrobe/craft/AH/bazaar) | TAKE — day one | ✔ On our pages and other windows. Not on the inventory screen (10.22) |
| 10.3 | Slot locking + item protection (server-enforced) | TAKE | |
| 10.4 | Search everywhere (inventory highlight, storage, AH/bazaar w/ history) | TAKE | |
| 10.5 | Sort button on every container | TAKE | |
| 10.6 | Unified storage overlay (all vault/sack pages, one searchable screen) | TAKE — Void Vault heritage | |
| 10.7 | Live prices + full item appraisal in tooltips | TAKE (we own the bazaar data) | |
| 10.8 | Craftable-now list + craft-from-storage + confirm guards (Quickcraft v2 spec) | TAKE | |
| 10.9 | Rarity-tinted slots, slot-text numbers, tooltip cooldown timers | TAKE | |
| 10.10 | Loadouts + wardrobe hot-swap (keybinds) | TAKE | |
| 10.11 | Native profit/drop trackers + item pickup log HUD | TAKE | |
| 10.12 | Fully draggable/scalable player HUD (scoreboard, bars, trackers) | TAKE — generalize /packsettings pattern | |
| 10.13 | Radial quick-action menu (hold key → wheel) | DECIDE — depends on Hytale input support | |
| 10.14 | Recipe browser (item DB + recipes + usages, searchable) | TAKE | |
| 10.15 | Public data API so community client mods can exist (HypixelModAPI lesson) | TAKE (post-launch ok) | |
| 10.16 | Dungeon map + solver-friendly data built in (don't make modders reverse-engineer) | TAKE (dungeons phase) | |
| 10.17 | **LOCKED (Skyy):** F6 hover → smart market search (Bazaar for commodities, AH for uniques), default for all | TAKE — locked | ✔ |
| 10.18 | **LOCKED (Skyy):** F5 hover → recipe ("how to make it"), F7 hover → usages ("what it makes") — keys rebindable | TAKE — locked | ✔ |
| 10.19 | **LOCKED (Skyy):** hotbar-end menu w/ remote Enchanting/Anvil/AH/Bank/Bazaar, each permanently unlocked by its quest | TAKE — locked | ✔ |
| 10.20 | Principle: convenience is earned content, never paid/temporary (anti-Booster-Cookie) | TAKE — locked | ✔ |
| 10.21 | **LOCKED (Skyy):** search/recipe hotkeys on normal rebindable keys, implemented via in-page KeyDown bindings (verified server-side-possible) | TAKE — locked | ✔ |
| 10.22 | **LOCKED (Skyy):** UI build freeze until NoesisGUI rework ships; then: all facility buttons in the inventory screen, hotbar menu only as fallback | TAKE — locked | ✔ MODIFY (batch 2) — best placeholders everywhere else, refined as we go. Skip buttons and custom UI on the **inventory screen** only. F5/F6/F7 and the other ✔ QoL rows stay |
| 10.23 | **LOCKED (Skyy):** Lunar-style HUD editor for our widgets — individually movable/scalable/toggleable, preset bundles that can be split apart | TAKE — locked | ✔ |
| 10.24 | Standalone client-side "Hytale HUD editor" mod (vanilla HUD, works on any server, Mod Browser distribution) | LATER — someday list, good marketing | |
| 10.25 | **LOCKED (Skyy):** map ships with live party-member positions (Wynntils' best trick) — party system and map integrate from day one | TAKE — locked | ✔ |
| 10.26 | **LOCKED (Skyy):** quest nav = compass marker default; on-demand temporary beacon + ground-light/particle trail (BL4 "V" style); fully toggleable. Trigger = Quest Compass item until engine keybinds exist | TAKE — locked | ✔ |
| 10.27 | **LOCKED (Skyy):** party HUD widget — member names + HP + stamina + mana | TAKE — locked | ✔ |
| 10.28 | Voice-acted quest NPCs (Voices-of-Wynn style; AI voice gen makes it cheap) | TAKE — content phase (P6) | |

## 11. WHAT WE ADD (neither game has it — Skyy's "what if anything we are adding")
*Empty on purpose. Ideas so far — add yours:*

| # | Idea | Notes | ☐ DECISION |
|---|---|---|---|
| 11.1 | (Hytale-native hook: use Hytale's own factions/biome identity — goblins, Kweebecs, the Void — instead of copying Wynn provinces?) | Chapter 1 makes goblins + Void the canon threat | |
| 11.2 | (Smithing mastery: signature crafts — put your name on gear you craft, top-smith leaderboard?) | | |
| 11.3 | ... | | |

---
*The 2026-09-23 call locked the ✔ rows and the master-plan phases were re-cut to match. Unmarked rows are still open. Build work that already started is tracked in `HANDOFF.md`; this sheet does not reopen it.*
