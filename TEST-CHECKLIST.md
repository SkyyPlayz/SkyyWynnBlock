# SKYY'S TEST CHECKLIST

Short version since 2026-10-05. The numbered in-game steps live in `docs/tests/<period>.md` (word for word); every section ever written is
listed in [docs/tests/README.md](docs/tests/README.md). Each deploy adds ONE section at the END of the newest month file
(`docs/tests/2026-10.md`) and one line under "Test next" below; a line leaves this list once Skyy has tested it (log the result in
`docs/log/<YYYY-MM>.md`).

## Test next - deployed, no test result logged yet (as of 2026-10-05)

All steps are in `docs/tests/2026-10.md` - search the section name.

1. SkyyProfiles 0.1.5 - delete a profile + 6-hour undo (ROLLBACK FLOOR once you delete one).
2. SkyyClasses 0.1.10 - Warrior Wood Shield in the kit; Priest self-heal 100%.
3. SkyyGuilds 0.1.5 + 0.1.6 - % disband refunds, Contribution column, 35% leave refund.
4. SkyyMenu 0.3.4 - the menu item per profile; Server Setup times in seconds.
5. SkyySkills 0.4.11 - Priest heal XP 1 / 1.25 per HP.
6. SkyyAccessories 0.5.2 + SkyySacks 0.7.10 - Workbench "Accessories & Bags" tab; Charcoal goes in the Smithing bag.
7. SkyyIslands 0.5.5 - a deleted owner's island closes to co-op members.
8. Phase 1 of the 2026-10-02 answers - SkyyCollections 0.2.5 (coins never buy tiers / recipes / bags) + SkyyEssentials 0.1.7 (bags
   blocked in /trade). (Auto-refill and the Skills widget from the same section are already seen working.)
9. SkyyMenu 0.3.5 - the Mods list matches today's versions.
10. SkyyHud 0.3.13 - small widget boxes (Game Clock reaches the corner) + combat widget colours.
11. SkyyTrees 0.3 - the Alchemy + Smithing trees (the class-tree probe page is already seen).
12. SkyyMobs 0.1.3 - the mob health bar follows a live Strength change (the Gear 0.2.2 half of that section is seen).

Already seen working since 2026-10-01 (details in `docs/log/2026-10.md`): SkyyMobs 0.1 / 0.1.1 / 0.1.2, SkyySacks 0.7.11 refill + 0.7.12
bench + inventory crafting, SkyySkills 0.4.12 - 0.4.15, SkyyHud 0.3.11 + 0.3.12, SkyyBank 0.1.6, SkyyWorldGen 0.1, SkyyMenu 0.3.6,
SkyyCooking 0.1.4, SkyyBazaar 0.1.3, SkyyArmory 0.1 staffs + wands, SkyyTrees 0.3.1 probe page, SkyyGear 0.2.2 tooltips, SkyyUiProbe 0.4
minimap probes, SkyyAccessories 0.5.4 Lantern.

## If anything crashes or misbehaves
Send the newest `...\Saves\HUD mod\logs\<time>_server.log` (and the client log from `UserData\Logs`) plus a screenshot; fixes from Skyy's
tests always come first.
