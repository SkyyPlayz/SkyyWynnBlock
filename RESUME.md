# SkyWynn - RESUME HERE (updated 2026-10-17 ~08:20 MDT; Skyy resets the session after this)

Big picture: `STATUS.md`. Map: `INDEX.md` (every folder has a README). Rules: `PROJECT-RULES.md`. Versions: `HANDOFF.md`.
Skyy's tests: `TEST-CHECKLIST.md`. History: `docs/log/2026-10.md`. Decisions word for word: `docs/answered/<topic>.md`. Open: `OPEN-QUESTIONS.md`.

## START HERE (new session)
1. `git pull --rebase --autostash`; check usage (ccd get_usage). Deploy target world **NewBetaTest** (`tools/deploy_set.py` WORLD).
2. Rounds: while Skyy chats on other topics run builders as PLAIN Agents and spawn critics yourself (workflow builders refuse); else the
   saved workflow `skywynn-round`. Deploy (game closed): skill `skywynn-deploy` = backup -> `smoke_test.py --allow-pack-api` (Perfect
   Parries pack-API fail is third-party) -> `deploy_set.py --yes` (check the LAST line says "deployed N mods") -> `record_deploy.py` -> commit -> tidy.
3. After Skyy plays: skill `skywynn-logs` (`python tools/log_scan.py --ours`, then `--recycle`).

## LIVE NOW (deployed 2026-10-17, TEST-CHECKLIST 172-179)
- 172: Accessories 0.5.23 (Void Charms -> top-bar Market disconnect fixed), Gear 0.3.18 (Breaking Speed row first, accessory Breaking
  Power, red/green requirement lists), Islands 0.5.19 (6 named island homes, `/is sethome <name>`, `/is <name>`).
- 173: FP1 Potion Flask + Food Pouch = Cooking 0.1.11 + Sacks 0.8.18 + Wardrobe 0.2.8 (Storage > Supplies, /flask /pouch). FLOOR Cooking 0.1.11.
- 174: Menu 0.3.37 (Teleport page: warps with APPROVED icons art/warp-icons, island homes, homes, Arrange; Void Charms amulet icon) +
  Essentials 0.1.14 (/back, /sethome + /home 2 homes, /warpadmin icons; islands fail closed, instances refused).
- SkyyFlaskProbe retired 10-17 (RETIRED list).
- 175: Accessories 0.5.24 (Void Charms name). 176: Sacks 0.8.19 / Essentials 0.1.15 / Auctions 0.1.12 / Menu 0.3.38 (Void Charms
  rename, icon ids > 32, Arrange Prev/Next + dots), Classes 0.1.37 (Breach x Mark), Wardrobe 0.2.9 (Requip leaves Pouch food), Nestkeeper ON.
- 177: ORES ROUND = WorldGen 0.7.3 (Lead / Chromium / Slag / Titanium ores, Dusk / Azurvane / Cinder / Lumen + Electrum alloys, vanilla-vein
  copies, Gold Z4-5) + Accessories 0.5.25 (Furnace Charm I-V + Eternal Flame) + Sacks 0.8.20 + Collections 0.2.25 + Bazaar 0.1.20 + Skills 0.4.49;
  the five ores mods roll back TOGETHER (deploy_set STOP guard).
- 178: PR #17 merged = Gear 0.3.19 + Mobs 0.1.10: The Armory sets drop from mobs (49 sets / 1,067 ids), Mythic boss bags (once per fight),
  Mythic / UT crafting refused, Alteration keeps rolls, rolled-piece salvage via /craft refused (Requip only); Void Charms Gear texts done.

