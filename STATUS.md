# SkyWynn - STATUS (big picture for any agent; current to 2026-10-14 ~13:00 MDT)

Read this first if you only have the repo. It says where the pack is, where it is going, what is decided and what still needs work. Details
live in the linked files; this page is only the map. Update it when a system changes state (see section f).

Core gameplay loop, as a clickable diagram (stages, how they feed each other, mods + live versions): https://claude.ai/artifact/GgipsncNYu15wgTLcn2gUX (private - Skyy shares it).

## a) What SkyWynn is and how the repo works

SkyWynn is Skyy's (GitHub SkyyPlayz, they/them) public Hytale server pack: about 35 standalone `Skyy*` mods plus a few third-party mods,
blending Hypixel SkyBlock (islands, skills, collections, bags, bazaar, minions-style progression) and Wynncraft (classes, levelled gear,
abilities, zones). Goal: solo + private worlds first, server-ready backbones, and in the end every mod is our own; some mods ship alone on
CurseForge later. The game is **Hytale 0.7.1**; Skyy tests in their own world ("HUD mod"). The repo is PUBLIC: it holds build scripts, specs
and docs, never game files or built jars.

How to navigate: [PROJECT-RULES.md](PROJECT-RULES.md) (the rules), [INDEX.md](INDEX.md) (where every file is + search recipes),
[HANDOFF.md](HANDOFF.md) (versions, rollback floors, UI + command rules), [RESUME.md](RESUME.md) (today's state + next steps),
[ARCHITECTURE.md](ARCHITECTURE.md) (one line per mod, build / deploy / CI), [DECISIONS.md](DECISIONS.md) (index of locked decisions),
[docs/answered/README.md](docs/answered/README.md) (every Skyy answer, word for word), [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md),
[TEST-CHECKLIST.md](TEST-CHECKLIST.md), [ROADMAP.md](ROADMAP.md), [PACK.md](PACK.md) (third-party mods). Live versions = the SET in
`tools/deploy_set.py` (same table in HANDOFF section 1).

## b) Where it is at (system by system)

State words: **live+tested** (Skyy saw it work), **live+untested** (deployed, waiting for Skyy), **built not deployed**, **spec only**, **idea**.
"Skyy-tested?" comes from [TEST-CHECKLIST.md](TEST-CHECKLIST.md) (numbers = its entries) and [docs/tests/README.md](docs/tests/README.md).
Versions below are the SET at 2026-10-14 12:42 deploy; three more rounds (Gear 0.3.5 + Fishing 0.1.5 + Merchants 0.1.4, Classes 0.1.23 +
Trees 0.3.8) are built or building and not in the SET yet (see section c).

| System | Mods + live version | State | Skyy-tested? | Main doc |
|---|---|---|---|---|
| Skills + XP | Skills 0.4.37, Collections 0.2.14 (XP routing), Hud 0.3.23 (XP flash) | live+untested (new: perfect dodge, Fishing / Ranching / Orchard skills 0.4.37); older curves, Mana, Acrobatics seen working | partly (0.4.12-0.4.16 seen; 63, 72, 101 open) | [research/Overall-Level-Spec.md](research/Overall-Level-Spec.md), [docs/answered/skills.md](docs/answered/skills.md) |
| Classes + abilities | Classes 0.1.22, Skills 0.4.37 (Mana), Armory 0.1.25 (class weapons), AbilityProbe 0.1 | 7 classes playable (Warrior, Archer, Mage, Priest, Berserker, Monk, Assassin); Spellblade = draft. ABILITIES live+untested for **Mage + Priest only**: rune keys (Ability 2 / 3 + crouch), `/cast` backup, ability panel on the right of the class tree, ability levels (max 25), modifiers (slots unlock at ability Lv 2/4/6/8/10). Warrior / Berserker / Archer / Monk / Assassin abilities queued | no (11, 65, 95; rune keys U1-U10 unproven) | [research/classes/README.md](research/classes/README.md), [research/Ability-Framework-Mage-Spec.md](research/Ability-Framework-Mage-Spec.md), [docs/answered/classes.md](docs/answered/classes.md) |
| Skill trees + class trees | Trees 0.3.7 | live+untested (class path trees ON, free respec, ability + modifier nodes; 6 nodes still waiting: Mage PA4 / PC2, Priest PA2 / PB2); gathering trees seen working | partly (31, 42, 95) | [research/Skill-Trees-Spec.md](research/Skill-Trees-Spec.md), [research/Skill-Trees-2-Spec.md](research/Skill-Trees-2-Spec.md) |
| Gear, lifelong tools, tier gate, Sigils, gathering armor | Gear 0.3.4, Armory 0.1.25, Collections 0.2.14, Islands 0.5.8 | live+untested: rarity, levels, identify, reforge, Anvil tabs; lifelong tools (/pickaxe etc., exact-tool summon), tool tier gate (1 tier up 2.5x hits, 2 up 10x, 3+ refused), harvest gate (crops 2+ tiers above refused), Sigils + armor levels + hoe area (0.3.4). Gathering armor: Mining sets done; Foraging / Farming sets not built | mostly no (6-10, 77, 83, 85, 86, 88, 97) | [SkyyGear-Plan.md](SkyyGear-Plan.md) (Skyy's, never edit), [research/Tool-Levels-Spec.md](research/Tool-Levels-Spec.md), [research/Gathering-Progression-Spec.md](research/Gathering-Progression-Spec.md), [docs/answered/gear.md](docs/answered/gear.md) |
| Accessories | Accessories 0.5.13 | live+tested (Accessory Bag, Lantern recipes, booster accessories; tab order untested) | yes, tab order 72 open | [research/Accessory-Table-Spec.md](research/Accessory-Table-Spec.md), [research/Booster-Accessories-Spec.md](research/Booster-Accessories-Spec.md) |
| Bags / Void / auto-pickup | Sacks 0.8.4 (Magic Bags + Pocket Dimension "Void"), Mobs 0.1.8 | live+untested: Void, auto-pickup of blocks / mob drops / F-harvest into Void; older bags seen working | partly (70, 78, 84) | [research/Bags-v2-Spec.md](research/Bags-v2-Spec.md), [docs/answered/bags.md](docs/answered/bags.md) |
| Collections | Collections 0.2.14 | live+untested (CRAFT buttons, locked recipes, Enchanted tier III + Compressing tab, shard credit); core seen working | partly (19, 71, 97, 100) | [research/Collections-Spec.md](research/Collections-Spec.md) |
| Economy: coins, bank, bazaar, AH, merchants, trade | Coins 0.1.7, Bank 0.1.11, Bazaar 0.1.11, Auctions 0.1.5, Merchants 0.1.3, Essentials 0.1.9 (/trade) | live; coins + bank seen working, merchants shop + buying seen working 2026-10-10, Bazaar / AH search + categories and `/ahadmin closeall` untested. NPC shops = spec only; SkyyEconomy merge parked | partly (16, 21, 37, 90) | [research/Economy-Audit-1014.md](research/Economy-Audit-1014.md), [research/Auction-House-Spec.md](research/Auction-House-Spec.md), [research/Trade-Spec.md](research/Trade-Spec.md), [docs/answered/economy.md](docs/answered/economy.md) |
| Islands + shards + totems | Islands 0.5.8, Shards 0.2, Menu 0.3.23 (Shards tile) | Islands live (private, co-op, visitors, settings). Shards: Farming shard + hub + 6 slots + Wheat island + Harvest Spirit (0.1) and totems / workers / rank / Collect (0.2) live+untested; the other five shards (Mining, Foraging, Orchard, Ranching, Combat) not built | islands yes; shards no (94, 100) | [research/Gathering-Shards-Spec.md](research/Gathering-Shards-Spec.md), [research/Island-Settings-Spec.md](research/Island-Settings-Spec.md) |
| Rebirth (R1-R10) | Rebirth 0.3 (feature switched OFF), Skills 0.4.36+, Coins 0.1.7, Bank 0.1.11, Profiles 0.1.13 | R1 counter + caps, R2 Nexus page, R3 transactional rebirth (resets skills / purse / bank, level coins x0.8 per rebirth, bank bonus), R4 Continue + AH / Bazaar close, R8 rebirth tree (50 points) built and live; R5 tree + ability levels, R6 class tree, R7 gear reset (in Gear 0.3.5, running), R9 collection ranks (in Shards 0.2) / R10 switch-on test still open | no (87, 93, 99) | [research/cloud/Rebirth-Spec.md](research/cloud/Rebirth-Spec.md) (FINAL, build order in section 6) |
| Quests + NPCs + markers | Quests 0.3, Hud 0.3.23 (quest widget) | live+untested: tutorial line, Quest Tracker, skip + optional tasks, class gear rewards, hub areas, co-op, Quest Board + Marlow NPCs, daily jobs, markers | partly (71, 76, 96; 4 hub spots to set by Skyy) | [research/cloud/SkyyQuests-Spec.md](research/cloud/SkyyQuests-Spec.md), [research/SkyyQuests-Tutorial-Spec.md](research/SkyyQuests-Tutorial-Spec.md) |
| Exploration, Lost Loot, airdrops | Exploration 0.2.8 | live+untested: Exploration skill, map chunks, island checklist; Lost Loot piles (4 tiers), reveal page, supply drops | partly (45, 92) | [research/Exploration-0.2-Spec.md](research/Exploration-0.2-Spec.md), [research/Exploration-Build-Spec.md](research/Exploration-Build-Spec.md) |
| Mobs + mob levels | Mobs 0.1.8 (+ Better Mob Expansion, OFF) | live; level plates, curves, level gap seen working; 280 roles on 0.7; zone difficulty tables | yes (0.1 - 0.1.2), curve 35 open | [research/Mob-Levels-Plan.md](research/Mob-Levels-Plan.md), [research/Mob-Curve-Spec.md](research/Mob-Curve-Spec.md) |
| Pets | Pets 0.2.5 | live+untested: slot pets phase 1 (pet slot full buffs, summon slot 50%), visible followers, /pets, 30 launch kinds, owner key for pet kills. Fighting pets (0.4), mounts, flying / water pets, eggs, Stable not built | partly (51, 52, 73, 89) | [research/Pets-Roster.md](research/Pets-Roster.md), [research/cloud/Pets-Spec.md](research/cloud/Pets-Spec.md), [docs/answered/pets.md](docs/answered/pets.md) |
| Fishing | Fishing 0.1.4 (HyFishing OFF) | live+untested: stage 1 (Fishing Bench, rods + reels T0-T2, cast / bite / fight HUD, Zone 1 fish); stage 2 (lifelong pole, more fish, Fishing tree) not built; 0.1.5 pole in the running Gear round | partly (20, 101) | [research/cloud/SkyyFishing-Spec-Draft.md](research/cloud/SkyyFishing-Spec-Draft.md) |
| Cooking | Cooking 0.1.6 | live+tested (food Grade, XP by craft difficulty); Cooking Skill spec has further phases | yes (41) | [research/Cooking-Skill-Spec.md](research/Cooking-Skill-Spec.md) |
| World gen, zones, hubs | WorldGen 0.5.1 (/zone 1 test island), Menu 0.3.23 (hubs), Islands 0.5.8 (/hub) | Zone 1 test island + 0.7 port live; real Zone 1 town + the zone archipelago not built (specs + probe results); menu hubs live | WorldGen no (5, 62) | [research/SkyyWorldGen-Plan.md](research/SkyyWorldGen-Plan.md), [research/Zone-1-Town-Build-Plan.md](research/Zone-1-Town-Build-Plan.md), [research/Hubs-Spec.md](research/Hubs-Spec.md), [research/cloud/Zone-Archipelago-Spec.md](research/cloud/Zone-Archipelago-Spec.md) |
| HUD, menu, settings, admin page | Hud 0.3.23, Menu 0.3.23, UiProbe 0.6 / UiProbeB 0.5 | live+untested: HUD editor, notification feed, per-player message routes, SkyWynn Menu (layout D), player Settings (Messages tab), Server Setup (all mods editable in game), NEW Admin page (`/modconfig admin`, 4 tabs, confirm buttons). Sky Window UI kit blocked on Skyy's `/skyprobe kit` | partly (66, 69, 80, 81, 98) | [research/Settings-Spec.md](research/Settings-Spec.md), [research/Server-Setup-Spec.md](research/Server-Setup-Spec.md), [research/Admin-Page-Plan.md](research/Admin-Page-Plan.md), [research/Vanilla-UI-Style-Guide.md](research/Vanilla-UI-Style-Guide.md) |
| Profiles, wardrobe, vault | Profiles 0.1.13, Wardrobe 0.2.1, Vault 0.1.6 | live+untested: profiles = full saves (cap 6, rename, delete + 6 h undo), wardrobe loadouts (armor + hotbar + pet + abilities), Vault pages + lifelong-tool fetch hook; Requip / Smithing pages in Gear | partly (32, 55, 58, 74, 91) | [research/cloud/Wardrobe-Spec.md](research/cloud/Wardrobe-Spec.md), [research/Requip-Smithing-Spec.md](research/Requip-Smithing-Spec.md), [docs/answered/social.md](docs/answered/social.md) |
| Party, guilds, ranks | Party 0.1.7, Guilds 0.1.7, Ranks 0.1.1 | live; guild bank refunds + TPA button untested; guild games = spec only | partly (46, 47) | [research/Guild-Games.md](research/Guild-Games.md), [docs/plans/SkyyGuilds-Plan.md](docs/plans/SkyyGuilds-Plan.md) |
| Pack mods | see [PACK.md](PACK.md) | ON: More Crossbow Tiers, Dynamic Seasons 7.0.2, Perfect Parries 0.9.7, BetterMap 1.3.9, NoCube's Orchard, Multitools (changed at runtime by Gear), MoreTotems (folded in part). OFF (broken on 0.7): Saplings From Trees, TheArmory, HyFishing, Better Mob Expansion | seasons / parries / map 82 open | [PACK.md](PACK.md), [research/Mods-Folder-Survey.md](research/Mods-Folder-Survey.md) |
| Not started (specs / ideas) | - | Slayers, minions, dungeons + capstone, events, gems, upgrade ladders, inventory buttons / offhand, NPC shops, Tab / prestige economy, Shaman class, dragon pets | - | [ROADMAP.md](ROADMAP.md) "Later", [research/cloud/Slayers-Spec.md](research/cloud/Slayers-Spec.md), [docs/plans/SkyyDungeons-Plan.md](docs/plans/SkyyDungeons-Plan.md), [research/Gems-Ideas.md](research/Gems-Ideas.md) |

Today (2026-10-14) about 30 mod versions were deployed in 5 deploy batches (06:00, 06:26, 08:35, 11:04, 12:42; log lines in
[docs/log/2026-10.md](docs/log/2026-10.md)); nothing from today's batches has been played yet. Skyy also owes: run `/aprobe` and
`/skyprobe kit`, set the 4 quest hub spots, test checklist entries 72-101, send Grok video notes.

## c) Where it is going (in order)

1. **Land the running rounds** (RESUME "START HERE"): gear5 (Gear 0.3.5 + Fishing 0.1.5 + Merchants 0.1.4: Vault summon for lifelong tools,
   identify reveal, lifelong pole, rebirth R7 gear reset, Sigils never in shops); classes2 (Classes 0.1.23 + Trees 0.3.8: Monk + Assassin
   abilities + R5 / R6 rebirth parts). Each deploys only with the game closed.
2. **Class ability batch** (queued): Warrior + Berserker + Archer abilities (same framework as Mage / Priest), then the 6 waiting tree nodes
   and the Priest Elemental Bubble. Specs: [research/classes/README.md](research/classes/README.md), [research/cloud/Class-Ability-Engine-Spec.md](research/cloud/Class-Ability-Engine-Spec.md).
3. **Shards phase 7**: Mining / Foraging / Orchard / Ranching / Combat shards ([research/Gathering-Shards-Spec.md](research/Gathering-Shards-Spec.md) section 11).
4. **Rebirth R10**: switch-on test and release of the feature, after Skyy has seen the Nexus tooltip ([research/cloud/Rebirth-Spec.md](research/cloud/Rebirth-Spec.md)).
5. **Sound pass** ([research/Sound-Pass-Plan.md](research/Sound-Pass-Plan.md)) and **load test tool** ([research/Load-Test-Plan.md](research/Load-Test-Plan.md)).
6. **Sky Window UI kit** into `tools/skyyui.py` - blocked on Skyy's `/skyprobe kit`; restyle menus after it ([research/Hubs-Spec.md](research/Hubs-Spec.md)).
7. **Ability rune keys proven** by Skyy's first Mage play + log scan (U1-U10 in [research/Ability-Framework-Mage-Spec.md](research/Ability-Framework-Mage-Spec.md)).
8. **Open build phases in older specs:** Gathering ladder phases C-G (Foraging / Mining / Farming armor, farming gates, extras) in
   [research/Gathering-Progression-Spec.md](research/Gathering-Progression-Spec.md); Fishing stage 2; Pets phases 3-8 (fighting pets / SkyyPets 0.4,
   eggs, mounts) in [research/Pets-Roster.md](research/Pets-Roster.md); Zone 1 town P0-P4 ([research/Zone-1-Town-Build-Plan.md](research/Zone-1-Town-Build-Plan.md)); NPC shops
   ([research/cloud/NPC-Shops-Spec.md](research/cloud/NPC-Shops-Spec.md)); Slayers; Quests Zone 1 line ([research/cloud/SkyyQuests-Zone1-Spec.md](research/cloud/SkyyQuests-Zone1-Spec.md)).
9. **Architecture merge** into about 10 jars, LAST and alone ([research/Architecture-Spec.md](research/Architecture-Spec.md)); fold MIT mods (Multitools, Reforged
   Weapons, MoreTotems Water Totem, BetterBiomes, More Mounts) with credit.
10. **Release**: Skyy's call on edited vanilla JSONs + third-party permissions ([research/Release-Packaging-Plan.md](research/Release-Packaging-Plan.md)), then `tools/release_pack.py`;
    Pocket Dimension release kit first ([research/cloud/PocketDimension-Release-Kit.md](research/cloud/PocketDimension-Release-Kit.md)).
11. **Parked specs**: gems, inventory buttons / offhand ([research/Inventory-Offhand-0.7.md](research/Inventory-Offhand-0.7.md)), upgrade ladders ([research/cloud/Upgrade-Ladders-Spec.md](research/cloud/Upgrade-Ladders-Spec.md)),
    pet eggs v2, guide fairy, Structure mods ([research/Structure-Mods-Survey.md](research/Structure-Mods-Survey.md)), recheck of the 4 mods broken on 0.7 (after 2026-10-19 build our own).

The long-range phase table is [ROADMAP.md](ROADMAP.md) (P0-P7).

## d) What is decided (one line per area)

Newest line in `docs/answered/<topic>.md` wins. [DECISIONS.md](DECISIONS.md) indexes the big ones by date.

| Area | Locked in short | Words |
|---|---|---|
| Project / process | public repo; solo + private worlds first; every mod ends up our own; check for an existing mod before building; no duplicates between mods; Claude merges its own PRs; smoke tests on a world copy | [project.md](docs/answered/project.md) |
| Classes + abilities | 7 classes (Spellblade draft); each levels its own weapon skill; our own runes + modifiers controlled in the class tree; ability max level 25; modifier slots at Lv 2/4/6/8/10; Mage + Priest first; panel on the right; Ability 2 / 3 + crouch keys (no client mods) | [classes.md](docs/answered/classes.md) |
| Gear | rarity, item levels, identify, reforge level-up, lifelong tools, tool tier gate, harvest gate (crops 2+ tiers above refused, hands = Crude), Sigils (Mythic Sigil stays, rare Zone 4 boss drop), Light armor only from The Armory pool later | [gear.md](docs/answered/gear.md) |
| Skills + rebirth | curves, Mana, Acrobatics, Cooking, Smithing; skill trees; rebirth FINAL (16 answers; levels above 100 do not count for Overall Level / Mana / leaderboards) | [skills.md](docs/answered/skills.md), [research/cloud/Rebirth-Spec.md](research/cloud/Rebirth-Spec.md) |
| Economy | coins never buy tiers / recipes / bags; bank interest once a day (2 / 1 / 0.5%); rebirth coin factor 0.8; block /pay and AH buys between profiles of one account; Bazaar price x2 per tier | [economy.md](docs/answered/economy.md) |
| Bags | Magic Bags + Pocket Dimension (Void), auto-refill, /craft, Enchanted tier, Lantern, collections never reset | [bags.md](docs/answered/bags.md) |
| Mobs | levelled mobs, zone difficulty, mob curve and level gap | [mobs.md](docs/answered/mobs.md) |
| World | zone islands (far apart), private islands + starter shards, exploration + lore | [world.md](docs/answered/world.md) |
| UI | looks vanilla; inline pages only (no `.ui` files); everything admin-editable in Server Setup; Sky Window kit later; hubs + menu layout D | [ui.md](docs/answered/ui.md), [HANDOFF.md](HANDOFF.md) section 2 |
| Social | profiles = full saves, party, guilds, ranks + permissions made in game | [social.md](docs/answered/social.md) |
| Pets | slot pets (pet slot + 50% summon slot), dragons later, 30 launch kinds | [pets.md](docs/answered/pets.md) |

## e) What still needs refining

- **Open questions waiting on Skyy:** [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md) (every question has today's default live; topics: project / release,
  world + exploration + structures, skills, gear + sigils, economy, classes + abilities, pets, rebirth, shards, quests, ui + sounds + admin page).
  Questions go to Skyy as popups ("Send questions as popups. Ill answer when i can.").
- **Untested:** TEST-CHECKLIST entries 72-101 (all of 2026-10-13 and 2026-10-14) plus older never-confirmed items 5-58.
- **UNVERIFIED engine points:** ability rune keys U1-U10 (Mage + Priest on Ability 2 / 3 + crouch) - scan server AND client logs after Skyy plays;
  rebirth Nexus tooltip (keep Rebirth OFF until seen); Lost Loot beam / sparkle looks and reveal page layout; client behaviour after a refused harvest;
  shard menu looks; admin page danger buttons in a live world.
- **Known gaps / follow-ups from today's rounds:** SkyySkills halves XP only for left-click breaks and sickle swings (F-harvest one tier up may pay
  full XP); sickles cap at Iron so a Crude sickle sweeps crops a Crude hoe is refused on; pet-kill loot waits for fighting pets (SkyyPets 0.4);
  Collections should exempt shard credit from its 20,000 / minute cap; Collect in shards goes to the inventory until Sacks has a give bridge;
  Guild info needs names with spaces (Guilds fix); Fishing / Ranching / Orchard have no /skills rows or HUD lines yet; Fishing tree not built; rebirth
  rollback is unsafe above 1000 tree points (reset points first); two rain totems live until the MoreTotems pack mod is switched off.
- **Release blockers** ([research/Release-Packaging-Plan.md](research/Release-Packaging-Plan.md)): 4 jars (Skills, Armory, Gear, Trees) hold edited vanilla JSONs -
  Skyy decides redistribution after Hytale's modding terms are checked; Dynamic Seasons + More Crossbow Tiers have no stated pack permission (ask the authors);
  [research/Licence-Audit.md](research/Licence-Audit.md) for the rest.
- **Balance work:** the Class Balance Workbench (artifact; refresh + republish whenever class / skill / Mana / ability numbers change; see
  [docs/log/2026-10.md](docs/log/2026-10.md) 2026-10-08 line) and [research/Economy-Audit-1014.md](research/Economy-Audit-1014.md) (level-coin faucet 36M per profile over 10 runs; real
  coin sink still missing; merchant scaling per rebirth; bank bonus size).
- **Bigger rebuilds waiting:** Architecture merge, replacing the third-party mods, the four broken-on-0.7 pack mods.

## f) How to help

Where to look:

| You need | Look at |
|---|---|
| What is live + versions | `tools/deploy_set.py` SET, [HANDOFF.md](HANDOFF.md) section 1 |
| Today's state + next steps | [RESUME.md](RESUME.md), newest lines of [docs/log/2026-10.md](docs/log/2026-10.md) |
| Why something was decided | `grep -n "<word>" docs/answered/*.md` (newest line wins) |
| A feature's design | `research/<Feature>-Spec.md`; one file per class in [research/classes/README.md](research/classes/README.md); cloud drafts in `research/cloud/` |
| What to test | [TEST-CHECKLIST.md](TEST-CHECKLIST.md), steps in [docs/tests/README.md](docs/tests/README.md) |
| How to build | [tools/AGENT-BRIEF.md](tools/AGENT-BRIEF.md), [tools/CONFIG-CONTRACT.md](tools/CONFIG-CONTRACT.md), [tools/PROFILES-CONTRACT.md](tools/PROFILES-CONTRACT.md), [ARCHITECTURE.md](ARCHITECTURE.md) |
| Third-party mods + permissions | [PACK.md](PACK.md) |
| Cloud / remote sessions | [CLOUD-RESUME.md](CLOUD-RESUME.md), [ART-RESUME.md](ART-RESUME.md) |

Rules you must follow ([PROJECT-RULES.md](PROJECT-RULES.md) has all of them):

- The repo is PUBLIC: never commit game files, vanilla-derived assets, other authors' files, built jars or personal data.
- Game files and Skyy's `UserData` are read-only; never start or kill the game; never enter passwords or tokens.
- Deploy only through the main session (`python tools/deploy_set.py --yes`, game closed, backup first). Build agents do not commit, deploy or edit the
  core docs; only the files their task names.
- Never edit [SkyyGear-Plan.md](SkyyGear-Plan.md) or [SkyyGear-Stat-Catalog.md](SkyyGear-Stat-Catalog.md) (Skyy's own design).
- Check for an existing mod before building one; no duplicate features between mods; pack mods only by item id, never copy their files.
- UI looks vanilla, inline pages only, no underscores in element ids; everything an owner might change is editable in Server Setup.
- Record a finished thing before starting the next (log line, HANDOFF versions, RESUME), keep docs' line endings, run `python tools/docs_check.py`
  before committing docs.
- Unsure about a design choice: ask as a question with a recommended default and put it in [OPEN-QUESTIONS.md](OPEN-QUESTIONS.md); Skyy's words go word for word into `docs/answered/`.
