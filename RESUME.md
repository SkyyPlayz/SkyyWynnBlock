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

**Live in the "HUD mod" world (last deploy 2026-09-29 06:56, backup `backups\deploy-20260929-0656`, = `tools/deploy_set.py` SET, 22 Skyy
mods + 2 pack mods):** SkyyHud 0.3.10, SkyySacks 0.7.7, SkyyCoins 0.1.5, SkyyCollections 0.2.3, SkyyParty 0.1.5, SkyyBank 0.1.3,
SkyyIslands 0.5.3, SkyyBazaar 0.1.2, SkyyGear 0.1, SkyySkills 0.4.6, SkyyAccessories 0.4.4, SkyyClasses 0.1.7, SkyyMenu 0.3.3,
SkyyEssentials 0.1.5, SkyyProfiles 0.1.2, SkyyCooking 0.1.2, SkyyTrees 0.2.4, SkyyExploration 0.2.1, SkyyGuilds 0.1.3, SkyyVault 0.1.3,
SkyyAuctions 0.1.2, SkyyRanks 0.1.1; SkyyRolls RETIRED (switched off, replaced by SkyyGear); pack mods More Crossbow Tiers (Serj),
Saplings From Trees (Helios). What each does: HANDOFF section 3 table. Test list: TEST-CHECKLIST.md, newest section "Round 9 + SkyyGear"
(its step 0 = settings Skyy changes first: gear level check off for testing, three Trees values). Rounds 8 and 9 are not tested in game yet.

**Important rule (commit ab75b6c):** Skyy edited these GENERATED scripts directly with locked defaults: `SkyySkills\build_skyyskills_0.4.5.py`,
`SkyyTrees\build_skyytrees_0.2.3.py`, `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`. Never regenerate those
four from their old patch scripts (their successors 0.4.6 / 0.2.4 / 0.1.7 / 0.1.3 are built from the edited scripts and are live).

## 3. What to do next (on Max 5x run about 4-6 agents at a time, sonnet for reviews)

1. **Skyy tests** round 8 + round 9 + SkyyGear (TEST-CHECKLIST sections "Round 8" and "Round 9 + SkyyGear"); fix what they report first.
2. **Open questions** from the round: OPEN-QUESTIONS.md "Round 9 + SkyyGear defaults" (48h floor, clampToLevel, real gear level table,
   Ranks placeholders) and "Round 8 defaults".
3. **Vanilla UI pass (IN PROGRESS):** kit `tools\skyyui.py` 1.4 + guide. 2026-09-30 05:55 DEPLOYED 12 restyles (Bank, Party, Accessories,
   Classes, Profiles, Vault, Collections, Guilds, Islands, Skills, Trees, Exploration) after Skyy's /skyprobe run (results: HANDOFF log
   2026-09-30 05:55). NEXT: kit 1.5 = record the probe results (PROBED: base, base4, flex, layout-right, button-text, value-ref, number-field,
   tooltip, progress, memories-bar, itemslot, dropdown, search-field, spinner, tile, text-mask, disabled; FAILED: quality-frame, slot-background;
   checkbox partial), fix the probe base2 sample texts + option_row right padding + guide wording (Primary is blue), button labels sized by
   text_width; then the remaining batches: Bazaar + Auctions, Sacks /craft, Essentials, Menu (add the version bumps + SkyyUiProbe to MODS), Hud;
   then retire SkyyUiProbe (RETIRED list).
3b. **Queued (Skyy decisions 2026-09-30, OPEN-QUESTIONS LOCKED):** SkyyAccessories 0.5 booster lines (spec research\Booster-Accessories-Spec.md; workflow script skywynn-accessories-0-5-boosters, run wf_9134fcdc-a2c, stopped before it started to save the 5-hour limit - re-run it); in flight: SkyyGear 0.1.1 finish + 0.1.2 Charged Attack Damage, SkyySkills 0.4.8 caster Mana, SkyyBank 0.1.5, SkyyProfiles 0.1.4 + SkyyClasses 0.1.9, SkyyVault 0.1.5 arrow click; READY + pinned: SkyySacks 0.7.8. Runes (0.7 beta): research\Hytale-Runes-Research.md, fixes needed when the beta goes live: research\PreRelease-Compat-Report.md.
4. **Small follow-ups:** config kit keeps 10 old file versions (tools/skyycfg.py KEEP 20 -> 10); SkyyGuilds xpSkills mid-run change credits
   a skill's whole saved XP (fix in the next Guilds version); Archery 15+ extra bolts and the late-game holstered reload (approved, later).
5. **After Skyy tests the separate economy mods:** SkyyEconomy 0.1 = Coins + Bank + Bazaar + Auctions merged (`SkyyEconomy-Plan.md`; use the
   RETIRED list), then NPC shops (SkyyEconomy 0.2).

Every round: build (no `--deploy`), review (sonnet), fix, cross-check with the whole set (one JVM, -Xverify:all, the Adventurer permission
audit), pin versions in `tools/deploy_set.py`, commit + push, back up, then `python tools/deploy_set.py --yes` with the game closed
(Skyy's standing auto-deploy rule), then add the TEST-CHECKLIST section and the HANDOFF log line.

## 4. Open questions still waiting on Skyy
See `OPEN-QUESTIONS.md` (only lines not marked ANSWERED / LOCKED). Also: the collections the Bag spec proposes for the Foraging, Farming,
Combat and Smithing bags; the SkyyGear spec's open questions (section 12); the Admin / Developer permission sets for SkyyRanks.
