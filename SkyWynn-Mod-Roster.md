# SKYWYNN MOD ROSTER — every module we need, and what's buildable today

> **Stale as of 2026-09-22.** Prefer `DESIGN-STATUS.md` and `HANDOFF.md` for what is built, what is locked, and current versions. The tiers and statuses below were not refreshed. One 2026-09-24 addition is recorded at the bottom so it is not only in the newer docs.

*2026-09-22. Each ships standalone-capable (zero external deps, version-first names) and slots into the pack later.
"NOW" = no dependency on the NoesisGUI UI rework, the rune system, Chapter 2 crafting rework, or the hand-built world.*

## Legend
**NOW** = buildable today · **SOON** = needs another NOW-mod first · **WAIT: X** = blocked on engine update X · **CONTENT** = needs world/team

---

## TIER 1 — FOUNDATIONS (the P0 spikes + data cores) — ALL BUILDABLE NOW
| # | Mod | What it is | Depends on | Status |
|---|---|---|---|---|
| 1 | **SkyyHud** | Customizable HUD, widgets, editor, layout codes | — | **NOW — in progress (0.1.3 deployed)** |
| 2 | **SkyySacks** | Auto-collect material sacks, craft-from, sack-of-sacks | — | **NOW — in progress** |
| 3 | **SkyyCoins** | THE economy core: per-player ledger, /balance /pay, NPC sell-value config, death coin-loss, admin grants. **LOCKED (Skyy): death penalty editable in-game via `/deathpenalty 5%` (fixed) or `/deathpenalty 5%-10%` (random roll in range each death)** | — | **NOW — P0 spike, highest priority after Sacks** |
| 4 | **SkyyCollections** | Lifetime per-item gather counters + milestone tracker + UI (Bestiary counts ride along) | — | **NOW** — recipe-LOCKING needs a spike (can we gate recipes per player?), but counting + milestones + UI work today |
| 5 | **SkyyIslands** | Private instanced island per player + /home teleport + co-op invites | — | **NOW — P0 spike #2** (engine instanced worlds; dungeons already instance, so proven-adjacent) |
| 6 | **SkyyRolls** | Reforge/identification engine: RNG stats in ItemStack metadata + reforge anvil UI | — | **NOW — P0 spike #3** (must prove metadata survives save/reload) |
| 7 | **SkyyParty** | Party system: invite/kick/leave, party chat, member data feed (HP/stamina/mana/position) | — | **NOW** — built to FEED the future map + the party HUD widget (your locked integration) |

## TIER 2 — ECONOMY & PROGRESSION (need Tier-1 pieces) — SOON
| # | Mod | What | Depends on | Status |
|---|---|---|---|---|
| 8 | **SkyyBank** | Bank + interest + upgrade tiers + death-loss sheltering (your 4.8 question) | Coins | **SOON** (small, right after Coins) |
| 9 | **SkyyBazaar** | Commodity order book: instant buy/sell + buy/sell orders | Coins, Sacks | **SOON — flagship** |
| 10 | **SkyyAuctions** | Auction House + BIN for uniques | Coins, Rolls (item metadata) | **SOON** |
| 11 | **SkyySkills** | Unified skill list w/ passive XP + level rewards (clean-room; RPGLeveling/MMOSkillTree as reference only) | Coins (rewards) | **NOW-able** — gathering/combat XP events proven by existing mods; start with Mining/Foraging/Farming |
| 12 | **SkyyMenu** | Hotbar-end quick access: Enchanting/Anvil/AH/Bank/Bazaar remote, quest-unlocked | Bank/Bazaar/AH | **SOON** (thin layer once facilities exist) |
| 13 | **SkyyWardrobe** | Gear loadouts + hot-swap | — | **NOW-able**, small; pairs with SkyyHud keybind limits |
| 14 | **SkyyNav** | Quest-nav tech: compass/map marker + on-demand beacon + particle trail (Quest Compass item trigger) | — | **NOW-able as tech demo** with manual waypoints; quests plug in later |
| 15 | **SkyyMinions** | Island minions: placeable generators, tiers, fuel/storage upgrades | Islands (for placement rules), Collections (drops count) | **SOON** — entity+timer patterns proven (Clay Factoria/Resource Chickens refs) |

