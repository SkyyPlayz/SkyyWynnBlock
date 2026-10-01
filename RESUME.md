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
3b. **State 2026-09-30 17:05 (all queued work DEPLOYED):** Sacks 0.7.8, Bank 0.1.5, Profiles 0.1.4, Classes 0.1.9, Skills 0.4.9, Vault 0.1.5, Essentials 0.1.6 (durability switch), Gear 0.1.2 (levels + charged attack), Accessories 0.5 (boosters). Weekly usage 69% on 2026-09-30 with 5.6 days left - keep the next rounds small. NEXT (in order, when Skyy has tested): (1) fixes from Skyy's tests; (2) Skyy's answers to OPEN-QUESTIONS (Mana Regen perks, mob level plan's 17 questions, vault one-click arrow, Vampire bow, staff check on Crystal staffs); (3) small UI follow-ups: Profiles footer Close, kit 1.5 (PROBED from the probe results - skyyui_test fails 1 stale check), option_row padding, Primary=blue wording; (4) remaining vanilla restyles: Bazaar + Auctions, Sacks /craft, Essentials pages, Menu (+ MODS data bumps), Hud; retire SkyyUiProbe; (5) SkyyMobs stage 1 after the mob plan answers; (6) when Hytale 0.7 goes live: research\PreRelease-Compat-Report.md fixes, then class abilities on runes (research\Hytale-Runes-Research.md).
3f. **BUILD QUEUE 2026-10-01 (launch as slots free, max 4 at once):** (1) SkyyGear 0.1.3 - every world chest's untagged gear unidentified on first open + a full level table for the ~60 non-metal gear families that today fall back to vanilla ItemLevel 10-75 (Skyy: Stone Trork Daggers ask Lv 25): place them around Skyy's metal tiers (Stone/Bone/Wool/Soft 0-5, Scrap/Rusty/Linen/Light 10, Cotton/Medium/Tribal 15, Silk/Heavy/Doomed/Zombie 20-25, Crystal/Cindercloth/Scarab/late spellbooks 30-40), editable, untouched-default migration, list them for Skyy; (2) SkyyClasses 0.1.10 - Warrior kit + Weapon_Shield_Wood (off-hand), Priest self-heal default 100% + label; (3) SkyyGuilds 0.1.5 - disband pays the bank by % of each member's net deposits; (4) SkyyMenu 0.3.4 - menu item per profile, Server Setup ms rows shown in seconds with decimals, MODS data version bumps. Running: SkyyAccessories 0.5.1, SkyyCooking 0.1.3 + SkyySacks 0.7.9, SkyySkills 0.4.10, SkyyProfiles 0.1.5.
3h. **RUNNING 2026-10-01 (Skyy answers):** SkyyIslands 0.5.5 (a deleted owner profile closes the island to co-op; members released on archive) + SkyyGuilds 0.1.6 (leave/kick refund 35% of contribution) - one workflow, run wf_48ca0039-9bc; resume with Workflow({scriptPath, resumeFromRunId}). Weekly usage 85% at launch.
3g. **RESUMED after the usage reset (2026-10-01); if stopped again, resume each with Workflow({scriptPath, resumeFromRunId}); files may hold partial edits:** (SkyyProfiles 0.1.5 delete+undo DEPLOYED 2026-10-01), (SkyyGear 0.1.3 chests + level table DEPLOYED 2026-10-01; next SkyyMenu: bump MODS_VERSIONS Gear 0.1.3), (SkyyClasses 0.1.10 Warrior shield + Priest 100% DEPLOYED 2026-10-01). SkyyGuilds 0.1.5 DEPLOYED 2026-10-01. SkyyMenu 0.3.4 DEPLOYED 2026-10-01. (seconds + menu item per profile). DEPLOYED 2026-09-30 evening: Skills 0.4.10 (class XP x3), Cooking 0.1.3 + Sacks 0.7.9 (campfire XP 0.25), Accessories 0.5.1 (old ids hidden, Stamina +3..12 / +2.5..10%).
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
