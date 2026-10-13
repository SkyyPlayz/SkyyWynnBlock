# CurseForge mod survey for Hytale 0.7, by area (cloud draft)

Cloud draft, 2026-10-13. Paper research; nothing installed or tested. Skyy: "survey of Hytale mods per area" (task from the main session).

## Decisions this draft follows

| Decision | Source |
|---|---|
| Every mod in the pack should end up our own; third-party mods are stopgaps. | PACK.md (top note); docs/answered/project.md |
| Vanilla first, then borrow ideas or licence-allowed code; never build new when you can steal what already works. | PROJECT-RULES.md section 2 |
| Pack mods are reacted to by id at runtime only. Never ship a file overriding their ids, never copy recipes / numbers / models / textures, never bundle or re-upload. All Rights Reserved (ARR) = ask the author first. | PROJECT-RULES.md section 2; PACK.md |
| Advanced Farming dropped, ideas built into our own tools. | docs/answered/project.md line 36 |
| Licence verdicts already checked for ~40 mods; this survey reuses them and does not re-decide them. | research/Licence-Audit.md |
| Already-sorted mods (clash list, top picks, author asks). | research/Mods-Folder-Survey.md, research/Author-Requests.md, research/cloud/NoCube-Mods-Survey.md |

## How reliable this is (read first)

