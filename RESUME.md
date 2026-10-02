# SkyWynn - RESUME HERE (updated 2026-10-01)

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
| Backups made before every deploy (Skyy jars + world config.json + Skyy_* mod data; git-ignored) | `backups\deploy-<date>-<time>\` (newest: `deploy-20261001-0737`) |
| Hytale server jar + game assets (read-only) | `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\Server\HytaleServer.jar`, `...\latest\Assets.zip` |
| Installed mods (deploy target; other authors' mods read-only) | `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Mods\` |
| The test world | `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Saves\HUD mod\` (`config.json` = which mods are enabled) |
| Skyy mods' saved data in that world | `...\Saves\HUD mod\mods\Skyy_Skyy<Mod>\` (stable across versions) |
| Server logs / client logs | `...\Saves\HUD mod\logs\<time>_server.log`, `C:\Users\SkyLo\AppData\Roaming\Hytale\UserData\Logs\<time>_client.log` |
| Claude's memory for this project (outside the repo) | `C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\memory\` |
| Toolchain | Python 3.12 + `jpype1` + `jdk4py` (no javac anywhere); Git Bash / PowerShell |

Other folders next to the project (`Hytale mods WORK\Hytale mods`, `Your new mods`, `lynk to Hytale Game`) are Skyy's, not part of the build.

## 2. Where we got to

**Live in the "HUD mod" world (last deploy 2026-10-01, backup `backups\deploy-20261001-0737`, = `tools/deploy_set.py` SET, 23 Skyy mods
+ 2 pack mods):** SkyyHud 0.3.10, SkyySacks 0.7.10, SkyyCoins 0.1.5, SkyyCollections 0.2.4, SkyyParty 0.1.6, SkyyBank 0.1.5,
SkyyIslands 0.5.5, SkyyBazaar 0.1.2, SkyyGear 0.1.3, SkyySkills 0.4.11, SkyyAccessories 0.5.2, SkyyClasses 0.1.10, SkyyMenu 0.3.4,
SkyyEssentials 0.1.6, SkyyProfiles 0.1.5, SkyyCooking 0.1.3, SkyyTrees 0.2.5, SkyyExploration 0.2.2, SkyyGuilds 0.1.6, SkyyVault 0.1.5,
SkyyAuctions 0.1.2, SkyyRanks 0.1.1, SkyyUiProbe 0.2 (dev mod, retire later); SkyyRolls RETIRED; pack mods More Crossbow Tiers (Serj),
Saplings From Trees (Helios). What each does: HANDOFF section 3 table.

**Not tested in game yet (deployed 2026-10-01):** Profiles 0.1.5 (delete + 6 h undo; ROLLBACK FLOOR 0.1.5 once anything was deleted),
Classes 0.1.10 (Warrior Wood Shield, Priest self-heal 100%), Guilds 0.1.5 -> 0.1.6 (% disband refunds, Contribution column, 35% leave
refund), Menu 0.3.4 (seconds in Server Setup, menu item per profile), Gear 0.1.3 (all world-chest gear unidentified, 59 non-metal level rows),
Skills 0.4.11 (Priest heal XP 1 / 1.25), Accessories 0.5.2 + Sacks 0.7.10 (Workbench "Accessories & Bags" tab, Charcoal -> Smithing bag),
Islands 0.5.5 (deleted owner closes the island). Test steps: the newest TEST-CHECKLIST sections. Skyy can already set copper armor to Lv 1
in Server Setup -> Gear -> Levels (`Armor_Copper` = 1).

**Important rule (commit ab75b6c):** Skyy edited these GENERATED scripts directly with locked defaults: `SkyySkills\build_skyyskills_0.4.5.py`,
`SkyyTrees\build_skyytrees_0.2.3.py`, `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`. Never regenerate those
four from their old patch scripts (their successors 0.4.6 / 0.2.4 / 0.1.7 / 0.1.3 are built from the edited scripts and are live).

## 3. What to do next (Max 5x: at most 3-4 workflows at once, sonnet for reviews)

**Usage:** weekly usage was 94%+ on 2026-10-01; it resets 2026-10-06 ~15:00 UTC. Until then only small fixes from Skyy's tests.
Nothing is running (no workflow to resume).

1. **Skyy tests the 2026-10-01 deploys**; fix what they report first (auto-deploy each fixed round with the game closed).
2. **NEXT BIG ROUND (after the weekly reset), all decided by Skyy 2026-10-01:**
   - SkyySkills: a flatter class skill XP curve (skill 20 in hours of play, 40 in days; existing XP kept, levels recomputed upward;
     editable rows).
   - SkyyGear 0.2 stages 0-3 from `research/Gear-Levels-Wynn-Spec.md`: a stored per-item level that sets base stats AND the use
     requirement (gate skill as ruled 2026-09-25), crafted at your level inside overlapping material bands (Wood 1-13, Copper 10-18 -
     copper ARMOR 1-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril 40-49), base damage + armor by level;
     vanilla materials cover 1-49, our own tiers 50+ later; tools reforgeable once gathering stats exist.
   - Workbench recipes for wands, spellbooks and staffs by material (so "crafted at your level" works for Priest / Mage).
   - The next SkyyGear also ships `Armor_Copper=1` as a default; the next SkyyMenu bumps MODS_VERSIONS (Gear 0.1.3, Skills 0.4.11,
     Accessories 0.5.2, Sacks 0.7.10, Islands 0.5.5, Guilds 0.1.6 and later).
3. **Plans written, waiting (not built):**
   - `research/SkyyWorldGen-Plan.md` - World Gen V2 zone islands (one world per zone, terraced rings = levels, rim easy -> summit
     hardest). Skyy's answers: ZONE BANDS Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60, more past 60; a summit PORTAL to the
     next island that opens after the boss (staged unlock: summit -> class skill 20 / 30 / 45 -> guardian); every zone has a starter town
     built around a VANILLA temple (the Zone 1 town is the hub, no separate hub island) with a warp unlocked with the zone; at least one
     outpost town per biome with an unlockable warp. Build starts with a 3-ring Zone 1 test island when Skyy says go.
   - `research/Mob-Levels-Plan.md` (SkyyMobs) - re-fit its zone bands to the new ones when building.
   - `research/Pets-Idea.md` - one pet system (SkyBlock-style buff pets: farming, mining, foraging, general combat + at least one class pet
     per class at launch; better pets fight; mount pets; an active slot + an unlockable mount slot that still gives weaker buffs).
   - `research/Dragon-Pets-Idea.md` - dragon boss + egg, Zone 5 dinosaur caves, quest-line hatching, elements Earth / Thunder / Water /
     Fire / Air + secret Blood / Void / Light / Crystal, rideable dragons, dragon-only islands. Idea only.
4. **Open questions for Skyy** (OPEN-QUESTIONS.md, lines not ANSWERED / LOCKED): bags collecting from the hotbar too; Mana Regen perks;
   staff check on the Crystal staffs; Vampire bow and charged attacks; Vault one-click arrow; the mob level plan's questions; the
   SkyyGear spec leftovers.
5. **Vanilla UI pass leftovers:** kit 1.5 (record the /skyprobe results as PROBED; skyyui_test has 1 stale fail "base-gated
   WrapMaxLines"), then restyle Bazaar + Auctions, Sacks /craft, Essentials, Menu, Hud; retire SkyyUiProbe (RETIRED list).
6. **Small follow-ups:** config kit keeps 10 old file versions (tools/skyycfg.py KEEP 20 -> 10); Archery 15+ extra bolts and the late-game
   holstered reload (approved, later); Skills / Collections leaderboards should skip deleted / archived profiles (profile:fn:state).
7. **After Skyy tests the separate economy mods:** SkyyEconomy 0.1 = Coins + Bank + Bazaar + Auctions merged (`SkyyEconomy-Plan.md`; use the
   RETIRED list), then NPC shops (SkyyEconomy 0.2).
8. **Hytale 0.7 (pre-release):** runes = the base for class abilities; SkyyIslands / Menu / Profiles need fixes when 0.7 goes live
   (`research/Hytale-Runes-Research.md`, `research/PreRelease-Compat-Report.md`).
9. **Housekeeping:** a stray untracked `PROJECT\` folder in the repo root (an agent's scratch made with a bad relative path) - never
   commit it; Skyy deletes it (the permission check blocks Claude from deleting it).

Every round: build (no `--deploy`), review (sonnet), fix, cross-check with the whole set (one JVM, -Xverify:all, the Adventurer permission
audit), pin versions in `tools/deploy_set.py`, commit + push, back up, then `python tools/deploy_set.py --yes` with the game closed
(Skyy's standing auto-deploy rule), then add the TEST-CHECKLIST section and the HANDOFF log line.

## 4. Open questions still waiting on Skyy
See `OPEN-QUESTIONS.md` (only lines not marked ANSWERED / LOCKED). Also: the collections the Bag spec proposes for the Foraging, Farming,
Combat and Smithing bags; the SkyyGear spec's open questions (section 12); the Admin / Developer permission sets for SkyyRanks.
