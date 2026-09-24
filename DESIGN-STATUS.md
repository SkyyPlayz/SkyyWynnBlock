# SkyWynn - design status (2026-09-24, owner decisions the same day)

A plain-language snapshot for planning sessions. SkyWynn is a Hytale server pack that blends Hypixel SkyBlock (private island, skills,
collections, bags, bazaar, accessories) with Wynncraft (classes, a chain of zone islands, quests, dungeons). It is built as standalone
"Skyy" mods. Goal (Skyy): 100% usable in solo and private multiplayer worlds, and ready for anyone to run a server with.

Where the detail lives: `HANDOFF.md` (the locked decisions + current state), `SkyWynn-Decisions.md`, `SkyWynn-Master-Plan.md`,
the `Skyy*-Plan.md` files, the build specs in `research/`, `PACK.md` (third-party mods), `TEST-CHECKLIST.md`.

## What a player can do (live now or in the next deploy)

**Profiles and classes**
- Design default is **6 profiles** per player (2026-09-24, raised from 4), SkyBlock style. There will be in-game ways to raise that cap;
  the method is not chosen yet. **Code follow-up:** SkyyProfiles 0.1 still caps at 4 (`DEF_MAX_PROFILES = 4`). Do not change the jar in a docs pass.
- Each profile is a full separate save: its own class, island, inventory, coins, bank, bags,
  skills, collections, accessories and skill trees. Creating a profile is where you pick your class (Archer, Warrior or Mage), and it is locked.
- Switching profiles swaps the inventory and sends you to that profile's island; it is crash-safe.
- Classes lock the combat path only: each class can only fight with its own weapons (a popup shows the weapon and why). Gathering is open to all.
- Launch classes in the jar: Archer, Warrior, Mage. Assassin and Shaman are later. **Berserker is back on the roster, status PENDING**
  (owner wants it; details and timing wait on a talk with the builder — not placed before or after Assassin/Shaman).
  **Code follow-up:** SkyyClasses 0.1.4 has no Berserker. 0.1.2+ already set `ALLOW_SWITCH=false` (the paid class switch is gone). Adding Berserker is future code, not a return to the 0.1.1 spike.

**Islands**
- A private island per profile (created on first `/island`), a shared hub, visiting and co-op invites. Visitors can look but not touch.
- Next up: an island settings menu like the Minecraft SkyBlock plugins (per-role permissions, visitors on/off, biome, ...), `/island reset`.

