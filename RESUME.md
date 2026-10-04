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

**Usage:** Skyy moved back to the big Max plan on 2026-10-02 (weekly reset to 0%). All open questions were answered on 2026-10-02 -
OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02" (rounds 1-9) is the source of truth.

**2026-10-02 status:** DEPLOYED today, NOT tested by Skyy yet (TEST-CHECKLIST: the five newest sections): phase 1 (deploy-20261002-1300)
SkyySacks 0.7.11, SkyyCollections 0.2.5, SkyyEssentials 0.1.7, SkyyUiProbe 0.3, SkyyHud 0.3.11; the big round (deploy-20261002-1303)
SkyySkills 0.4.12 + SkyyGear 0.2 stage 1 (Gear ROLLBACK FLOOR in deploy_set.py); SkyyMobs 0.1 NEW (deploy-20261002-1643); SkyySacks 0.7.12
bags in bench + inventory crafting (deploy-20261002-1707); SkyyMenu 0.3.5 Mods list (deploy-20261002-1812). RUNNING (relaunched 2026-10-03 21:18 after an interrupt had stopped them): Lantern = SkyyAccessories 0.5.4 (wf_5c31a4e3-a33) and SkyyGear 0.2.2 tooltip / crit (wf_ec10c0ea-410); scripts in tools/dev/scratch/wfscripts/. ALSO RUNNING (22:18): SkyyMobs 0.1.3 client health-bar fix (wf_5300d8b6-004; Skyy saw the Yeti bar empty after ~4 of ~8 hits after switching to Custom). ALSO RUNNING (21:40): SkyyUiProbe 0.4 minimap probes P1-P5 (wf_590435db-51a, lean; BetterMap stays OFF in the test world until the minimap widget round adds it to PACK_THIRD_PARTY with its stats off - Skyy toggles it for probe P4). Skyy: stop starting new rounds near 95% weekly usage.
USAGE 2026-10-03 23:15: weekly 90% -> the running rounds (Lantern, Gear 0.2.2, probe 0.4, mob curve spec) finish and deploy; NO NEW ROUNDS until the Mon 2026-10-06 15:00 UTC reset (Skyy: stop near 95%). SkyyMobs 0.1.3 READY + PINNED, deploy when the game is closed. Next after the reset: Gear 0.2.3 craft Smithing XP, then the queue below.
QUEUE ORDER (Skyy 2026-10-03 evening, LATEST - wins over every queue line below; weekly usage 81% -> big rounds wait for the Mon 2026-10-06
15:00 UTC reset unless Skyy says go; test fixes any time): 1) Lantern = SkyyAccessories 0.5.4 (replaces Night Vision; check every accessory /
bag tier is crafted from the previous one); 2) SkyyGear tooltip / crit build (wand + staff "Charged shot - N Mana - dmg" / "Quick shot" lines,
drop the Damage Data note + hide the box where possible, CRIT! popup + Impact_Critical sparks, red crit number behind a switch) + SkyyArmory
staff damage default ~120-125% (Mage glass cannon); 2b) TEST FIX (Skyy 2026-10-03 evening: "crafted 10 iron wands and didnt get any smithing xp"): SkyyGear 0.2.3 = Smithing XP for crafting weapons + armor (xp.craft by rarity x a steep tier factor, Crude / Wood much less, tools pay on reforge; full round - level-ups pay coins; + drop the grey armor line "(Health / Resistance below are vanilla - before levels)" if 0.2.2 left it - still shown on Skyy's Fabled Iron Greaves screenshot) right after 0.2.2 is READY (its base); tool levels become 0.2.4, the loot round 0.2.5 (keeps identify XP); 3) MINIMAP: SkyyUiProbe map-picture probe -> SkyyHud minimap widget (BetterMap joins the
pack, hstats off, hub in allowedWorlds); 4) /island STARTER SHARDS (SkyyIslands); 5) MOB CURVE rebalance spec -> build (MOVED UP after Skyy's Lv 33 Yeti test - spec RUNNING (relaunched 22:20 with the Custom 20/8 test: wf_fa1d5000-f0c -> research/Mob-Curve-Spec.md, + a side check of the staff-handover WARN in today's log); build = SkyyMobs 0.1.4 after Skyy's answers; + armor Health keeps pace with mob damage - Skyy: "the hp you get from armor should also go up with the level"; it does since Gear 0.2.1 via base.curve, tune it WITH the mob curve, own armor curve row if needed); 6) WORLDGEN STAGE 2
spec -> build; 7) SkyyGear TOOL LEVELS = 0.2.4 (revise research/Tool-Levels-Spec.md with Skyy's answers first); 8) SkyyGear LOOT round = 0.2.5 (revise
research/Loot-Unid-Spec.md: rarity loot boxes, level range, tiered craft XP; + Smithing readers + gear:extras); 8a) WAND BURST (Skyy 2026-10-03 evening: wand charged shot -> AoE burst, less damage in a big area, Priest + allies inside heal +10%; staffs stay single-target) = SkyyArmory 0.1.1 + SkyyClasses 0.1.12 (+ SkyyGear tooltip words), full round; + MONK replaces the unplayable Shaman slot (Skyy: our own classes, not Wynncraft's; staff kind open - default Bo staffs) after research/Class-Roles-Ideas.md (RotMG-style class roles research running, a big class-idea list split vanilla / needs custom gear); 8c) PARTY TPA BUTTONS (Skyy 2026-10-03: a TPA button per member row + ACCEPT TPA on the Party page; SkyyParty 0.1.7 + SkyyEssentials 0.1.8 bridge to its /tpa + /tpaccept; full round); 8b) STATS PAGE (Skyy 2026-10-03 evening: "this menus should show me all my stats with my current gear, accessory's skill and class bonuses ... like on skyblock" - Your Profile -> a SkyBlock-style Stats page with per-source breakdowns; spec drafted by the cloud (CLOUD-RESUME top task -> research/cloud/Stats-Page-Spec.md), local check + multi-mod build after the weekly reset); 9) ACCESSORY TABLE (paused spec -
decide whether the pack still wants it now that Pocket Dimension keeps the Workbench tab); 10) small follow-ups (the staff-handover start-up WARN is a false alarm - SkyySkills + SkyyArmory checks must read the item's file path, not the pack label (HANDOFF 2026-10-03); SkyyMobs 0.1.3 HP-bar fix
paused, Collections sickle crops, Menu Mods list, tree:reads readers in Skills / Gear / Sacks, Auctions mystery categories, class trees ON
after /tree probe, Mage health / defence); LAST (Skyy: "Move 3 to last"): SKYY'S POCKET DIMENSION spec + release build + CurseForge kit.
DEPLOYED 2026-10-02: 22:40 SkyyMobs 0.1.1 difficulty ladder; 23:35 SkyyAccessories 0.5.3 Night Vision; 23:55 SkyyMobs 0.1.2 health floor + live re-apply; 2026-10-03 00:03 SkyyCooking 0.1.4 Grade strength + XP x0.5; 00:09 SkyySkills 0.4.13 + SkyyHud 0.3.12 combat widget + Mana while charging; 00:28 SkyyBank 0.1.6 stuck-page fix; 01:07 SkyyGear 0.2.1 damage + armor by level; 02:09 SkyyWorldGen 0.1 NEW Zone 1 test island (/zone 1, admin); 03:36 SkyySkills 0.4.14 kill XP by level + roll XP + gathering x3 + sickle XP; 05:21 SkyyMenu 0.3.6 stuck-page fix; 07:53 SkyyHud 0.3.13 small boxes + combat colours; 08:48 SkyyTrees 0.3 Alchemy + Smithing trees, class trees OFF; 09:28 SkyyBazaar 0.1.3 every bag item + Smithing tab; 09:46 the SkyyArmory round (SkyyArmory 0.1 NEW + SkyySkills 0.4.15 + SkyyClasses 0.1.11); 12:26 SkyyTrees 0.3.1 waiting class nodes skipped (TEST-CHECKLIST newest sections).
RUNNING (2026-10-02 late evening; resume any with Workflow({scriptPath, resumeFromRunId})): 
ULTRACODE (Skyy: "use ultracode on big jobs", Fable allowed): SkyyTrees 0.3 build (Alchemy + Smithing + class trees, coin respec, Dust
defaults; wf_3f431935-177) and the Accessory Table spec (wf_7abd78e6-aa2 -> research/Accessory-Table-Spec.md); SPECS: tool levels
(wf_c0c52e96-7aa -> research/Tool-Levels-Spec.md), loot round (wf_cefcd0b5-cd1 -> research/Loot-Unid-Spec.md), SkyyArmory metal wands
(wf_0f61c6f1-4fe -> research/SkyyArmory-Spec.md) + the wand ART PROOF agent (tools/skyyart.py + preview sheet for Skyy to pick style A/B).
QUEUED: SkyyGear 0.2.2 TOOL LEVELS after 0.2.1; SkyyGear 0.2.3 LOOT round after 0.2.2 (drop boost
4% per leveled kill + ~1 in 3 chests, Wynncraft-style mystery unidentified items, Smithing-tree identify-rarity hook). SkyyArmory 0.1 (NEW
mod: Copper -> Mithril/Onyxium wands, tap = blue quick shot, hold = charged shot, Mana + damage per metal) after Skyy picks the art style.
ACCESSORY TABLE after the Night Vision round = SkyyAccessories next + SkyySacks 0.7.13 (+ /craft respects vanilla's Memories level).
SkyyTrees 0.3 after the trees spec (Smithing tree incl. identify-rarity node; Mining Dust default 5 XP per Dust).
RUNNING (2026-10-03 morning, Skyy's pacing = 1-2 big rounds at a time): (SkyyArmory round DONE + deployed). After them: revise Tool-Levels-Spec (Power names, hoe/sickle lock ON, every new
tool levelled, hatchet power lower + earlier swing speed) -> SkyyGear 0.2.2; revise Loot-Unid-Spec (level range, rarity loot boxes, tiered craft
XP) -> SkyyGear 0.2.3; finish the paused Accessory Table spec -> build; SkyyMobs 0.1.3 HP-bar fix; SkyyCollections sickle crops.
RIGHT AFTER THE ARMORY ROUND: a small SkyyGear tooltip build - wands / staffs show "Charged shot - N Mana - damage at Lv X" + "Quick shot - M Mana
- damage" instead of the melee line (SkyyArmory bridge with each wand's shots; renumber the tool build to the next free SkyyGear version);
remove the grey "Damage Data box is vanilla" note and HIDE the vanilla box where an item-type way exists (Skyy: hide it, no note).
ALSO RUNNING: Night Vision
glare research agent. The follow-up SkyyGear build also gets the crit indicator (CRIT! popup + Impact_Critical sparks; red number behind a
switch - research/Crit-Indicator-Research.md).
QUEUE AFTER THE CURRENT ROUNDS (weekly 69% on 2026-10-03 midday, resets Mon 15:00 UTC - keep ~10% for test fixes): (1) SkyyAccessories
0.5.4 LANTERN line replacing Night Vision (glow like a torch, range up with a hidden helper light above the wearer, brightness capped;
each tier crafted from the previous - research/NightVision-Glare-Research.md), (2) the SkyyGear tooltip / crit follow-up, (3) SKYY'S
POCKET DIMENSION spec + build, (4) MINIMAP: SkyyUiProbe map-picture probe then the SkyyHud minimap widget on the engine map stream
(BetterMap joins the pack, hstats off; research/Minimap-Research.md) (public bags mod; release files to Desktop\Hytale mods WORK\Your new mods), then the items below.
NEXT BIG ROUNDS after Armory / Trees: FIRST (Skyy: "on the next run") the /ISLAND STARTER SHARDS upgrade - SkyyIslands: island 3x with a
small hill, more trees, a cave, a bridge to a 2nd island with mobs, a 3rd island with the portal (boss later); spec first from
research/cloud/Starter-Shard-Layout.md. Then (a) MOB CURVE REBALANCE spec - Wynncraft-style exponential mob health /
damage, a steeper gear curve to match, brutal at +20 levels, kill XP moved off raw health (SkyyMobs + SkyyGear + SkyySkills); (b)
NEXT BIG ROUND after Armory / Trees: SKYYWORLDGEN STAGE 2 (Skyy 2026-10-03: random island shape, vanilla Zone 1 generation inside it -
rivers, mountains, caves, goblin camps - a mountain rising to the middle, harder biomes toward the middle as a tendency, ~3x bigger,
biomes as varied as vanilla; ALL zone islands in ONE world so Zone 2 is visible from Zone 1) - research / spec first. Crit indicator research agent running -> research/Crit-Indicator-Research.md.
PAUSED 2026-10-03 ~06:35 UTC to save the 5-hour window (74%, weekly 53%) - resume with Workflow({scriptPath, resumeFromRunId}); finished
agents replay from cache, the interrupted one re-runs (its half-written work files get rewritten):
- SkyyTrees 0.3 ultracode build: part 1 done, part 2 (class tree) was running. scriptPath C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK-SkyWynn-PROJECT\077f1485-8367-478d-8718-87cb80a267c4\workflows\scripts\skywynn-trees03-ultracode-wf_3f431935-177.js, run wf_3f431935-177.
- Accessory Table spec: research + Fable spec done, the 3 critics were running. scriptPath C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK\077f1485-8367-478d-8718-87cb80a267c4\workflows\scripts\skywynn-accessory-table-spec-wf_7abd78e6-aa2.js, run wf_7abd78e6-aa2.
- SkyyMobs 0.1.3 HP-bar fix: builder was running. scriptPath C:\Users\SkyLo\.claude\projects\C--Users-SkyLo-Desktop-Hytale-mods-WORK-SkyWynn-PROJECT\077f1485-8367-478d-8718-87cb80a267c4\workflows\scripts\skywynn-mobs013-hpbar-wf_edf71a00-cec.js, run wf_edf71a00-cec.
DONE + DEPLOYED 2026-10-03: SkyyMenu 0.3.6 - after the menu's Island / Hub tile, CloseTask's setPage(None) on the new world
leaves the engine's page-ack counter stuck, so EVERY custom page ignores clicks until the next world change (Bank 0.1.6 heals itself; the
rest do not). Fix: skip / Dismiss instead of setPage(None) after a world change + a generic guard that forgets a stale page at world join.
CROSS-BUILD NOTES (2026-10-03): the loot round needs SkyyMobs mob:fn:levelAt (next SkyyMobs after the 0.1.3 HP-bar fix) and SkyyAuctions
0.1.3 (AH categories for mystery items); SkyyGear 0.2.3 must use the reader-flag key names SkyyTrees 0.3 ships (the loot spec proposed
gear:tree:readers - reconcile when the trees build lands); SkyyArmory 0.1 must publish gear:loot:add:SkyyArmory. Open spec questions for
Skyy (all have defaults): tool levels 5, loot round 6 (OPEN-QUESTIONS Q&A, 2026-10-02/03 SPEC DONE lines).
NEXT (needs Skyy): test results; the art style pick; the trees/0.7 questions when that plan lands; open questions in OPEN-QUESTIONS (bag
stacking cap, idle-stack refill, in-combat Mana for non-casters, class coin rate).

1. **Skyy tests the 2026-10-01 deploys**; fix what they report first (auto-deploy each fixed round with the game closed).
2. **THE BIG ROUND (phase 2, after the quick fixes), all decided by Skyy 2026-10-01 / 2026-10-02:**
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
