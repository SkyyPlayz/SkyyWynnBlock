# LOCAL-RESUME - work split between the local session and Cobb (Skyy's Grok bot)

Made 2026-10-17 by Cobb (Skyy: "make a local-resume, so we can do a clear work split. and keep what you are working on listed so
there isnt a conflict. so local can keep working while you handle big builds."). Read this after RESUME.md, every session.

## Who does what

| Local session (Skyy's PC) | Cobb (Grok bot, cloud) |
|---|---|
| Deploys (`tools/deploy_set.py`, skill `skywynn-deploy`) | Big builds (spec -> build / patch scripts -> critics -> fix) |
| Smoke tests, game logs (`tools/log_scan.py`) | One fresh Claude Code / OpenRouter session per job |
| Small bug fixes and small fixes | Design, docs specs, beta-test video reviews |
| Trusted rebuild of every Cobb PR against the real install, then cross-check, pin, deploy | Hands off through ONE pull request per job, no jars |
| Assets.zip steps Cobb marks UNVERIFIED | Never deploys, never touches the game install or Skyy's PC |

Server jar and game-file rules for cloud builds: CLOUD-RESUME.md "Cloud build trial".

## Work locks (check before you start anything)

A mod listed here is LOCKED to that owner. The other side does not edit its scripts, patches, harness or pins until the lock
is released. Cobb adds and removes Cobb's rows; the local session adds and removes its own rows if it wants to reserve a mod.
Release a row when its PR is merged (or the job is dropped) and log it in docs/log.

| Mod(s) | Owner | Job | Branch / PR | Since | Status |
|---|---|---|---|---|---|
| SkyyGear, SkyyMobs (+ loot) | Cobb | RESUME NEXT 3: Armory / Void Armor sets + weapons as mob drops with our modifiers (other sets TODO until author OKs) | `cloud/trial-armor-drops` (PR link added when opened) | 2026-10-17 | Building |
| SkyyWorldGen, SkyyAccessories, SkyySacks, SkyyCollections, SkyyBazaar, SkyySkills (+ tools/tier_tags.py, tools/skyyench.py) | Local | Zone ores + alloys + Furnace Charm (research/Zone-Ores-Alloys-Spec.md) | local, no PR | 2026-10-17 | Building |

Free for the local session: everything not in the table (e.g. the Void Charms rename round in RESUME, skipping Gear until the row
above is released).

## Rules
1. Before any job, pull and read this table. If your mod is locked by the other side, pick other work or ask Skyy.
2. Cobb never works on a mod the local session has listed or has uncommitted changes to that Skyy mentioned.
3. Version numbers: Cobb takes the next free version and says so in the PR; if the local session bumps the same mod anyway,
   the local session's version wins and Cobb rebases.
4. Shared files (RESUME.md, STATUS.md, HANDOFF.md, PACK.md, docs/log): Cobb only appends in its PR; the local session merges.
5. Never edit SkyyGear-Plan.md or SkyyGear-Stat-Catalog.md (either side, unless Skyy says).

## Undo
Delete this file and its RESUME.md pointer; CLOUD-RESUME.md "Cloud build trial" has the pre-split rules.
