# CLOUD-RESUME - rolling to-do for cloud sessions

Work a cloud session can do while the local session waits (usage limits, Skyy away). Started 2026-10-02.

## How this file works (read every time)

- **Rolling list:** do the top open task, then mark it `[x]` with the date and the output file. When you open this file and see `[x]`
  items, first add one line per item to `research/cloud/LOG.md`, then DELETE those items here and top the list back up to about 8
  open tasks (ideas: RESUME.md section 3, OPEN-QUESTIONS.md open lines, the plans in `research/`). Keep this file under ~80 lines.
- **Cloud limits:** no access to Skyy's PC, the Hytale game files (`HytaleServer.jar`, `Assets.zip`), installed mods or the test world.
  You cannot build, test or deploy. Only add tasks that need none of that. Any fact you cannot check without the game files: mark it
  **UNVERIFIED** and list it under "For the local session" in your output.
- **Where results go:** new files in `research/cloud/` (one file per task). You may push straight to `main` ONLY changes to this file and
  to `research/cloud/` (always `git pull --rebase --autostash` first). Any change to another file goes through a pull request.
- **Never touch:** build / patch scripts, `tools/deploy_set.py`, jars, `SkyyGear-Plan.md`, `SkyyGear-Stat-Catalog.md`.
- Follow `PROJECT-RULES.md`. Skyy uses they/them. Plain English, tables, short.

## Open tasks (top = next)

- [ ] **SkyyQuests design** (OPEN-QUESTIONS: "quest hooks ship with SkyyQuests"). The story scripts need a quest system that does not exist: quest steps and flags per
      profile, NPC dialogue windows (vanilla look), objectives (kill / collect / craft / reach / talk), rewards, quest log page, bridge keys other mods can call. Read
      `research/cloud/Story-Script-*.md`, `Dragon-Quest-Spec.md`, `tools/PROFILES-CONTRACT.md`. Output: `research/cloud/SkyyQuests-Spec.md`.
- [ ] **Outposts list** - LOCKED R9: about 30-35 outpost towns, one per biome group, each an unlockable warp. List every outpost per zone (shared between near-identical
      biome variants) with name, biome, ring, what it sells, warp rules. Read `research/Mob-Levels-Refit.md`, `SkyyWorldGen-Plan.md`. Output: `research/cloud/Outposts-List.md`.
- [ ] **Slayers spec** (`SkyyDungeons-Plan.md`: core loop, not the spine) - research Hypixel Slayers on the web, propose SkyWynn slayer quests per zone (boss, tiers, rewards,
      XP, anti-farm). Output: `research/cloud/Slayers-Spec.md`.
- [ ] **Capstone dungeon spec** - the one endgame dungeon after Zone 4/5 (`SkyyDungeons-Plan.md`, Decisions row 7.5): research Hypixel Catacombs / Wynncraft raids, propose floors,
      rooms, bosses, party size, scaling, rewards. Output: `research/cloud/Capstone-Dungeon-Spec.md`.
- [ ] **Accessory acquisition** - Accessories are admin-give only today ("drops / chests later", HANDOFF 2026-09-30). Propose how players earn the booster accessories:
      zone chests, boss drops, event tokens, shop, crafting; per rarity. Read `SkyyAccessories-Plan.md`, `research/Booster-Accessories-Spec.md`. Output: `research/cloud/Accessory-Acquisition.md`.
- [ ] **Prestige system spec** from `research/cloud/Tab-Economy.md` section 5: what resets, what is kept, perks, caps, the ticket number joke, per-profile storage. Output: `research/cloud/Prestige-Spec.md`.
- [ ] **Zone specials / "mayor lite"** - rotating global buffs announced by the Board (Elites-Events-Spec 2.5): research SkyBlock mayor perks, propose a small rotating-buff system with
      rows, schedule and anti-stacking. Output: `research/cloud/Zone-Specials-Spec.md`.
- [ ] **SkyyArmory roadmap** - Skyy named a new content mod SkyyArmory (2026-10-02): our own weapons and armor, starting with metal
      Priest wands made by recolouring the vanilla Wood Wand (same model, new texture, like the vanilla Rotten Wand; OPEN-QUESTIONS Q&A).
      Propose the next items per class (Mage / Archer / Warrior / Berserker / Priest) and our own Lv 50-100 tiers: names, tier ladder,
      which vanilla model each could reuse, stat identity per class (Wynncraft-inspired, web research). Output: `research/cloud/SkyyArmory-Roadmap.md`.
- [ ] **Tool progression research** - tools are getting levels gated by Mining / Foraging / Farming (OPEN-QUESTIONS 2026-10-02 tool lock).
      Research Wynncraft gathering tool tiers / levels / gathering speed and Hypixel Mining Speed / Fortune numbers on the web; compare
      with our bands (Wood 1-13, Copper 10-18, Iron 15-23 ...) and the x3 -> x1.5 early XP boost; flag pacing risks. Output:
      `research/cloud/Tool-Progression-Research.md`.

<!-- 2026-10-02 local session: the magic weapon recipes shipped in SkyyGear 0.2 (8 recipes) - removed from this list. -->
<!-- 2026-10-02 local session: 'Skill-tree pass 2 notes' removed - the local research/Skill-Trees-2-Spec.md covers it. -->

## Done (delete after logging - see the rules above)

(none; the finished tasks are logged in `research/cloud/LOG.md`)
