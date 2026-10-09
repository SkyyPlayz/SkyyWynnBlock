# SkyWynn - ARCHITECTURE (how the pack is built, 2026-10-09)

How the mods fit together, how they are built, and how they reach the game.
Short on purpose. Each part links to the file that holds the detail.

## 1. The big idea

- SkyWynn is a family of standalone `Skyy*` server mods for Hytale.
- Every mod works alone. Together they make the pack.
- Mods never depend on each other. They share data through one JVM map: `skyy.bridge`.
- Player data is per profile (`tools/PROFILES-CONTRACT.md`).
- Each mod saves under `<world>/mods/Skyy_Skyy<Mod>/` (example `Skyy_SkyyVault`). No version in the name, so data survives updates.
- Every setting an owner might change is editable in game: SkyWynn Menu -> Server Setup (`tools/CONFIG-CONTRACT.md`).

## 2. The mods

One folder per mod. Live versions: [HANDOFF.md](HANDOFF.md) section 1 (= the SET in `tools/deploy_set.py`).

### Player systems

| Folder | What it does |
|---|---|
| `SkyyProfiles` | profiles = full saves (default cap 6), delete with undo, Health saved per profile |
| `SkyyClasses` | pick a class, class kits, Priest healing |
| `SkyySkills` | skills + XP, class weapon skills, class Mana pools, dodge roll on a sprint press |
| `SkyyTrees` | skill trees: gathering, Acrobatics, Exploration, Alchemy, Smithing, class trees |
| `SkyyCooking` | cooked food gets a Grade from your Cooking level |
| `SkyyExploration` | Exploration skill, spots, island checklist, Unclaimed Luggage |
| `SkyyFishing` | our fishing, stage 1: bench, rods, reels, Zone 1 fish (HyFishing stays until stage 2) |
| `SkyyCollections` | collections and tiers that unlock recipes and bags |

### Items and combat

| Folder | What it does |
|---|---|
| `SkyyGear` | gear rarity, item levels, identify, reforge, mystery bags, tooltips |
| `SkyyArmory` | our own weapons: wands, staffs, spellbooks, kunai, Monk moves, wand signature |
| `SkyyAccessories` | Accessory Bag, booster accessories, Lantern |
| `SkyySacks` | Magic Bags (pocket dimension): auto-collect, refill, crafting from bags |
| `SkyyMobs` | mob levels + difficulty |

### Money and trading

| Folder | What it does |
|---|---|
| `SkyyCoins` | coin purse, /pay, death penalty |
| `SkyyBank` | bank + daily interest |
| `SkyyBazaar` | Bazaar market, a tab per bag type, search |
| `SkyyAuctions` | auction house (buy it now) |
| `SkyyVault` | extra storage pages |

Coins, Bank, Bazaar and Auctions will merge into one mod, SkyyEconomy (`docs/plans/SkyyEconomy-Plan.md`).

### World and social

| Folder | What it does |
|---|---|
| `SkyyIslands` | private islands, co-op, visitors, /hub |
| `SkyyWorldGen` | Zone 1 test island (admin only for now) |
| `SkyyParty` | parties, TPA buttons |
| `SkyyGuilds` | guilds + guild bank |
| `SkyyRanks` | ranks + permissions made in game |
| `SkyyEssentials` | /tpa, /trade and the few commands vanilla lacks |

### Screens

| Folder | What it does |
|---|---|
| `SkyyHud` | HUD widgets + editor (move / scale / hide), minimap |
| `SkyyMenu` | SkyWynn Menu, Stats page, player Settings, Server Setup for admins |

### Test probes and retired mods