- **CurseForge, GuildOrder, BisectHosting and every other site were blocked from the cloud** (WebFetch fails with a DNS error). Everything online below is from WebSearch snippets only. Where a snippet gave no fact it says **UNVERIFIED**.
- **Download counts:** the only numbers I could source are May 2026 snapshots from a third-party wiki (BetterMap about 791K, EyeSpy about 613K, Wan's Wonder Weapons about 539K, RPG Leveling about 440K, MMO Skill Tree about 408K; [GuildOrder category leaders](https://guildorder.com/games/hytale/wiki/curseforge-category-leaders)) plus a few page snippets. Every other count is **UNVERIFIED**. Do not treat any as current.
- **Hytale 0.7 (Update 7 / Chapter 1) shipped 2026-10-12** (research/cloud/Hytale-0.7-Watch.md). I found **no source that confirms any specific mod works on it**. The "0.7" column is therefore from the manifest `ServerVersion` field in Skyy's own folder (research/Mod-Database.md, snapshot before the 0.7 release): `<0.7.0` = capped below 0.7 (expect "unsupported" until the author updates); `*` or no cap = loads, but untested on 0.7; a range reaching 0.7 or 0.8 = author declared it. Even a good range is not proof it works, because 0.7 removed chunk / block methods.
- **Licences:** only quoted where research/Licence-Audit.md or a snippet shows the exact text. Otherwise **UNVERIFIED - read the page's License field**.
- Links: where a search returned the real page I give it; otherwise "search CurseForge for <name>" (slug not confirmed, I did not guess URLs).

## Our Skyy* mods (what overlaps)

SkyyAccessories, SkyyArmory, SkyyAuctions, SkyyBank, SkyyBazaar, SkyyClasses, SkyyCoins, SkyyCollections, SkyyCooking, SkyyEssentials, SkyyExploration, SkyyFishing, SkyyGear, SkyyGuilds, SkyyHud, SkyyIslands, SkyyMenu, SkyyMerchants, SkyyMobs, SkyyParty, SkyyPets, SkyyProfiles, SkyyRanks, SkyyRolls, SkyySacks, SkyySkills, SkyyTrees, SkyyVault, SkyyWardrobe, SkyyWorldGen (+ probe mods). Pack mods today (PACK.md): More Crossbow Tiers, Saplings From Trees, Dynamic Seasons, Perfect Parries, Multitools, NoCube Orchard, Better Mob Expansion, BetterMap; HyFishing and The Armory are switched off.

Verdict words: **fold** = learn from it, we build our own; **pack** = use as a pack mod by id at runtime; **skip**; **ask** = ask the author first.

---

## 1. World gen / structures

Ours: SkyyWorldGen, SkyyIslands, SkyyExploration, SkyyTrees. Sky islands are ours; vanilla nodes first.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| BetterBiomes 1.2.0 | cyberpiratepenguin | [page](https://www.curseforge.com/hytale/mods/betterbiomes) | UNVERIFIED | **MIT** ("BetterBiomes is released under the MIT License", page snippet) | `>=0.6.8 <0.7.0` = capped below 0.7 | 108 items, 427 worldgen files, new biomes, ores, plants | Overlaps SkyyWorldGen's zones and may fight over biome files. **Fold** (MIT: ideas, even code, allowed with notice). Pack only if SkyyWorldGen is not the world generator for that world - it is, so **skip as pack**. |
| YUNG's HyDungeons 0.1.1 | YUNGNICKYOUNG (Refresh Studios) | search CurseForge for the name | UNVERIFIED; BisectHosting top-10 snippet puts it at number 10 early on | ARR (research/Licence-Audit.md) | `*` (no cap) | Instanced skeleton dungeons through portal keys, no vanilla overrides | Fits our dungeons idea (research/cloud/Capstone-Dungeon-Spec.md). **Ask** (draft #6 in research/Author-Requests.md), then **pack**. |
| Tower of Shiva 1.5.1 | Adathan | search CurseForge | UNVERIFIED | ARR | `>=0.5.1` (no cap) | Boss dungeon; overrides worldgen Settings.json | **Ask** (#1). Check Settings.json clash with SkyyWorldGen before any pack use. |
| Fullmetal Labyrinth 1.10.11 | Lunaronin777 | search CurseForge | UNVERIFIED | UNVERIFIED | `>=0.6.8 <0.7.0` | 811 worldgen files, 173 NPCs: a big labyrinth world | World-sized; fights SkyyWorldGen. **Skip** (maybe look at layouts for ideas, ask first). |
| Marsi Dungeon 0.4.0 | Marsi | named in the [CurseForge contest NPC finalists](https://curseforge.com/community-picks/hytale/curseforge-may26-npcs) | UNVERIFIED | UNVERIFIED | no cap | Randomised dungeon prefabs, enemies, puzzles, loot, hub upgrades (458 items, 641 worldgen) | Big and self-contained; own loot would clash with SkyyRolls. **Skip**, borrow the "random prefab room" idea (**fold**). |
| Welkin 1.0.2 | wyvernling | already surveyed in research/Mods-Folder-Survey.md | - | ARR | pinned to a 2026.05 pre-release | Sky instance, clouds, glider; overrides 196 vanilla generator files, 90 stale | **Skip**; technique already taken (jittered cell grid + warp, own words). Optional ask #9. |

Also seen, not rated: Distant Oceans (ocean biomes, **ARR** per its [page](https://www.curseforge.com/hytale/mods/distant-oceans/gallery) snippet, "Early Access" version) - skip; Hysuna (one marsh biome via /instances) - skip; Epic World Edit (world-pack builder, [page](https://www.curseforge.com/hytale/mods/epic-world-edit)) - a dev tool, not a pack mod.

---

## 2. Mobs

Ours: SkyyMobs (levels, zone env ids), Better Mob Expansion in the pack.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| Better Mob Expansion 3.5 (+ Humans 1.2) | Frah | in the pack (PACK.md) | UNVERIFIED | **GPLv3** (research/Licence-Audit.md); credit + link required | `*` | About 30 mobs in Zone 1-4 spawns | **Pack** (already). Keep it as a separate jar. |
| Aures Rare Monsters | BlackAures | search CurseForge | UNVERIFIED | ARR; Permissions: "You are allowed to include this mod in Curseforge modpacks and use this mod in your videos." No reupload elsewhere, no content reuse, no paid modpacks | `>=0.5.1 <0.666.0` = reaches 0.7 | 54 rare variants, horn armor | Mini-boss candidates. **Pack** (ask #5 covers credit and paid ranks, since paid ranks are a possible plan). |
| Forgotten Creatures 1.3.1 | Pedrijoe | search CurseForge | UNVERIFIED | ARR, no modpack text | exact `0.6.0` pin | 41 NPCs on vanilla models; patches 21 vanilla files (same as Better Mob Expansion) | **Ask** (#4). If no: **fold** the zone-variety idea. |
| Bio's Kobolds 1.3.2 | Bio_the_LizardWizard | search CurseForge | UNVERIFIED | **CC BY 4.0** | pinned to build 2026.03.26 | Kobold caravans, marauders, Cargo Drake | Licence allows reuse with credit. **Pack** by role id later, or **fold** the idea of roaming merchants (we build our own). |
| NoCube Undead Warriors 0.1.0 | NoCube | research/cloud/NoCube-Mods-Survey.md | UNVERIFIED | NoCube rule: modpacks OK with a link, no modifying (permissions text for this mod UNVERIFIED) | pinned build | Random skeleton warriors in Zone 1 | **Pack** later (research/Mods-Folder-Survey.md item 7); test the spawn-file override first. |
| Kami OreGolems 1.0.7 | Kami | search CurseForge | UNVERIFIED | UNVERIFIED | `>=0.6.0` (no cap) | 47 ore golem NPCs | Fits mining zones. **Ask** (licence unknown), else **fold**. |
| Hytaria | (author UNVERIFIED) | [page](https://www.curseforge.com/hytale/mods/hytaria) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Snow biome, oasis, ice mobs, goblin raid event, reworked boss | Large content mod, own biomes. **Skip** (clashes with SkyyWorldGen). |

Skip outright (clash list): Pedrijoe PJ-Difficulty, MmoMobScaling, EndlessEliteMobs (mob scaling = SkyyMobs); Spawn Manager (MIT, but our own spawn files do it).

---

## 3. Pets + mounts

Ours: SkyyPets (design in research/cloud/Pet-Core-Spec.md and research/cloud/Pets-Spec.md). Skyy's pets are eggs, levels, Grades; a second pet system would clash.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| Alec's Tamework 5.2.1 | Alechilles | [page](https://www.curseforge.com/hytale/mods/alecs-tamework) | about 120.6K; v2.8.2 dated 2026-04-11 on the snippet's file (our jar is 5.2.1, so the snippet is old) | **GPL-3.0 + Section 7(b) credit** (research/Licence-Audit.md); the page field says "Custom License" | `>=0.6.0 <0.8.0` and `>=0.7.0-pre.5` = **declared 0.7** | Taming framework, 65 NPCs, tranquilizer | Good engine. We tame via SkyyPets. **Fold** the taming-behaviour idea; **pack** only if we want tamable wildlife. Needs a decision. |
| Alec's Animal Husbandry 4.0.1 | Alechilles | [files](https://www.curseforge.com/hytale/mods/alecs-animal-husbandry/files/8222883) | UNVERIFIED | GPL-3.0 + 7(b) | `>=0.6.7 <0.7.0` = capped | 304 NPCs, breeding, saddles | Farm animals; overlaps our farming. **Fold** ideas; **skip** as pack for now. |
| Kazzy's Pets & Mounts 2.0.5 | Kazopalooza | search CurseForge (the snippet search found no page) | UNVERIFIED | ARR (research/Mods-Folder-Survey.md) | `*` | 100+ pets and mounts (144 items, 166 NPCs) | Directly clashes with SkyyPets. **Ask** only if we want its mount models; else **skip**. |
| Dragon Nestkeeper | BlackAures | search CurseForge | UNVERIFIED | ARR; page: "made for use in any modpacks" | `>=0.5.1 <0.666.0` | Dragon eggs, nestkeeper bench, mountable dragons | Fits the Zone 5 dragon idea. **Pack** after the credit ask (#5). |
| Traveling Mounts | cali19 | [files](https://www.curseforge.com/hytale/mods/traveling-mounts/files/7651684) | about 20.9K (1.0.8 snippet; ours is 1.1.2) | UNVERIFIED | `2026.03.26` pin | Tamed mountable companions in crates | Crate model clashes with eggs. **Skip**; **fold** the mount idea. |
| Better Pets | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/better-pets-mounts/install) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Server pets by config.yaml | **Skip** (own system). |
| Mounts+ | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/mountsplus) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Makes any entity mountable, by admin command or drop | **Fold** (see how mount-anything works) / **skip**. |
| HorseOverhaul Revamp | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/horseoverhaul-revamp) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Taming, saddles with storage, whistle, levelling | **Fold** whistle + saddle-storage ideas. |

Also: Spark Lantern Pets and FPetsPlugin (cosmetic floating pets) - **fold** only. DarkMatter Mounts is pinned `=0.6.8` - skip.

---

## 4. Weapons + combat animations

Ours: SkyyGear, SkyyClasses, SkyyAccessories (weapons are our design; Perfect Parries is in the pack).

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| Perfect Parries 0.9.6 | narwhals | in the pack | UNVERIFIED | **ARR** (research/Licence-Audit.md) | `>=0.6.0 <0.7.0` = **capped, risk for us** | Parries, counters, posture / stun | **Pack** (already); #15 ask pending. Check 0.7 first (For the local session). |
| Perfect Dodges 0.5.16 / Perfect Utils 1.2.0 / Zephyr 0.4.0 | narwhals | search CurseForge | UNVERIFIED | UNVERIFIED (author's Parries is ARR, likely the same) | all `<0.7.0` | Dodges, helper library, movement | Zephyr and dodges are on the clash list (research/Mods-Folder-Survey.md). **Skip**; Perfect Utils only if Parries needs it. |
| Wan's Wonder Weapons 1.1.0 | wanmine | in a [CurseForge roundup](https://blog.curseforge.com/9-great-hytale-combat-mods-on-curseforge/) | about 539K (May 2026 snapshot) | UNVERIFIED (the snippets gave none) | `>=0.6.0 <0.7.0` = capped | Relic weapons with abilities | Overlaps our own specials and Mythic ladder. **Fold** the ability ideas; **ask** before any pack use. |
| MovesetSwitcher | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/movesetswitcher) | UNVERIFIED | UNVERIFIED | UNVERIFIED | `/moveset` swaps a weapon's combat animations, works on modded weapons | Per-class animation per weapon is exactly our Requip / class need. **Ask** (licence unknown), else **fold** (learn how the swap is done). |
| Arcane Power 3.2.0 | Tayko_Dev | search CurseForge | UNVERIFIED | ARR | `<0.7.0` | Spellbooks, maces, bows, cloth armor | Fills Mage gaps (research/Mods-Folder-Survey.md). **Ask** (#7); needs a 0.7 update first. |
| Aegos 1.7.0 | Zbeve | search CurseForge | UNVERIFIED | ARR | `<0.7.0` | Seeking bow | Special drop. **Ask** (#2). |
| Starky's Mjolnir / Shield Captain America | StarkyMods | search CurseForge | UNVERIFIED | UNVERIFIED | `<0.7.0` | Themed weapons | Brand-themed. **Skip**. |
| Reforged Weapons 4.4 / Combat Tweaks / Hyguns / Craftable Katanas | various | [Combat Tweaks](https://www.curseforge.com/hytale/mods/combat-break), [Hyguns](https://www.curseforge.com/hytale/mods/hyguns/files/8297054), [Katanas](https://www.curseforge.com/hytale/mods/craftable-katanas) | UNVERIFIED | Katanas page: "You're free to: Use this mod in your own projects" (snippet) - may be a summary only; others UNVERIFIED | UNVERIFIED | Weapon packs | New weapon ids bypass our Grades table. **Skip**; Katanas only if Skyy wants one. |

Hytale 0.7 adds a first-party **Rune Ability system** and goblin gadgets (research/cloud/Hytale-0.7-Watch.md). Mods that add abilities may be overtaken by it.

---

## 5. Farming

Ours: SkyyCooking, SkyyTrees, the gathering ladder (research/cloud/SkyBlock-Gathering-Progression.md). Skyy dropped Advanced Farming and wants the ideas built in.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| NoCube Orchard 0.0.2 | NoCube | in the pack; [page](https://www.curseforge.com/hytale/mods/nocubes-orchard-hytale) | UNVERIFIED | ARR; "allowed to include this mod in modpacks"; no reuse | no cap | 9 fruit trees, Orchard Bench, Fruit Press, juices | **Pack** (already). |
| HyFarming | UNVERIFIED | [files](https://www.curseforge.com/hytale/mods/hyfarming/files/7636673) | 1.0.6 on 2026-02-17 (snippet); UNVERIFIED now | UNVERIFIED | UNVERIFIED | More crops, enhanced tools, packing machine, crop boxes sold for gold | The "sell crop boxes" piece clashes with SkyyBazaar. **Fold** ideas (automation machines); ask if wanted as a pack mod. |
| Farming Overhaul 2.4.0 | Krynnx | search CurseForge | UNVERIFIED | UNVERIFIED | `2026.03.26` pin | 16 items | On the clash list ("farming overhauls"). **Skip**. |
| ResourceFarm [Crops] | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/resourcefarm) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Ore plants for every vanilla ore | Nice SkyBlock-style idea (grow ore). **Fold**. |
| AutoFarmer / Forever Tilled And More / HyRise | UNVERIFIED | [AutoFarmer](https://www.curseforge.com/hytale/mods/autofarmer), [Forever Tilled](https://www.curseforge.com/hytale/mods/forever-tilled-and-more), [HyRise](https://www.curseforge.com/hytale/mods/hyrise-farming) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Auto water + harvest in 3 tiers (3x3x3 to 7x7x7); permanent tilled soil; wild-seed progression | Tiered auto-farm = a minion-style SkyBlock fit. **Fold** (own tiers, own numbers). |
| Alec's Animal Husbandry | Alechilles | see section 3 | - | GPL-3.0 + 7(b) | capped | Livestock, breeding | **Fold** (ideas). |
| More Foods / Culinary / Bakehouse | various | research/cloud/NoCube-Mods-Survey.md | - | NoCube rule | - | Food | Overlaps SkyyCooking. **Skip** / **fold**. |

---

## 6. UI / HUD

Ours: SkyyHud, SkyyMenu (vanilla-look kit, `tools/skyyui.py`). Other HUD or map mods are on the clash list.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| BetterMap 1.3.8 | Paralaxe + Theobosse (ninesliced) | in the pack; [file](https://www.curseforge.com/hytale/mods/bettermap/files/7690513) | about 791K (May 2026 snapshot) | **AGPL-3.0** | `<0.7.0` = capped | Persistent map, waypoints, cave view | **Pack** (already, never bundled; SkyyHud minimap is clean-room). 0.7 update needed. |
| EyeSpy 2026.9.1 | JarHax | [file](https://www.curseforge.com/hytale/mods/eyespy/files/7642244) | about 613K (May 2026 snapshot) | UNVERIFIED | `>=0.6.0` (no cap) | Look-at HUD: block, mob, chest names, health | Overlaps our target info. **Fold** the idea, or **pack** if the licence allows (ask / read page). |
| MultipleHUD 1.0.8 | Buuz135 | via [HUDRouter](https://www.curseforge.com/hytale/mods/hudrouter) | UNVERIFIED | UNVERIFIED | `>=0.5.0` | Lets several mods show a HUD at once | HUDRouter calls it stale. Check how SkyyHud and BetterMap share the HUD slot. **Pack** only if conflicts appear. |
| HyUI | Ellie | [page](https://www.curseforge.com/hytale/mods/hyui) | UNVERIFIED | UNVERIFIED | `<0.6.0` in our jar (old) | UI library with a multi-HUD manager | We use our own kit. **Fold** (study); **skip**. |
| Skill HUD 6.2.8 / ClockHud / Wayfinder | various | search CurseForge | UNVERIFIED | UNVERIFIED | `*` mostly | Skill bars, clock, waypoints | Clash with SkyySkills and SkyyHud. **Skip**. |

Update 7 redid the vanilla HUD and the Mana max (research/cloud/Hytale-0.7-Watch.md); the plan to move to NoesisGUI is announced, not shipped. So HUD mods may break and ours need a release-day check.

---

## 7. Quests

Ours: SkyyQuests specs (research/cloud/SkyyQuests-Spec.md, research/cloud/SkyyQuests-Zone1-Spec.md); no SkyyQuests mod exists yet.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| QuestLines (+ Denizens) | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/questlines), [Denizens](https://www.curseforge.com/hytale/mods/questlines-denizens) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Dialogue trees and quests on any NPC; branching, multi-stage boss fights | Closest to our NPC-quest spec. **Fold** (study the dialogue-tree data shape); **ask** if a pack mod is wanted. |
| OpenQuests | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/openquests) | UNVERIFIED | UNVERIFIED | UNVERIFIED | No-code quests in the Asset Editor, given on connect or by rewards | **Fold** (data-driven quests are a good shape for server owners). |
| QuestBook | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/questbook/install) | UNVERIFIED | UNVERIFIED | UNVERIFIED | FTB-Quests-style book UI, JSON quests | **Fold** (UI idea). |
| NPC Dialog + NPC Quests | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/npc-dialog-npc-quests-maker) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Prerequisites, item checks, rewards, chains | **Fold**. |
| Natural 20 | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/natural-20) | UNVERIFIED | UNVERIFIED | UNVERIFIED | d20 skill-check quests; gold "!" turns blue "?" on turn-in | The "!" / "?" markers are worth copying as an idea. **Fold**. |
| MMO Skill Tree & Abilities 1.7.0 | Ziggfreed | [file](https://www.curseforge.com/hytale/mods/mmo-skill-tree/files/7712147) | about 408K (May 2026 snapshot) | UNVERIFIED | `<0.7.0` | Skills plus an NPC quest log | On the clash list (skills / levels). **Skip**. |
| Aetherhaven 3.2.1 | Hexvane | research/Mods-Folder-Survey.md | - | ARR | `<0.7.0` | Town game, quest board, festivals | Design reference only. **Skip**. |

No quest mod is in the pack, so quests stay **our own build**; none here needs an install.

---

## 8. Server admin

Ours: SkyyEssentials, SkyyRanks, SkyyProfiles, SkyyMenu Server Setup (everything editable in game, tools/CONFIG-CONTRACT.md). Admin and boards mods are on the clash list.

| Mod | Author | Link | Downloads / update | Licence | 0.7 | Adds | Overlap and verdict |
|---|---|---|---|---|---|---|---|
| EliteEssentials 2.0.9 | UNVERIFIED | [page](https://curseforge.com/hytale/mods/eliteessentials) | file dated 2026-06-23 (snippet) | page claims **MIT**, open source on GitHub (not verified against the repo LICENSE) | UNVERIFIED | Homes, warps, TPA, RTP, kits, economy, bans, mutes, admin UI | Overlaps SkyyEssentials and SkyyCoins (its economy would fight ours). **Fold** (MIT: ideas ok); do not run beside SkyyCoins. |
| HyperEssentials 0.1.0 | UNVERIFIED | [page](https://www.curseforge.com/hytale/mods/hyperessentials) | UNVERIFIED | UNVERIFIED | `2026.03.26` pin | 10 modules, 50+ commands, HyperPerms + VaultUnlocked integration | Same overlap. **Skip**. |
| HyEssentialsX / HyCore / HyCommands | various | [HyEssentialsX](https://www.curseforge.com/hytale/mods/hyessentialsx), [HyCore](https://www.curseforge.com/hytale/mods/hycore-essentials), [HyCommands](https://www.curseforge.com/hytale/mods/hycommands) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Permissions, balances, teleports | **Skip**. |
| LuckPerms | (Hytale port; author UNVERIFIED) | search CurseForge | UNVERIFIED | UNVERIFIED | UNVERIFIED | Groups and permission nodes; named as the key plugin in a [guide](https://www.thespike.gg/hytale/beginner-guides/hytale-plugins) | A standard permissions backend; SkyyRanks is ours. **Pack** only if Skyy wants a standard backend on the public server; check SkyyRanks can read it. |
| CoreProtect (Hytale Edition) | UNVERIFIED | search CurseForge (named in [Host Havoc](https://hosthavoc.com/blog/hytales-most-popular-mods)) | UNVERIFIED | UNVERIFIED | UNVERIFIED | Logs block / player actions, rollbacks | No overlap with ours, and valuable for a public server (grief rollbacks, dupe tracing). **Pack** (best admin pick), after licence + 0.7 check. |
| AdminUI 1.0.8 | Buuz135 | search CurseForge | UNVERIFIED | UNVERIFIED | `>=0.6.0` | Admin UI | Overlaps Server Setup. **Skip**. |
| Lootr 0.3.12 | Noobanidus | search CurseForge | UNVERIFIED | **MIT** | `>=0.6.2` | Per-player loot chests | No overlap, fixes chest-loot races. **Pack** (and could fold, MIT). |
| Lucky Mining 1.0.7 / VeinMining 2.4.0 | Buuz135 / EineNT | search CurseForge | UNVERIFIED | **MIT** both | Lucky Mining `>=0.6.0`; VeinMining `<0.7.0` | Mining bonus; vein mining | Overlap mining skill. **Fold** (MIT), likely skip. |

---

## INSTALL LIST for Skyy (ordered)

Only mods that fit, with no overlap, and whose licence allows pack use. None is verified on 0.7, so check each page's "Game Version" and "Last Updated" before installing.

| # | Mod | Why | Licence status |
|---|---|---|---|
| 1 | CoreProtect (Hytale Edition) | rollbacks and action logs for a public server; no overlap | UNVERIFIED - read the page first |
| 2 | Lootr (Noobanidus) | per-player chests; fits chest loot | MIT - ok |
| 3 | Aures Dragon Nestkeeper + Rare Monsters (BlackAures) | Zone 5 dragons, mini-bosses | ARR; modpacks ok, no paid modpacks - send message #5 first |
| 4 | Alec's Tamework (Alechilles) | only if we want tamable wildlife; declared 0.7 | GPL-3.0 + credit - separate jar is fine |
| 5 | Bio's Kobolds (Bio_the_LizardWizard) | kobold models and Cargo Drake, by role id | CC BY 4.0 - credit and link |
| 6 | YUNG's HyDungeons | instanced dungeons | ARR - ask (#6) |

Already in the pack and still wanted: Better Mob Expansion (GPLv3), Saplings From Trees (GPLv3), NoCube Orchard (ARR, modpacks ok), BetterMap (AGPL, never bundled), Multitools (MIT), Dynamic Seasons (ARR, no permission text), Perfect Parries (ARR, ask #15), More Crossbow Tiers (ARR, no permission text).

---

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | The CurseForge survey could not read licences or 0.7 status from here. May the local session open the pages and fill the UNVERIFIED cells? | [Yes, the local session checks the 6 install-list pages first] |
| 2 | Do you want a standard permissions mod (LuckPerms) on the public server, or keep SkyyRanks only? | [SkyyRanks only] |
| 3 | CoreProtect for the public server: yes? | [Yes, after the page check] |
| 4 | Pets: stay fully our own (SkyyPets) and use Kazzy / Traveling Mounts only as idea sources? | [Yes] |
| 5 | Quests: build our own (SkyyQuests from the specs), taking dialogue-tree ideas from QuestLines? | [Yes] |
| 6 | MovesetSwitcher (per-weapon animation swap): ask its author whether it can be a pack mod? | [Yes, ask once the page is read] |
| 7 | The messages in research/Author-Requests.md are still unsent: send #5 and #6 first (they unlock the install list)? | [Yes] |
| 8 | BetterBiomes is MIT. Fold biome ideas into SkyyWorldGen? | [Ideas only, no copied files] |

## For the local session

- Open each page in the install list and the "Hytale 0.7 = yes" candidates; record "Game Version", "Last Updated", License field word for word.
- Read the `ServerVersion` of the jars after the 0.7 release: the folder snapshot predates it. Capped mods: Perfect Parries, BetterMap, Dynamic Seasons, Arcane Power, Aegos, Alec's Animal Husbandry, Wan's Wonder Weapons (all `<0.7.0`).
- Alec's Tamework declares `>=0.7.0-pre.5 <0.7.0` in the manifest: read the actual range string in `manifest.json` (it looks inconsistent) and test it on 0.7.
- Run `python tools/ci/crosscheck.py` against the 0.7 jar with any pack candidate installed; look for overrides of vanilla spawn or worldgen files (Better Mob Expansion, Forgotten Creatures, Tower of Shiva, Welkin).
- Check that MultipleHUD / HyUI do not fight SkyyHud and BetterMap for the HUD slot.
- Check whether CoreProtect exists as a Hytale mod under that exact name and who the author is (the snippet only said "Hytale Edition" in a Host Havoc post).
- Licence cells marked UNVERIFIED must not be turned into PACK.md rows until read.
