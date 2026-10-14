# Structure mods survey - 2026-10-14

World structures (dungeons, ruins, villages, camps, towers) for Hytale 0.7.x from CurseForge, checked on the live pages today (WebSearch + page fetch of the CurseForge
Hytale section) and against our own records: `PACK.md`, `research/Mod-Database.md` / `Mod-Database-Overview.md`, `research/Mods-Folder-Survey.md` (2026-10-09),
`research/Licence-Audit.md`. CurseForge shows "All Rights Reserved" and no modpack sentence for every structure mod below, so under PROJECT-RULES section 2 none can be
shipped or listed in PACK.md until the author says yes. The search listing only shows 66 "dungeon" projects, so this is the top of the list, not every mod.

## 0. Short version

1. **Nothing is a drop-in.** Every structure mod found is All Rights Reserved with no modpack statement, so the verdict for each is "ask the author" or "learn".
2. **Only two hit 0.7 today:** OpenStructure (joszza, updated 2026-10-12, page says 0.7) and GlymeraStructures (GlymeraCraft, updated 2026-10-14, file tagged 0.7 but its text
   still says 0.6.x - inconsistent). The best content mod, "Dungeons and more Structures" (joszza, 25 structures), is tagged 0.6 (updated 2026-09-23).
3. **Best path for the pack: OpenStructure + the author's structure pack.** OpenStructure is a worldgen hub (spawn rules from content packs, paste engine, admin UI, public API)
   by the same author as the 25-structure pack; if joszza agrees to a modpack listing, it gives us structures without building a placement engine. That is one ask for two mods.
4. **Our own world:** `SkyyWorldGen` makes the sky islands. The zone worlds are vanilla terrain with `Env_Zone1-4`, which already contain vanilla villages, temples and dungeons.
   More structures there only matter for loot spots (Lost Loot piles, luggage sites) and mini bosses - both of which we are building ourselves.
5. **Learn from, build ourselves:** the paste engine idea (structure files placed on new chunks from a spawn-rule table) is simple; if no author agrees, SkyyWorldGen can place prefabs
   with the same idea.

## 1. Candidates

| Mod | Author | Adds | Game version on page | Licence | Modpack | Dupes with our pack | Verdict |
|---|---|---|---|---|---|---|---|
| **OpenStructure** | joszza | worldgen hub: places structures from pack spawn rules in NEW chunks, paste engine, admin UI, public API; 260 downloads (new) | 0.7 (+0.6), updated 2026-10-12 | All Rights Reserved | not stated | none (we have no placement engine); touches worldgen like SkyyWorldGen - needs a clash check | **ask** (pack candidate with the next row) |
| **Dungeons and more Structures** | joszza | 25 structures: camps, mines, airships, taverns, floating islands, frozen tower, shipwrecks; Astral Voidcaller boss, Ice Magus mini boss, traveling merchant camp; optional Lootr / Aetherhaven integration; 17.1K downloads | 0.6 (+0.5), updated 2026-09-23 | All Rights Reserved | not stated | merchant camp vs SkyyMerchants (roaming merchants, our design: take OUR merchant, drop theirs if separable - it is not); bosses vs SkyyMobs levels | **ask**, wait for 0.7 tag |
| **GlymeraStructures** | GlymeraCraft | raises how often villages, dungeons, encounters, temples, shipwrecks generate (density 10-35% -> up to 100%), removes spawn restrictions, `/` toggle, restart to apply; 3.1K downloads | 0.7 tagged, text says 0.6.x, updated 2026-10-14 | All Rights Reserved | not stated | none, but it edits VANILLA filters (same files SkyyWorldGen may touch) | **learn** (a one-number density idea); skip as a dependency |
| **YUNG's HyDungeons** | YUNGNICKYOUNG | procedural dungeon instances through the Ancient Portal (one dungeon type); 178K downloads | Early Access | All Rights Reserved | ask (Licence-Audit: NO - ask) | overlaps our planned capstone dungeon spec (research/cloud/Capstone-Dungeon-Spec.md) | **learn** (instancing, portal key flow), skip pack unless Skyy wants it |
| **MAJOR DUNGEONS** | MAJOR76 | custom instanced dungeons, gear, merchants | 0.6 (excludes 0.7 per the 10-09 survey) | not found | - | own currency and merchant clash with SkyyCoins / SkyyMerchants | **skip** |
| **Restored Ruins** | Joshieman | overworld ruin structures (Castle Arena at last report; more promised) | not confirmed (page not found) | not checked | - | none | **check later** |
| **Aetherhaven** | Hexvane | villages / settlement structures + block palettes (80 structures in the 10-09 database) | `<0.7.0` | All Rights Reserved, no LICENSE in the jar | - | town / NPC systems overlap our hubs | **learn** (design reference only, per Licence-Audit) |
| **Tower of Shiva / Shiva's Ice Cave / Void Asylum / Boss Library** | Adathan | boss dungeons / towers; Tower of Shiva overrides worldgen Settings.json | Early Access | All Rights Reserved | ask (one message covers all, Licence-Audit row 124) | clash with SkyyWorldGen Settings.json (Tower of Shiva) | **ask once** if Skyy wants end bosses; else skip |
| **Marsi Dungeon** | MarsiMods | randomized-prefab dungeons with puzzles and loot (DungeonBlockSpawner, doors, colliders) | Early Access | not stated | - | capstone dungeon spec | **learn** (random prefab assembly) |
| **Dungeons And More** | Puzambus | decaying world with ancient dungeons, undead | Early Access | - | - | - | skip |
| **Land1's Endgame Dungeons** | LAND1 | high-difficulty multi-stage dungeons | Early Access | - | - | capstone spec | skip (maybe learn) |
| **Endgame & QoL 6.0** | Lewaii (Config) | endgame, reworked dungeons and bosses, own dimension; 486K downloads | 0.7 | - | - | huge: gear, bosses, UI (Endgame&QoL is already in the "not included" list of PACK.md) | **skip** (a second pack inside the pack) |
| **Great Wall Outpost** | Jotty0101 | one stone wall with three towers and loot (prefab) | Early Access | - | - | none | learn / ask if a prefab is wanted for an outpost |
| **Structure Atlas** | lorddionysus13 | detects structures, pins them on the map, `/atlas`; not a structure mod | 0.5, updated 2026-06-19 | All Rights Reserved | not stated | BetterMap (pack) already pins map points | skip |
| **Skylands Imagined** | JacobG555 | fragment world with floating islands, ore, caves, four biomes | Early Access | All Rights Reserved | not stated | SkyyWorldGen (our islands) | skip |
| **Kami OreGolems, Bio's Kobolds, Better Biomes** | (from the 10-09 survey) | mobs / biomes, no structures worth packing | - | MIT for Better Biomes | - | Better Biomes is on the MIT fold list (RESUME item 6) | not for this question |