| Folder | What it is |
|---|---|
| `SkyyUiProbe` | dev probes for UI tests (op only) |
| `SkyyGatherProbe` | gathering probes, A + B jars (remove after Skyy's test) |
| `SkyyTownProbe` | Zone 1 town probe (remove after Skyy's test) |
| `SkyyKeyProbe` | which keys reach the server (remove after Skyy's test) |
| `SkyyReelProbe` | RETIRED - replaced by SkyyFishing |
| `SkyyMonkProbe` | RETIRED - Monk moves live in SkyyArmory |
| `SkyyRolls` | RETIRED - replaced by SkyyGear; never comes back |

Third-party mods in the pack: `PACK.md`.

## 3. How a build works

| Step | What happens | File |
|---|---|---|
| 1 | Each mod version is ONE Python script with the Java source inside. | `Skyy<Mod>/build_skyy<mod>_<ver>.py` |
| 2 | The script compiles the Java with javassist through jpype. No javac. | `tools/skyybuild.py`, `tools/javassist.jar` |
| 3 | It reads the game's `HytaleServer.jar` + `Assets.zip` read-only. Game files are never committed. | - |
| 4 | Vanilla-based art is made at build time, straight into the jar. | `tools/skyyart.py` |
| 5 | A new round's harness runs every new code path. Not every older version has one. | `Skyy<Mod>/test_skyy<mod>_<ver>.py` |

- **No harness yet:** SkyySacks before 0.7.8, and the live SkyyAuctions 0.1.2, SkyyRanks 0.1.1 and SkyyCoins 0.1.5. The rule is in `.claude/workflows/skywynn-round.js`.
- **New version = a patch script.** `tools/<mod>_<ver>_patch.py` makes the next script from the current one.
  Edit the patch, never the generated script (except the 4 Skyy hand-edited - see RESUME "Never forget").
- **Shared kits** (copied into each jar, so still no runtime links):
  `tools/skyyui.py` (vanilla-look UI), `tools/skyycfg.py` (Server Setup), `tools/skyymove.py` (movement),
  `tools/skyywbtab.py` (Workbench tab).
- **Rules for build agents:** `tools/AGENT-BRIEF.md`.
- **Round sizes** (full / lean / ultracode): `PROJECT-RULES.md` section 4.

## 4. Deploy and rollback

All mods ship together as one pinned set: the SET in `tools/deploy_set.py`.

| Step | Command | What it does |
|---|---|---|
| 1 | (game closed) | never kill the game; the deploy waits |
| 2 | `python tools/backup_deploy.py` | backs up Skyy jars, world `config.json`, every `Skyy_*` data folder |
| 3 | `python tools/deploy_set.py --yes` | the ONLY deploy path; copies the SET jars, turns on the pack mods, switches off RETIRED mods |
| 4 | `python tools/record_deploy.py ...` | writes the deploy into tests, index, HANDOFF, checklist and log in one go |
| 5 | `python tools/tidy_local.py --yes` | tidies the local-only files |

- `tools/deploy_set.py` refuses to run while a Hytale server runs.
- It refuses a SET that splits SkyyArmory from its partner versions of SkyySkills + SkyyClasses.
- **Rollback floors** (versions you must never go below): HANDOFF section 1 + the comments in `tools/deploy_set.py`.
  Read them before any rollback.
- Backups live in the local `backups` folder on Skyy's PC (git-ignored). Its README lists how to restore.
- Full procedure: `PROJECT-RULES.md` section 3.

## 5. Checks (CI)

| Check | Runs where | What it checks |
|---|---|---|
| `tools/ci/lint.py` | GitHub Actions on every push + PR, and locally | Python parses, no game files / big files, no `.ui` files, no underscores in UI ids, command permission rules |
| `tools/ci/crosscheck.py` | locally (needs the game's jar) | every SET jar in ONE JVM: bytecode verify, access audit, player-permission audit |
| `tools/docs_check.py` | locally, before docs commits | no doc line lost, no new broken paths |

Lint must show 0 fails before a pin. The cross-check must say READY.

## 6. Local and cloud sessions

| | Local session | Cloud session |
|---|---|---|
| Runs on | Skyy's PC | the cloud (no PC, no game files) |
| Reads first | [RESUME.md](RESUME.md) | [CLOUD-RESUME.md](CLOUD-RESUME.md) |
| Can build + deploy | yes | no |
| Pushes to `main` | yes | only `CLOUD-RESUME.md` + `research/cloud/` |
| Anything else | - | through a pull request |
| Talks to the other | sends messages | appends to `research/cloud/OUTBOX.md` |

- The local session folds the cloud log (`research/cloud/LOG.md`) into `docs/log/`.
- Full rules: `PROJECT-RULES.md` section 8.

## 7. The UI rule (always)

> **Every custom UI must match Hytale's native look.**
> It should feel like part of the game, not like a mod.
> (Skyy, 2026-09-28 - HANDOFF section 2, rule 0)

- Use vanilla colours, fonts, frames, buttons, spacing and sounds - copied from the game's own UI.
- Build with the shared kit `tools/skyyui.py`. Its contract: `research/Vanilla-UI-Style-Guide.md`.
- Pages are built inline in code. Never ship `.ui` files.
- No underscores in UI element ids.
- No custom UI on the vanilla inventory screen.
- The hard-won UI + command rules: [HANDOFF.md](HANDOFF.md) sections 2 + 3.
