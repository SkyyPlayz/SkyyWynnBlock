# Pack candidates survey, 2026-10-18 (Kazzy Pets and Mounts, Workbench Tier Keeper, GlymeraHeads, RG Buckets)

Skyy's words: `docs/answered/project.md` 103-105 (plus the bucket line from the main session). Sources: the jars / zips in Skyy's Mods folder (copied to scratch,
read only, scratch deleted) and the CurseForge / GitHub pages. Licence on the page = the CurseForge field; the linked licence pages were not readable.
Nothing here was tested in game. Answers go in `docs/answered/project.md`; pack entries in `PACK.md`.

## Summary

| Mod | Licence | Verdict |
|---|---|---|
| Kazzy's Pets & Mounts 2.5 (page; Mods folder has 2.0.5) | All Rights Reserved, no modpack statement | SKIP (clashes with SkyyPets) |
| Workbench Tier Keeper 1.0.0 | MIT (CurseForge + GitHub LICENSE) | FOLD the idea into our code (small); never run it beside KeepBenchTiers |
| GlymeraHeads 6.0.0 | All Rights Reserved, no modpack statement | ASK the author; as shipped the helmets break our bands |
| RG Better Lava and Water Buckets 1.1.4b | All Rights Reserved, no modpack statement | SKIP; keep our own Infinite Water Bucket |

## 1. Kazzy's Pets & Mounts (Kazopalooza)

- **Fit:** manifest ServerVersion `*`, page tag "Early Access", newest file Jan 2026. Assets only, no Java. Not run on 0.7.x.
- **Adds (zip):** 144 items (1 Egg Nest bench, 1 Mount Collar, ~142 "Egg Spawner" items: 54 mount, 88 pet), 152 NPC roles (97 Pet, 54 Mount, 1 wandering merchant),
  1 barter shop (Egg Trader, pays Ingredient_Life_Essence 50-75 per egg, restock 3 days), 1 Feran merchant model, 4 spawn files (`Spawns_Zone1..4_*`, they add the
  merchant at weight 0.35 to the vanilla animal spawn lists, so they replace those vanilla files = clash with any mod editing the same spawns). Egg bench recipes cost
  100 Life Essence. No commands. Mounts / pets are invulnerable NPCs that drop their egg when sent away; nothing is saved per player.
- **Duplicates:** SkyyPets (own pet slots, hatchery, levels, summon slot; `research/cloud/Pet-Core-Spec.md` already says Kazzy stays off) and its mount phase 5;
  Dragon Nestkeeper (kept for the dragon only, `research/Nestkeeper-Pack-Check.md`); DarkMatter / More / Traveling Mounts (judged in `docs/answered/pets.md` 47).
  The Egg Trader is a second shop path for Life Essence outside SkyyMerchants / Bazaar. Keep-best rule: ours wins (levels, slots, saved data).
- **By id:** nothing maps. Its eggs are one-use spawners with no owner, while SkyyPets keeps one owned record per pet slot. No tier for Grades / tier tags / Bazaar.
- **Recommend:** SKIP. Its NPCs use vanilla `Appearance` ids (e.g. Boar), so there are no custom mount models to take. Idea to learn: the Mount Collar
  (hold it, press F on a mount, it returns to its egg) for SkyyPets phase 5.

## 2. Workbench Tier Keeper (Samiracle_)

- **Licence:** MIT on CurseForge and GitHub (Sami2EaCOS/WorkbenchTierKeeper). The LICENSE text names "Buuz135" as copyright holder, so keep that notice if code is copied.
  OK to fold with the notice.
- **Fit:** ServerVersion `*`, page "Early Access", Jan 2026. Not run on 0.7.x.
- **Adds:** 10 classes (break / place block systems, per-chunk tier map, item metadata key `wtkeeper:tier`, `WorkbenchPick` interaction), 17 overrides of vanilla
  `Server/Item/Items/Bench/Bench_*.json` (tier state on the item) and a lang file with "Tier N" description lines. No commands, no NPCs.
- **Duplicates:** (a) `KeepBenchTiers-1.4.1` (NoeKing, ServerVersion ^0.7.0, runtime only, no bench JSON; also a sticks recipe and unlimited teleporters) does the same job: pick ONE.
  (b) `VisualBenchTiers` 1.2.0 (Cified, models for tier 2+ benches) overrides 5 of the same `Bench_*.json` files (Alchemy, Armour, Farming, Tannery, Weapon): one winner per file,
  the loser's text / model is lost. (c) `UnifiedWorkbench-0.10` (master bench, ServerVersion 0.7.*) is a different job, not a duplicate.
  Ours: nothing in our build scripts keeps a bench tier today. `tools/skyywbtab.py` already notes that Tier Keeper and Extended Backpacks both override `Bench_WorkBench.json`; our tab is added at runtime so it survives either.
