# SkyWynn - RESUME HERE (written 2026-09-28)

Read this first when picking the project back up. It says where everything lives on Skyy's PC, what state things are in, and exactly
what to do next. Detail: `HANDOFF.md` (section 3 = current state, section 6 = the full running log), `OPEN-QUESTIONS.md` (every
decision with its default or LOCKED answer), `SkyWynn-Decisions.md` (change notes), `DESIGN-STATUS.md` (plain-language overview).

## 1. Where things live on Skyy's PC

| What | Path |
|---|---|
| Project folder = this git repo (public: github.com/SkyyPlayz/SkyyWynnBlock, branch `main`) | `C:\Users\SkyLo\Desktop\Hytale mods WORK\SkyWynn PROJECT\` |
| One build script per mod version (Java inside Python) + the built jar next to it (jars are git-ignored) | `SkyyXxx\build_skyyxxx_<ver>.py`, `SkyyXxx\SkyyXxx-<ver>.jar` |
| Patch scripts that derive version N+1 from N (edit the patch, not the generated script) | `tools\<mod>_<ver>_patch.py` |
| Shared build bootstrap (JVM, javassist, assemble, deploy, enable in world) | `tools\skyybuild.py`, `tools\javassist.jar` |
| Deploy the whole set to the test world (game closed) | `python tools\deploy_set.py --yes` (`--check` only verifies jars) |
| Lint / CI rules (syntax, forbidden files, UI ids, command permissions, perm_group_leaks) | `python tools\ci\lint.py` |
| Admin-settings kit every mod uses for SkyWynn Menu -> Server Setup | `tools\skyycfg.py` (kit 1.1), harness `tools\skyycfg_test.py`, contract `tools\CONFIG-CONTRACT.md` |
| Profile contract (per-profile data, busy flag) | `tools\PROFILES-CONTRACT.md` |
| Builder brief (the rules every build agent must follow) | `tools\AGENT-BRIEF.md` |
| Engine inspection helpers (reflect, constant-pool grep, bytecode dump, callers) | `tools\dev\` (`reflect.py`, `cpgrep.py` - run inside tools\dev, `bc.py`, `bcfull.py`, `bcfull2.py`, `callers.py`) |
| Scratch for agents (git-ignored, delete after use) | `tools\dev\scratch\` |
| Backups made before every deploy (Skyy jars + world config.json + Skyy_* mod data; git-ignored) | `backups\deploy-<date>-<time>\` (newest: `deploy-20260925-0824`) |
| Hytale server jar + game assets (read-only) | `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar`, `...\latest\Assets.zip` |
| Installed mods (deploy target; other authors' mods read-only) | `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods\` |
| The test world | `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Saves\HUD mod\` (`config.json` = which mods are enabled) |
| Skyy mods' saved data in that world | `...\Saves\HUD mod\mods\Skyy_Skyy<Mod>\` (stable across versions) |
| Server logs / client logs | `...\Saves\HUD mod\logs\<time>_server.log`, `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Logs\<time>_client.log` |
| Claude's memory for this project (outside the repo) | `C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\memory\` |
| Toolchain | Python 3.12 + `jpype1` + `jdk4py` (no javac anywhere); Git Bash / PowerShell |

Other folders next to the project (`Hytale mods WORK\Hytale mods`, `Your new mods`, `lynk to Hytale Game`) are Skyy's, not part of the build.

## 2. Where we got to

**Live in the "HUD mod" world (last deploy 2026-09-25 08:24, = `tools/deploy_set.py` SET, 22 Skyy mods + 2 pack mods):**
SkyyHud 0.3.10, SkyySacks 0.7.6, SkyyCoins 0.1.5, SkyyCollections 0.2.2, SkyyParty 0.1.4, SkyyBank 0.1.3, SkyyIslands 0.5.2,
SkyyBazaar 0.1.2, SkyyRolls 0.1.5, SkyySkills 0.4.5, SkyyAccessories 0.4.4, SkyyClasses 0.1.6, SkyyMenu 0.3.2, SkyyEssentials 0.1.4,
SkyyProfiles 0.1.2, SkyyCooking 0.1.2, SkyyTrees 0.2.3, SkyyExploration 0.2.1, SkyyGuilds 0.1.3, SkyyVault 0.1.2, SkyyAuctions 0.1.1,
SkyyRanks 0.1; pack mods More Crossbow Tiers (Serj), Saplings From Trees (Helios). What each does: HANDOFF section 3 table.
Not yet tested in game: almost everything from 2026-09-24 22:53 on - TEST-CHECKLIST.md sections from "BETA ROUND 1" down (the vault was verified).

**Stopped 2026-09-28:** Skyy's plan dropped from Max to Pro and weekly Claude Code usage reached 98%. Skyy chose to WAIT FOR THE WEEKLY
RESET. Nothing below is built yet. Specs are written and committed; the working tree is clean.

**Important rule (commit ab75b6c):** Skyy edited these GENERATED scripts directly with locked defaults: `SkyySkills\build_skyyskills_0.4.5.py`,
`SkyyTrees\build_skyytrees_0.2.3.py`, `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`. The live jars were
built BEFORE that edit. Never regenerate those four from their old patch scripts; each next version derives from the EDITED script.

## 3. What to do next (in this order; on Pro run 1-3 agents at a time, sonnet where possible)

1. **SkyyGear spec fix** - apply `research/SkyyGear-Stage1-Spec-Review-Findings.md` (13 findings) to `research/SkyyGear-Stage1-Spec.md`,
   and make sure the spec has: Wynn rarities (Normal, Unique, Rare, Legendary, Fabled, Mythic + Set); a GATE SKILL per gear piece (combat ->
   class weapon skill, mining gear -> Mining, foraging -> Foraging, farming -> Farming; stage 1 builds combat only but the check is generic);
   SkyyGear replaces SkyyRolls; mob + world-chest gear drops unidentified; old gear plain until reforged.
2. **Round 8** (Skyy's 2026-09-25 answers; specs ready):
   - SkyyParty 0.1.5 + SkyyEssentials 0.1.5: party invites / tpa requests / private messages switches BLOCK the sender (research/Settings-Spec.md
     refusing version), staff bypass default on; Essentials also: trades survive damage (tradeCancelOnDamage false), warps page no longer moves
     the world spawn. SkyyEssentials uses patch scripts since 0.1.4 (`tools/essentials_0_1_4_patch.py`).
   - SkyySkills 0.4.6 (from the EDITED 0.4.5): `research/Overall-Level-Spec.md` (base Mana 10, Mage/Priest 20, Overall Level = average of
     skills with a small Health + Mana bonus per level) + Skyy locks: self-heal Divinity XP 0.25/HP (heal-XP bridge gets an optional trailing
     Boolean self), crossbow load survives teleports, keep the big-arrow meter, sound + chat hint on restore, /settings switches for those three.
   - SkyySacks 0.7.7 + SkyyCollections 0.2.3: `research/Bag-Restructure-Spec.md` - bag tiers by rarity (Normal, Unique, Rare, Legendary; old
     Small/Medium/Large items keep working), Mythic Omni Bag (all 5 Legendary bags -> one bag, 100,000 per item for every bag type, tabs per
     type), bags unlocked from collections, Mining bag from IRON.
3. **Round 9** (Skyy's commit ab75b6c locks, listed as LOCKED lines in OPEN-QUESTIONS.md):
   - SkyyTrees 0.2.4 (from EDITED 0.2.3): Tree Feller extra logs 1/2/4/5/6/10 at levels 1-6, cooldown 3 s; Double Jump -> Acrobatics tier III
     slot 7 (replaces Sprinter; Quick Dodge back to tier II) with save migration; hatchet swing speed only on wood (never mobs / weapon axes).
   - SkyyClasses 0.1.7 (from EDITED 0.1.6): class kit straight into the hotbar at class select/change; Healing Totem Priest-only; heal lines
     every 10 s; send self-heal amounts to SkyySkills (Boolean self); daily Archer arrow refill; class-switch rows greyed out in Server Setup.
   - SkyyVault 0.1.3 (from EDITED 0.1.2): buyConfirmCoins (50,000): cheaper pages buy at once, dearer ones ask "Buy page X for Y coins?" in a
     dialog; a plain click turns the page at once.
   - SkyyIslands 0.5.3: admins may invite co-op, visitor limit 10, beds visitor-level (chests member, crafting trusted).
   - SkyyRanks 0.1.1: seeded Member, Admin, Developer + a protected Owner rank; rank editor for ops + Owner only.
4. **SkyyGear 0.1 build** per the fixed spec (new mod `SkyyGear\build_skyygear_0.1.py`), then SkyyAuctions 0.1.2 (gear compat + AH locks:
   48h pays double the listing fee, a different profile may buy your listing, Magic Bags + Accessory Bag blocked) and SkyyMenu 0.3.3 (Identify
   tile, Mods text, Settings icon at slot 39, permission-based settings visibility). Deploy: add SkyyGear 0.1 to SET, remove SkyyRolls, put
   `SkyyRolls` in deploy_set's `RETIRED` list.
5. **Vanilla UI look (Skyy, 2026-09-28):** every UI must look and feel as close to vanilla Hytale as possible. First research the vanilla
   styles in Assets.zip (panel frames, colours, fonts, button styles, spacing, sounds) and put them in one shared style helper for the build
   scripts; every NEW page uses it from then on, and the existing Skyy pages (menu, bags, skills, trees, collections, bank, bazaar, AH, vault,
   island menu, Server Setup, ...) get a vanilla-style pass over time.
6. **Small follow-ups:** config kit keeps 10 old file versions (tools/skyycfg.py KEEP 20 -> 10); SkyyGuilds xpSkills mid-run change credits
   a skill's whole saved XP (fix in the next Guilds version); Archery 15+ extra bolts and the late-game holstered reload (approved, later).
7. **After Skyy tests the separate economy mods:** SkyyEconomy 0.1 = Coins + Bank + Bazaar + Auctions merged (`SkyyEconomy-Plan.md`; use the
   RETIRED list), then NPC shops (SkyyEconomy 0.2).

Every round: build (no `--deploy`), review (sonnet), fix, cross-check with the whole set (one JVM, -Xverify:all, the Adventurer permission
audit), pin versions in `tools/deploy_set.py`, commit + push, back up, then `python tools/deploy_set.py --yes` with the game closed
(Skyy's standing auto-deploy rule), then add the TEST-CHECKLIST section and the HANDOFF log line.

## 4. Open questions still waiting on Skyy
See `OPEN-QUESTIONS.md` (only lines not marked ANSWERED / LOCKED). Also: the collections the Bag spec proposes for the Foraging, Farming,
Combat and Smithing bags; the SkyyGear spec's open questions (section 12); the Admin / Developer permission sets for SkyyRanks.