## TIER 3 — BLOCKED ON ENGINE UPDATES — WAIT (design now, build later)
| # | Mod | What | Blocked on |
|---|---|---|---|
| 16 | **SkyyClasses** | Archer/Warrior/Mage + ability trees as curated rune access | **WAIT: rune system** reaching release (Update 7 waves / Chapter 1) |
| 17 | **SkyySmithing** | Ingredient crafting + reforging as one skill | **WAIT: Chapter 2 crafting rework** (don't over-invest in current benches) |
| 18 | **SkyyStats** | Unified stat sheet (SkyBlock stats × Wynn SP) applied to combat | Partially NOW (data model), full **WAIT: rune/combat APIs** for application |
| 19 | Inventory-screen overhaul (buttons-in-inventory, equipment slots) | Your locked UI preference | **WAIT: NoesisGUI rework** (your build freeze) |
| 20 | **SkyyMap** | ONE-renderer full map + minimap + party + quest layers (BetterMap-class, no double-render lag) | Your call: design-for-integration now, build later; also benefits from cubic-chunk/worldgen dust settling |
| 21 | **SkyySlayers / Dungeons / Raids / World Events** | Boss content stack on Encounter Manager | **WAIT: Chapter 1 in release** (Encounter Manager is pre-release today) |

## TIER 4 — PACK-ERA (need economy+world+team) — CONTENT PHASE
| # | Mod | What |
|---|---|---|
| 22 | **SkyyEnchanting** | SkyBlock-model enchanting (table/books/ultimates) |
| 23 | **SkyyAccessories** | Accessory bag, Magical Power, tuning |
| 24 | **SkyyPets** | Leveling companions |
| 25 | **SkyyQuests** | Quest engine + tracker (uses SkyyNav + engine Objectives system) + voiced NPCs |
| 26 | **SkyyGuilds** | Guilds/territory (PartyPro reference; builds ON SkyyParty) |
| 27 | **SkyyMayors** | Rotating elected global buffs + event calendar |
| 28 | World/zones/hub | The hand-built world itself (build team). Server chain only — solo generation is SkyyWorldGen at the bottom (2026-09-24), not this row |

## Internal (not a mod): **SkyyCore**
Shared code (player-data store, UI doc builder w/ the single-line rules, ledger API, config loader) — **shaded into every jar** per your no-external-deps rule. One codebase, zero runtime deps.

---

## RECOMMENDED BUILD ORDER FROM TODAY
1. **SkyyHud** — finish editor verification (in-game test pending) → v0.2 widgets
2. **SkyySacks** — v0.1 (pool, sweep, UI, 9 sack items)
3. **SkyyCoins** — small, unblocks half the roster
4. **SkyyIslands spike** — the riskiest unknown; fail-fast matters
5. **SkyyRolls spike** — metadata persistence proof
6. **SkyyCollections** — counting + UI
7. **SkyyBank → SkyyBazaar → SkyyAuctions** — the economy chain
8. **SkyySkills + SkyyParty** in parallel with economy
9. Re-evaluate the WAIT tier the moment Chapter 1 / NoesisGUI / runes hit release.

*Everything in Tiers 1–2 is also a legitimately useful standalone public mod — each one is Mod Browser marketing for the server later.*

---

## Added 2026-09-24 (not part of the stale tier list above)

| Mod | What | Status |
|---|---|---|
| **SkyyEconomy** | ONE mod for money (Skyy 2026-09-24): SkyyCoins + SkyyBank + SkyyBazaar + SkyyAuctions (BIN auction house) merged; later NPC shops (set up in game) and item value / networth. `/trade` goes to SkyyEssentials instead. | **Next round** after the separate versions are tested. `SkyyEconomy-Plan.md` |
| **In-game server setup** | Not a mod: every Skyy mod gets an in-game config page under SkyWynn Menu -> Mods (admins), plus big editors (NPC shops, quests, ranks + permissions). | **Planned.** `SkyWynn-Server-Setup-Plan.md` |
| **SkyyWorldGen** (name TBD) | Solo path for the zone island chain. Uses Hytale's World Gen 2 to auto-generate the world as flying islands split by zone. The server chain stays hand-built shared worlds. | **Planned, not started.** Whether World Gen 2 can do this is open research. See `SkyWynn-Decisions.md` change notes, `SkyyIslands-Plan.md`, `DESIGN-STATUS.md`. |

Mods that exist in `HANDOFF.md` and are missing from the 2026-09-22 tables (Profiles, Guilds, Trees, Cooking, Exploration, and later versions of the mods above) are tracked there and in `DESIGN-STATUS.md`, not by rewriting this file.
