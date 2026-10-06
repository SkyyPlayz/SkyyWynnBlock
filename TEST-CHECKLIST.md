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
5. SkyyGear 0.1.3 - every world-chest weapon / armor drops unidentified; the 59 non-metal level rows in Server Setup -> Gear -> Levels.
6. SkyySkills 0.4.11 - Priest heal XP 1 / 1.25 per HP.
7. SkyyAccessories 0.5.2 + SkyySacks 0.7.10 - Workbench "Accessories & Bags" tab; Charcoal goes in the Smithing bag.
8. SkyyIslands 0.5.5 - a deleted owner's island closes to co-op members.
9. Phase 1 of the 2026-10-02 answers - SkyyCollections 0.2.5 (coins never buy tiers / recipes / bags) + SkyyEssentials 0.1.7 (bags
   blocked in /trade). (Auto-refill and the Skills widget from the same section are already seen working.)
10. SkyyMenu 0.3.5 / 0.3.6 - the Mods list matches today's versions (0.3.6's stuck-page fix is already seen; the list itself is not).
11. SkyyHud 0.3.13 - small widget boxes (Game Clock reaches the corner) + combat widget colours.
12. SkyyTrees 0.3 - the Alchemy + Smithing trees (the class-tree probe page is already seen).
13. SkyyMobs 0.1.3 - the mob health bar follows a live Strength change (the Gear 0.2.2 half of that section is seen).
14. SkyyCooking 0.1.4 - food Grade strength (+32% per Grade); you saw the XP rate (still too fast - tuned live), not the Grade strength.
15. SkyyBazaar 0.1.3 - the Smithing tab, every bag item listed, processed goods +20% (you only said "bizzar looks good").
16. SkyySkills 0.4.15 - class Mana pools (Priest +5 / Mage +10 max Mana per class level); staffs work, the pools were not checked.
19. SkyyExploration 0.2.3 - Overview never sticks on "Loading..." (also after world changes).
20. SkyyMenu 0.3.7 - Mods list says Lantern, lists SkyyArmory, today's versions.
21. SkyyCollections 0.2.6 - /collections top hides deleted (undo window) and archived profiles.
22. SkyyGear 0.2.3 - crafting weapons + armor pays Smithing XP (10 Iron wands = ~2,500+); wand tooltip follows Armory damage edits.
23. SkyyBazaar 0.1.4 - progression prices (ores / logs / crops / seeds / saplings / hides / cloth x2 per tier).
24. SkyyParty 0.1.7 + SkyyEssentials 0.1.8 - TPA button per party member + Accept TPA (needs 2 players).
25. SkyySkills 0.4.16 - Mining's own slower curve (your Mining levels go up once, with coins); no Mining XP boost.
26. SkyyTrees 0.3.2 + SkyyMenu 0.3.8 - class trees are ON (/tree class); the Mods list shows today's versions.
27. Pack mods HyFishing + Dynamic Seasons + NoCube's Orchard - no errors; fishing, seasons, orchard work next to our mods.
28. SkyyCollections 0.2.7 + SkyyAccessories 0.5.6 - Lantern recipes unlock at Tree Sap tiers I / III / V / VIII; locks follow profile switches.
29. SkyyBazaar 0.1.5 + SkyySacks 0.7.13 - sell straight from your bags (sap, ore ...); Buy/Sell buttons use Hytale stacks (ore 25).

Already seen working since 2026-10-01 (details in `docs/log/2026-10.md`): SkyyMobs 0.1 / 0.1.1 / 0.1.2, SkyySacks 0.7.11 refill + 0.7.12
bench + inventory crafting, SkyySkills 0.4.12 - 0.4.14, SkyyHud 0.3.11 + 0.3.12, SkyyBank 0.1.6, SkyyWorldGen 0.1, SkyyMenu 0.3.6
(stuck-page fix), SkyyArmory 0.1 staffs (+ the Iron wand in play), SkyyTrees 0.3.1 probe page, SkyyGear 0.2.2 tooltips, SkyyUiProbe 0.4
minimap probes, SkyyAccessories 0.5.4 Lantern, SkyyAccessories 0.5.5 Lantern edges (2026-10-05), SkyySkills 0.4.16 Mining
level-up payout (log + coins checked 2026-10-05), SkyyCooking 0.1.5 + 0.1.6 XP (skewers + Flour, 2026-10-05).

## If anything crashes or misbehaves
Send the newest `...\Saves\HUD mod\logs\<time>_server.log` (and the client log from `UserData\Logs`) plus a screenshot; fixes from Skyy's
tests always come first.