**Skills (level cap 100 each, SkyBlock XP curve, coins on every level)**
- Gathering: Mining, Foraging, Farming (with double drops and small stat perks).
- Acrobatics (mcMMO style): running, jumping, dodging and big survived falls level it; speed, jump height, less fall damage.
- Class weapon skills: Archery, Swordsmanship, Sorcery (combat XP goes to your class's weapon skill; no shared Combat skill).
- Alchemy: brew at the Alchemy Bench; potions last longer as you level.
- Smithing: smelting ore into bars at a furnace (later: reforging and powders).
- Cooking: food you cook carries a Grade from your Cooking level - 2x stronger and longer at level 50, 4x at 100. The Campfire accessory
  is an emergency cook (half XP, 75% of the bonus).
- Exploration: first-time world chests, walking new ground, discovering Hytale's zones; +max Stamina per level; titles; no XP boosters.

**Skill trees (`/tree`)**
- Mining, Foraging, Farming, Cooking, Acrobatics and Exploration trees. Tokens from skill levels unlock nodes, Dust from XP levels them,
  free respec. The Exploration tree is a first draft (most slots "coming later").

**Collections (SkyBlock style, `/collections`)**
- About 100 item collections (logs per wood type, stone, ores, crops, mob drops); tiers pay coins, skill XP and recipe unlocks.
- **Coin-bypass is tiered (2026-09-24):** coins can bypass collections in the early game and the first half of mid game. Toward late game
  those items can no longer be bought or sold (bazaar/market), so that progression is earned. Many items will also have level requirements.
  **Open:** the exact cutoff per collection and tier, and which level type gates an item (skill vs class vs combat level).
  **Code follow-up:** SkyyCollections 0.2 still sells bypass on the older per-curve walls (Bulk through V, Standard through IV, Rare through III,
  Elite never). That is not the new cutoff, and it does not take items off the market. SkyyBazaar 0.1.1 has no late-game sell wall.

**Bags, crafting and economy**
- Magic bags (Mining, Foraging, Farming, Combat) pool matching pickups; `/craft` crafts from inventory + bags with tabs Crafting, Smithing
  (tools, weapons, armor), Farming, Campfire, Furnace, Tannery, Collections and a search box. Real benches also draw from bags.
- Alchemy and Cooking are table-only (their bench accessories were retired); accessories bag with bench accessories and stat talismans.
- Coins, a bank with interest (per profile), a bazaar, item rolls (reforge + stats, shown on the item).

**Social**
- Parties (invite, kick, promote, party chat, a party page) and guilds (ranks, guild chat, guild bank, guild XP from members' skills,
  seasons, a guild page). HUD widgets for both.

**Interface**
- A SkyWynn Menu item (everything in one place, warps, teleports), a customizable HUD (drag, size, colour, bold, italic, glow per widget).

## Decided but not built yet
- **Tree felling pays per log**: today one cut drops the whole tree but pays for 1 log; every felled log will pay XP and count for collections.
- **Tree Feller** perk breaks logs sideways on the same height (Hytale already fells the tree once the base is gone).
- **Double Jump** node in the Acrobatics tree (crouch in mid-air).
- **Player Settings menu**: switch each kind of chat notification on or off.
- **Bags**: smelted bars go in the Mining bag; all bag tabs always shown; bag sizes will come from collections.
- **Exploration backbones**: an island checklist and admin-placed discovery spots, so a server only has to add content.

## Direction: our own content
Eventually every mod in the pack is SkyWynn's own; third-party mods (crossbow tiers, saplings) are stopgaps. A custom gear line is planned: Wynncraft-style weapons (rolled IDs, powders, elements), SkyBlock-style tools (reforges, fortune) and armor - built on the item rolls + tooltip system that works now, and the source of Smithing XP from reforging and powders. We rebuild features ourselves rather than copying other authors' files. Draft plan: `SkyyGear-Plan.md`.

## Later (needs the server / the island chain)
Discovery and secret spots, island arrival, dungeons, Echo Shards (void shards; half = no coin loss when falling into the void, all = creative
flight on your island), island completion, zone hunts, town warps (starter town free, others via quests / scrolls), lootrun camps, map reveal,
cosmetics, Hunting, Fishing, Taming / pets, Dungeoneering, territory war.

**Island chain (2026-09-24).** The spine is unchanged: one floating island per zone. Much of it will be **server-side** (hand-built shared worlds).
For **solo** players, a new mod is planned: **SkyyWorldGen** (name TBD). It would use Hytale's World Gen 2 to auto-generate the world as flying
islands split by zone. Status: planned, not started. Whether World Gen 2 can do that is an open research item.

**Garden is parked.** The dedicated farming island is on the back burner. Farming stays on the main islands (private island and the zone chain) for now.

## Open questions (Skyy + design)
1. **Bags:** should the Mining bag upgrades come from the Cobblestone or the Iron collection? Which collection grows the Foraging, Farming and
   Combat bags? (Today every bag is craftable at a Workbench, so the bag rewards on collection tiers do nothing yet.)
2. **Settings menu:** when someone turns off party invites, teleport requests or private messages - refuse the sender, or just hide it?
   Staff bypass? Anything that should stay always-on?
3. **Tree felling:** felled logs pay full XP? Leaves pay XP? Tree Feller cooldown (5 s suggested)? Two players on one tree? Do double drops
   count for collections? Apple, bamboo and ice trees are missing from the game's own tree lists - count them anyway?
4. **Double Jump:** tier II (replaces Quick Dodge; no tree dodge bonus before Acrobatics 45) or tier III? Double-jump boots as gear for the real
   jump key? Height and stamina numbers.
5. **Campfire accessory:** it gives only the guaranteed Grade (no skill-tree Grade chances or extra-dish perks) - right for an emergency cook?
6. **Islands:** what should visitors be allowed to use by default (today: doors only)? The island settings menu will make it the owner's call.
7. **Exploration:** what else should level it past about level 25 (it is one-time only for now)? The rest of the Exploration tree.
8. **Accessories:** Endurance / Intelligence talismans flat or percent; the accessory power questions in `SkyyAccessories-Plan.md`.
9. **Classes:** Assassin and Shaman design (Shaman's weapons and skill name); the ability system waits on Hytale's Chapter 1 runes.
   **Berserker** is a separate pending item (2026-09-24): the owner wants it back and needs to talk with the builder before any design or
   timing. Do not invent it, and do not assume it ships before or after Assassin/Shaman.
10. **Profile cap:** how does a player raise the cap above the new default of 6? (Method TBD. Code still enforces 4.)
11. **Coin-bypass cutoff:** where, per collection and per tier, does the late-game wall start (no more buy or sell on the bazaar/market)?
    Which level type gates items — skill, class, or combat level?
12. **World Gen 2:** can it auto-generate a world of flying islands split by zone? That research gates SkyyWorldGen. Not started.

## Not yet seen in game (first things to watch in the next test)
Rolls on item tooltips, the HUD glow and colours, Party and Guild widgets, the island starter kit fix, Exploration chests / titles / zones,
the Acrobatics tree nodes, the Campfire tab.
