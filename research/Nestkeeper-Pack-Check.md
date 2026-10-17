# Dragon Nestkeeper (Aures) - pack check, 2026-10-17

Skyy 2026-10-17 (gear.md 247): popup "Add it (Recommended)" -> duplicate check, PACK.md entry, switch it on, one in-game look test, then a Dragon pet kind.
Sources: Skyy's Mods folder `0.6.1_Aures_Dragon Nestkeeper_28_08_2026.zip` (read only), `research/Licence-Audit.md` 58, `research/Mods-Folder-Survey.md` row 2,
`docs/answered/pets.md` 28-30, 58, 66, `docs/answered/project.md` 40, `research/Dragon-Pets-Idea.md`.

## 1. Licence / permission

| Item | Status |
|---|---|
| Licence | CurseForge "All Rights Reserved"; page text "made for use in any modpacks"; no LICENSE in the zip (Licence-Audit 58) |
| Pack use | stated OK (link the page https://www.curseforge.com/hytale/mods/aures-dragon-nestkeeper). Folding / copying / reupload: NO |
| Aures' answer | Skyy asked 2026-10-06 (log line 132). Skyy 2026-10-16 (pets.md 58): "aures already gave the okay." = our secondary pet slot may summon the dragon by id at runtime, files never copied. The exact wording of Aures' reply is not in the repo (UNVERIFIED) |
| Not covered | recolouring or tracing their model / texture (icon "look like the dragons in the mod", pets.md 30), extra element dragons made from their model. Needs a separate ask |
| Manifest | `BlackAures:Aures - Dragon Nestkeeper`, version 28.08.2026, ServerVersion `>=0.5.1 <0.666.0`, no dependencies, no Java (assets only) |

## 2. What it adds (read from the zip)

| Group | Content |
|---|---|
| Dragons | `Nestkeeper_Dragon_Plain_1..4`, `Nestkeeper_Dragon_Tundra_1..4` (1 Weakling, 2 Smalling, 3 Biteling, 4 Flyling = adult, mountable with saddle, pettable, fire / wind / acid breath attacks, MaxHealth 121 on Plain_4). An Azure model folder ships but has no role, so it is unused |
| Nests | 4 nest NPCs (Plain / Tundra x Live / Old) spawning in `Env_Zone1_Forests` / `Env_Zone1_Plains` (Plain) and Tundra envs, weight 5, day 1-23 |
| Items | dragon eggs, egg fragments, Dragon Shed Hide (+ salvage), 6 dragon foods (meat / mushroom per stage), Dragon Saddle, Dragon Gone (release), Nestkeeper Bench + nest furniture |
| Saurians | `Nestkeeper_Saurian` NPC race with a barter shop (`BarterShops/Saurian_Nestkeeper`), saurian spawner egg, statue drop |
| Misc | drops tables, particles, sounds, a custom UI page set, `memories.categories.nestkeeper` lang keys (memories) |
| Commands / Java | none |

## 3. Clash and duplicate check (PROJECT-RULES section 2 "No duplicates")

| Check | Result |
|---|---|
| Vanilla file override | none. Python compare against the release Assets.zip: only `Server/Languages/en-US/server.lang` shared (every mod has it) |
| Same paths as another mod in Skyy's folder | none beyond `server.lang` / `manifest.json.bak` (checked all zips + jars) |
| Mounts in the pack | pack has no mount mod. More Mounts, DarkMatterMounts, Kazzy, cali19, Aures Horse Skins sit in the folder but are NOT in PACK.md. Our own mounts = SkyyPets mount pets on shrunk vanilla models. The dragon is the only dragon mount, so no duplicate |
| Dragons | ours: none built. `Dragon-Pets-Idea.md` plans a Dragon_Fire / Dragon_Frost boss, 5 quest + 4 secret element dragons, flight at about level 10. Nestkeeper covers only 2 types (Plain, Tundra) x 4 growth stages. NOT a clash today; it overlaps the idea for dragon-as-pet growth and flight. Decision needed on the other 7 elements (section 5) |
| Mobs / pets | Better Mob Expansion (pack, OFF): no dragons. SkyyPets: dragon is a new kind, no duplicate. Rare Monsters (same author) is NOT in the pack; separate question |
| Items | dragon food, saddle, eggs: none in our mods. Our eggs are SkyyPets pet eggs (hatchery); Nestkeeper eggs are a different, wild-nest feature (see Q2) |
| Bench | `Bench_Nestkeeper` is a furniture bench. We centralise crafting in menus (Menu-Pattern); a separate bench is a small clutter cost. It only crafts Nestkeeper things |
| Saurian trader | roaming merchants are SkyyMerchants; the Saurians are a fixed barter NPC in the wild. Mild overlap (trade); they trade for the author's own items |
| Levels | nests spawn in Zone 1; SkyyMobs levels by zone env id. Dragon roles will be levelled like other Zone 1 mobs, adult Flyling is strong for Zone 1 (UNVERIFIED in game) |
| Engine | built for 0.6.1; no Java, `<0.666` range accepted. 0.7.2 load: smoke test needed (not run today) |

## 4. Verdict: PACK it

Pack mod (not folded). Zero vanilla overrides, no duplicate with our mods or the other pack mods, permission stated, and Aures agreed to the pet-slot summon.
Learn from it too: its role template (`Template_Nestkeeper_Dragon_*`, `IsMountable`, `MountAnchor*`, `DragonSaddleItemSet`, food-driven growth stages) is the best reference for our own mount / growth work; reuse nothing by copy.

PACK.md row text for the main session:

> | Dragon Nestkeeper (`BlackAures:Aures - Dragon Nestkeeper`) | BlackAures (Aures) | 28.08.2026 | 0.6.1_Aures_Dragon Nestkeeper_28_08_2026.zip | Wild dragon nests (Zone 1 Forests / Plains + Tundra), raise Plain and Tundra dragons Weakling to Flyling with food, saddle and mount, dragon eggs, Dragon Shed Hide, Nestkeeper Bench, Saurian traders (Skyy, 2026-10-17: "Add it"). SkyyPets summons its dragon through the secondary pet slot by NPC id at runtime (Aures agreed, pets.md 2026-10-16). LICENCE: All Rights Reserved; page says "made for use in any modpacks"; link https://www.curseforge.com/hytale/mods/aures-dragon-nestkeeper; NO folding, NO copied or traced model / texture, NO recolour without asking Aures (Discord https://discord.gg/aSRPHxHKPg). No vanilla overrides, no dependencies, no commands. Same author's Rare Monsters / Horse Skins are not in the pack. |

Also: `tools/deploy_set.py` PACK_THIRD_PARTY entry (main session) and enable in NewBetaTest; update Licence-Audit pointer if wanted.

## 5. What the Aures dragon pet (SkyyPets) needs

| # | Need | Notes |
|---|---|---|
| 1 | Pack entry + enabled in the world | section 4 |
| 2 | Look probe | Server Setup > Pets > Pet looks, row `Nestkeeper_Dragon_Plain_4 | 1 | walk` (pets.md 66). Check it spawns as a pet model, scale, walk / idle animations, and that the pet system does not also run the dragon's own role AI (breath, hostile PredatorsBig attitude) |
| 3 | Which stage | pet should show a stage by pet level (Weakling Lv 1 -> Flyling at the "ride at level 10" idea). Ids `_1.._4`; each is its own appearance |
| 4 | Two types | Plain and Tundra only. Other elements need our own art or Aures' OK to recolour (Q3) |
| 5 | Mount / flight | the Nestkeeper mount works on its NPC role (`IsMountable`, saddle). A pet-summoned model is likely not rideable; riding the dragon needs the real NPC. Probe; fall back to "pet looks like the dragon, mount is the Nestkeeper dragon" |
| 6 | No double systems | do not enable Nestkeeper eggs / feeding for the pet; the pet gets XP / levels from SkyyPets. The wild nest dragons stay Aures' feature |
| 7 | Icon | draw an original icon in the same style (pets.md 30) until Aures OKs rendering from the model |
| 8 | Slot rule | summon slot = 50% buffs (SkyyPets 0.4.3); the dragon is the secondary-slot pet per the 10-06 plan |
| 9 | Tier tag + roster | pet rarity and egg path from the SkyyPets roster; tier tag per `tools/tier_tags.py` |

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Switch Nestkeeper on for everyone in the world now, so wild nests spawn in Zone 1? | [yes, test world first, one look test] |
| 2 | Keep Nestkeeper's own taming (eggs, food, saddle) alongside our pet dragon, or hide it? (it cannot be hidden without editing their files; so keep) | [keep both; pet = ours, wild = theirs] |
| 3 | Ask Aures to allow recoloured / extra element dragons (Fire, Water, Earth, Thunder, Air + secret four) based on their model? | [yes, one message; until then Plain + Tundra only] |
| 4 | Also pack Aures' Rare Monsters (permission: CurseForge modpacks OK) and Horse Skins? | [separate mod check, not now] |
| 5 | Wild adult dragons in Zone 1 are strong; let SkyyMobs level them high or lower their spawn? | [leave, look in the test] |
