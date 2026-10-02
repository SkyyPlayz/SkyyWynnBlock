# Test now - what has not been tested in game yet

Cloud summary, 2026-10-02. Source: `RESUME.md` section 2 ("Not tested in game yet (deployed 2026-10-01)"), `HANDOFF.md` line 215 ("the 2026-10-01 deploys are not tested; older
sections were tested or superseded") and the newest sections of `TEST-CHECKLIST.md` (lines 1027-1097). I only read the docs; I cannot know what Skyy has since tried.
Older deploys (Accessories 0.5 and Skills 0.4.9 from 2026-09-30 and before) are treated as tested.

**Order = riskiest first** (risk = what breaks or is lost if it is wrong). Full numbered steps stay in TEST-CHECKLIST.md; the "Do this" column is the shortest useful check.

| # | Mod and version | Risk | Why it is risky | Do this (2-5 minutes) | Needs | Full steps |
|---|---|---|---|---|---|---|
| 1 | **SkyyProfiles 0.1.5** (delete + 6 h undo) | **High** - lost profile data; rollback floor 0.1.5 once anything was deleted | Deleting archives a whole profile (island, coins, skills, bags, items); restore must bring it back exactly; slot limit can be gamed | Make a throwaway profile with an item and coins. /profiles -> Delete it -> check the greyed card, slot freed -> Restore -> switch to it: everything back. Then try the "all slots used" refusal | one spare profile | TEST-CHECKLIST 1027, steps 1-4 |
| 2 | **SkyyIslands 0.5.5** (deleted owner closes the island) | **High** - players kicked, island access | Needs a second player; deleting a profile sends visitors away and closes the island; restoring must reopen it | With Wesley as co-op member: delete the owner profile -> Wesley cannot visit/warp and is sent away within ~5 s; restore -> he can go again | **second player** | TEST-CHECKLIST 1085, steps 1-4 |
| 3 | **SkyyGuilds 0.1.5 -> 0.1.6** (money refunds, Contribution) | **High** - coins | One-time history seed, % disband refunds, 35% leave refund, kick refunds to offline members' active profile | Check one GodSquad seed line in the log; /guild shows Contribution; deposit 1,000 and leave: confirm says 350 back and the purse gets +350; try a disband split | second member helps | TEST-CHECKLIST 1045 + 1085 (steps 5-8) |
| 4 | **SkyyGear 0.1.3** (59 level rows + unidentified chest gear) | **Medium-high** - config migration + loot | Migration appends 59 rows once (undoable, has a History snapshot); every world chest weapon/armor now unidentified; own chests/vault/bags must stay untouched | Log line "added 59 level family rows" once; Server Setup -> Gear -> Levels shows them; open a prebuilt chest: gear unidentified; open your own chest: untouched | a structure chest | TEST-CHECKLIST 1064 |
| 5 | **SkyyMenu 0.3.4** (menu item per profile, seconds in Server Setup) | **Medium** - duplicate or missing items; setting migration | Item arrives within ~6 s per profile; must never duplicate on world switch/relog; seconds editing has validation rules | Switch profile: one item arrives once. Relog twice: no extra copy. /modconfig -> Skills Advanced: jump cooldown 0.8; type 0.19 (refused), 0.24 (saved), Undo | two profiles | TEST-CHECKLIST 1055 |
| 6 | **SkyyAccessories 0.5.2 + SkyySacks 0.7.10** (Workbench "Accessories & Bags" tab; Charcoal -> Smithing bag) | **Medium** - items auto-moved | Charcoal is auto-moved into the Smithing bag when picked up; the new Workbench tab order; crafting recipes unchanged | Open a Workbench: new bag-icon tab at the right end, check the order; craft one accessory and one bag; with a Smithing bag pick up charcoal into the main inventory: it moves in ~2 s | charcoal, Smithing bag | TEST-CHECKLIST 1077 |
| 7 | **SkyySkills 0.4.11** (Priest heal XP 1 / 1.25) | **Low-medium** - XP file migration | Changes 3 xp.properties lines once; heal XP no longer x3 | Log has one "xp.properties updated" line; /skills -> Divinity shows the 1 / 1.25 / 900 text; heal a party member: Divinity XP = HP healed | Priest + a party member | TEST-CHECKLIST 1072 |
| 8 | **SkyyClasses 0.1.10** (Warrior Wood Shield, Priest self-heal 100%) | **Low** | New Warrior kit puts a shield in the off-hand; re-giving a kit while holding it must not duplicate | New Warrior profile: sword in hotbar, shield in off-hand, right click guards; /classadmin kit again: second shield goes to hotbar. Priest: own heal = member heal | new Warrior and Priest profile | TEST-CHECKLIST 1038 |

## Suggested sessions (so Skyy can batch them)

| Session | Includes | Time | Notes |
|---|---|---|---|
| A - alone | 1 (Profiles), 4 (Gear), 5 (Menu), 6 (Workbench tab), 7 (Skills if a Priest profile exists), 8 (Classes) | about 20 min | One throwaway profile covers 1, 5, 8 |
| B - with Wesley | 2 (Islands), 3 (Guilds) | about 15 min | Both need a second player; do them in one go |

## Things to send back after testing (helps the local session)

- Screenshots of: the greyed deleted-profile card (1), the Contribution column (3), the Workbench new tab (6).
- The first-start log lines named above (they prove each one-time migration ran exactly once).
- Anything that looks cut off ("..." labels on Profiles Delete/Switch: TEST-CHECKLIST 1027 step 7).
- If a number looks wrong (refund, XP), the exact value shown.

## Not tested but waiting on something else

| Item | Waiting on |
|---|---|
| Class skill XP curve, Gear 0.2, mob levels, pets, Pocket Shards | built after the weekly usage reset on 2026-10-06 (RESUME.md section 3) - nothing to test yet |
| Rollback reminder | Never roll SkyyProfiles below 0.1.5 once a profile was deleted (`tools/deploy_set.py` floors) |

## For the local session

I could not check game state, deploy backups or logs. Verify the "not tested" list with Skyy before relying on it; if some of these were tested after the RESUME note, tick them off here and in TEST-CHECKLIST.
