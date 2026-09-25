# SkyWynn - design status (updated 2026-09-25 after the overnight build rounds)

A plain-language snapshot for planning sessions. SkyWynn is a Hytale server pack that blends Hypixel SkyBlock (private island, skills,
collections, bags, bazaar, accessories) with Wynncraft (classes, a chain of zone islands, quests, dungeons). It is built as standalone
"Skyy" mods. Goal (Skyy): 100% usable in solo and private multiplayer worlds, and ready for anyone to run a server with.

Where the detail lives: `HANDOFF.md` (the locked decisions + current state), `SkyWynn-Decisions.md`, `SkyWynn-Master-Plan.md`,
the `Skyy*-Plan.md` files, the build specs in `research/`, `PACK.md` (third-party mods), `TEST-CHECKLIST.md`.
**Every choice the builds made for Skyy (with the live default): `OPEN-QUESTIONS.md`.**

## What a player can do (live now or in the next deploy)

**Profiles and classes**
- Design default is **6 profiles** per player (2026-09-24, raised from 4), SkyBlock style. There will be in-game ways to raise that cap;
  the method is not chosen yet. **Code follow-up:** SkyyProfiles 0.1 still caps at 4 (`DEF_MAX_PROFILES = 4`). Do not change the jar in a docs pass.
- Each profile is a full separate save: its own class, island, inventory, coins, bank, bags,
  skills, collections, accessories and skill trees. Creating a profile is where you pick your class (Archer, Warrior or Mage), and it is locked.
- Switching profiles swaps the inventory and sends you to that profile's island; it is crash-safe.
- Classes lock the combat path only: each class can only fight with its own weapons (a popup shows the weapon and why). Gathering is open to all.
- Classes: Archer, Warrior, Mage, and (locked 2026-09-25, being built) **Berserker** (Fury: axes, battleaxes, maces, clubs) and **Priest**
  (an AoE healing support class; Divinity: wands and spellbooks; its weapon hits heal the party until real spells exist; much of it custom
  later). Assassin and Shaman later. Every class gets a kit with its basic weapon when you pick it. `ALLOW_SWITCH=false` (no paid switch).

**Islands**
- A private island per profile (created on first `/island`), a shared hub, visiting. Visitors can look but not touch (doors and seats work).
- Co-op (live 2026-09-25): `/island invite` makes a friend a co-op member (their `/island` goes to your island); Trusted players may only
  build; the Owner keeps kick and disband; island Admins change settings. `/island menu` has the members, a permission grid per role,
  visit modes (open / closed / co-op only), bans, and `/island reset` (3 confirms, 24 h cooldown).

