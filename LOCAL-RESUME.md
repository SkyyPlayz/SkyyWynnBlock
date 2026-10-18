# LOCAL-RESUME - work split between the local session and Cobb (Skyy's Grok bot)

Made 2026-10-17 by Cobb (Skyy: "make a local-resume, so we can do a clear work split. and keep what you are working on listed so
there isnt a conflict. so local can keep working while you handle big builds."). Read this after RESUME.md, every session.

## Who does what

**STATUS (Skyy 2026-10-17): Cobb is currently NOT building. Everything in RESUME.md and LOCAL-RESUME.md is on the local
session's table for now. Cobb only does orchestration, design, specs and test-video reviews until Skyy says otherwise.**

| Local session (Skyy's PC) | Cobb (Grok bot, cloud) - NO BUILDING for now (Skyy 2026-10-17) |
|---|---|
| ALL builds now, incl. big ones + the queue below | Orchestration, design, specs, briefs |
| Deploys (`tools/deploy_set.py`, skill `skywynn-deploy`), smoke tests, game logs | Beta-test video reviews, PR reviews |
| Trusted rebuild of Cobb's open PR #17, then cross-check, pin, deploy | Doc-only PRs (like this one), never deploys |
| Assets.zip steps marked UNVERIFIED | Never touches the game install |

Server jar and game-file rules for cloud builds: CLOUD-RESUME.md "Cloud build trial".

## Work locks (check before you start anything)

A mod listed here is LOCKED to that owner. The other side does not edit its scripts, patches, harness or pins until the lock
is released. Cobb adds and removes Cobb's rows; the local session adds and removes its own rows if it wants to reserve a mod.
Release a row when its PR is merged (or the job is dropped) and log it in docs/log.

| Mod(s) | Owner | Job | Branch / PR | Since | Status |
|---|---|---|---|---|---|
| SkyyGear | Local | Gear 0.3.25: multitool merge, accBp cache, GearReq red row, CAD trust for A2 weapons | local, no PR | 2026-10-18 | Building |

Cobb holds no locks now. PR #17 merged + deployed 2026-10-17 (TEST-CHECKLIST 178); the Void Charms Gear texts went into Gear 0.3.19.

## Handed to the local session (from Cobb)

- 2026-10-17 METAL ITEM ART (Skyy: "my Claude can easily do simple designs ... only have Quirk do armor"): the local session makes the
  simple metal item art; Quirk does ARMOR ONLY (in Blockbench). Scope, for every zone metal (Bronze, Thorium, Lead, Dusk, Cobalt,
  Chromium, Azurvane, Adamantite, Slag, Cinder, Mithril, Titanium, Lumen - table in research/Zone-Tiers-Idea.md):
  - Tools: hatchet, pickaxe, multitool, harvester, watering can (fertilizing = a watering can upgrade).
  - Metal weapons, matching the vanilla metal weapon set.
  - Crossbows for every metal.
  - Any other item made from metal. NOT charms (they use their own metals; fix later).
  Method: start from the vanilla model + texture in Assets.zip (Common/Items/Tools, Common/Items/Weapons) and recolour / lightly edit it,
  so each metal looks like its armor family. Make only what's missing (check vanilla, art/, Quirk's tool gap table first).
  Crossbows: More Crossbow Tiers (Serj) is "All Rights Reserved" on CurseForge and still only marked for 0.6.8, so we can't copy its
  textures without Serj's OK. Default: make our own from the vanilla Iron crossbow for all our metals. Optional: Skyy asks Serj.

## Local build queue (from Cobb, Skyy 2026-10-17; start each on Skyy's go, one mod / branch per job)

Private art inputs live OUTSIDE the repo on Skyy's PC: `Hytale mods WORK\SkyWynn-PRIVATE-art\`. They contain vanilla-derived
geometry: never commit, upload or share them. Only our textures go in mods, pointing at vanilla models.
Metals source of truth: `SkyWynn-PRIVATE-art\metal-art\skywynn-metals-build-spec.md` (locked rules, sections 1-8).

1. MINING ARMOR Z2-Z5 into SkyyGear (Mining sets live in Gear GearMine; there is no SkyyForaging mod - local 2026-10-17). Quirk's approved sets (Skyy 2026-10-17): Z2 Lead/Dusk, Z3 Chromium/Azurvane,
   Z4 Slag/Cinder, Z5 Titanium/Lumen. Inputs: `SkyWynn-PRIVATE-art\mining-armor\Z2_Thorium..Z5_Mithril` (each set retextures
   that zone's vanilla base armor). Ship our textures + item defs that point at the vanilla models.
2. METAL VOLUME ART (art only, no game code). Inputs: `SkyWynn-PRIVATE-art\metal-art\` (TASK-metal-art.md, Quirk's zone palette
   cards, her approved Titanium + Lumen tools as the sample, skywynn-custom-weapons-list.md, skywynn-metal-items-inventory.md).
   Make: ore + bar for Lead, Chromium, Slag, Titanium; bars only for Dusk, Azurvane, Cinder, Lumen (+ Electrum = Gold + Silver);
   all 9 weapon families (Wand, Crossbow, Spellbook, Kunai, Bo, Gauntlets, Soul Cage, Great Shield, Mage staff) in all 8 new metals;
   then every other metal item in the inventory. Excluded: charms, bench accessories, dropped vanilla tools (scythe, hoe),
   Foraging / Farming armor, fishing (waits for a full fishing build). The zone palette cards are enough (no per-metal cards).
3. METALS BUILD (unassigned until Skyy says): ores, spawn, smelting, alloys, Fortune, tools/weapons per the spec.
   STATUS 2026-10-17 (local): ores + spawn rules + smelting + alloys + Electrum + Furnace Charm are LIVE (TEST-CHECKLIST 177;
   research/Zone-Ores-Alloys-Spec.md). Still open: Fortune upgrades (spec 5), metal tools / weapons / mining sets per metal (need SkyyGear after
   PR #17 + SkyyArmory), the 15-step tool tier ladder question (spec 2), real art instead of the build-time recolour placeholders (item 2).

## Rules
1. Before any job, pull and read this table. If your mod is locked by the other side, pick other work or ask Skyy.
2. Cobb never works on a mod the local session has listed or has uncommitted changes to that Skyy mentioned.
3. Version numbers: Cobb takes the next free version and says so in the PR; if the local session bumps the same mod anyway,
   the local session's version wins and Cobb rebases.
4. Shared files (RESUME.md, STATUS.md, HANDOFF.md, PACK.md, docs/log): Cobb only appends in its PR; the local session merges.
5. Never edit SkyyGear-Plan.md or SkyyGear-Stat-Catalog.md (either side, unless Skyy says).

## Undo
Delete this file and its RESUME.md pointer; CLOUD-RESUME.md "Cloud build trial" has the pre-split rules.
