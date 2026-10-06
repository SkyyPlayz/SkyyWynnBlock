# Hytale 0.7 (Update 7 / Chapter 1) Watch

Cloud draft, 2026-10-06. Paper research; nothing built or tested. Inputs read: `research/PreRelease-Compat-Audit-1002.md` (sections 1, 4, 5, 7, 8; our own bytecode check of 0.7.0-pre.4), `research/cloud/Zone-Specials-Spec.md` (style). Web: search snippets only (hytale.com, supercraft.host, bisecthosting, massivelyop were blocked for page fetch), so wording below is from snippets, not full patch notes. Every item is marked **CONFIRMED** (official source or Hytale's own notes quoted by a secondary site) or **RUMOUR / UNCLEAR**.

Naming: Hytale says "Update N". Our jar numbers are 0.N.x. Update 6 = 0.6.x (our 0.6.8). **Update 7 = 0.7.0 = "Chapter 1".**

## 1. Bottom line

- **Chapter 1 / Update 7 ships Monday 2026-10-12, six days from today.** Date announced 2026-09-24 with a teaser trailer.
- The audit (2026-10-02) already tested pre.4: all 24 jars load; **3 engine methods are gone** (Islands, Menu, Profiles break); 9 rebuilds stop on new data. The fix list is ready (Audit section 7).
- Official notes warn plugin authors of removed chunk / block methods and renamed types. That matches what our audit found. Whatever pre-release build ships on the 12th may differ from pre.4, so **re-run the link check on the real release jar** (section 5).
- Nothing found yet about a *later* update (0.8+). See section 4.

## 2. CONFIRMED timeline

| Date | Event | Source |
|---|---|---|
| 2026-01-13 | Early Access launch. | [PCGamesN roadmap](https://www.pcgamesn.com/hytale/roadmap), [Wabbanode](https://wabbanode.com/blog/hytale/hytale-server-hosting-january-2026) |
| 2026-01-17 | Update 1 "Legacy & Lore". | [mein-mmo](https://mein-mmo.de/hytale-erstes-grosses-update-kommt/) |
| 2026-05/06 | Update 5: controller support, Server Discovery, social sidebar, Trigger Volume tool, audio pitch shift, world-gen V2 thread allocation. | [BisectHosting](https://www.bisecthosting.com/de-de/blog/hytale-update-5-patch-notes-release-date-social-tools-pre-release) |
| 2026-08-27 | **Update 6 released.** In-game mod browser (6,203 mods at launch), five Hardcore rule sets, 16M-block builder selections, server crash-recovery settings, runtime controls for world gen and view distance. Packet layouts changed during its pre-release. | [MassivelyOP](https://massivelyop.com/2026/08/21/hytale-brings-update-6-next-week-with-a-hardcore-mode-and-network-improvements/), [G-Portal](https://www.g-portal.com/en/news/hytale-update-6-hardcore-mod-browser-en), [Survival Servers](https://www.survivalservers.com/news/hytale-update-6/) |
| 2026-09-03 | **Update 7 pre-release, Part 1 / wave 1** opens (Launcher > Settings > Pre-Release). Notes later extended through 2026-09-24. | [hytale.com pre-release notes (Update 7)](https://hytale.com/news/2026/9/pre-release-patch-notes-update-7), [Supercraft](https://supercraft.host/wiki/hytale/hytale_update_7_pre_release_chapter_1/) |
| 2026-09-24 | **Chapter 1 date announced: 2026-10-12.** | [Shockbyte](https://shockbyte.com/blog/hytale-chapter-1-release-date), [MassivelyOP](https://massivelyop.com/2026/09/25/hytales-update-7-brings-a-new-dungeon-and-tweaks-to-items-and-enemies-october-12/), [MMOHuts](https://mmohuts.com/news/hytales-chapter-1-update-arrives-october-12-with-goblin-dungeon-and-rune-abilities) |
| 2026-10-12 | **Chapter 1 / Update 7 release.** | same |

## 3. What Update 7 changes (CONFIRMED, by area)

| Area | What the sources say | Source |
|---|---|---|
| Plugin API | The pre-release notes "remove or lock a long list of older chunk and block methods, so a plugin still calling them will not compile." Types are renamed (`DurabilityOperator` becomes `ComparisonOperator`). Method signatures plugin authors override changed. "Expect some plugins to stop loading until their authors release a new version." | [hytale.com notes](https://hytale.com/news/2026/9/pre-release-patch-notes-update-7) via search summary |
| Combat / items | **Rune Ability system** (collect runes, slot in a Runebinder's Effigy). First five: Enrage, Fireball, Imbue Poison, Ground Slam, Wind Strike. Studio says it "is expected to change a lot before Chapter 1 releases". | [Supercraft](https://supercraft.host/wiki/hytale/hytale_update_7_pre_release_chapter_1/), [BisectHosting](https://www.bisecthosting.com/blog/hytale-update-7-patch-notes-highlights-more) |
| Items | Goblin gadgets: Scrap Drill, Spyglass, Scrap Glider, Rocket Boots (double jump), Hookshot + Hook Anchors. Gliders keep momentum and can dive / ascend. New blocksets. | [Switchblade Gaming](https://www.switchbladegaming.com/hytale/update-7-patch-notes-rune-abilities/) |
| Mobs / content | Six Goblin NPCs (Scrapper, Miner, Guardian, Lobber, Burner, Feastmaster), a new goblin dungeon, "tweaks to items and enemies". | same, MassivelyOP link in section 2 |
| Server rules | "Live server rule changes" (runtime-changeable settings; follows Update 6's runtime world-gen / view-distance controls). Details not seen. | [Supercraft](https://supercraft.host/wiki/hytale/hytale_update_7_pre_release_chapter_1/) snippet |

Not found in any snippet (so **no confirmed statement**): permissions-system changes, networking / packet changes in Update 7, entity-stat API changes, world-gen API changes. Our own audit found the stat / HUD side (vanilla Mana max 0 to 100, HUD redone) from the jar itself; that is a verified fact about pre.4, not an official announcement.

## 4. Later than 0.7 (what is announced)

| Item | Status | Source |
|---|---|---|
| **UI moving to NoesisGUI** (XAML, asset-driven, server-modifiable benches, tab menu, inventories) | CONFIRMED as a plan from a dev Q&A. One snippet says "update 6"; it did **not** visibly land in 0.6.8 or the 0.7 pre-release as far as our audit shows (Audit found the Custom UI kit still working). Treat the timing as unknown. The studio says the legacy custom UI "will not be removed in the near future but will eventually be retired." | [hytalemodding.dev Q&A](https://hytalemodding.dev/en/docs/qna/26-05-2026), [CurseForge FAQ](https://blog.curseforge.com/hytale-faq-answered-by-simon-and-slikey-from-hypixel-studios/) |
| Minigames, machinima tools, server-side custom UI "within the next few months" | CONFIRMED as a dev tease (no dates) | [KitGuru](https://www.kitguru.net/gaming/matthew-wilson/hytale-devs-tease-magic-system-mod-support-and-more-ahead-of-chapter-1-update/) |
| Full crafting rework "planned for Chapter 2" | CONFIRMED as a plan, no date. Would hit every bench / recipe mod (Sacks, Cooking, Gear). | KitGuru, same link |
| **Server source code release** | Promised Nov 2025 for "1-2 months" after EA; as of May 2026 **not shipped**, no new date. A modding / API Terms of Service is expected with it. We found nothing newer. | [GuildOrder status page](https://guildorder.com/games/hytale/wiki/server-source-release-status) (third party) |
| Specific 0.8 date or feature list | **RUMOUR / none found.** Do not plan around one. | - |

RUMOUR / speculation (label only, not for planning):
- The Rune Ability system and HUD may be reworked again before or after the 12th (the studio itself says it will change). Our class-ability / Mana design depends on it (section 5, Skills).
- Some sites imply the pre-release build changes again between now and the 12th (waves). Plausible, **unconfirmed** for server APIs.

## 5. Per mod area: likely breaks and release-day checks

"Audit" = `research/PreRelease-Compat-Audit-1002.md` against 0.7.0-pre.4 (rev fab7fc95). The audit is bytecode and asset diffs only; nothing ran in game.

| Area (mods) | Likely break (from Audit) | Check on release day |
|---|---|---|
| **UI pages** (Menu, Sacks, Bank, Party, Guilds, Auctions, Bazaar, Vault, Hud) | No custom-UI engine member changed. But 15 kit builds stop at `SUI.verify` (close-X anchor, `tools/skyyui.py` l.2612, 1 of 273 values fails on 0.7). Live jars are unaffected. HUD: vanilla HUD redone, vanilla Mana bar now shows for everyone (max 100). Menu icon `Furniture_Ancient_Chest_Large_Treasure` is gone. | Open every page in game; compare HUD widgets with the new vanilla HUD; check missing-icon placeholders; rebuild one kit page to confirm the verify fix. Watch for the NoesisGUI switch (section 4). |
| **Interactions / projectiles / runes** (Skills, Gear, Classes) | New rune interactions `Ability_ChargedShot_Release_1-4` cost 10 / 20 / 30 / 50 Mana and stop the Skills spell generator. `InteractionContext.getRootInteractionId` now returns the rune cast root (id -11): a rune cast never looks like a charged weapon attack. 21 staffs lost their per-staff charged Mana var. | Cast wand / staff / spellbook and one rune; check Mana drain and class gates; swing a charged weapon after a rune cast. Re-read the rune notes: the system may have changed since pre.4. |
| **Stat modifiers** (Skills, Gear, Accessories) | `EntityStatsSystems$Recalculate`, `StatModifiersManager`, `ArmorDamageReduction` orderings pass. Vanilla Mana Max goes 0 to 100, so Skills' base Mana (`target - vanilla max`, floored 0) gives every class 100 Mana. | Check Mana / Health totals for each class; check accessories still stack; Skyy decision pending (Base Mana). |
| **World gen / zones / mobs** (Exploration, Mobs, Islands, Collections) | `BlockChunk.getEnvironment` deprecated (still works; per-section `EnvironmentSection` is the new read). 12 levelled roles gone; 37 new roles get no level. 9 new goblin chest drop lists have no XP row. **Islands:** `WorldChunk.setBlock(IIILString)` removed and `ChunkLightingManager.invalidateLightInChunk(ChunkStore,..)` removed, so new islands come out empty and unlit. Update 6 / 7 world-gen V2 thread changes are confirmed; we do not use them. | **Brand-new player `/island`** (blocks, chest, kit, light); mob level plates on goblin / void mobs; zone titles (Exploration still uses the deprecated boolean title overload). |
| **Commands / events** (Essentials, Profiles, Ranks, Menu) | `ISpawnProvider.getSpawnPoint(World,UUID)` removed (now `getSpawnPointAsync`): `/hub` without `/sethub`, Menu Spawn, Profiles fallback fail. **`PlayerConnectEvent` is now async** (Profiles join hook may run off-thread). `hytale:Adventurer` permission and `PlayerChatEvent` unchanged. No command-name clash. | `/hub` with and without `/sethub`; Menu > Spawn; profile switch (look for "connect handler failed"); join with a profile; run `tools/ci/crosscheck.py` permission audit. |
| **Item assets** (Gear, Classes, Cooking, Trees, Collections, Exploration) | Gone: `Glider` item, `Objective_Treasure_Map`, `Flamethrower_Goblin`. New: `Weapon_Bangstick`, `Weapon_Longsword_Ruined_Giant`, `Weapon_Flamethrower_Scrap`, Sadwillow trunk, Lime mushroom. Cooking: food buffs now 360 s, `Food_Instant_Heal_Bread` is Percent Health 10. `Skyy_Tree_Chop.json` lacks `Trigger_Explosion_State_Generic`. Collection counts: mushrooms 20, trunks 34. | Rebuild each stopped script and read its assert; spot-check new gear level, dish buffs, hatchet on explosive blocks, collection rows for the two new blocks. |
| **Bridge** (`skyy.bridge` map, plain java.lang types) | No engine member involved. Risk is indirect: a mod that fails to load or rebuild drops its bridge keys. | After deploy, grep logs for each mod's bridge registration; test one cross-mod call per pair (Coins with Bazaar, Islands with Profiles). |

## 6. Release-day checklist

Safe rules first (PROJECT-RULES 1): game closed, never kill it, back up first (`python tools/backup_deploy.py`), deploy only via `python tools/deploy_set.py --yes`.

| # | Step | Pass looks like | Owner |
|---|---|---|---|
| 1 | Confirm 0.7 is the **release** (not only pre-release), note jar version + revision | revision recorded in log | local |
| 2 | Diff the new jar against pre.4 (rev fab7fc95) with the Audit method | no new missing members | local |
| 3 | `crosscheck.py --baseline` (all SET jars, `-Xverify:all`, access + Adventurer audit) | 0 fails | local |
| 4 | Ship the "both versions" fixes first: Islands 0.5.6 (8-arg setBlock, `invalidateLoadedChunks`), Menu 0.3.6 (hub stopgap + icon swap), Profiles travel (Audit sec. 7 items 1, 2, 12) | build, pin, deploy | local |
| 5 | Fix `tools/skyyui.py` l.2612 and bump KIT_VERSION so the 15 UI builds run | `skyyui_test.py` green | local |
| 6 | New-player `/island`, `/hub` (both modes), Menu > Spawn, profile switch | chest, kit, light, warp all work | Skyy |
| 7 | Mana / class check: every class cast, one rune, Mana totals | no Mana line error in log | Skyy |
| 8 | UI look-over: all pages, HUD next to vanilla HUD, icons | no missing icons, no overlap | Skyy |
| 9 | Cooking / Gear / Collections / Exploration / Trees / Mobs / Classes rebuilds (decisions needed, Audit sec. 7 items 4-11) | each build passes its asserts | local |
| 10 | Log, HANDOFF versions table, RESUME, TEST-CHECKLIST section, tidy (PROJECT-RULES 5) | committed + pushed | local |
| 11 | Check Update 7 patch notes again after release for anything not in pre-release | notes read, new rows added to this file | local |

## For the local session (UNVERIFIED)

- Whether the **release jar equals pre.4**. Check the revision; later waves (through 2026-09-24 notes) may have changed more than we tested. Re-run the Audit link check.
- The exact list of removed chunk / block methods in the official notes (hytale.com page was blocked for me). Compare to the 3 methods we found; there may be others our mods do not call.
- Whether `PlayerConnectEvent` really runs on a non-world thread (Audit sec. 9).
- Whether the official notes list **permission, networking, or stat API** changes (none seen in snippets).
- Whether rune abilities still cost Mana and use `Ability_ChargedShot_Release_1-4` at release.
- Whether NoesisGUI shipped in 0.7 and whether the legacy `CustomUIPage` / `.ui` kit still renders (Audit says yes on pre.4).
- Update 6 pre-release notes URL carries a May 2026 date while Update 6 released 2026-08-27: the date string looks inconsistent. Not important, listed so nobody trusts it.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Switch the live modpack to 0.7 the same day (12th) once the "both versions" fixes are deployed, or wait a few days for wave patches? | Wait 2-3 days, then switch. |
| 2 | Rune ability costs: divide like spells, or keep vanilla cost? (Audit decision, still open; the rune system may change.) | Decide after release, keep vanilla until then. |
| 3 | Base Mana: keep "every class has 100 Mana" because vanilla Max is now 100? | Keep, revisit with class abilities. |
| 4 | Should we stay on 0.6.8 for Skyy's test world until fixes are tested, using the pre-release only on a copy? | Yes. |