## RUNNING / JUST BUILT
- COBB (Skyy's Grok bot) STOPPED BUILDING 10-17 (LOCAL-RESUME.md, PR #16 merged): all builds are local again; Cobb = design / specs /
  reviews. Cobb's armor-drops PR #17 (Gear 0.3.19 + Mobs 0.1.10) is HANDED TO LOCAL: review, trusted rebuild, smoke, pin, merge.
  Trial rules + undo: CLOUD-RESUME.md "Cloud build trial". Metals source of truth (Cobb): SkyWynn-PRIVATE-art\metal-art\skywynn-metals-build-spec.md (outside the repo).
- WORK SPLIT + LOCKS: `LOCAL-RESUME.md` (made by Cobb = Skyy's Grok bot) - check its lock table before any job.
- Smelting charm -> FURNACE CHARM (below). Wynn elements spec research/Wynn-Elements-Spec.md + structure ask (joszza) wait on Skyy.
- NEXT (Skyy picks): LOCAL-RESUME queue (mining armor Z2-Z5, metal art, Fortune + metal tools / weapons), UT lines for 5 UT sets (spec Q1),
  crossbows (TASK-crossbows-from-vanilla.md), OPEN-QUESTIONS answers. Salvagebench guard live (Gear 0.3.20, TEST 179).
- Zone metals (Skyy's table, research/Zone-Tiers-Idea.md): Bronze / Dusk / Azurvane / Cinder / Lumen; Quirk sends art drafts per family.

## NEXT (small first; Skyy: "work through the small things and the next up list. save the bigger ones for later")
1. Small LOWs left from reviews (optional): Gear accBp per-hit cache + GearReq missing red row (gear 0.3.18 review); Menu warp names with
   '.' can't be arranged, Arrange has no prev/next; Essentials icon ids > 32 chars dropped on restart; Requip deposit strands claimed food.
2. Menu rebuilds now need a `TAB_ICON` for `storage:supplies` (tools/skyyui.py has the Supplies tab) - add one (art) in the next Menu round.
3. Armor/weapons from The Armory + Arcane Robes + others as mob drops with our modifiers (gear.md 10-17; research/Armor-Set-Count.md):
   per zone (5 zones) x weight: fewer normal sets low, 2 UT + 1 Mythic at the zone's top combat band; UT/basic = recolours (of the cooler
   modded sets), coolest looks saved for Mythic, own designs last. Packable now: Void Armor (CC BY-NC). Ask authors (Skyy sends): Fyrrage
   (Fantastic Knight + Outlanders), Elemental Knights, stonedturtle, SlverSkull (Arcane Robes). Add Patchly + The Armory 1.23.0 to PACK.md.
   ULTRACODE round (Gear + Mobs + loot) once Skyy OKs the ask list.
4. Nestkeeper into the pack (dup check, PACK.md) then the Aures dragon pet; Wynn elements spec (Earth/Thunder/Water/Fire/Air, Imbue all 5);
   zone gathering spots + seeds locked behind collections + crop islands for Eternal seeds
   (100 / +200 / +500) - world.md 10-17.
5. Small list: smelting accessory, lifelong multitool merge, Hud ability icons (6 classes), Mage PA4 (Armory blink bridge), structure mods +
   joszza draft, flip lint MENU_PATTERN_FAIL, skyyeggs ORDER, Profiles carry Accessory Power / retired files.
6. IDEA (Skyy "dont change now"): research/Zone-Tiers-Idea.md - 3 gathering tiers per zone (2 ores + own alloy; metals = mining sets + tools
   only, combat gear drops only), end of Zone 4 at Lv 50, Zone 5 after rebirth; Silver/Gold kept for charms.
7. LATER (Skyy): Beastmastery, Void Particles, totems, Armory gear + movement, mod compression (sections stay separate), SkyyCore 1.0.1 HubBar.

## Never forget
- Commit ab75b6c: Skyy hand-edited 4 GENERATED scripts (`SkyySkills\build_skyyskills_0.4.5.py`, `SkyyTrees\build_skyytrees_0.2.3.py`,
  `SkyyClasses\build_skyyclasses_0.1.6.py`, `SkyyVault\build_skyyvault_0.1.2.py`); never regenerate them from their old patches.
- Rollback floors + go-together rules: comments in `tools/deploy_set.py` (newest: FP1 Cooking 0.1.11 needs Sacks 0.8.18 + Wardrobe 0.2.8).
- Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md`. Menus follow research/Menu-Pattern.md (no back buttons, top rows always,
  requirements as a red/green list). Replace commands, never add extra. Ask Skyy in popups, one at a time.
- If a builder's smoke server is still running, deploy_set refuses - wait (never kill it). `python tools/tidy_local.py --yes` after deploys.

## On Skyy's PC (read-only except the deploy)
Project = this repo. Game: `C:\Users\SkyLo\AppData\Roaming\Hytale\install\release\package\game\latest\` (`Server\HytaleServer.jar`,
`Assets.zip`). Mods: `...\Hytale\UserData\Mods\`. Test world: `...\UserData\Saves\NewBetaTest\` (mod data `mods\Skyy_Skyy<Mod>\`, server
logs `logs\`); client logs `...\UserData\Logs\`. Backups: `backups\` (git-ignored). Toolchain: Python 3.12 + jpype1 + jdk4py (no javac).
LOCAL ONLY, never in git: game files, UserData, backups, built jars (except `tools\javassist.jar`), `build_classes\`, `tools\dev\scratch\`.
