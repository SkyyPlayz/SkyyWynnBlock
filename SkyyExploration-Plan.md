# SkyyExploration - plan
*Skyy's Exploration call, 2026-09-24. Research: `research/Exploration-Research.md` (option ids A1-D5 and questions Q1-Q9 below refer to its sections 4 and 5).*

Exploration is a SkyySkills skill (its own row) whose XP comes from the SkyyExploration mod. Most discovery content is server-specific
(it needs the island chain, the hub and towns built), so it waits for the server build. What works in single player is built now.

## Build now (single player)

| Id | What | Notes |
|---|---|---|
| per level | **A little max Stamina per level** | Skyy: "for now lets make exploration boost your stamina, a little with each level" |
| B1 | **Coins per level** | Same as the other skills |
| A4 | **World chests**: first open of each world-generated chest gives XP | Player-placed chests never count |
| B2 | **Chest luck**: a small chance per level of an extra roll from a world chest | Depends on A4 |
| A5 | **Map coverage**: small XP per new chunk walked | No XP while flying (/fly, creative flight); teleporting does not block |
| A6 | **Zone discovery**: Hytale's own zones (engine zone data) give XP the first time | Kept per profile (the engine's own list is per account) |
| D3 | **Titles** (start with titles; cosmetics later) | Earned at Exploration milestones |
| trees | **Exploration gets its own skill tree** (Q7 yes); **Acrobatics gets its own tree too** | Exploration tree: the health bonus (B4) lives here; the rest of the Exploration tree is "figure out later" (Skyy) - ship a small first draft. Acrobatics tree: a Stamina upgrade node |

## Next (SkyyExploration 0.2): backbones for server content
Skyy: build the backbone for the island checklist now; the checklist content itself waits for the server. Pack goal: 100% usable solo and in private multiplayer, prepared for server use.
- **Island checklist backbone (C2):** a checklist per island/world, per profile, with a completion % on /explore; entry types: discovery spot, secret spot, world chest, Echo Shard (later), custom; entries defined in a config file + admin commands so a server builder fills it in.
- **Discovery / secret spots backbone (A1/A2):** admin-placed named spots (position + radius + XP + secret flag), banner + sound on first arrival, feeding the checklist. Works on any world, including a private multiplayer world.

## Later (when the server is built)

| Id | What | Skyy's notes |
|---|---|---|
| A1, A2 | Discovery spots + secret spots on every island | Yes, with the server |
| A3 | First arrival on an island | Yes, with the server |
| A7 | First clear of a story dungeon / cave | With the server |
| B3 | Finder sense (compass / HUD hint to undiscovered spots) | "could be cool", build later |
| C1 | **Echo Shards** (fairy-soul style), hand in 5 at a time | Each hand-in: a few more backpack slots. Collecting HALF the shards: an accessory that stops coin loss on death WHEN falling into the void. Collecting ALL: an accessory that grants permanent creative flight, but only on your private island |
| C2 | Island completion % checklist | Liked; server-specific (needs the hub to test properly) |
| C3 | Zone hunt with a finder compass | Liked |
| C4, C5 | Egg hunt, museum | Skip |
| D1 + D2 | Warps | Each island has several towns/cities. The first (starter) town of each island is unlocked for free by discovering it; warps to the other towns come from quests; more obscure locations are unlocked by scrolls from quests or crafting (scroll recipes unlocked by collections) |
| D3 | Cosmetics | Later (titles now) |
| D4 | Lootrun-style camp on 100% islands | Sounds good |
| D5 | Map reveal: POIs appear on the map after discovery | Skyy really likes it |

## Answers (Q1-Q9)

1. **Per profile** for now: Exploration progress is separate per profile. Keep the map, lose the warps (a new profile keeps map knowledge, not warps). May change later.
2. **One-time** sources for now. Skyy will figure out more ways to level Exploration.
3. **No XP boosters** for Exploration XP.
4. **Collectible rewards**: accessory slots (definitely), coins, and bag capacity. Bag capacity needs a slight bag restructure: each bag's MAIN expansion is tied to a collection in its field (e.g. the Mining bag grows per Iron collection tier), and Exploration gives slight extra boosts.
5. **Warps**: the starter town of each island is free by finding it; warps to the other towns are tied to quests.
6. **Echo Shards** (name kept). Lore: powerful shards of the void, scattered across the lands when the void ripped the world apart and split it into floating islands. You can still hear them ringing with the echoes of the calamity.
7. **Yes**, Exploration gets its own skill tree.
8. **No /fly on the main exploration islands**; teleporting does not block Exploration XP.
9. **Shared worlds** like the SkyBlock hub and the Wynncraft world; only your own island is private.

## Future project (Skyy)
Use Hytale's world gen 2 system to make a mod that generates the world as a series of floating islands.
