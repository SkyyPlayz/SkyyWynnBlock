# Pack check: Mycology 0.3.8 (MMartinsar) (2026-10-23)

Read-only check (Sonnet). Sources: `Mycology_v0.3.8.zip` in Skyy's Mods folder (copied to scratch, read, scratch deleted), Assets.zip 0.7.4
(read only), a real smoke run (`tools/dev/scratch/smoke/20261023-085301.log`), our current builds (`tools/deploy_set.py` SET), `PACK.md`,
`research/Balance-P6-Gathering-Spec.md`. Nothing was built, edited, deployed or sent. Licence: MIT per Skyy; the manifest carries no
licence field and the CurseForge page was NOT re-fetched (UNVERIFIED - check the page text and keep the MIT line + credit if folded).

Legend: VERIFIED = read in the zip / Assets.zip / the smoke log. UNVERIFIED = needs an in-game look.

## 0. Short answer

- **Loads on 0.7.4: YES.** The range `>=0.6.8 <0.7.0` only gives a WARN + one SEVERE summary line ("asset packs are targeting an older server
  version"); the pack loads ("Loaded pack: MMartinsar:Mycology from Mycology.zip"). The server booted; no Mushrim role or model failed.
- **Three real problems:** (1) 2 items point at an effect that does not exist in 0.7 (`Food_Instant_Heal_T2`); (2) all 19 Mushrim spawn in
  **Zone 1** and always drop the vanilla mushroom crop items, which breaks our rule "wild mushrooms only from Zone 4, Mushroom = T15"; (3) the
  edible mushrooms (Mana regen, Stamina, Slow, Poison) cut across our food-family rules (Mushroom = Strength only).
- **Verdict: FOLD the creatures (MIT, credited), do NOT use the crop overrides or the kebab.** Not "pack whole" (section 4).

## 1. Does it load on our 0.7 server? (VERIFIED)

Method: `tools/smoke_test.py` cannot take a `.zip` through `--jar` (it needs a `<Mod>-<ver>.jar` name and copies it as `<Mod>.jar`; a `.jar`
is loaded as a Java plugin and fails with an NPE: "Failed to load plugin ...Mycology.jar", no Main class). So I ran the smoke from a
scratch wrapper that did the same run but copied the file as `Mycology.zip` (`--light --skip-pack-audit`; the real SET, 37 mods + the 15
pack mods + Mycology). No repo file changed.

| Check | Result |
|---|---|
| Boot | `Hytale Server Booted!` after 76 s, clean stop, our 36 ready lines present (the 37th "no ready line" is Mycology itself - an asset pack has none) |
| Version range | WARN `targets server version range '>=0.6.8 <0.7.0' ... 0.7.4` + SEVERE `One or more asset packs are targeting an older server version`. **Only a warning, it does not block loading.** (The smoke test prints Mycology under "not made for game 0.7.4".) |
| Asset validation | 1 new record: `Food_Kebab_Meat_Mushroom` - `[LOC] Key 'server.items.Food_Kebab_Meat_Mushroom.description' does not exist in server.lang` (cosmetic: its lang file has the name but no description). The other 11 "Failed to validate" records are the same ones as before (NoCube Orchard x3, Zip Line x7, Spellbook_Bishop) - not Mycology. |
| NPC roles / models | all 19 roles + 19 `Tamed_*` roles + 19 models loaded; no `FAIL` line for any Mushrim (the only NPC FAIL is `Rb_Bridge_Guard`, River Bridges, not ours to fix here) |
| Spawns | 38 WARN lines: `NPCSpawn Mushrim_X_WorldNPCSpawn references multiple times NPC Mushrim_X. Ignoring all but first.` Each spawn file lists the same NPC 3 times (SpawnBlockSet Grass / Soil / Mud); the engine keeps only the first (Grass). Author bug, harmless. |
| Lang | the 20-line `server.lang` merges with ours (key-merge, no clash: only `items.Food_Kebab_Meat_Mushroom.name`, `memories.categories.Mushrim.title`, 19 `npcRoles.Mushrim_*.name`). The 81 "multiple definitions" warnings are the same as the baseline (ours / Orchard). |
| 0.7 breakage in its own data | **`Food_Instant_Heal_T2` is not in Assets.zip 0.7.4** (the only food effect is `Food_Instant_Heal_T1`; vanilla `Food_Kebab_Mushroom` now uses T1 + `HealthRegen_TierCheck_T2`). Mycology uses it in `Plant_Crop_Mushroom_Glowing_Red` and `Food_Kebab_Meat_Mushroom`. It is inside `InteractionVars`, so the loader did not flag it; at eating time the instant heal is probably skipped or logs an error (UNVERIFIED in game). Every other id it references exists (checked all `EffectId` / `Parent` / `Reference` values). |

If the range check ever blocks loading (a later server build that enforces it): the only fixes are the author raising `ServerVersion`, or
folding the files into our own pack (MIT) so no foreign manifest is checked. Nothing to do today.

## 2. What it ships and overrides (VERIFIED against Assets.zip)

541 files (the manifest says `IncludesAssetPack false` but the zip is a plain asset pack; there is no code). 21 paths already exist in
Assets.zip, so it overrides 21 vanilla files; everything else is new:

| Kind | Count | Notes |
|---|---|---|
| Overrides: `Server/Item/Items/Plant/Crop/Plant_Crop_Mushroom_<Cap/Common/Flatcap/Glowing/Shelve>_*.json` | 19 | the 19 wild-mushroom crop items. Adds `Interactions.Secondary` = `Root_Secondary_Consume_Food_T1/T2` + `InteractionVars` (instant effect) so the mushroom can be eaten. Also **removes** `InteractionHint pick`, `PhysicalMaterialId Foliage`, `TextureComputedColor` and `IsWeaponBreakable:false`; the glowing ones lose their vanilla poison-on-eat. |
| Override: `Server/NPC/Groups/Capture_Crate.json` | 1 | adds `*Mushrim*` to the capture-crate list (Visscas_Slime_Stuff, Mods folder only, also overrides this file; not in the pack) |
| Override: `Server/Languages/en-US/server.lang` | 1 | key-merged, fine |
| New: `Plant_Seeds_Mushroom` / `Plant_Crop_Mushroom_Block_*` / `Plant_Crop_Mushroom_Cap_Brown` item ids | 0 changed | **`Plant_Seeds_Mushroom`, the giant mushroom blocks and the spore block are NOT touched.** Only the 19 pickable crop items. |
| New items | 1 | `Food_Kebab_Meat_Mushroom` ("Meat and Mushroom Skewer", T3, Uncommon, Cooking Bench Prepared: stick + 2 Meats + 2 Mushrooms; effects `Food_Instant_Heal_T2` (missing) + `HealthRegen_TierCheck_T2` + `Meat_TierCheck_T2`) |
| New NPC roles | 38 + 19 | 19 `Mushrim_*` (Template_Animal_Neutral, 38 HP, wander 12, tameable) + 19 `Tamed_Mushrim_*` (Template_Livestock) |
| Spawn / drop / model files | 19 + 19 + 19 | spawns in 4 Zone-1 environments by day (hours 6-18) |
| UI / art | 27 UI (Memories page: 19 npc cards + 2 category icons...), 342 animation files, 19 blockymodels + textures, 19 generated icons | |

Mushroom effects it adds to the 19 crop items (eating one):

| Group | Effect |
|---|---|
| Cap Brown, Cap Green, Common Brown, Flatcap Blue / Green, Shelve Brown / Green | heal T1 (about +5 %) |
| Cap White, Common Lime, Shelve Yellow | heal T1 + `Food_Stamina_Regen_Tiny` |
| Common Blue | heal T1 + `Mana_Regen_Low` |
| Glowing Blue | `Mana_Regen_High` (T2 chain) |
| Glowing Green | `Food_Stamina_Regen_Small` (T2 chain) |
| Glowing Red | `Food_Instant_Heal_T2` (missing in 0.7) |
| Cap Poison, Cap Red, Glowing Orange, Glowing Purple | `Poison_T1` (you poison yourself) |
| Glowing Violet | `Slow` |

Mushrim: all 19 spawn in `Env_Zone1_Forests`, `Env_Zone1_Autumn`, `Env_Zone1_Azure`, `Env_Zone1_Plains`, daytime, 38 HP, and each drops
**exactly 1-3 of its own vanilla mushroom crop item** (Choice weight 100, no random miss). The Brown Cap Mushroom is our **T15
Mushroom crop** item.

## 3. Duplicates and clashes (PROJECT-RULES 2)

### 3.1 vs OUR mods

| Their thing | Ours | Clash? | Decision |
|---|---|---|---|
| Mushrim drop 1-3 `Plant_Crop_Mushroom_*` in Zone 1, 38 HP | Balance-P6: "wild mushrooms only from Zone 4" (removed in Zones 1-3 of new land); `tier_tags.MUSHROOM_ROWS` Cap Brown = T15; SkyyGear F-pickup / hit gate keys on those ids (`PK_ROWS`, 15-step ladder); SkyyBazaar prices (Cap Brown 456.75, P7); Collections "Mushroom" line counts the 19 ids | **YES, big.** A T1 player kills a 38 HP critter for a T15 crop worth hundreds of coins; the tier gate only checks blocks / F-pickup, not mob drops | Do not run the Mushrim as written. Fold with our edits: spawn only in Zone 4+ environments (`Env_Zone4_Forests`, `Env_Zone4_Jungles`, `Env_Zone4_Wastes` ...), drops = something not T15 coins (a Mushrim Spore Cap item or the spores), see 4 |
| Edible raw mushrooms: Mana Regen, Stamina, Slow, self-Poison | SkyyCooking food families (Veggie = Health, **Fruit = Mana**, Meat = Stamina, **Mushroom = Strength only**, "one food type, not all 3", Skyy 2026-10-16); Cooking 0.1.12 left mushrooms "not edible in vanilla" on purpose | **Yes** (Mushroom giving Mana / Stamina breaks the one-food-type rule; Mana from food is a Fruit job; Poison / Slow = trap items) | Do not use the 19 crop overrides. Raw mushrooms stay vanilla (not edible). If Skyy wants raw mushrooms edible, do it in SkyyCooking as a Strength-only snack, never Mana / Stamina |
| `Food_Kebab_Meat_Mushroom` (T3 stick + 2 Meats + 2 Mushrooms) | SkyyCooking dishes: Mushroom Skewer (vanilla `Food_Kebab_Mushroom`), Hunter's / Forest / Woodland Skewer, Forager's Pie ... all graded G0-G12 with family numbers | Overlap (a Meat + Mushroom skewer) and it is ungraded, uses a missing effect, would escape the family rule | Skip it. Our Cooking can add a "Meat and Mushroom Skewer" dish itself (Stamina + Strength) if wanted; idea only |
| 19 tamable Mushrim + `Tamed_*` livestock roles (feed Plant_Crop_Corn_Item / Feedbag) | SkyyPets: per-profile RECORDS (never items), roster `research/Pets-Roster.md` (~110 pets, vanilla model ids at runtime), Pets-Roster row 63 `Mushee` ("no vanilla role") | Different system: Mycology tames a world NPC (vanilla tame), ours summons a record. Same idea (a mushroom critter) - Mushrim are exactly the "mushroom pets" the roster lacks | **Best of each:** Mycology's 19 models as pet LOOKS (pet kind `Mushrim`, skins = the 19 variants), by model id at runtime (`Mushrim_Cap_Red_Model_Asset`) - allowed as a read-by-id (PROJECT-RULES 2, "react by id"), not a copy. Vanilla tame of Mushrim should be OFF (a second pet system); capture-crate use is harmless |
| Memories category `Mushrim` (19 collectible cards) | vanilla Memories + AutoMemories (Mods folder) | none in our mods | harmless; keeps vanilla Memories flow |
| `*Mushrim*` in Capture_Crate | none of ours | Visscas_Slime_Stuff (not in pack) overrides the same file | only if both ever packed (then one wins, no merge) |

SkyyMobs: Mushrim are neutral animals; no `Mushrim_*` row exists in the rank table (UNVERIFIED how SkyyMobs treats an unknown neutral role: if
it levels every NPC by zone, a Zone-1 Mushrim becomes Lv 1-20; if it skips neutrals, it stays 38 HP). Check before any spawn.

### 3.2 vs the pack mods in PACK.md / `PACK_THIRD_PARTY`

| Pack mod | Overlap with Mycology |
|---|---|
| NoCube Orchard (`NoCube:[NoCube's] Orchard`) | none: no mushroom item, no shared path (VERIFIED by path scan; fruit juices only) |
| DynamicSeasons (BlueOrbit) | patches 14 crops + overrides `Root_Secondary_Consume_Food_T1`; Mycology's mushrooms *reference* that root interaction, so after DynamicSeasons they eat through its version (harmless; no path clash, no mushroom file in DynamicSeasons) |
| Dragon Nestkeeper (BlackAures) | 3 `Nestkeeper_Mushroom_Food_*` dragon foods (different ids); no clash. Its dragons use vanilla tame like Mushrim, no overlap |
| The Armory, StructureV2, DungeonBosses, River Bridges, Souls like Bosses, Multitools, Perfect Parries, BetterMap, WeaponCustomHUD, ZipLine, ZoneViewControl, More Crossbow Tiers | none (path scan: only the key-merged `server.lang` is shared). Souls like Bosses has `Plant_Crop_Mushroom_Shelve_Night` (its own id, no clash) |
| Mods folder only, NOT packed, that do clash | **Taintedroots 1.1.0** overrides 3 of the same crop files (`Cap_Red`, `Common_Brown`, `Shelve_Brown`) and **Visscas_Slime_Stuff** overrides `Capture_Crate.json`; Alec's Tamework also has a mushroom seed. All stay OFF (not in `PACK_THIRD_PARTY`) - never enable Taintedroots with Mycology |

No other pack mod adds wild mushroom critters, edible mushrooms or a mushroom pet; so there is no duplicate to drop. The only duplicate is
inside our own plan: a mushroom pet (Mushee / Mushrim) and the Mushroom food families.

### 3.3 What would change in OUR mods either way (rows by id)

| Mod | Row / id | Change |
|---|---|---|
| `tools/tier_tags.py` | `MUSHROOM_ROWS`: `Plant_Crop_Mushroom_Cap_Brown` (crop), `Plant_Seeds_Mushroom` (spore), `Plant_Spores_Mushroom_Eternal` | **none** (Mycology changes no id) |
| SkyyCollections 0.2.32 | `MUSH` regex `Plant_Crop_Mushroom_(Cap|Common|Flatcap|Glowing|Shelve)_` = 19 ids | none (same ids). Open: do Mushrim drops count in the Mushroom line (only block / F-pickup do today)? UNVERIFIED |
| SkyyGear 0.3.40 | `PK_ROWS` (F-pickup tier gate on the same 5 prefixes) | none; but it does not cover mob drops - see the fix in section 4 |
| SkyyBazaar 0.2.1 | sells the same 19 ids | none |
| SkyyCooking 0.1.16 | `Food_Kebab_Meat_Mushroom`, raw-mushroom eating | only if Skyy wants a Meat + Mushroom dish or an edible raw mushroom (Strength only) |
| SkyySacks 0.8.28 | food list (line 1093: `Food_Kebab_Mushroom`, `Food_Salad_Mushroom` ...) | add `Food_Kebab_Meat_Mushroom` only if the kebab is kept (default: skipped) |
| SkyyMobs 0.1.18 | rank rows for `Mushrim_*` (normal, neutral critter) + the zone level | add 19 rows (or one wildcard `Mushrim_*`) before any Mushrim spawns |
| SkyyPets (0.4.12 / the new 0.4.13) | pet kind `Mushrim` with the 19 model ids as skins (Pets-Roster) | optional, later round; model ids are checked against the loaded assets at build, so the build must tolerate Mycology absent |
| `tools/deploy_set.py` | `PACK_THIRD_PARTY` | only if "pack whole" is chosen (section 4) |

## 4. Verdict

**FOLD the creature part (MIT: copy with the licence text + credit), skip the rest.** Not "pack whole" because:

1. The Zone-1 spawn + guaranteed T15 drop bypasses the gathering-tier design and the economy (3.1). We cannot fix it in the pack: the
   rule is "never ship a file overriding their item ids", and their spawn / drop files are theirs; patching them in place means editing a
   foreign mod. MIT lets us fold, so the fix is ours to make.
2. The 19 crop overrides cut across the food-family rules and remove the vanilla pick hint, hit material and weapon-unbreakable flag
   (mushrooms become weapon-breakable) - behaviour we did not choose.
3. It targets 0.6.x and already has one broken 0.7 reference (`Food_Instant_Heal_T2`), so as-is it would need the author or us anyway.

What "fold" means here (proposal, nothing built):
- **Keep:** the 19 Mushrim models / animations / textures, `Server/Models`, the 19 `Mushrim_*` + `Tamed_*` roles, UI Memories cards, names
  (about 500 of the 541 files). Credit: "Mycology by MMartinsar (MIT)" in PACK.md + server credits, MIT text kept in the folded folder.
- **Change (ours):** spawn environments -> Zone 4+ (`Env_Zone4_Forests`, `Env_Zone4_Jungles`, `Env_Zone4_Wastes`; vanilla Zone-4 mushrooms are
  there too, so it matches the P6 design "mushrooms from Zone 4"); fix the duplicated NPC entries in each spawn file; drops = not the T15
  crop (default: a Mushrim cap item that sells at a low price, or the spores `Plant_Seeds_Mushroom`; Skyy picks); tameable stays OFF (our pet records
  replace it); give them SkyyMobs rows and levels.
- **Drop:** the 19 crop-item overrides (raw mushrooms stay vanilla), `Food_Kebab_Meat_Mushroom` (idea only; our Cooking has the dish
  system), the `Capture_Crate` override (add only if we want crate capture).
- **Where the fold lives:** a new asset-only folder (for example `SkyyMushrims`, in its README / `INDEX.md`, not a code mod) or inside the
  next SkyyMobs / SkyyPets round. Pets get the models by id at runtime once they exist.
- Cheaper alternative if Skyy does not want a new folder: **LEARN only** - take the idea and the 19 looks for pets (look names + the
  tame / feed pattern), draw our own Mushree line later. This is the default if the zone-gate fix is not wanted this week.

"Pack whole" stays possible only as a short test: put `MMartinsar:Mycology` in `PACK_THIRD_PARTY` and set Zone-1 spawn off via a
SkyyMobs "never spawn" list (needs a new rule; UNVERIFIED that one exists); it still leaves problems 2 and 3.

## 5. Questions for Skyy (each with default)

1. **Fold only the Mushrim creatures (Zone 4+), and leave the edible-mushroom overrides + kebab out?** [Yes, fold; mushrooms stay vanilla.]
2. **Mushrim drops: a cheap Mushrim cap item (low price, Cooking ingredient) instead of the T15 crop?** [Yes; the T15 crop stays a Zone-4+ / Zone-5 plant.]
3. **Use the 19 Mushrim looks as pet skins (SkyyPets kind `Mushrim`) and keep vanilla taming of them OFF?** [Yes; pets stay records.]
4. **Want a Meat + Mushroom Skewer dish in SkyyCooking (Stamina + Strength, graded like the others)?** [Later, with the next Cooking dishes.]

## 6. For the local session (UNVERIFIED unless said)

1. `tools/smoke_test.py` cannot add a `.zip` pack mod through `--jar` (needs `<Mod>-<ver>.jar`; the file would be copied as `.jar` and loaded as a Java plugin). A `--pack <path>` option (copy under its own name) would let every pack check run a smoke; I used a scratch wrapper. Small tools fix.
2. Whether the 3.3 `Food_Instant_Heal_T2` failure is silent or an error at eat time (VERIFIED missing in Assets.zip; the loader did not warn).
3. How SkyyMobs levels an unknown neutral role (`Mushrim_*`) and whether Mushrim drops count in the Collections Mushroom line.
4. MIT licence on the CurseForge page (Skyy said MIT; the manifest has no licence field).
5. Whether vanilla `Template_Livestock` tamed Mushrim follow / despawn badly on our island worlds (not played).
6. Smoke log kept: `tools/dev/scratch/smoke/20261023-085301.log` (the pack run with Mycology on; pack with `python tools/tidy_local.py --yes --scratch smoke`). Not played in game.