**Skills (level cap 100 each, SkyBlock XP curve, coins on every level)**
- Gathering: Mining, Foraging, Farming (with double drops and small stat perks).
- Acrobatics (mcMMO style): running, jumping, dodging and big survived falls level it; speed, jump height, less fall damage.
- Class weapon skills: Archery, Swordsmanship, Sorcery (combat XP goes to your class's weapon skill; no shared Combat skill).
- Alchemy: brew at the Alchemy Bench; potions last longer as you level.
- Smithing: smelting ore into bars at a furnace (later: reforging and powders). A higher Smithing level will also raise a **smithing rarity** stat (better chance to craft a higher rarity). That stat is not in the live skill.
- Cooking: food you cook carries a Grade from your Cooking level - 2x stronger and longer at level 50, 4x at 100. The Campfire accessory
  is an emergency cook (half XP, 75% of the bonus).
- Exploration: first-time world chests, walking new ground, discovering Hytale's zones; +max Stamina per level; titles; no XP boosters.
  Live 2026-09-25: admin-placed discovery and secret spots (banner, sound, XP) and an island checklist with a completion %.
- Felled trees pay for every log (XP, double drops, collections). Party members nearby share 50% of combat XP. Double Jump (crouch in mid-air).

**Skill trees (`/tree`)**
- Mining, Foraging, Farming, Cooking, Acrobatics and Exploration trees. Tokens from skill levels unlock nodes, Dust from XP levels them,
  free respec. The Exploration tree is a first draft (most slots "coming later").

**Collections (SkyBlock style, `/collections`)**
- About 100 item collections (logs per wood type, stone, ores, crops, mob drops); tiers pay coins, skill XP and recipe unlocks.
- **Coin-bypass is tiered (2026-09-24):** coins can bypass collections in the early game and the first half of mid game. Toward late game
  those items can no longer be bought or sold (bazaar/market), so that progression is earned. Every gear item has a level requirement
  (which level type is still open).
  **Open:** the exact cutoff per collection and tier, and which level type gates an item (skill vs class vs combat level).
  **Code follow-up:** SkyyCollections 0.2 still sells bypass on the older per-curve walls (Bulk through V, Standard through IV, Rare through III,
  Elite never). That is not the new cutoff, and it does not take items off the market. SkyyBazaar 0.1.1 has no late-game sell wall.

**Bags, crafting and economy**
- Magic bags (Mining, Foraging, Farming, Combat, and Smithing for bars, leather and hides) pool matching pickups; `/craft` crafts from inventory + bags with tabs Crafting, Smithing
  (tools, weapons, armor), Farming, Campfire, Furnace, Tannery, Collections and a search box. Real benches also draw from bags.
- Alchemy and Cooking are table-only (their bench accessories were retired); accessories bag with bench accessories and stat talismans.
- Coins, a bank with interest (per profile, `/bank` page), a bazaar (custom amounts), item rolls shown SkyBlock style
  ("Damage: 11-48 (+24%)") with a `/reforge` anvil page.
- Auction House (live 2026-09-25): Buy It Now only (bids later), `/ah` with categories, search, sort, rarity; Hypixel fees; listings belong to
  the profile that made them. `/vault`: item storage shared by all your profiles. `/trade`: two-player trade window with coins.
- **SkyyEconomy (Skyy, 2026-09-24):** Coins, Bank, Bazaar and the Auction House become one mod in the next round; later NPC shops (set up
  in game) and an item value / networth tool. `/trade` goes in SkyyEssentials. Plan: `SkyyEconomy-Plan.md`.

**Social**
- Parties (invite, kick, promote, party chat, a party page, shared combat XP) and guilds (Leader / Admin / Member, guild chat, guild bank
  with per-rank daily withdraw limits and a full log, guild XP from members' skills, seasons, a guild page). HUD widgets for both.
- Ranks (live 2026-09-25, SkyyRanks): server ranks made in game, with permissions and a chat prefix `[Rank] [Title] Name`.

**Interface**
- A SkyWynn Menu item (everything in one place, warps, teleports, Island menu, Bank, Vault, Reforge, Party, Guild, Auction House),
  a customizable HUD (drag, size, colour, bold, italic, glow per widget).
- Player Settings (`/settings`): switch each kind of chat message on or off (the invite / teleport / message switches wait for Skyy).
- Server Setup (admins, live 2026-09-25): SkyWynn Menu -> Server Setup lists every Skyy mod; a mod that has adopted the new config kit gets
  an in-game settings page with a change log, undo, file history and export/import codes.

## Decided but not built yet
- **Every mod's settings in game**: DONE 2026-09-25 for 18 mods (Server Setup pages); Coins, Bank, Bazaar and Auctions get theirs as SkyyEconomy.
- **SkyyEconomy**: Coins + Bank + Bazaar + Auction House as one mod, after Skyy tests the separate versions; then NPC shops set up in game.
- **Bags**: bag sizes will come from collections (waits on the Cobblestone-vs-Iron answer).
- **Big in-game editors**: NPC shops (SkyyEconomy 0.2), island template, warps page, NPC quests (future SkyyQuests).
- **Gear (`SkyyGear-Plan.md`, locked 2026-09-24, not built):** every gear item has a level requirement and a rarity tier. Higher Smithing = higher smithing rarity = better odds of a higher-rarity craft. Higher rarity = better reforge rolls. Mobs drop unidentified weapons and armor. Combat armor and weapons copy Wynncraft. Gathering gear is SkyBlock-style farming and foraging sets (mining likely the same). Wardrobe + loadouts save and quick-swap a set. A loadout saves armor, the Equipment bar (necklace, cloak, ring, belt; working name Equipment, name not final), and the selected Accessory Power buff. Pets join once pets exist. Placeholders are fine; nothing on the inventory screen. Identify is a `/identify` menu for now and an NPC later. It costs coins, scaling with rarity and level (formula open). Mob drops can be any rarity. Some sets are drop-only and some are craft-only. Sets have set bonuses. Accessory Power: each accessory has its own buff and adds power; total power feeds one selectable buff (Warrior and Elementalist are examples; the full list and numbers are open). **Stats (change note 9):** the five Wynn skill points are not the gear sheet. Combat, defence, and mana are locked in `SkyyGear-Plan.md`. Fortune from the earlier mix was not re-opened. The catalog's next blank table is Movement. Class skill trees are Borderlands-style research (Borderlands 4), not designed. SkyyRolls 0.1.3 still shows rolls immediately. None of the identify step, the Equipment bar, set bonuses, or the selectable Power buff is in a jar.

## Direction: everything editable in game (Skyy, 2026-09-24)
Everything a server owner might change should be editable in game: SkyWynn Menu -> Mods (admins) -> click a mod -> its config page, plus
editors for NPC shops, NPC quests, ranks and permissions, the island template and the market. Files stay and always match the game.
Plan: `SkyWynn-Server-Setup-Plan.md`.

## Direction: our own content
Eventually every mod in the pack is SkyWynn's own; third-party mods (crossbow tiers, saplings) are stopgaps. The gear line is locked in `SkyyGear-Plan.md` (2026-09-24): combat armor and weapons copy Wynncraft (unidentified drops, level + rarity on every piece), gathering armor is SkyBlock-style farming and foraging sets (mining likely the same), and Smithing level feeds smithing rarity. It still sits on the item rolls + tooltip system that works now. Reforging and powders remain later Smithing XP. We rebuild features ourselves rather than copying other authors' files.

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
8. **Accessories:** Endurance / Intelligence talismans flat or percent. The shape of Accessory Power is locked (own buff plus one selectable buff that scales with total power). Still open in `SkyyAccessories-Plan.md`: the full buff list, the numbers, and the older draft questions (AP-by-rarity, tuning, slot prices).
9. **Classes:** Assassin and Shaman design (Shaman gets a custom weapon; its skill name); the ability system waits on Hytale's Chapter 1
   runes. Berserker and Priest were locked 2026-09-25 (the Priest's real AoE heals come with the spell system).
10. **Profile cap:** how does a player raise the cap above the new default of 6? (Method TBD. SkyyProfiles 0.1 still enforces 4; 0.1.1 in the adoption round raises it to 6.)
11. **Coin-bypass cutoff:** where, per collection and per tier, does the late-game wall start (no more buy or sell on the bazaar/market)?
    Which level type gates items — skill, class, or combat level?
12. **World Gen 2:** can it auto-generate a world of flying islands split by zone? That research gates SkyyWorldGen. Not started.
13. **Gear (open):** which level type gates a gear item (skill, class, or combat)? Exact rarity names and colours (Wynn's list vs SkyyRolls Common..Legendary)? The Equipment bar's final name? The identify cost formula (coins that scale with rarity and level are locked)? Powder slots and how powders drop? Bazaar vs auction house for rolled items? Combat, defence, and mana are marked in `SkyyGear-Stat-Catalog.md` (change note 9). The next blank table is Movement, then gathering, loot, powers, and Major IDs. Still open inside that pass: per-element main-attack and spell % (leaning skip), Reflection, life-steal numbers, magic-using classes for Mana Regen, and the amounts for Overall Level and skill upgrades. The SkyWynn Accessory Power buff list and its numbers stay open. The Hypixel list in the catalog is research.
14. **Class skill trees (open research):** Borderlands-style, not a straight line. Read the Borderlands 4 notes in `SkyyGear-Plan.md` (three trees, row gates, branches and capstones, respec). Do not design SkyWynn trees yet. Class roles, including a later Priest, are also open.

## Not yet seen in game (first things to watch in the next test)
Everything from 2026-09-24 22:53 on (TEST-CHECKLIST sections BETA ROUND 1, SkyyAuctions 0.1, Round 2, Round 3): vault, reforge page,
island co-op and menu, guild limits, felled-tree XP, double jump, party XP, /trade, discovery spots, auction house, Settings, Server Setup, ranks.