- **By id:** none needed (no new ids). Our `Bench` own-ladder tag (`ladder_tag(n, "Bench")`) could be shown on the same item text.
- **Recommend:** FOLD (small lean round): copy the idea, not the 17 JSON overrides (they go stale on game updates and collide with VisualBenchTiers). A runtime break / place
  system storing the tier in item metadata, tier line added from code, owned by whichever mod owns bench code (SkyyGear or SkyySacks). Until built: pack ONE of KeepBenchTiers / Tier Keeper, never both.

## 3. GlymeraHeads (GlymeraCraft)

- **Licence:** All Rights Reserved; the page is silent on modpacks (the same author's farming mods said "free for personal and server use", `research/Farming-Mods-Survey.md`, but not Heads). Cannot fold; packing needs the author's OK.
- **Fit:** page says "stable 5 only" yet lists file 6.0.0 under 0.7 (Oct 13, 2026); manifest ServerVersion `*`. Not run.
- **Adds:** Java plugin + assets. 153 `GlymeraSkull_*` placeable blocks (decor, `Furniture.Beds` category, stack 16), 140 `GlymeraHelm_*` helmets (page says 139),
  1 mystery skull + 1 mystery helm (two workbench recipes; `MysteryCraftSystem` swaps the crafted result for a random one). Command `/glymeraheads reload` (OP, re-reads
  `plugins/GlymeraHeads/helm_overrides.json`, positions only). The helmets have no recipe of their own; they come only from the mystery craft.
- **Helmet stats (read from the JSON):** Epic, ItemLevel 50, Physical + Projectile resistance 8% each, +14 Health (Additive), 180 durability, hides hair / ears. Same for every mob.
- **Level bands:** ItemLevel 50 is zone 3 (T7 Cobalt 40-48 / T8 Chromium 48-55 in `research/Level-Bands-20-Spec.md`), yet the mystery craft needs only Bone + Wildmeat / Iron Bar
  from a zone-1 bench, so it would out-gear zone-1 and zone-2 helmets. We cannot ship an override of their ids. Our code can only re-grade by id at runtime
  (Grades reads item ids; confirm the Head slot is covered) and cannot add a tier tag to their lang text.
- **Duplicates:** none for the skull decor in our mods or the pack. The helmets overlap our head slot / armor ladder.
- **Recommend:** the SKULL blocks are the good part (decor, no stats). A pack mod can only be switched off whole, so ask GlymeraCraft for (a) pack permission and
  (b) a build without the stat helmets, or cosmetic-only ones. Until answered: SKIP. Building our own would need 150 new mob models (large art job), not worth it.

## 4. RG Better Lava and Water Buckets (Rargelinha) - page only, not in the Mods folder

- **Licence:** All Rights Reserved; no modpack statement. File RGMtbuck-1.1.4b.zip, Apr 11, 2026, tagged "Early Access". Not inspected.
- **Adds (page):** 4 buckets: Iron 10, Silver 20, Gold 40, Cobalt 80 charges; one source block per click; partial refills; recipe = base metal + Adamantite + Water Essence.
  **Lava is NOT in it yet** (listed under "Planned"), so the title over-promises. Dependencies not shown.
- **Infinite Water Bucket plan** (`research/Farming-Mods-Survey.md` section 3: SkyyGear `Tool_SkyyInfiniteWaterBucket`, 15 Plant_Crop_Mana3 + 8 Container_Bucket at the Farming bench, MID GAME):
  a different job. Theirs is a finite early / mid bucket, ours is the endgame farming reward, so they would coexist by id. But their recipe needs Adamantite (T10) for an Iron (T2) bucket, which is out of band.
- **Silver / Gold:** `tools/tier_tags.py` has no Silver or Gold steps (left untagged on purpose), so no tag clash. Their order Iron < Silver < Gold < Cobalt is vanilla order, not our 15-metal ladder; the charge counts would need the bands re-applied.
- **Watering can:** our can refills from a hand-made raycast on `Water_Source` / `Water`; their buckets place real `Water_Source` blocks, so our can could refill from one. No by-id link; no conflict found, but unverified (jar not read).
- **Recommend:** SKIP (ARR, EA-era, no lava yet, recipe breaks bands). Keep our own Infinite Water Bucket. If Skyy wants multi-charge buckets, ours is a small build: charge-state items in SkyyGear using the same `PlaceFluid` pattern.

## Questions for Skyy (defaults in [brackets])

1. Kazzy's Pets & Mounts: skip, SkyyPets stays the only pet system? [Yes, skip]
2. Bench tier keeping: fold the Tier Keeper idea (MIT) into our own code as a small round, then drop KeepBenchTiers? [Yes; for now keep KeepBenchTiers only, Tier Keeper off]
3. GlymeraHeads: ask GlymeraCraft for pack permission and a version without the stat helmets? [Yes, ask; skip until answered]
4. Multi-charge buckets: skip, and maybe build a small charge-bucket line of our own later? [Skip; no own line yet]