## 2. What the pack already has (so we do not duplicate)

| Thing | Where |
|---|---|
| Sky islands + void world | SkyyWorldGen 0.5.1 (island generator, own) |
| Zones 1-4 terrain, villages, temples, vanilla dungeons | vanilla worldgen with `Env_Zone1-4`; SkyyMobs levels them |
| Roaming merchant | SkyyMerchants 0.1.3 (own) - a structure mod's merchant camp is a duplicate |
| Luggage / loot sites | SkyyExploration 0.2.7 (own), Lost Loot piles + airdrops planned |
| Capstone dungeon | planned, research/cloud/Capstone-Dungeon-Spec.md - overlaps every dungeon mod |
| Pack third-party structure mods | none in `PACK_THIRD_PARTY` |

## 3. Recommendation

| Step | Action |
|---|---|
| 1 | Send ONE message to joszza (CurseForge comment or the Authors Discord link in PACK.md): ask for a modpack / server-pack listing of **OpenStructure** and **Dungeons and more Structures** on 0.7, and whether the merchant camp can be turned off. |
| 2 | While waiting: build nothing. The content value is moderate (camps, mines, airships) and the world is zone-driven by our own mobs. |
| 3 | If joszza says no: add a small "prefab placer" to SkyyWorldGen only if Lost Loot / luggage sites need structures (not before). Use the idea from OpenStructure (spawn rules per zone, new chunks only), no code copied. |
| 4 | Recheck Restored Ruins, Glymera and Dungeons and more Structures in a week for the 0.7 tag and a modpack statement. |
| 5 | Record the choice in PACK.md once an author answers (only then). |

## UNVERIFIED

| # | Item |
|---|---|
| 1 | Licence text beyond "All Rights Reserved" (each page links a licence page that was not in the fetched text). Some CurseForge pages say "modpacks allowed" only on that licence page. |
| 2 | Whether OpenStructure and Dungeons and more Structures run together on 0.7.1 and next to SkyyWorldGen / Perfect Parries / DynamicSeasons (no test done; the smoke test with `--allow-pack-api` would show asset or API failures). |
| 3 | Restored Ruins details (the page was not found by search). |
| 4 | Download counts are from the listing and not dated. |
| 5 | Search covered only the queries "dungeon" and the general web search; a village / tower specific CurseForge search returned 0 projects, so village mods are not found rather than absent. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | OK to message joszza asking for modpack use of OpenStructure + Dungeons and more Structures (and the merchant camp off switch)? | [yes, you send it or I draft the text] |
| 2 | Do you want more world structures at all before release, or keep zones vanilla + our loot piles? | [keep vanilla, add loot piles first] |
| 3 | Boss dungeons from Adathan (Tower of Shiva, Void Asylum) as end-game: one ask message for all four? | [no, our own capstone dungeon] |
| 4 | If no author agrees: build a small prefab placer into SkyyWorldGen? | [only if loot piles need it] |
